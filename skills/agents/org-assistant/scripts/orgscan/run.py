"""One scan of one organisation: read every source, gather what changed, settle the batch
already sent, and wake the assistant thread when decide() says so. `references/scan.md`
describes the files and the failure rules this follows."""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import store
from .calls import Executor, SourceError, run
from .changes import TALLIES, gather, muted
from .decide import decide
from .sources import ADAPTERS, PLANNED
from .sources import t3 as t3_source

ACTIVE = {"preparing", "queued", "starting", "running", "waiting"}  # T3 runs still under way
SEEN_FOR = timedelta(days=7)
EMPTY_PENDING = {"sent": None, "gathered": [], "seen": {}}


class Context:
    def __init__(self, profile: dict, now: datetime, ledger: dict):
        self.profile, self.now, self.ledger = profile, now, ledger
        self.tz = ZoneInfo(profile["timezone"])
        self.schedule = profile["schedule"]
        self.thread = profile.get("thread", "")
        self.since: datetime | None = None
        self.command = profile.get("executor", {}).get("command", [])

    def executor(self, source: dict, tools) -> Executor:
        if not self.command:
            raise SourceError("the profile has no [executor] command")
        return Executor(self.command, {**source, "tools": [t for t in source.get("tools", tools) if t in tools]})


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _local(value: str | None, tz) -> str:
    if not value:
        return "never"
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(tz).strftime("%a %d %b %H:%M")


def health_line(snapshot: dict, tz) -> str:
    parts = []
    for name, state in sorted(snapshot.get("health", {}).items()):
        if state.get("ok"):
            parts.append(f"{name} ok")
        else:
            reason = "sign-in expired" if state.get("error") == "auth" else "failing"
            parts.append(f"{name} {reason} ×{state.get('failures', 1)}")
    return " · ".join(parts + [f"scanned {_local(snapshot.get('last_scan'), tz)}"])


def wake_message(org: str, batch: dict, snapshot: dict, tz) -> str:
    refs = ", ".join(f"{item['kind']} {item['ref']}" for item in batch["items"][:12])
    more = f", and {len(batch['items']) - 12} more" if len(batch["items"]) > 12 else ""
    return (f'<org-assistant org="{org}" batch="{batch["id"]}" kind="{batch["kind"]}" try="{len(batch["tries"]) + 1}">\n'
            f"Use /org-assistant: post batch {batch['id']} from pending.json, then mark it delivered.\n"
            f"Why now: {batch['reason']}. {len(batch['items'])} items{': ' + refs + more if refs else ''}.\n"
            f"Health: {health_line(snapshot, tz)}\n</org-assistant>\n")


def _batch_id(org: str, now: datetime, pending: dict) -> str:
    base = f"{org}-{now.strftime('%Y%m%d-%H%M')}"
    taken = {(pending.get("sent") or {}).get("id")}
    ident, n = base, 1
    while ident in taken:
        n += 1
        ident = f"{base}-{n}"
    return ident


def _delivered(ledger: dict) -> set:
    return {ledger.get("last_delivered")} | {d.get("batch") for d in ledger.get("delivered", [])}


def _settle(pending: dict, now: datetime) -> None:
    """Moves the sent batch's ids into `seen`, so the same events never join a later batch."""
    for item in pending["sent"]["items"]:
        if item["kind"] not in TALLIES:
            pending["seen"][item["id"]] = _iso(now)
    pending["last_delivered"] = pending["sent"]["id"]
    pending["sent"] = None


def scan_org(org: str, now: datetime, dry_run: bool = False, inline: bool = False,
             since: timedelta | None = None, out=sys.stdout) -> int:
    """Scans one organisation; returns 1 when the unit should fail, else 0."""
    try:
        profile = store.load_profile(org)
    except store.ProfileError as error:
        print(f"org-assistant: {error}", file=sys.stderr)
        return 1
    folder = store.state_dir(org)
    if dry_run:  # reads only, so it needs no lock and creates no folder
        return _scan(org, profile, folder, now, dry_run, inline, since, out)
    with store.locked(folder) as held:
        if not held:
            print(f"org-assistant: {org}: another scan holds the lock; skipping this one", file=sys.stderr)
            return 0
        return _scan(org, profile, folder, now, dry_run, inline, since, out)


