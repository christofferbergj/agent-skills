"""The model's edits to ledger.json, the one state file the scan reads but never writes.
Each command reads the file, changes one thing, and replaces it atomically."""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from . import store

KEEP = 50  # entries kept in each history list


def _utc(value: str, tz: str) -> str:
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=ZoneInfo(tz))
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def edit(org: str, args) -> str:
    """Applies one `assistant.py ledger` command and returns what to print."""
    profile = store.load_profile(org)
    tz = profile["timezone"]
    path = store.state_dir(org) / "ledger.json"
    ledger = store.read_json(path, {})
    what = args.what
    if what == "show":
        import json
        return json.dumps(ledger, indent=1, ensure_ascii=False)
    if what == "delivered":
        ledger["last_delivered"] = args.batch
        ledger["delivered"] = ([{"batch": args.batch, "at": _now()}] + ledger.get("delivered", []))[:KEEP]
        out = f"batch {args.batch} delivered"
    elif what in ("quiet", "pause"):
        key = f"{'quiet' if what == 'quiet' else 'paused'}_until"
        ledger[key] = None if args.until == "off" else _utc(args.until, tz)
        out = f"{key}: {ledger[key] or 'off'}"
    elif what == "mute":
        ledger["mutes"] = [m for m in ledger.get("mutes", []) if m.get("ref") != args.ref]
        ledger["mutes"].append({"ref": args.ref, "until": _utc(args.until, tz) if args.until else None})
        out = f"muted {args.ref}"
    elif what == "unmute":
        ledger["mutes"] = [m for m in ledger.get("mutes", []) if m.get("ref") != args.ref]
        out = f"unmuted {args.ref}"
    elif what == "call":
        call = ledger.get("call")
        if args.action == "set":
            if call:
                raise SystemExit("a call is already open; queue this one, or clear the open call first")
            ledger["call"] = {"text": args.text, "since": _now()}
        elif args.action == "clear":
            ledger["call"] = None
            queue = ledger.get("queue", [])
            if queue:
                ledger["call"], ledger["queue"] = {**queue[0], "since": _now()}, queue[1:]
        elif args.action == "queue":
            ledger.setdefault("queue", []).append({"text": args.text, "queued": _now()})
        elif args.action == "drop":
            if call:
                ledger.setdefault("dropped", []).insert(0, {**call, "dropped": _now()})
                ledger["dropped"] = ledger["dropped"][:KEEP]
            ledger["call"] = None
        if args.action != "show":
            store.write_json(path, ledger)
        call = ledger.get("call")
        if not call:
            return f"no open call · {len(ledger.get('queue', []))} queued"
        since = datetime.fromisoformat(call["since"].replace("Z", "+00:00"))
        minutes = int((datetime.now(timezone.utc) - since).total_seconds() // 60)
        return f"open call ({minutes} min old): {call['text']} · {len(ledger.get('queue', []))} queued"
    elif what == "started":
        ledger.setdefault("started", []).append({"thread": args.thread, "ticket": args.ticket, "at": _now()})
        out = f"started {args.thread} for {args.ticket}"
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
        ledger["depends"] = [d for d in ledger.get("depends", []) if d != pair]
        if not args.remove:
            ledger["depends"].append(pair)
        out = f"{args.ticket} {'no longer depends' if args.remove else 'depends'} on {args.on}"
    elif what == "lead":
        ledger.setdefault("leads", []).append({"ticket": args.ticket, "on": args.on, "answer": args.answer,
                                               "at": _now()})
        out = f"lead {args.ticket} → {args.on}: {args.answer}"
    elif what == "log":
        ledger.setdefault("log", []).insert(0, {"at": _now(), "kind": args.kind, "text": args.text})
        ledger["log"] = ledger["log"][:KEEP * 4]
        out = f"logged {args.kind}"
    else:
        raise SystemExit(f"unknown ledger command {what}")
    store.write_json(path, ledger)
    return out
