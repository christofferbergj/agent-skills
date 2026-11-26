"""Linear: the user's inbox as the event feed, their open tickets with relations and status
history, the tickets those depend on, and each listed team's changes since the last scan.
Reads only; never marks an inbox item read. Keeps ids, states, and staff names, never titles."""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from ..calls import Executor, SourceError
from ..changes import change
from ..times import iso, parse

TOOLS = ("tools.linear.get_notifications", "tools.linear.list_issues", "tools.linear.get_issue")
ISSUE = re.compile(r"/issue/([A-Z][A-Z0-9]*-\d+)")
CLOSED = {"completed", "canceled", "duplicate"}
PAGES = 20  # at most 1,000 inbox items or 5,000 team updates a scan
TEAM_MEMORY = timedelta(days=30)
# Inbox type → change kind; any other type is `linear.other`, shown in the pulse.
INBOX = {
    "issueAssignedToYou": "ticket.assigned",
    "issueUnassignedFromYou": "ticket.unassigned",
    "issueStatusChanged": "ticket.changed",
    "issueCommentMention": "ticket.mention",
    "issueMention": "ticket.mention",
    "issueNewComment": "ticket.comment",
}  # Due dates and blockers come from the tickets themselves, so their inbox items aren't repeated.
MINE_FIELDS = ["id", "status", "statusType", "priority", "dueDate", "assigneeId", "updatedAt", "project", "team"]
TEAM_FIELDS = ["id", "status", "statusType", "assignee", "assigneeId", "createdAt", "updatedAt", "completedAt",
               "project"]


def _iso(moment: datetime) -> str:
    return iso(moment, ms=True)


def _priority(value) -> int | None:
    return value.get("value") if isinstance(value, dict) else value


def _pages(executor: Executor, tool: str, args: dict, key: str, stop=None) -> list[dict]:
    """Every item across up to PAGES pages; `stop(item)` ends the walk early."""
    items, cursor = [], None
    for _ in range(PAGES):
        page = executor.call([(tool, {**args, **({"cursor": cursor} if cursor else {})})])[0]
        if not isinstance(page, dict) or not isinstance(page.get(key), list):
            raise SourceError(f"{tool} returned no {key} list")
        items.extend(page[key])
        cursor = page.get("cursor")
        if not page.get("hasNextPage") or not cursor or (stop and any(stop(item) for item in page[key])):
            break
    return items


