#!/usr/bin/env python3
"""Resolve a delegate's model, effort, and speed, stepping cross-vendor targets down as Codex usage runs low.

Reads PSTACK_CONFIG or ~/.config/pstack/config.json. Every key is optional:

  {"codexUsage": {"fastWhileLeft": 40, "skipWhenLeft": 5},
   "claude-code": {
     "review": {"providerInstanceId": "codex", "model": "gpt-6.1-sol",
                "effort": {"full": "xhigh", "delta": "high"}, "serviceTier": "priority"},
     "computerUse": {"providerInstanceId": "codex", "model": "gpt-6.1-sol",
                     "effort": {"routine": "medium", "hard": "high"}, "serviceTier": "priority"},
     "roles": {"how-explorer": {"model": "haiku", "effort": "low"}}},
   "codex": {"review": {"model": "claude-opus-5-5", "effort": {"full": "xhigh", "delta": "high"}}}}

codexUsage thresholds are percent of Codex usage left: below fastWhileLeft a Codex
target drops to serviceTier "default", and below skipWhenLeft it becomes run "fallback".
Usage comes from the newest snapshots in $CODEX_HOME/sessions, so the check stays local.

The review and computer-use roles run on the other vendor. Every other role is one of
Pstack's native roles and runs on the parent host: a fast role on the host's fast model
(Sonnet in Claude Code; Codex keeps its own model), the rest on the parent's model. A
native Codex role runs fast while Codex usage allows, and Claude never runs fast. Native
roles take upstream's labels in kebab case; reflect-judgment shortens "reflect judgment,
divergent, synthesizer", and fast-code names its "fast code model". A roles entry overrides
the model or sets an effort; "inherit-parent" or "auto" as the model keeps the parent's.
"""

import argparse
from datetime import datetime, timezone
from itertools import islice
import json
import math
import os
from pathlib import Path
import re
import sys
import time

# role: (config entry, effort key, default effort)
CROSS_VENDOR_ROLES = {
    'review-full': ('review', 'full', 'xhigh'),
    'review-delta': ('review', 'delta', 'high'),
    'computer-use': ('computerUse', 'routine', 'medium'),
    'computer-use-hard': ('computerUse', 'hard', 'high'),
}
# Native roles: exploration, collection, tooling review, check runs, and trivial edits run fast;
# code, judgment, prose, and synthesis keep the parent's model.
FAST_ROLES = {'how-explorer', 'why-investigators', 'reflect-tooling', 'swarm-workers', 'fast-code'}
PARENT_ROLES = {'feature-refactoring', 'bug-fix', 'perf-issue', 'hillclimb', 'hardest-tasks', 'judgment-and-prose', 'how-explainer', 'why-synthesizer', 'reflect-judgment'}
FAST_MODEL = {'claude-code': 'sonnet'}
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
THRESHOLDS = {'fastWhileLeft': 40, 'skipWhenLeft': 5}
# Bounds that keep the usage scan to a few small reads.
DAY_DIRS, LOGS, TAIL_BYTES = 7, 8, 256 * 1024


def table(value):
    return value if isinstance(value, dict) else {}


def text(value):
    return value if isinstance(value, str) and value else None


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except OverflowError:
        return None


def load_config(path):
    try:
        return table(json.loads(path.read_text()))
    except (OSError, ValueError):
        return {}


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


def modified(path):
    try:
        return path.stat().st_mtime
    except OSError:
        return 0


def recent_logs(sessions):
    """Return the most recently written logs from the newest day folders that hold any."""
    days = (day for day in sorted(sessions.glob('*/*/*'), reverse=True) if any(day.glob('*.jsonl')))
    logs = [path for day in islice(days, DAY_DIRS) for path in day.glob('*.jsonl') if path.is_file()]
    return sorted(logs, key=modified, reverse=True)[:LOGS]


def last_snapshot(log):
    """Return the last Codex rate-limit snapshot in the log's tail as (timestamp, limits)."""
    with log.open('rb') as stream:
        stream.seek(max(0, stream.seek(0, os.SEEK_END) - TAIL_BYTES))
        tail = stream.read().decode('utf-8', 'replace')
    end = len(tail)
    while True:
        found = tail.rfind('"rate_limits":', 0, end)
        if found < 0:
            return None
        start = tail.rfind('\n', 0, found) + 1
        stop = tail.find('\n', found)
        end = start
        try:
            event = json.loads(tail[start : stop if stop >= 0 else len(tail)])
        except ValueError:
            continue
        limits = table(table(table(event).get('payload')).get('rate_limits'))
        if limits and limits.get('limit_id') in (None, 'codex'):
            return text(event.get('timestamp')) or '', limits


