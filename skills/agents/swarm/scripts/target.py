#!/usr/bin/env python3
"""Resolve a delegate's model, effort, and speed, stepping Codex targets down as Codex usage runs low.

Reads PSTACK_CONFIG or ~/.config/pstack/config.json. Every key is optional:

  {"codexUsage": {"skipWhenLeft": 5},
   "claude-code": {
     "review": {"providerInstanceId": "codex", "model": "gpt-6.1-sol",
                "effort": {"full": "xhigh", "delta": "high"}, "serviceTier": "priority"},
     "computerUse": {"providerInstanceId": "codex", "model": "gpt-6.1-sol",
                     "effort": {"routine": "medium", "hard": "high"}, "serviceTier": "priority"},
     "roles": {"how-explorer": {"model": "haiku", "effort": "low"}}},
   "codex": {"review": {"model": "claude-opus-5-5", "effort": {"full": "xhigh", "delta": "high"}}}}

A Codex target runs at serviceTier "priority" unless configured otherwise while every usage
window is on pace: its percent left is at least the share of the window still to run, so a
window that resets soon can be spent down. A window behind pace drops it to "default" unless
banked resets cover the gap; a reset counts as a full window when it outlasts that window and
pro rata when it expires sooner. Below skipWhenLeft percent left, a cross-vendor target becomes
run "fallback". Claude targets carry no speed. Usage comes from the newest snapshots in
$CODEX_HOME/sessions, so the check stays local. Banked resets come from `codex app-server`,
cached for an hour, and are read only when a window is behind pace.

The review and computer-use roles run on the other vendor. Every other role is one of
Pstack's native roles and runs on the parent host: fast-code on the host's fast model
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
import subprocess
import sys
import threading
import time

# role: (config entry, effort key, default effort)
CROSS_VENDOR_ROLES = {
    'review-full': ('review', 'full', 'xhigh'),
    'review-delta': ('review', 'delta', 'high'),
    'computer-use': ('computerUse', 'routine', 'medium'),
    'computer-use-hard': ('computerUse', 'hard', 'high'),
}
# Native roles: trivial edits run fast; exploration, collection, tooling review, check runs, code,
# judgment, prose, and synthesis keep the parent's model.
FAST_ROLES = {'fast-code'}
PARENT_ROLES = {'how-explorer', 'why-investigators', 'reflect-tooling', 'swarm-workers', 'feature-refactoring', 'bug-fix', 'perf-issue', 'hillclimb', 'hardest-tasks', 'judgment-and-prose', 'how-explainer', 'why-synthesizer', 'reflect-judgment'}
FAST_MODEL = {'claude-code': 'sonnet'}
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
THRESHOLDS = {'skipWhenLeft': 5}
# Bounds that keep the usage scan to a few small reads.
DAY_DIRS, LOGS, TAIL_BYTES = 7, 8, 256 * 1024
# Banked resets change a few times a month, so one app-server read serves an hour.
RESETS_TTL, RESETS_TIMEOUT = 3600, 5


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


def even_pace(window, now):
    """Return the percent left that spending evenly to the reset would leave, or None without a reset time and length."""
    resets, minutes = number(window.get('resets_at')), number(window.get('window_minutes'))
    if resets is None or minutes is None or minutes <= 0:
        return None
    return min(100, max(0, 100 * (resets - now) / (minutes * 60)))


def read_usage(sessions, now):
    """Return the windows of the newest snapshot and its time, or None.

    Each window has its percent left, reset time, and even-pace percent."""
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
    windows = []
    for window in (table(limits.get('primary')), table(limits.get('secondary'))):
        left = window_left(window, now)
        if left is not None:
            windows.append({'left': left, 'resets': number(window.get('resets_at')), 'pace': even_pace(window, now)})
    # Windows alone decide: rate_limit_reached_type is an account-wide reason with no reset time,
    # and a live usage-limit error already sends the caller to its fallback.
    return {'windows': windows, 'seen': seen} if windows else None


def fetch_reset_credits():
    """Ask Codex's app-server for the account's banked resets and return their expiry times, or None."""
    requests = [
        {'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'pstack-target', 'version': '1'}}},
        {'method': 'initialized'},
        {'id': 2, 'method': 'account/rateLimits/read', 'params': {}},
    ]
    try:
        server = subprocess.Popen(['codex', 'app-server'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except OSError:
        return None
    reply = {}

    def read():
        for line in server.stdout:
            try:
                message = table(json.loads(line))
            except ValueError:
                continue
            if message.get('id') == 2:
                reply.update(message)
                return

    reader = threading.Thread(target=read, daemon=True)
    try:
        # The server exits on end of input before it answers, so input stays open until the reply.
        server.stdin.write(''.join(json.dumps(request) + '\n' for request in requests))
        server.stdin.flush()
        reader.start()
        reader.join(RESETS_TIMEOUT)
    except OSError:
        return None
    finally:
        server.kill()
        server.wait()
        if reader.ident is not None:
            reader.join(1)
        for stream in (server.stdin, server.stdout):
            try:
                stream.close()
            except OSError:
                pass
    if 'result' not in reply:
        return None
    summary = table(table(reply['result']).get('rateLimitResetCredits'))
    credits = summary.get('credits')
    if not isinstance(credits, list):
        # Without detail rows only the count is known, so each reset counts as never expiring.
        return [None] * max(0, min(int(number(summary.get('availableCount')) or 0), 100))
    return [number(credit.get('expiresAt')) for credit in map(table, credits) if credit.get('status') == 'available']


def unexpired(value, now):
    if not isinstance(value, list):
        return None
    return [entry for entry in value if entry is None or (number(entry) is not None and entry > now)]


def reset_credits(cache, now):
    """Return the expiry times of the account's banked resets, None for one that never expires, or None when unknown."""
    try:
        cached = table(json.loads(cache.read_text()))
    except (OSError, ValueError):
        cached = {}
    fetched, expiries = number(cached.get('fetchedAt')), unexpired(cached.get('expiries'), now)
    if fetched is not None and 0 <= now - fetched < RESETS_TTL:
        return expiries
    # A failed read keeps the last known resets, whose expiry still counts against now, and waits
    # the same hour before trying again, so an offline machine pays the timeout once an hour.
    fresh = unexpired(fetch_reset_credits(), now)
    expiries = fresh if fresh is not None else expiries
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({'fetchedAt': now, 'expiries': expiries}))
    except OSError:
        pass
    return expiries


