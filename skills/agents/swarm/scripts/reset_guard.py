#!/usr/bin/env python3
"""Redeem a banked Codex reset before it lapses unused.

A redeem restarts every usage window, so a reset is redeemed only when it would otherwise expire.

- The week is the usage window a day or longer that resets last; a shorter window never decides.
- A reset that expires before the week resets is redeemed once the week has --redeem-when-left
  percent or less left, or within --margin-hours of its expiry, whichever comes first.
- The earliest such reset goes first, at most one per run. Resets that outlast the week, never
  expire, or are of another type are left alone.

It needs a signed-in `codex` CLI on PATH and target.py beside it. Run it from any scheduler, such
as cron, a systemd timer, or launchd, every 30 minutes or so. It prints a line only when it redeems
a reset, so its output can go straight to whatever channel you want notices in. A nonzero exit
means a reset may lapse unseen, so treat it as an alert: it exits 1, with the reason on stderr,
when Codex's rate limits can't be read, hide a reset's id or expiry, list fewer resets than they
count, or give no day-long window a reset time while a reset could expire, and when a redeem
neither resets Codex nor finds the reset already redeemed.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import NamedTuple

import target

CALL_TIMEOUT = 30
CLIENT = 'pstack-reset-guard'
MARGIN_HOURS = 3


class Window(NamedTuple):
    left: float
    resets: float


def parse_week(result):
    """Return the window a day or longer that resets last, or None, since a shorter window never decides a redeem."""
    limits = target.table(target.table(result).get('rateLimits'))
    windows = []
    for window in map(target.table, (limits.get('primary'), limits.get('secondary'))):
        used, minutes, resets = (target.number(window.get(key)) for key in ('usedPercent', 'windowDurationMins', 'resetsAt'))
        if used is not None and minutes is not None and minutes >= 1440 and resets is not None:
            windows.append(Window(max(0, 100 - used), resets))
    return max(windows, key=lambda window: window.resets, default=None)


def decide(week, expiring, now, redeem_when_left, margin_hours):
    """Return the earliest reset that lapses before the week once it is due, or None."""
    lapsing = min((credit for credit in expiring if credit.expires < week.resets), key=lambda credit: credit.expires, default=None)
    if lapsing is not None and (week.left <= redeem_when_left or lapsing.expires - now <= margin_hours * 3600):
        return lapsing
    return None


def redeem_summary(credit, week):
    return f'the banked Codex reset expiring {target.moment(credit.expires)}: {round(week.left)}% was left of the week ending {target.moment(week.resets)}'


def consume(credit, summary):
    """Consume the banked reset, print the result, and return whether Codex redeemed it."""
    reply = target.app_server_call('account/rateLimitResetCredit/consume', {'creditId': credit.id, 'idempotencyKey': f'reset-guard:{credit.id}'}, CALL_TIMEOUT, CLIENT)
    outcome = target.table(reply).get('outcome')
    if outcome == 'reset':
        print(f'Redeemed {summary}.')
    elif outcome == 'alreadyRedeemed':
        print(f'Codex had already redeemed {summary}.')
    else:
        detail = 'codex app-server gave no result' if reply is None else f'Codex answered {json.dumps(outcome)}'
        print(f'Could not redeem {summary}: {detail}.', file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--redeem-when-left', type=float, default=target.thresholds(target.load_config(target.config_path()))['skipWhenLeft'], help='Percent left in the week at which to redeem (default: codexUsage.skipWhenLeft in PSTACK_CONFIG or ~/.config/pstack/config.json, now %(default)s)')
    parser.add_argument('--margin-hours', type=float, default=MARGIN_HOURS, help='Redeem a lapsing reset this many hours before it expires (default %(default)s)')
    parser.add_argument('--dry-run', action='store_true', help='Print the reset it would redeem without redeeming it')
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
    failed = False
    if banked.short:
        print(f'Codex lists {len(banked.credits)} of {banked.count:g} banked resets; the others go unchecked.', file=sys.stderr)
        failed = True
    week = parse_week(result)
    expiring = [credit for credit in banked.credits if credit.kind == target.CODEX_RESET and credit.expires is not None and credit.expires > now]
    if expiring and week is None:
        print('Codex reports a banked reset that could expire but no usage window a day or longer with a reset time.', file=sys.stderr)
        return 1
    redeem = decide(week, expiring, now, args.redeem_when_left, args.margin_hours)
    if redeem is not None:
        summary = redeem_summary(redeem, week)
        if args.dry_run:
            print(f'Dry run: would redeem {summary}.')
        elif not consume(redeem, summary):
            failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
