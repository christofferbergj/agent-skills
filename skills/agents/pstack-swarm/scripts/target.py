#!/usr/bin/env python3
"""Resolve a cross-vendor delegate's model, effort, and speed, stepping down as Codex usage runs low."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time

ROLES = {'review-full': ('review', 'full'), 'review-delta': ('review', 'delta'), 'computer-use': ('computerUse', 'routine'), 'computer-use-hard': ('computerUse', 'hard')}
EFFORTS = {'review': {'full': 'xhigh', 'delta': 'high'}, 'computerUse': {'routine': 'medium', 'hard': 'high'}}
THRESHOLDS = {'fastWhileLeft': 40, 'skipWhenLeft': 5}
# Usage is read from local session logs only, so the check costs milliseconds and never waits on the network.
DAYS, FILES, TAIL = 3, 8, 256 * 1024


def codex_home():
    return Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')


def configured_codex_model(home):
    try:
        for line in (home / 'config.toml').read_text().splitlines():
            if line.lstrip().startswith('['):
                return None
            found = re.match(r'\s*model\s*=\s*"([^"]+)"', line)
            if found:
                return found[1]
    except OSError:
        return None
    return None


def latest_rate_limits(sessions):
    days = sorted(sessions.glob('*/*/*'), reverse=True)[:DAYS]
    logs = sorted((path for day in days for path in day.glob('*.jsonl')), key=lambda path: path.stat().st_mtime, reverse=True)[:FILES]
    for log in logs:
        with log.open('rb') as stream:
            stream.seek(max(0, stream.seek(0, os.SEEK_END) - TAIL))
            text = stream.read().decode('utf-8', 'replace')
        end = len(text)
        while True:
            found = text.rfind('"rate_limits":', 0, end)
            if found < 0:
                break
            start = text.rfind('\n', 0, found) + 1
            stop = text.find('\n', found)
            try:
                event = json.loads(text[start:stop if stop >= 0 else len(text)])
                limits = event['payload']['rate_limits']
                if isinstance(limits, dict):
                    return limits, event.get('timestamp')
            except (ValueError, KeyError, TypeError):
                pass
            end = found
    return None, None


def window_left(window, now):
    resets = window.get('resets_at')
    # A window whose reset time has passed starts fresh.
    return 100 if resets and resets <= now else max(0, 100 - window['used_percent'])


def usage_left(limits, now):
    """Return the percent left in the tightest window and that window's reset time."""
    windows = [window for window in (limits.get('primary'), limits.get('secondary')) if isinstance(window, dict) and isinstance(window.get('used_percent'), (int, float))]
    if not windows:
        return None, None
    tightest = min(windows, key=lambda window: window_left(window, now))
    left = 0 if limits.get('rate_limit_reached_type') else window_left(tightest, now)
    return round(left), tightest.get('resets_at')


def describe(left, resets):
    until = f" until {datetime.fromtimestamp(resets, timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}" if resets else ''
    return f'Codex usage {left}% left{until}'


def resolve(parent, role, config, home, now):
    section, size = ROLES[role]
    if section == 'computerUse' and parent == 'codex':
        return {'role': role, 'run': 'self', 'reason': 'Codex runs computer use itself'}
    host = config.get(parent) if isinstance(config.get(parent), dict) else {}
    entry = host.get(section) if isinstance(host.get(section), dict) else {}
    vendor = 'claude-code' if parent == 'codex' else 'codex'
    effort = (entry.get('effort') or {}).get(size) if isinstance(entry.get('effort'), dict) else None
    effort = effort or EFFORTS[section][size]
    target = {'role': role, 'run': vendor, 'providerInstanceId': entry.get('providerInstanceId'), 'model': entry.get('model'), 'effort': effort, 'serviceTier': entry.get('serviceTier')}
    if vendor == 'claude-code':
        return target
    target['model'] = target['model'] or configured_codex_model(home)
    # GPT models never run above xhigh.
    if effort in ('max', 'ultra'):
        target['effort'] = 'xhigh'
    thresholds = dict(THRESHOLDS, **(config.get('codexUsage') if isinstance(config.get('codexUsage'), dict) else {}))
    try:
        limits, seen = latest_rate_limits(home / 'sessions')
    except OSError:
        limits, seen = None, None
    left, resets = usage_left(limits, now) if limits else (None, None)
    if left is None:
        target['note'] = 'Codex usage unknown; using the configured speed'
        return target
    target['usage'] = {'left': left, 'seenAt': seen}
    if left < thresholds['skipWhenLeft']:
        return {'role': role, 'run': 'fallback', 'reason': describe(left, resets), 'usage': target['usage']}
    if left < thresholds['fastWhileLeft']:
        target['serviceTier'] = 'default'
        target['note'] = f'Standard speed: {describe(left, resets)}'
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=sorted(ROLES))
    parser.add_argument('--parent', choices=['codex', 'claude-code'], required=True, help='The host running this session')
    args = parser.parse_args()
    path = Path(os.environ.get('PSTACK_CONFIG') or Path.home() / '.config' / 'pstack' / 'config.json')
    try:
        config = json.loads(path.read_text())
        config = config if isinstance(config, dict) else {}
    except (OSError, ValueError):
        config = {}
    target = resolve(args.parent, args.role, config, codex_home(), time.time())
    print(json.dumps({key: value for key, value in target.items() if value is not None}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
