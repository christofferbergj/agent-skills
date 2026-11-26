"""What a change is, and how soon each kind reaches the user. A change holds ids, kinds,
states, counts, and staff names only: never a ticket title, a message body, or anything
about a practitioner. `references/scan.md` lists the kinds for people."""
from __future__ import annotations

NOW, BATCH, PULSE = "now", "batch", "pulse"

# kind: (tier, urgent). Urgent kinds are the ones a weekend, or a day past its delta cap,
# still wakes for: a person waiting on the user, a new assignment, a deadline within 24 hours.
KINDS = {
    "ticket.assigned": (NOW, True),
    "ticket.unassigned": (NOW, False),
    "ticket.changed": (NOW, False),
    "ticket.mention": (NOW, True),
    "ticket.comment": (NOW, False),
    "ticket.unblocked": (NOW, False),
    "deadline.soon": (NOW, True),
    "slack.waiting": (NOW, True),
    "pr.review_requested": (NOW, True),
    "pr.changes_requested": (NOW, False),
    "pr.ci_failed": (NOW, False),
    "issue.assigned": (NOW, True),
    "release.awaited": (NOW, False),
    "dependency.changed": (BATCH, False),
    "ticket.new_in_project": (BATCH, False),
    "thread.finished": (BATCH, False),
    "thread.waiting": (BATCH, False),
    "ticket.moved": (PULSE, False),
    "linear.other": (PULSE, False),
    "pr.approved": (PULSE, False),
    "pr.opened": (PULSE, False),
    "pr.closed": (PULSE, False),
    "release.new": (PULSE, False),
    "issue.new": (PULSE, False),
    "thread.waits_on_you": (PULSE, False),
    "team.pulse": (PULSE, False),
    "slack.channel": (PULSE, False),
}
# Kinds that sum into one item per ref instead of arriving one by one.
TALLIES = {"team.pulse", "slack.channel"}


def change(kind: str, ref: str, at: str, key: str = "", scope: str = "", **detail) -> dict:
    """One change. Its id is the same however often the scan sees the same event, so a scan
    that runs twice over it, after a crash, adds it once."""
    if kind not in KINDS:
        raise ValueError(f"unknown change kind {kind}")
    ident = f"{kind}:{ref}" if kind in TALLIES else f"{kind}:{ref}:{key or at}"
    item = {"id": ident, "kind": kind, "ref": ref, "at": at, "detail": detail}
    if scope:
        item["scope"] = scope
    return item


def tier(item: dict) -> str:
    return KINDS[item["kind"]][0]


def urgent(item: dict) -> bool:
    return KINDS[item["kind"]][1]


def _add(into: dict, extra: dict) -> dict:
    out = dict(into)
    for key, value in extra.items():
        if isinstance(value, bool) or not isinstance(value, (int, float, dict)):
            out[key] = value
        elif isinstance(value, dict):
            out[key] = _add(out.get(key) or {}, value)
        else:
            out[key] = (out.get(key) or 0) + value
    return out


def gather(items: list[dict], new: list[dict], seen: dict) -> list[dict]:
    """items plus new: a tally adds its counts to the item with its id; any other change
    joins once, skipping an id already gathered, in flight, or delivered (`seen`)."""
    out = [dict(item) for item in items]
    index = {item["id"]: i for i, item in enumerate(out)}
    for item in new:
        if item["kind"] in TALLIES and item["id"] in index:
            old = out[index[item["id"]]]
            out[index[item["id"]]] = {**old, "at": item["at"], "detail": _add(old["detail"], item["detail"])}
        elif item["id"] not in index and item["id"] not in seen:
            index[item["id"]] = len(out)
            out.append(item)
    return out


def muted(item: dict, mutes: list[dict], now: str) -> bool:
    """A mute names a ref (DEV-12, owner/repo#3), a scope (slack:C123), or a kind."""
    for mute in mutes:
        if mute.get("until") and mute["until"] <= now:
            continue
        if mute.get("ref") in (item["ref"], item.get("scope"), item["kind"]):
            return True
    return False
