#!/usr/bin/env python3
"""Redeem a banked Codex reset before it lapses unused.

A banked reset lapses when it expires before the latest usage window, the week, resets: a redeem
resets every window, so one that outlasts the week can still serve a later week. The earliest
lapsing reset is redeemed when the tightest window has --redeem-when-left percent or less left,
or when it expires within --margin-hours; at most one per run. Resets that never expire or
outlast the week, and resets of another type, are never redeemed. The first run that sees a
lapsing reset prints a heads-up, remembered in --state. Prints one line per heads-up or redeem
and nothing otherwise. Exits 1 when Codex's app-server can't be read or the redeem fails.
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

CODEX_RESET = 'codexRateLimits'
CALL_TIMEOUT = 30
CLIENT = 'pstack-reset-guard'


class Window(NamedTuple):
    left: float
    resets: float | None


class Credit(NamedTuple):
    id: str
    kind: str | None
    expires: float | None


class Decision(NamedTuple):
    notices: tuple
    redeem: Credit | None
    warned: frozenset


class Unreadable(Exception):
    pass


def parse_windows(result, now):
    limits = target.table(target.table(result).get('rateLimits'))
    windows = []
    for window in map(target.table, (limits.get('primary'), limits.get('secondary'))):
        used, resets = target.number(window.get('usedPercent')), target.number(window.get('resetsAt'))
        if used is not None:
            windows.append(Window(100 if resets is not None and resets <= now else max(0, 100 - used), resets))
    return windows


def parse_credits(result):
    """Return the available banked resets, or raise Unreadable when the reply hides one's id or expiry."""
    summary = target.table(target.table(result).get('rateLimitResetCredits'))
    rows = summary.get('credits')
    if not isinstance(rows, list):
        if target.number(summary.get('availableCount')) in (None, 0):
            return []
        raise Unreadable(f"Codex reports {summary['availableCount']} banked resets without their details")
    credits = []
    for row in map(target.table, rows):
        if row.get('status') != 'available':
            continue
        expires = row.get('expiresAt')
        if target.text(row.get('id')) is None or (expires is not None and target.number(expires) is None):
            raise Unreadable('Codex lists an available banked reset without a usable id or expiry')
        credits.append(Credit(row['id'], row.get('resetType'), expires))
    return credits


def decide(windows, credits, now, warned, redeem_when_left=5, margin_hours=3):
    """Return which lapsing resets to announce, which one to redeem, and the announced ids to remember."""
    week = max((window.resets for window in windows if window.resets is not None), default=None)
    lapsing = sorted(
        (credit for credit in credits if credit.kind == CODEX_RESET and credit.expires is not None and week is not None and now < credit.expires < week),
        key=lambda credit: credit.expires,
    )
    redeem = None
    if lapsing:
        tightest = min(window.left for window in windows)
        if tightest <= redeem_when_left or lapsing[0].expires - now <= margin_hours * 3600:
            redeem = lapsing[0]
    notices = tuple(credit for credit in lapsing if credit.id not in warned and credit != redeem)
    available = {credit.id for credit in credits}
    remembered = {*warned, *(credit.id for credit in notices), *([redeem.id] if redeem else [])}
    return Decision(notices, redeem, frozenset(remembered & available))


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


def notice(credit, windows, args):
    week = max(window.resets for window in windows if window.resets is not None)
    return (
        f'Heads-up: a banked Codex reset expires {target.moment(credit.expires)}, before the week resets {target.moment(week)}. '
        f'It will be redeemed automatically at {args.redeem_when_left:g}% left or {args.margin_hours:g} h before it expires.'
    )


def redeem_summary(credit, windows):
    tightest = min(windows, key=lambda window: window.left)
    ending = f' of the window ending {target.moment(tightest.resets)}' if tightest.resets is not None else ''
    return f'the banked Codex reset expiring {target.moment(credit.expires)}: {round(tightest.left)}% was left{ending}'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--redeem-when-left', type=float, default=target.THRESHOLDS['skipWhenLeft'], help='Percent left in the tightest window at which to redeem (default %(default)s)')
    parser.add_argument('--margin-hours', type=float, default=3, help='Redeem a lapsing reset this many hours before it expires (default %(default)s)')
    parser.add_argument('--state', type=Path, default=Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'pstack' / 'reset-guard.json', help='JSON file of announced reset ids')
    parser.add_argument('--dry-run', action='store_true', help='Print what would happen without redeeming or writing state')
    args = parser.parse_args()
    now = time.time()
    result = target.app_server_call('account/rateLimits/read', {}, CALL_TIMEOUT, CLIENT)
    if not isinstance(result, dict):
        print('Could not read Codex rate limits from codex app-server.', file=sys.stderr)
        return 1
    try:
        windows, credits = parse_windows(result, now), parse_credits(result)
    except Unreadable as error:
        print(f'{error}.', file=sys.stderr)
        return 1
    if credits and not any(window.resets is not None for window in windows):
        print('Codex reports banked resets but no usage window with a reset time.', file=sys.stderr)
        return 1
    warned = load_warned(args.state)
    decision = decide(windows, credits, now, warned, args.redeem_when_left, args.margin_hours)
    prefix = 'Dry run: ' if args.dry_run else ''
    for credit in decision.notices:
        print(prefix + notice(credit, windows, args))
    if not args.dry_run and decision.warned != warned:
        save_warned(args.state, decision.warned)
    if decision.redeem is None:
        return 0
    summary = redeem_summary(decision.redeem, windows)
    if args.dry_run:
        print(f'Dry run: would redeem {summary}.')
        return 0
    reply = target.app_server_call('account/rateLimitResetCredit/consume', {'creditId': decision.redeem.id, 'idempotencyKey': f'reset-guard:{decision.redeem.id}'}, CALL_TIMEOUT, CLIENT)
    outcome = target.text(target.table(reply).get('outcome'))
    if outcome is None:
        print(f'Could not redeem {summary}.', file=sys.stderr)
        return 1
    print(f'Redeemed {summary}.' if outcome == 'reset' else f'Redeeming {summary} returned {outcome}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
