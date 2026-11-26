#!/usr/bin/env python3
"""The organisation assistant's scan and state, with no model. `references/scan.md` and
`references/state.md` describe what each command reads and writes.

  assistant.py scan [ORG ...] [--dry-run] [--since 24h]
                     scan each organisation (default: every profile) and wake its thread
                     when there is news; --dry-run reads the sources, prints the batch it
                     would send, and writes and sends nothing
  assistant.py scan ORG --inline
                     scan inside the assistant's own run ("scan now"): wake nothing, freeze
                     everything gathered as one batch, and print it for the run to post
  assistant.py status ORG
                     the health line, the scan stamp's age, the batch in flight, and holds
  assistant.py ledger ORG COMMAND ...
                     the model's edits to ledger.json; `assistant.py ledger ORG -h` lists them

Exits 1 when a unit should fail (two undelivered wakes, or a source failing three scans in a
row, or an unreadable profile), and 2 on a usage error. Times are UTC in files and the
profile's timezone on screen."""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from orgscan import ledger, store  # noqa: E402
from orgscan.decide import held  # noqa: E402
from orgscan.run import delivered, health_line, scan_org  # noqa: E402
from orgscan.times import parse  # noqa: E402

STALE = timedelta(minutes=90)
OVERVIEW_DUE = "09:30"


def _duration(text: str) -> timedelta:
    match = re.fullmatch(r"(\d+)([hd])", text)
    if not match:
        raise argparse.ArgumentTypeError("write a duration such as 24h or 2d")
    return timedelta(hours=int(match.group(1)) * (24 if match.group(2) == "d" else 1))


def _now(text: str | None) -> datetime:
    return parse(text) if text else datetime.now(timezone.utc)


def status(org: str, now: datetime) -> str:
    profile = store.load_profile(org)
    tz = ZoneInfo(profile["timezone"])
    folder = store.state_dir(org)
    snapshot = store.read_json(folder / "snapshot.json", {})
    pending = store.read_json(folder / "pending.json", {})
    book = store.read_json(folder / "ledger.json", {})
    lines = [f"Health: {health_line(snapshot, tz)}" if snapshot else "Health: no scan has run yet"]
    try:
        stamp = parse((folder / "scan.stamp").read_text().strip())
    except (OSError, ValueError):
        stamp = None
    local = now.astimezone(tz)
    clock = local.strftime("%H:%M")
    if stamp is None or ("09:15" <= clock <= profile["schedule"]["window"][1] and now - stamp > STALE):
        age = "never" if stamp is None else f"{int((now - stamp).total_seconds() // 60)} min ago"
        lines.append(f"⚠️ The last scan ran {age}: the timer may be stopped.")
    meta = pending.get("meta", {})
    shipped = meta.get("overview_on") == local.date().isoformat() and (
        meta.get("overview_id") in delivered(book) | {pending.get("last_delivered")})
    if local.weekday() < 5 and clock >= OVERVIEW_DUE and not shipped and not held(local, book, "overview"):
        lines.append(f"⚠️ No overview delivered today by {OVERVIEW_DUE}: the scan or the thread may be broken.")
    for name, state in sorted(snapshot.get("health", {}).items()):
        if not state.get("ok"):
            lines.append(f"⚠️ {name}: {state.get('message', 'failing')}")
    for slot, label in (("sent", "In flight"), ("inline", "Inline, not yet delivered")):
        batch = pending.get(slot)
        if batch:
            lines.append(f"{label}: batch {batch['id']} ({batch['kind']}, {len(batch['items'])} items, "
                         f"{len(batch.get('tries', []))} wakes)")
    lines.append(f"Gathered since: {len(pending.get('gathered', []))} changes")
    for key, label in (("quiet_until", "Quiet until"), ("paused_until", "Paused until")):
        until = parse(book[key]) if book.get(key) else None
        if until and until > now:
            lines.append(f"{label} {until.astimezone(tz):%a %d %b %H:%M}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="assistant.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan")
    scan.add_argument("orgs", nargs="*")
    scan.add_argument("--dry-run", action="store_true")
    scan.add_argument("--inline", action="store_true")
    scan.add_argument("--since", type=_duration, help="on a first scan, count changes from this long ago")
    scan.add_argument("--now", help=argparse.SUPPRESS)
    show = sub.add_parser("status")
    show.add_argument("org")
    show.add_argument("--now", help=argparse.SUPPRESS)
    book = sub.add_parser("ledger")
    book.add_argument("org")
    book.add_argument("--now", help=argparse.SUPPRESS)
    what = book.add_subparsers(dest="what", required=True)
    what.add_parser("show")
    what.add_parser("delivered").add_argument("batch")
    for name in ("quiet", "pause"):
        what.add_parser(name, help="until a time in the profile's timezone, or off").add_argument("until")
    mute = what.add_parser("mute")
    mute.add_argument("ref", help="a ticket, PR, slack:<channel>, or change kind")
    mute.add_argument("--until")
    what.add_parser("unmute").add_argument("ref")
    call = what.add_parser("call", help="the one open call, and the queue behind it")
    call.add_argument("action", choices=["show", "set", "clear", "queue", "drop"],
                      help="set and queue take the call's text; clear and drop take the open call's id")
    call.add_argument("text", nargs="?", default="")
    started = what.add_parser("started")
    started.add_argument("thread")
    started.add_argument("--ticket", required=True)
    what.add_parser("finished").add_argument("thread")
    waits = what.add_parser("waits", help="a PR that waits on another repository's release")
    waits.add_argument("pr")
    waits.add_argument("on", help="owner/repo, or off")
    depends = what.add_parser("depends", help="a dependency the user confirmed")
    depends.add_argument("ticket")
    depends.add_argument("on")
    depends.add_argument("--remove", action="store_true")
    lead = what.add_parser("lead", help="the user's answer about a mentioned ticket")
    lead.add_argument("ticket")
    lead.add_argument("on")
    lead.add_argument("answer", choices=["depends", "unrelated"])
    log = what.add_parser("log", help="what the user was told, asked, or answered")
    log.add_argument("kind", choices=["told", "asked", "answered", "offered", "declined"])
    log.add_argument("text")
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            if args.inline and len(args.orgs) != 1:
                parser.error("--inline scans exactly one organisation")
            orgs = args.orgs or store.orgs()
            now = _now(args.now)
            return max([scan_org(org, now, dry_run=args.dry_run, inline=args.inline, since=args.since)
                        for org in orgs] or [0])
        if args.command == "status":
            print(status(args.org, _now(args.now)))
            return 0
        if args.what == "call" and args.action != "show" and not args.text:
            parser.error(f"call {args.action} needs " + ("the call's text" if args.action in ("set", "queue")
                                                           else "the open call's id, such as c3"))
        print(ledger.edit(args.org, args, _now(args.now)))
        return 0
    except store.ProfileError as error:
        print(f"assistant.py: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