def banked_credit(expiries, resets, now):
    """Return the percent of a window that banked resets add before it resets."""
    return sum(100 if expiry is None or expiry >= resets else 100 * max(0, expiry - now) / (resets - now) for expiry in expiries)


def pace(usage, banked, now):
    """Return (fast, the window behind pace or None, banked resets read or None).

    banked is called only when a window is behind pace, so an on-pace check reads nothing more."""
    behind = [window for window in usage['windows'] if window['pace'] is not None and window['left'] < window['pace']]
    if not behind:
        return True, None, None
    window = min(behind, key=lambda window: window['left'] - window['pace'])
    expiries = banked()
    if expiries is None:
        return False, window, None
    covered = all(window['left'] + banked_credit(expiries, window['resets'], now) >= window['pace'] for window in behind)
    return covered, window, expiries


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


def pace_note(window, expiries):
    behind = f"{describe(round(window['left']), window['resets'])}, under the {round(window['pace'])}% even pace leaves"
    if expiries is None:
        return f'{behind}; banked resets unknown'
    return f"{behind}; {len(expiries)} banked reset{'' if len(expiries) == 1 else 's'}"


def resolve_native(parent, role, config, usage, banked, now):
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
        fast = usage is None or pace(usage, banked, now)[0]
        target['serviceTier'] = 'priority' if fast else 'default'
    target['effort'] = effort if effort in EFFORTS else None
    return target


def resolve(parent, role, config, codex_model, usage, banked, now):
    if role not in CROSS_VENDOR_ROLES:
        return resolve_native(parent, role, config, usage, banked, now)
    entry_name, effort_key, default_effort = CROSS_VENDOR_ROLES[role]
    entry = table(table(config.get(parent)).get(entry_name))
    vendor = 'claude-code' if parent == 'codex' else 'codex'
    effort = text(table(entry.get('effort')).get(effort_key)) or default_effort
    target = {'role': role, 'run': vendor, 'providerInstanceId': text(entry.get('providerInstanceId')), 'model': text(entry.get('model')), 'effort': effort}
    # Claude targets run at standard speed, so only a Codex target carries one.
    if vendor == 'claude-code':
        return target
    target.update(model=target['model'] or codex_model, effort=capped(effort), serviceTier=text(entry.get('serviceTier')) or 'priority')
    if usage is None:
        target['note'] = 'Codex usage unknown; using the configured speed'
        return target
    tightest = min(usage['windows'], key=lambda window: window['left'])
    left = round(tightest['left'])
    target['usage'] = {'left': left, 'seenAt': usage['seen']}
    if left < thresholds(config)['skipWhenLeft']:
        return {'role': role, 'run': 'fallback', 'reason': describe(left, tightest['resets']), 'usage': target['usage']}
    fast, window, expiries = pace(usage, banked, now)
    if expiries is not None:
        target['usage']['bankedResets'] = len(expiries)
    if not fast:
        target.update(serviceTier='default', note=f'Standard speed: {pace_note(window, expiries)}')
    elif window is not None:
        target['note'] = f'Banked resets keep fast mode: {pace_note(window, expiries)}'
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
    cache = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'pstack' / 'codex-reset-credits.json'
    now, codex_model, usage = time.time(), None, None
    other = 'codex' if args.parent == 'claude-code' else 'claude-code'
    runs_on = other if args.role in CROSS_VENDOR_ROLES else args.parent
    if runs_on == 'codex':
        codex_model = configured_codex_model(home)
        try:
            usage = read_usage(home / 'sessions', now)
        except (OSError, ValueError):
            usage = None
    target = resolve(args.parent, args.role, config, codex_model, usage, lambda: reset_credits(cache, now), now)
    print(json.dumps({key: value for key, value in target.items() if value is not None}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
