#!/usr/bin/env python3
"""Redeem a banked Codex reset before it lapses unused.

A banked reset lapses when it expires before the latest usage window, the week, resets: a redeem
resets every window, so one that outlasts the week can still serve a later week. The earliest
lapsing reset is redeemed when the week has --redeem-when-left percent or less left, by default
codexUsage.skipWhenLeft in PSTACK_CONFIG or ~/.config/pstack/config.json, or when it expires
within --margin-hours; at most one per run. A shorter window running low never triggers
a redeem. Resets that never expire or outlast the week, and resets of another type, are never
redeemed. The first run that sees a
lapsing reset prints a heads-up, remembered in --state. Prints one line per heads-up or redeem
and nothing otherwise. Exits 1 when Codex's app-server can't be read or a redeem neither resets
Codex nor finds the reset already redeemed.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from typing import NamedTuple

import target

CALL_TIMEOUT = 30
CLIENT = 'pstack-reset-guard'


class Window(NamedTuple):
    left: float
    resets: float | None


class Decision(NamedTuple):
    week: Window | None
    notices: tuple
    redeem: target.Credit | None
    warned: frozenset


def parse_windows(result):
    limits = target.table(target.table(result).get('rateLimits'))
    windows = []
    for window in map(target.table, (limits.get('primary'), limits.get('secondary'))):
        used = target.number(window.get('usedPercent'))
        if used is not None:
            windows.append(Window(max(0, 100 - used), target.number(window.get('resetsAt'))))
    return windows


def decide(windows, credits, now, warned, redeem_when_left=5, margin_hours=3):
    """Return the week, which lapsing resets to announce, which one to redeem, and the announced ids to remember."""
    week = max((window for window in windows if window.resets is not None), key=lambda window: window.resets, default=None)
    lapsing = sorted(
        (credit for credit in credits if credit.kind == target.CODEX_RESET and credit.expires is not None and week is not None and now < credit.expires < week.resets),
        key=lambda credit: credit.expires,
    )
    redeem = None
    if lapsing and (week.left <= redeem_when_left or lapsing[0].expires - now <= margin_hours * 3600):
        redeem = lapsing[0]
    notices = tuple(credit for credit in lapsing if credit.id not in warned and credit != redeem)
    available = {credit.id for credit in credits}
    remembered = {*warned, *(credit.id for credit in notices), *([redeem.id] if redeem else [])}
    return Decision(week, notices, redeem, frozenset(remembered & available))


def load_warned(path):
    try:
        ids = target.table(json.loads(path.read_text())).get('announced')
    except (OSError, ValueError):
        return frozenset()
    return frozenset(entry for entry in ids if isinstance(entry, str)) if isinstance(ids, list) else frozenset()


def save_warned(path, warned):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix=path.name, suffix='.tmp', delete=False) as stream:
        json.dump({'announced': sorted(warned)}, stream)
    os.replace(stream.name, path)


def notice(credit, week, args):
    return (
        f'Heads-up: a banked Codex reset expires {target.moment(credit.expires)}, before the week resets {target.moment(week.resets)}. '
        f'It will be redeemed automatically at {args.redeem_when_left:g}% left or {args.margin_hours:g} h before it expires.'
    )


def redeem_summary(credit, week):
    return f'the banked Codex reset expiring {target.moment(credit.expires)}: {round(week.left)}% was left of the week ending {target.moment(week.resets)}'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--redeem-when-left', type=float, default=target.thresholds(target.load_config(target.config_path()))['skipWhenLeft'], help="Percent left in the week at which to redeem (default: Pstack's codexUsage.skipWhenLeft, %(default)s)")
    parser.add_argument('--margin-hours', type=float, default=3, help='Redeem a lapsing reset this many hours before it expires (default %(default)s)')
    parser.add_argument('--state', type=Path, default=Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'pstack' / 'reset-guard.json', help='JSON file of announced reset ids')
    parser.add_argument('--dry-run', action='store_true', help='Print what would happen without redeeming or writing state')
    args = parser.parse_args()
    now = time.time()
    result = target.app_server_call('account/rateLimits/read', {}, CALL_TIMEOUT, CLIENT)
    if not isinstance(result, dict):
        print('Could not read Codex rate limits from codex app-server.', file=sys.stderr)
        return 1
    windows, credits = parse_windows(result), target.banked_credits(result)
    if credits is None:
        print("Codex's rate limits don't state each banked reset's id and expiry.", file=sys.stderr)
        return 1
    count = target.number(result['rateLimitResetCredits'].get('availableCount'))
    if count is not None and len(credits) < count:
        print(f'Codex lists {len(credits)} of {count:g} banked resets; the others go unchecked.', file=sys.stderr)
    warned = load_warned(args.state)
    decision = decide(windows, credits, now, warned, args.redeem_when_left, args.margin_hours)
    if credits and decision.week is None:
        print('Codex reports banked resets but no usage window with a reset time.', file=sys.stderr)
        return 1
    prefix = 'Dry run: ' if args.dry_run else ''
    for credit in decision.notices:
        print(prefix + notice(credit, decision.week, args))
    if not args.dry_run and decision.warned != warned:
        save_warned(args.state, decision.warned)
    if decision.redeem is None:
        return 0
    summary = redeem_summary(decision.redeem, decision.week)
    if args.dry_run:
        print(f'Dry run: would redeem {summary}.')
        return 0
    reply = target.app_server_call('account/rateLimitResetCredit/consume', {'creditId': decision.redeem.id, 'idempotencyKey': f'reset-guard:{decision.redeem.id}'}, CALL_TIMEOUT, CLIENT)
    outcome = target.table(reply).get('outcome')
    if outcome == 'reset':
        print(f'Redeemed {summary}.')
    elif outcome == 'alreadyRedeemed':
        print(f'Codex had already redeemed {summary}.')
    else:
        detail = 'codex app-server gave no result' if reply is None else f'Codex answered {json.dumps(outcome)}'
        print(f'Could not redeem {summary}: {detail}.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