def _scan(org, profile, folder, now, dry_run, inline, since, out) -> int:
    snapshot = store.read_json(folder / "snapshot.json", None)
    first = snapshot is None and since is None  # --since stands in for a snapshot from that long ago
    snapshot = snapshot or {"sources": {}, "health": {}, "meta": {}}
    pending = {**EMPTY_PENDING, **store.read_json(folder / "pending.json", {})}
    ledger = store.read_json(folder / "ledger.json", {})
    ctx = Context(profile, now, ledger)
    schedule = profile["schedule"]
    failed = []
    found: list[dict] = []
    for source in profile["sources"]:
        name, kind = source["name"], source["kind"]
        prev = snapshot["sources"].get(name)
        ctx.since = now - since if since and prev is None else None
        try:
            adapter = ADAPTERS.get(kind)
            if adapter is None:
                raise SourceError(PLANNED.get(kind, f"no adapter for kind {kind!r}"))
            section, changes = adapter(source, prev, ctx)
        except SourceError as error:
            old = snapshot["health"].get(name, {})
            count = old.get("failures", 0)
            snapshot["health"][name] = {"ok": False, "at": old.get("at"), "failures": count + 1,
                                        "error": "auth" if error.auth else "failed", "message": str(error)[:200]}
            print(f"org-assistant: {org}: {name}: {error}", file=sys.stderr)
            if count + 1 >= schedule["source_failures"]:
                failed.append(f"{name} failed {count + 1} scans in a row")
            continue
        snapshot["sources"][name] = section
        snapshot["health"][name] = {"ok": True, "at": _iso(now), "failures": 0}
        found.extend({**change, "source": name} for change in changes)
    snapshot["health"] = {k: v for k, v in snapshot["health"].items() if k in {s["name"] for s in profile["sources"]}}
    snapshot["last_scan"] = _iso(now)
    meta = snapshot.setdefault("meta", {})

    sent = pending["sent"]
    cutoff = _iso(now - SEEN_FOR)
    pending["seen"] = {k: at for k, at in pending["seen"].items() if at >= cutoff}
    flight = {item["id"]: True for item in sent["items"]} if sent else {}
    pending["gathered"] = [item for item in gather(pending["gathered"], found, {**pending["seen"], **flight})
                           if not muted(item, ledger.get("mutes", []), _iso(now))]

    thread = profile.get("thread", "")
    shown = t3_source.show(thread) if thread and not inline else None
    if thread and not inline and shown is None:
        print(f"org-assistant: {org}: can't read the assistant thread {thread}", file=sys.stderr)
    # A dry run with no thread yet decides as if an idle thread were there.
    busy = (shown is None or shown.get("status") in ACTIVE) if thread else not dry_run
    local = now.astimezone(ctx.tz)
    send = None
    note = ""
    if sent and sent["id"] in _delivered(ledger):
        _settle(pending, now)
        sent = None
    if inline:
        items = (sent["items"] if sent else []) + pending["gathered"]
        sent = pending["sent"] = {"id": _batch_id(org, local, pending), "kind": "inline", "items": items,
                                  "frozen_at": _iso(now), "tries": [], "reason": "scan now", "inline": True}
        pending["gathered"] = []
        note = "inline batch for this run to post"
    elif sent and not busy and sent["id"] in (shown or {}).get("lastText", ""):
        _settle(pending, now)
        sent = None
        note = "the thread's last reply already named the sent batch"
    elif sent and not busy:
        if len(sent["tries"]) >= 1 + schedule["retries"]:
            failed.append(f"batch {sent['id']} undelivered after {len(sent['tries'])} wakes")
            note = "wakes stopped: the sent batch was never delivered"
        else:
            send = sent
            note = "resending the undelivered batch"
    elif sent:
        note = "the sent batch waits for the busy thread"
    kind = items = None
    reason = note
    if sent is None and not first and (thread or dry_run):
        kind, items, reason = decide(local, schedule, meta, ledger, pending["gathered"])
        if kind and busy:
            reason = f"{reason}, held while the thread is busy or unreadable"
        elif kind:
            ids = {item["id"] for item in items}
            sent = pending["sent"] = {"id": _batch_id(org, local, pending), "kind": kind, "items": items,
                                      "frozen_at": _iso(now), "tries": [], "reason": reason}
            pending["gathered"] = [item for item in pending["gathered"] if item["id"] not in ids]
            today, clock = local.date().isoformat(), local.strftime("%H:%M")
            if kind == "overview":
                meta["overview_on"] = today
            else:
                meta.setdefault("deltas", {})[today] = meta.get("deltas", {}).get(today, 0) + 1
            meta.setdefault("slots", {})[today] = sorted(
                {*meta.get("slots", {}).get(today, []), *[s for s in schedule["batch_slots"] if s <= clock]})
            meta["deltas"] = {d: n for d, n in meta.get("deltas", {}).items() if d >= today}
            meta["slots"] = {d: s for d, s in meta["slots"].items() if d >= today}
            send = sent
    elif first:
        reason = "the first scan records a baseline and wakes nothing"
    elif not thread:
        reason = "the profile names no assistant thread, so nothing is sent"

    message = wake_message(org, send, snapshot, ctx.tz) if send else None
    shown_batch = send or (sent if inline else None)
    report = {"org": org, "at": local.isoformat(timespec="minutes"), "first": first, "dry_run": dry_run,
              "wake": (shown_batch or {}).get("kind") if send else None, "reason": reason,
              "batch": (shown_batch or {}).get("id"),
              "items": [{"id": i["id"], "kind": i["kind"], "ref": i["ref"]} for i in (shown_batch or {}).get("items", [])],
              "gathered": dict(Counter(i["kind"] for i in pending["gathered"])),
              "found": dict(Counter(i["kind"] for i in found)),
              "health": health_line(snapshot, ctx.tz), "failed": failed}
    if inline:
        report["batch_items"] = sent["items"]
    if dry_run:
        report["would_send"] = message
        print(json.dumps(report, indent=1, ensure_ascii=False), file=out)
        return 1 if failed else 0

    store.write_json(folder / "pending.json", pending)
    store.write_json(folder / "snapshot.json", snapshot)
    (folder / "scan.stamp").write_text(_iso(now) + "\n")
    if send:
        code, _, err = run(["t3", "thread", "send", thread, "-"], stdin=message)
        send["tries"].append({"at": _iso(now), "ok": code == 0})
        if code != 0:
            print(f"org-assistant: {org}: t3 thread send failed: {err.strip()[:200]}", file=sys.stderr)
        store.write_json(folder / "pending.json", pending)
    print(json.dumps(report, ensure_ascii=False), file=out)
    for reason in failed:
        print(f"org-assistant: {org}: {reason}", file=sys.stderr)
    return 1 if failed else 0
