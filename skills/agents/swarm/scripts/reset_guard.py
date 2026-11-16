#!/usr/bin/env python3
"""Redeem a banked Codex reset before it lapses unused.

A banked reset lapses when it expires before the latest usage window, the week, resets: a redeem
resets every window, so one that outlasts the week can still serve a later week. The earliest
lapsing reset is redeemed when the week has --redeem-when-left percent or less left, by default
codexUsage.skipWhenLeft in PSTACK_CONFIG or ~/.config/pstack/config.json, or when it expires
within --margin-hours; at most one per run. A shorter window running low never triggers a
redeem. Resets that never expire or outlast the week, and resets of another type, are never
redeemed. The first run that sees a lapsing reset it doesn't redeem prints a heads-up,
remembered in --state. Prints one line per heads-up or redeem and nothing otherwise.

Exits 1, with the reason on stderr, when Codex's rate limits can't be read, hide a banked
reset's id or expiry, list fewer resets than they count, or give no window a day or longer a
reset time while a banked reset could expire; when a redeem neither resets Codex nor finds the
reset already redeemed; or when --state can't be written, which never holds up a redeem.
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
MARGIN_HOURS = 3


class Window(NamedTuple):
    left: float
    resets: float


class Decision(NamedTuple):
    notices: tuple
    redeem: target.Credit | None


def parse_week(result):
    """Return the window a day or longer that resets last, or None, since a shorter window never decides a redeem."""
    limits = target.table(target.table(result).get('rateLimits'))
    windows = []
    for window in map(target.table, (limits.get('primary'), limits.get('secondary'))):
        used, minutes, resets = (target.number(window.get(key)) for key in ('usedPercent', 'windowDurationMins', 'resetsAt'))
        if used is not None and minutes is not None and minutes >= 1440 and resets is not None:
            windows.append(Window(max(0, 100 - used), resets))
    return max(windows, key=lambda window: window.resets, default=None)


def decide(week, expiring, now, announced, redeem_when_left, margin_hours):
    """Return which of the resets that could expire lapse before the week and need a heads-up, and which one to redeem."""
    lapsing = sorted((credit for credit in expiring if credit.expires < week.resets), key=lambda credit: credit.expires)
    redeem = None
    if lapsing and (week.left <= redeem_when_left or lapsing[0].expires - now <= margin_hours * 3600):
        redeem = lapsing[0]
    return Decision(tuple(credit for credit in lapsing if credit.id not in announced and credit != redeem), redeem)


def load_announced(path):
    try:
        ids = target.table(json.loads(path.read_text())).get('announced')
    except (OSError, ValueError):
        return frozenset()
    return frozenset(entry for entry in ids if isinstance(entry, str)) if isinstance(ids, list) else frozenset()


def save_announced(path, announced):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix=path.name, suffix='.tmp', delete=False) as stream:
        json.dump({'announced': sorted(announced)}, stream)
    os.replace(stream.name, path)


def notice(credit, week, args):
    return (
        f'Heads-up: a banked Codex reset expires {target.moment(credit.expires)}, before the week resets {target.moment(week.resets)}. '
        f'It will be redeemed automatically at {args.redeem_when_left:g}% left or {args.margin_hours:g} h before it expires.'
    )


def redeem_summary(credit, week):
    return f'the banked Codex reset expiring {target.moment(credit.expires)}: {round(week.left)}% was left of the week ending {target.moment(week.resets)}'


def redeem(credit, summary):
    """Consume the banked reset, print the result, and return the exit code."""
    reply = target.app_server_call('account/rateLimitResetCredit/consume', {'creditId': credit.id, 'idempotencyKey': f'reset-guard:{credit.id}'}, CALL_TIMEOUT, CLIENT)
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--redeem-when-left', type=float, default=target.thresholds(target.load_config(target.config_path()))['skipWhenLeft'], help="Percent left in the week at which to redeem (default: Pstack's codexUsage.skipWhenLeft, %(default)s)")
    parser.add_argument('--margin-hours', type=float, default=MARGIN_HOURS, help='Redeem a lapsing reset this many hours before it expires (default %(default)s)')
    parser.add_argument('--state', type=Path, default=Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'pstack' / 'reset-guard.json', help='JSON file of announced reset ids')
    parser.add_argument('--dry-run', action='store_true', help='Print what would happen without redeeming or writing state')
    args = parser.parse_args()
    now = time.time()
    result = target.app_server_call('account/rateLimits/read', {}, CALL_TIMEOUT, CLIENT)
    if not isinstance(result, dict):
        print('Could not read Codex rate limits from codex app-server.', file=sys.stderr)
        return 1
    banked = target.banked_credits(result)
    if banked is None:
        print("Codex's rate limits don't state each banked reset's id and expiry.", file=sys.stderr)
        return 1
    short = banked.short
    if short:
        print(f'Codex lists {len(banked.credits)} of {banked.count:g} banked resets; the others go unchecked.', file=sys.stderr)
    week = parse_week(result)
    expiring = [credit for credit in banked.credits if credit.kind == target.CODEX_RESET and credit.expires is not None and credit.expires > now]
    if expiring and week is None:
        print('Codex reports a banked reset that could expire but no usage window a day or longer with a reset time.', file=sys.stderr)
        return 1
    announced = load_announced(args.state)
    decision = decide(week, expiring, now, announced, args.redeem_when_left, args.margin_hours) if expiring else Decision((), None)
    prefix = 'Dry run: ' if args.dry_run else ''
    for credit in decision.notices:
        print(prefix + notice(credit, week, args))
    code = 0
    if decision.redeem is not None:
        summary = redeem_summary(decision.redeem, week)
        if args.dry_run:
            print(f'Dry run: would redeem {summary}.')
        else:
            code = redeem(decision.redeem, summary)
    remembered = frozenset({*announced, *(credit.id for credit in decision.notices)} & {credit.id for credit in banked.credits})
    if not args.dry_run and remembered != announced:
        try:
            save_announced(args.state, remembered)
        except OSError as error:
            print(f'Could not save the announced resets to {args.state}: {error}.', file=sys.stderr)
            return 1
    return 1 if short else code


if __name__ == '__main__':
    sys.exit(main())