def window_left(window, now):
    used, resets = number(window.get('used_percent')), number(window.get('resets_at'))
    if used is None:
        return None
    return 100 if resets is not None and resets <= now else max(0, 100 - used)


def read_usage(sessions, now):
    """Return (percent left in the tightest window, its reset time, snapshot time) from the newest snapshot, or None."""
    snapshots = []
    for log in recent_logs(sessions):
        try:
            snapshot = last_snapshot(log)
        except OSError:
            continue
        if snapshot:
            snapshots.append(snapshot)
    if not snapshots:
        return None
    seen, limits = max(snapshots, key=lambda snapshot: snapshot[0])
    windows = [(window_left(window, now), window) for window in (table(limits.get('primary')), table(limits.get('secondary')))]
    windows = [(left, window) for left, window in windows if left is not None]
    if not windows:
        return None
    # Windows alone decide: rate_limit_reached_type is an account-wide reason with no reset time,
    # and a live usage-limit error already sends the caller to its fallback.
    left, window = min(windows, key=lambda pair: pair[0])
    return round(left), number(window.get('resets_at')), seen


def describe(left, resets):
    try:
        until = f" until {datetime.fromtimestamp(resets, timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}" if resets else ''
    except (OverflowError, OSError, ValueError):
        until = ''
    return f'Codex usage {left}% left{until}'


def capped(effort):
    # GPT models never run above xhigh.
    return 'xhigh' if effort in ('max', 'ultra') else effort


def thresholds(config):
    configured = table(config.get('codexUsage'))
    return {key: default if number(configured.get(key)) is None else configured[key] for key, default in THRESHOLDS.items()}


def resolve_native(parent, role, config, usage):
    entry = table(table(table(config.get(parent)).get('roles')).get(role))
    model = text(entry.get('model'))
    if model is None:
        model = FAST_MODEL.get(parent) if role in FAST_ROLES else None
    elif model in ('inherit-parent', 'auto'):
        model = None
    effort = text(entry.get('effort'))
    target = {'role': role, 'run': parent, 'model': model}
    if parent == 'codex':
        effort = capped(effort)
        fast = usage is None or usage[0] >= thresholds(config)['fastWhileLeft']
        target['serviceTier'] = (text(entry.get('serviceTier')) or 'priority') if fast else 'default'
    target['effort'] = effort if effort in EFFORTS else None
    return target


def resolve(parent, role, config, codex_model, usage):
    if role not in CROSS_VENDOR_ROLES:
        return resolve_native(parent, role, config, usage)
    entry_name, effort_key, default_effort = CROSS_VENDOR_ROLES[role]
    entry = table(table(config.get(parent)).get(entry_name))
    vendor = 'claude-code' if parent == 'codex' else 'codex'
    effort = text(table(entry.get('effort')).get(effort_key)) or default_effort
    target = {'role': role, 'run': vendor, 'providerInstanceId': text(entry.get('providerInstanceId')), 'model': text(entry.get('model')), 'effort': effort}
    # Claude has no speed option, so only a Codex target carries one.
    if vendor == 'claude-code':
        return target
    target.update(model=target['model'] or codex_model, effort=capped(effort), serviceTier=text(entry.get('serviceTier')))
    if usage is None:
        target['note'] = 'Codex usage unknown; using the configured speed'
        return target
    left, resets, seen = usage
    limits = thresholds(config)
    target['usage'] = {'left': left, 'seenAt': seen}
    if left < limits['skipWhenLeft']:
        return {'role': role, 'run': 'fallback', 'reason': describe(left, resets), 'usage': target['usage']}
    if left < limits['fastWhileLeft']:
        target.update(serviceTier='default', note=f'Standard speed: {describe(left, resets)}')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('role', choices=sorted({*CROSS_VENDOR_ROLES, *FAST_ROLES, *PARENT_ROLES}))
    parser.add_argument('--parent', choices=['codex', 'claude-code'], required=True, help='The host running this session')
    args = parser.parse_args()
    if args.parent == 'codex' and args.role.startswith('computer-use'):
        parser.error('Codex runs computer use itself')
    config = load_config(Path(os.environ.get('PSTACK_CONFIG') or Path.home() / '.config' / 'pstack' / 'config.json'))
    home = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
    codex_model, usage = None, None
    other = 'codex' if args.parent == 'claude-code' else 'claude-code'
    runs_on = other if args.role in CROSS_VENDOR_ROLES else args.parent
    if runs_on == 'codex':
        codex_model = configured_codex_model(home)
        try:
            usage = read_usage(home / 'sessions', time.time())
        except (OSError, ValueError):
            usage = None
    target = resolve(args.parent, args.role, config, codex_model, usage)
    print(json.dumps({key: value for key, value in target.items() if value is not None}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
