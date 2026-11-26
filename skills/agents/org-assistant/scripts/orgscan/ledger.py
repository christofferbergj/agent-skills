"""The model's edits to ledger.json, the one state file the scan reads but never writes.
Each command reads the file, changes one thing, and replaces it atomically; running a
command twice leaves the ledger as running it once did."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import store
from .times import iso, parse

KEEP = 50  # entries kept in each history list
CHANGED = timedelta(minutes=15)  # a call that replaced another this recently makes a bare letter ambiguous


def _utc(value: str, tz: str) -> str:
    return iso(parse(value, ZoneInfo(tz)))


def _show_call(ledger: dict, now: datetime) -> str:
    call = ledger.get("call")
    queued = len(ledger.get("queue", []))
    if not call:
        return f"no open call · {queued} queued"
    minutes = int((now - parse(call["since"])).total_seconds() // 60)
    line = f"open call {call['id']} ({minutes} min old): {call['text']} · {queued} queued"
    if call.get("replaced") and now - parse(call["since"]) < CHANGED:
        line += f"\n⚠️ It replaced another call {minutes} min ago: {call['replaced']}. Ask which one a bare letter means."
    return line


def _open_next(ledger: dict, now: datetime, replaced: str | None) -> None:
    """Moves the oldest queued offer up as the call, numbering it."""
    queue = ledger.get("queue", [])
    ledger["call"] = None
    if queue:
        ledger["serial"] = ledger.get("serial", 0) + 1
        ledger["call"] = {"id": f"c{ledger['serial']}", "text": queue[0]["text"], "since": iso(now),
                          "replaced": replaced}
        ledger["queue"] = queue[1:]


def _call(ledger: dict, args, now: datetime) -> None:
    call = ledger.get("call")
    if args.action == "set":
        if call and call["text"] == args.text:
            return
        if call:
            raise SystemExit(f"call {call['id']} is open; queue this one, or clear that call first")
        ledger.setdefault("queue", []).insert(0, {"text": args.text, "queued": iso(now)})
        _open_next(ledger, now, ledger.pop("cleared", None))
    elif args.action == "queue":
        if (call and call["text"] == args.text) or any(q["text"] == args.text for q in ledger.get("queue", [])):
            return
        ledger.setdefault("queue", []).append({"text": args.text, "queued": iso(now)})
    elif args.action in ("clear", "drop"):
        if not call or call["id"] != args.text:  # already cleared: a repeat leaves the next call alone
            return
        if args.action == "drop":
            ledger["dropped"] = [{**call, "dropped": iso(now)}, *ledger.get("dropped", [])][:KEEP]
        recent = f"{call['id']}: {call['text']}"
        _open_next(ledger, now, recent)
        if ledger["call"] is None:
            ledger["cleared"] = recent if args.action == "clear" else None


def edit(org: str, args, now: datetime) -> str:
    """Applies one `assistant.py ledger` command and returns what to print."""
    tz = store.load_profile(org)["timezone"]
    path = store.state_dir(org) / "ledger.json"
    ledger = store.read_json(path, {})
    what = args.what
    if what == "show":
        return json.dumps(ledger, indent=1, ensure_ascii=False)
    if what == "call":
        if args.action != "show":
            _call(ledger, args, now)
            store.write_json(path, ledger)
        return _show_call(ledger, now)
    if what == "delivered":
        if ledger.get("last_delivered") != args.batch:
            ledger["delivered"] = [{"batch": args.batch, "at": iso(now)}, *ledger.get("delivered", [])][:KEEP]
        ledger["last_delivered"] = args.batch
        out = f"batch {args.batch} delivered"
    elif what in ("quiet", "pause"):
        key = "quiet_until" if what == "quiet" else "paused_until"
        ledger[key] = None if args.until == "off" else _utc(args.until, tz)
        out = f"{key}: {ledger[key] or 'off'}"
    elif what == "mute":
        ledger["mutes"] = [m for m in ledger.get("mutes", []) if m.get("ref") != args.ref]
        ledger["mutes"].append({"ref": args.ref, "until": _utc(args.until, tz) if args.until else None})
        out = f"muted {args.ref}"
    elif what == "unmute":
        ledger["mutes"] = [m for m in ledger.get("mutes", []) if m.get("ref") != args.ref]
        out = f"unmuted {args.ref}"
    elif what == "started":
        ledger["started"] = [s for s in ledger.get("started", []) if s.get("thread") != args.thread]
        ledger["started"].append({"thread": args.thread, "ticket": args.ticket, "at": iso(now)})
        out = f"following {args.thread} for {args.ticket}"
    elif what == "finished":
        ledger["started"] = [s for s in ledger.get("started", []) if s.get("thread") != args.thread]
        out = f"no longer following {args.thread}"
    elif what == "waits":
        ledger["waits"] = [w for w in ledger.get("waits", []) if w.get("pr") != args.pr]
        if args.on != "off":
            ledger["waits"].append({"pr": args.pr, "on": args.on})
        out = f"{args.pr} waits on {args.on}"
    elif what == "depends":
        pair = {"ticket": args.ticket, "on": args.on}
        ledger["depends"] = [d for d in ledger.get("depends", []) if d != pair] + ([] if args.remove else [pair])
        out = f"{args.ticket} {'no longer depends' if args.remove else 'depends'} on {args.on}"
    elif what == "lead":
        ledger["leads"] = [l for l in ledger.get("leads", []) if (l["ticket"], l["on"]) != (args.ticket, args.on)]
        ledger["leads"].append({"ticket": args.ticket, "on": args.on, "answer": args.answer, "at": iso(now)})
        out = f"lead {args.ticket} → {args.on}: {args.answer}"
    elif what == "log":
        entry = {"kind": args.kind, "text": args.text}
        if entry not in [{"kind": e["kind"], "text": e["text"]} for e in ledger.get("log", [])[:1]]:
            ledger["log"] = [{"at": iso(now), **entry}, *ledger.get("log", [])][:KEEP * 4]
        out = f"logged {args.kind}"
    else:
        raise SystemExit(f"unknown ledger command {what}")
    store.write_json(path, ledger)
    return out