def scan(source: dict, prev: dict | None, ctx) -> tuple[dict, list[dict]]:
    executor = ctx.executor(source, TOOLS)
    now = ctx.now
    baseline = prev is None and ctx.since is None
    prev = prev or {}
    since = parse(prev["at"]) if prev.get("at") else (ctx.since or now)
    changes: list[dict] = []

    # The inbox, newest first, back to the last item already seen.
    inbox_at = prev.get("inbox_at") or _iso(since)
    known = set(prev.get("inbox_ids", []))
    notes = _pages(executor, TOOLS[0], {"limit": 50}, "notifications", stop=lambda n: n.get("createdAt", "") < inbox_at)
    fresh = [n for n in notes if n.get("createdAt", "") >= inbox_at and n.get("id") not in known]
    status_noted = {m.group(1) for n in fresh if n.get("type") == "issueStatusChanged"
                     for m in [ISSUE.search(n.get("url") or "")] if m}
    newest = max([n.get("createdAt", "") for n in notes] + [inbox_at])
    inbox_ids = sorted({n["id"] for n in notes if n.get("createdAt") == newest} | (known if newest == inbox_at else set()))

    # The user's open tickets.
    listed = _pages(executor, TOOLS[1], {"assignee": "me", "limit": 250, "fields": MINE_FIELDS}, "issues")
    open_mine = [i for i in listed if i.get("statusType") not in CLOSED]
    me = next((i.get("assigneeId") for i in listed if i.get("assigneeId")), prev.get("me"))
    before = prev.get("mine", {})
    stale = [i["id"] for i in open_mine if baseline or i["id"] not in before or i.get("updatedAt", "") > _iso(since)]
    detail = {i["id"]: i for i in executor.call([(TOOLS[2], {"id": ref, "fields": ["id", "relations", "stateHistory"]})
                                                 for ref in stale])} if stale else {}
    mine = {}
    for issue in open_mine:
        ref = issue["id"]
        old = before.get(ref, {})
        rel = (detail.get(ref) or {}).get("relations") or {}
        blocked_by = sorted(b["id"] for b in rel.get("blockedBy", []) if isinstance(b, dict) and b.get("id")) \
            if ref in detail else old.get("blockedBy", [])
        mine[ref] = {"status": issue.get("status"), "type": issue.get("statusType"),
                     "priority": _priority(issue.get("priority")), "due": issue.get("dueDate"),
                     "project": issue.get("project"), "blockedBy": blocked_by,
                     "updatedAt": issue.get("updatedAt")}
        if baseline:
            continue
        for entry in (detail.get(ref) or {}).get("stateHistory") or []:
            started = entry.get("startedAt") or ""
            if started > _iso(since):
                name = (entry.get("state") or {}).get("name")
                kind = "ticket.changed" if ref in status_noted else "ticket.moved"
                changes.append(change(kind, ref, started, key=f"status@{started}", field="status", to=name))
        if old:
            for field in ("priority", "due"):
                if old.get(field) != mine[ref][field]:
                    changes.append(change("ticket.changed", ref, issue.get("updatedAt") or _iso(now),
                                          key=f"{field}@{issue.get('updatedAt')}", field=field, to=mine[ref][field],
                                          by="unknown"))
    # The inbox items, read against the user's tickets: a status change or a comment counts
    # only on their own ticket, and a status change the history already shows isn't repeated.
    moved = {c["ref"] for c in changes if c["detail"].get("field") == "status"}
    owned = set(mine) | set(before)  # a ticket closed or reassigned since the last scan was still theirs
    for note in [] if baseline else fresh:
        found = ISSUE.search(note.get("url") or "")
        ref = found.group(1) if found else "linear"
        kind = INBOX.get(note.get("type", ""), "linear.other")
        if kind in ("ticket.changed", "ticket.comment") and ref not in owned:
            kind = "linear.other"
        if kind == "ticket.changed" and ref in moved:
            continue
        changes.append(change(kind, ref, note["createdAt"], key=note["id"], type=note.get("type")))

    # Deadlines within 24 hours, each due date once.
    deadlines = dict(prev.get("deadlines", {}))
    for ref, issue in mine.items():
        due = issue.get("due")
        if not due:
            continue
        end = datetime.fromisoformat(due).replace(tzinfo=ctx.tz) + timedelta(days=1)
        if timedelta(0) < end - now <= timedelta(hours=24) and deadlines.get(ref) != due:
            deadlines[ref] = due
            if not baseline:
                changes.append(change("deadline.soon", ref, _iso(now), key=due, due=due))
    deadlines = {ref: due for ref, due in deadlines.items() if ref in mine}

    # Tickets the user's work waits on: typed blocked-by relations, and the ones the user confirmed.
    depends = {}
    for ref, issue in mine.items():
        for blocker in issue["blockedBy"]:
            depends.setdefault(blocker, set()).add(ref)
    for pair in ctx.ledger.get("depends", []):
        if pair.get("ticket") in mine and pair.get("on"):
            depends.setdefault(pair["on"], set()).add(pair["ticket"])
    # A blocker this scan can't read keeps its last state, so one deleted ticket can't stop the source.
    order = sorted(depends)
    fetched = executor.call([(TOOLS[2], {"id": ref, "fields": ["id", "status", "statusType", "assignee", "updatedAt"]})
                             for ref in order], partial=True) if depends else []
    deps, old_deps = {}, prev.get("deps", {})
    for ref, issue in zip(order, fetched):
        if not isinstance(issue, dict):
            if ref in old_deps:
                deps[ref] = old_deps[ref]
            continue
        deps[ref] = {"status": issue.get("status"), "type": issue.get("statusType"), "owner": issue.get("assignee")}
        moment = issue.get("updatedAt") or deps[ref]["status"]
        old = old_deps.get(ref)
        if baseline or not old or old.get("status") == deps[ref]["status"]:
            continue
        for blocked in sorted(depends[ref]):
            if deps[ref]["type"] in CLOSED:
                changes.append(change("ticket.unblocked", blocked, _iso(now), key=f"{ref}@{moment}",
                                      blocker=ref, to=deps[ref]["status"]))
            else:
                changes.append(change("dependency.changed", ref, _iso(now), key=f"{moment}@{blocked}",
                                      blocks=blocked, before=old.get("status"), to=deps[ref]["status"],
                                      owner=deps[ref]["owner"]))

    # Each team's movement since the last scan, as a pulse, and new tickets in the user's projects.
    team = {ref: seen for ref, seen in prev.get("team", {}).items() if seen[1] >= _iso(now - TEAM_MEMORY)}
    projects = {issue["project"] for issue in mine.values() if issue.get("project")}
    for name in source.get("teams", []):
        if baseline:
            break
        updated = _pages(executor, TOOLS[1], {"team": name, "updatedAt": _iso(since), "limit": 250,
                                              "fields": TEAM_FIELDS}, "issues")
        people: dict = {}
        new = 0
        for issue in updated:
            ref, status = issue.get("id"), issue.get("status")
            old = team.get(ref)
            team[ref] = [status, _iso(now)]
            if issue.get("assigneeId") == me or ref in mine:
                continue
            who = issue.get("assignee") or "unassigned"
            # A move needs the status this scan saw before; a finish needs only its completion time.
            moved = bool(old and old[0] != status)
            finished = issue.get("statusType") == "completed" and (issue.get("completedAt") or "") > _iso(since)
            if moved or finished:
                tally = people.setdefault(who, {"moved": 0, "finished": 0})
                tally["moved"] += moved or finished
                tally["finished"] += finished
            if issue.get("createdAt", "") > _iso(since):
                if issue.get("project") and issue["project"] in projects:
                    changes.append(change("ticket.new_in_project", ref, issue["createdAt"], project=issue["project"]))
                else:
                    new += 1
        if people or new:
            changes.append(change("team.pulse", name, _iso(now), key=_iso(since), people=people, new=new))
    state = {"at": _iso(now), "inbox_at": newest, "inbox_ids": inbox_ids, "me": me, "mine": mine,
             "deps": deps, "deadlines": deadlines, "team": team}
    return state, changes
