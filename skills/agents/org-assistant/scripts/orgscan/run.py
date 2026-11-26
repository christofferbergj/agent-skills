"""One scan of one organisation: read every source, gather what changed, settle the batch
already sent, and wake the assistant thread when decide() says so. `references/scan.md`
describes the files and the failure rules this follows.

Everything that decides a send (the batches, the gathered changes, and what today already
sent) lives in pending.json, written before snapshot.json: a crash between the two writes
only makes the next scan read the same events again, and their ids keep them from joining
twice."""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timedelta

from . import store
from .calls import Executor, SourceError, run
from .changes import gather, muted
from .decide import decide, held
from .sources import ADAPTERS, PLANNED, STILL
from .sources import t3 as t3_source
from .times import iso, parse

SEEN_FOR = timedelta(days=7)
INLINE_GRACE = timedelta(minutes=30)  # an inline batch older than this, undelivered, goes back to gathered
THREAD = "assistant thread"  # the health entry for reading the thread itself


class Context:
    def __init__(self, profile: dict, now: datetime, ledger: dict):
        from zoneinfo import ZoneInfo

        self.profile, self.now, self.ledger = profile, now, ledger
        self.tz = ZoneInfo(profile["timezone"])
        self.schedule = profile["schedule"]
        self.thread = profile.get("thread", "")
        self.since: datetime | None = None
        self.command = profile.get("executor", {}).get("command", [])

    def executor(self, source: dict, tools) -> Executor:
        if not self.command:
            raise SourceError("the profile has no [executor] command")
        return Executor(self.command, {**source, "tools": [t for t in source.get("tools", []) if t in tools]})


def _local(value: str | None, tz) -> str:
    return parse(value).astimezone(tz).strftime("%a %d %b %H:%M") if value else "never"


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


def delivered(ledger: dict) -> set:
    return {ledger.get("last_delivered")} | {d.get("batch") for d in ledger.get("delivered", [])}


def _freeze(org: str, pending: dict, local: datetime, kind: str, items: list[dict], reason: str) -> dict:
    """A new batch with an id no earlier batch had, its items taken out of `gathered`."""
    pending["serial"] = pending.get("serial", 0) + 1
    ids = {item["id"] for item in items}
    pending["gathered"] = [item for item in pending["gathered"] if item["id"] not in ids]
    return {"id": f"{org}-{local:%Y%m%d-%H%M}-{pending['serial']}", "kind": kind, "items": items,
            "frozen_at": iso(local), "tries": [], "reason": reason}


def _settle(pending: dict, slot: str, now: datetime) -> None:
    """Moves a delivered batch's ids into `seen`, so the same events never join a later batch."""
    for item in pending[slot]["items"]:
        pending["seen"][item["id"]] = iso(now)
    pending["last_delivered"] = pending[slot]["id"]
    pending[slot] = None


def _unfreeze(pending: dict, slot: str) -> None:
    """Puts an undelivered batch's items back at the front of `gathered`."""
    back = pending[slot]["items"]
    ids = {item["id"] for item in back}
    pending["gathered"] = back + [item for item in pending["gathered"] if item["id"] not in ids]
    pending[slot] = None


def _fail_health(snapshot: dict, name: str, error: SourceError, now: datetime) -> int:
    old = snapshot["health"].get(name, {})
    count = old.get("failures", 0) + 1
    snapshot["health"][name] = {"ok": False, "at": old.get("at"), "failures": count,
                                "error": "auth" if error.auth else "failed", "message": str(error)}
    return count


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
        return Scan(org, profile, folder, now, since).run(dry_run=True, inline=False, out=out)
    with store.locked(folder) as got:
        if not got:
            print(f"org-assistant: {org}: another scan holds the lock; skipping this one", file=sys.stderr)
            return 0
        return Scan(org, profile, folder, now, since).run(dry_run=False, inline=inline, out=out)


class Scan:
    def __init__(self, org: str, profile: dict, folder, now: datetime, since: timedelta | None):
        self.org, self.profile, self.folder, self.now, self.since = org, profile, folder, now, since
        loaded = store.read_json(folder / "snapshot.json", None)
        self.first = loaded is None and since is None  # --since stands in for a snapshot from that long ago
        self.snapshot = loaded or {"sources": {}, "health": {}}
        self.pending = {"sent": None, "inline": None, "gathered": [], "seen": {}, "meta": {},
                        **store.read_json(folder / "pending.json", {})}
        self.ledger = store.read_json(folder / "ledger.json", {})
        self.ctx = Context(profile, now, self.ledger)
        self.local = now.astimezone(self.ctx.tz)
        self.failed: list[str] = []

    def read_sources(self) -> list[dict]:
        """Every source's changes. A source with no snapshot yet counts from its first attempt,
        so one whose sign-in failed from the start still reports what happened meanwhile."""
        found = []
        starts = self.snapshot.setdefault("starts", {})
        for source in self.profile["sources"]:
            name, kind = source["name"], source["kind"]
            prev = self.snapshot["sources"].get(name)
            if prev is None:
                starts.setdefault(name, iso(self.now))
            self.ctx.since = (self.now - self.since if self.since else None if self.first else parse(starts[name])) \
                if prev is None else None
            try:
                adapter = ADAPTERS.get(kind)
                if adapter is None:
                    raise SourceError(PLANNED.get(kind, f"no adapter for kind {kind!r}"))
                try:
                    section, changes = adapter(source, prev, self.ctx)
                except (KeyError, TypeError, ValueError, AttributeError, IndexError) as error:
                    # A response in a shape the adapter doesn't know fails this source, not the scan.
                    raise SourceError(f"unexpected response ({type(error).__name__})")
            except SourceError as error:
                count = _fail_health(self.snapshot, name, error, self.now)
                print(f"org-assistant: {self.org}: {name}: {error}", file=sys.stderr)
                if count >= self.profile["schedule"]["source_failures"]:
                    self.failed.append(f"{name} failed {count} scans in a row")
                continue
            self.snapshot["sources"][name] = section
            starts.pop(name, None)
            self.snapshot["health"][name] = {"ok": True, "at": iso(self.now), "failures": 0}
            still = STILL.get(kind)
            if still:  # a change no longer true, such as a DM since answered, leaves the gathered list
                self.pending["gathered"] = [i for i in self.pending["gathered"]
                                            if i.get("source") != name or still(section, i)]
            found.extend({**change, "source": name} for change in changes)
        names = {s["name"] for s in self.profile["sources"]} | {THREAD}
        self.snapshot["health"] = {k: v for k, v in self.snapshot["health"].items() if k in names}
        self.snapshot["last_scan"] = iso(self.now)
        return found

    def read_thread(self) -> dict | None:
        """The assistant thread's state; an unreadable thread counts as a failing source."""
        thread = self.profile.get("thread", "")
        if not thread:
            return None
        shown = t3_source.show(thread)
        if shown is None:
            count = _fail_health(self.snapshot, THREAD, SourceError("t3 thread show: failed"), self.now)
            print(f"org-assistant: {self.org}: can't read the assistant thread {thread}", file=sys.stderr)
            if count >= self.profile["schedule"]["source_failures"]:
                self.failed.append(f"the assistant thread was unreadable {count} scans in a row")
        else:
            self.snapshot["health"].pop(THREAD, None)
        return shown

    def run(self, dry_run: bool, inline: bool, out) -> int:
        pending, schedule, now = self.pending, self.profile["schedule"], self.now
        found = self.read_sources()
        pending["seen"] = {k: at for k, at in pending["seen"].items() if at >= iso(now - SEEN_FOR)}
        done = delivered(self.ledger)
        for slot in ("sent", "inline"):
            if pending[slot] and pending[slot]["id"] in done:
                _settle(pending, slot, now)
        if pending["inline"] and (inline or now - parse(pending["inline"]["frozen_at"]) >= INLINE_GRACE):
            _unfreeze(pending, "inline")
        flight = [i["id"] for slot in ("sent", "inline") if pending[slot] for i in pending[slot]["items"]]
        pending["gathered"] = [i for i in gather(pending["gathered"], found, [*pending["seen"], *flight])
                               if not muted(i, self.ledger.get("mutes", []), iso(now))]

        thread = self.profile.get("thread", "")
        shown = None if inline else self.read_thread()
        # A dry run with no thread yet decides as if an idle thread were there.
        busy = (shown is None or shown.get("status") in t3_source.ACTIVE) if thread else not dry_run
        sent, send, reason = pending["sent"], None, ""
        if inline:
            pending["inline"] = _freeze(self.org, pending, self.local, "inline", list(pending["gathered"]),
                                        "scan now")
            reason = "inline batch for this run to post"
        elif sent and not busy and sent["id"] in shown.get("lastText", ""):
            _settle(pending, "sent", now)
            reason = "the thread's last reply already named the sent batch"
        elif sent and busy:
            reason = "the sent batch waits for the busy or unreadable thread"
        elif sent and held(self.local, self.ledger, sent["kind"]):
            reason = "the sent batch waits for the quiet or pause to end"
        elif sent and len(sent["tries"]) >= 1 + schedule["retries"]:
            self.failed.append(f"batch {sent['id']} undelivered after {len(sent['tries'])} wakes")
            reason = "wakes stopped: the sent batch was never delivered"
        elif sent:
            send, reason = sent, "resending the undelivered batch"
        if not inline and pending["sent"] is None and not self.first and (thread or dry_run):
            kind, items, reason = decide(self.local, schedule, pending["meta"], self.ledger, pending["gathered"])
            if kind and busy:
                reason = f"{reason}, held while the thread is busy or unreadable"
            elif kind:
                send = pending["sent"] = _freeze(self.org, pending, self.local, kind, items, reason)
                self._count(kind)
        elif self.first:
            reason = "the first scan records a baseline and wakes nothing"

        shown_batch = pending["inline"] if inline else send
        report = {"org": self.org, "at": self.local.isoformat(timespec="minutes"), "first": self.first,
                  "dry_run": dry_run, "wake": send["kind"] if send else None, "reason": reason,
                  "batch": shown_batch["id"] if shown_batch else None,
                  "items": [{"id": i["id"], "kind": i["kind"], "ref": i["ref"]} for i in (shown_batch or {}).get("items", [])],
                  "gathered": dict(Counter(i["kind"] for i in pending["gathered"])),
                  "found": dict(Counter(i["kind"] for i in found)),
                  "health": health_line(self.snapshot, self.ctx.tz), "failed": self.failed}
        if inline:
            report["batch_items"] = pending["inline"]["items"]
            report["in_flight"] = pending["sent"]
        message = wake_message(self.org, send, self.snapshot, self.ctx.tz) if send else None
        if dry_run:
            report["would_send"] = message
            print(json.dumps(report, indent=1, ensure_ascii=False), file=out)
            return 1 if self.failed else 0

        store.write_json(self.folder / "pending.json", pending)
        store.write_json(self.folder / "snapshot.json", self.snapshot)
        (self.folder / "scan.stamp").write_text(iso(now) + "\n")
        if send:
            code, _, _ = run(["t3", "thread", "send", thread, "-"], stdin=message)
            send["tries"].append({"at": iso(now), "ok": code == 0})
            if code != 0:
                print(f"org-assistant: {self.org}: t3 thread send exited {code}", file=sys.stderr)
            store.write_json(self.folder / "pending.json", pending)
        print(json.dumps(report, ensure_ascii=False), file=out)
        for line in self.failed:
            print(f"org-assistant: {self.org}: {line}", file=sys.stderr)
        return 1 if self.failed else 0

    def _count(self, kind: str) -> None:
        """Records what today sent, beside the batch, so the two are written together."""
        meta, schedule = self.pending["meta"], self.profile["schedule"]
        today, clock = self.local.date().isoformat(), self.local.strftime("%H:%M")
        if kind == "overview":
            meta["overview_on"], meta["overview_id"] = today, self.pending["sent"]["id"]
        else:
            meta.setdefault("deltas", {})[today] = meta.get("deltas", {}).get(today, 0) + 1
        meta.setdefault("slots", {})[today] = sorted(
            {*meta.get("slots", {}).get(today, []), *[s for s in schedule["batch_slots"] if s <= clock]})
        meta["deltas"] = {d: n for d, n in meta.get("deltas", {}).items() if d >= today}
        meta["slots"] = {d: s for d, s in meta["slots"].items() if d >= today}
