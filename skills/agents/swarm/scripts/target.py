#!/usr/bin/env python3
"""Resolve a delegate's model, effort, and speed, stepping Codex targets down as Codex usage runs low.

Reads PSTACK_CONFIG or ~/.config/pstack/config.json. Every key is optional:

  {"codexUsage": {"skipWhenLeft": 5, "paceSlackHours": 24, "floorPercent": 25, "reservePerDay": 15},
   "claude-code": {
     "review": {"providerInstanceId": "codex", "model": "gpt-6.1-sol",
                "effort": {"full": "xhigh", "delta": "high"}, "serviceTier": "priority"},
     "computerUse": {"providerInstanceId": "codex", "model": "gpt-6.1-sol",
                     "effort": {"routine": "medium", "hard": "high"}, "serviceTier": "priority"},
     "budget": "large",
     "roles": {"swarm-workers": {"model": "sonnet", "effort": "medium"}}},
   "codex": {"review": {"model": "claude-opus-5-5", "effort": {"full": "xhigh", "delta": "high"}}}}

A Codex target runs at serviceTier "priority" unless configured otherwise while every usage
window keeps its lines. Even pace: its percent left is at least the share of the window still
to run less paceSlackHours, so a day's lead, made up by the idle night, is allowed. The floor:
at least reservePerDay percent for each day a window of a day or longer still runs, capped at floorPercent, so
the window's last days keep enough for standard-speed work and a window that resets soon can
still be spent down. A window under either line drops it to "default" unless a banked reset
expires before that window resets: such a reset lapses unless redeemed now, so fast mode runs
on, to skipWhenLeft for a cross-vendor target, and the note names its expiry. A reset that outlasts the window keeps
its worth for a later week and keeps nothing fast. Below skipWhenLeft percent left, a
cross-vendor target becomes run "fallback". Claude targets carry no speed. Usage comes from the
newest snapshots in $CODEX_HOME/sessions, so the check stays local. Banked resets come from
`codex app-server`, cached for an hour per Codex account, and are read only when a window is
under a line or a cross-vendor target falls back.

Codex Computer Use drives a Mac desktop, so a computer-use role on any other machine, such as
a Linux server, is run "fallback" without reading usage, unless --on-mac says the child runs on
a linked macOS machine.

The review and computer-use roles run on the other vendor. Every other role is one of
Pstack's native roles and runs on the parent host. In Claude Code each takes upstream's
default model and effort: Opus at xhigh for code, judgment, and prose, Opus at high for
swarm workers and reflect tooling, and Fable at xhigh, one step below upstream's max, for
the hardest tasks. fast-code, for trivial edits, follows swarm workers there, as upstream's
do. A budget moves those default efforts as upstream's does: unlimited one
step up, large not at all, medium one step down, small two. Codex native roles keep the
parent's model and effort. A native Codex role runs fast while Codex usage allows, and Claude
never runs fast. Native roles take upstream's labels in kebab case; reflect-judgment shortens
"reflect judgment, divergent, synthesizer". long-running, the one local role, is a thread that
runs for hours, such as a coordinator or one of its workers; it keeps the parent's model, so
a roles entry can move those threads off a model with a tight weekly allowance. A roles entry
overrides the model or the effort; "inherit-parent" or "auto" as the model keeps the parent's
model and drops the default effort.
"""

import argparse
import contextlib
from datetime import datetime, timezone
from itertools import islice
import json
import math
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import time

# role: (config entry, effort key, default effort)
CROSS_VENDOR_ROLES = {
    'review-full': ('review', 'full', 'xhigh'),
    'review-delta': ('review', 'delta', 'high'),
    'computer-use': ('computerUse', 'routine', 'medium'),
    'computer-use-hard': ('computerUse', 'hard', 'high'),
}
# Upstream's Claude Code defaults, (model, effort) per native role. Fable at max timed out on
# long tasks and scored below xhigh in Claude Code benchmarks at about three times the cost.
CODE, WORKERS = ('opus', 'xhigh'), ('opus', 'high')
NATIVE_DEFAULTS = {'claude-code': {
    'feature-refactoring': CODE, 'bug-fix': CODE, 'perf-issue': CODE, 'hillclimb': CODE,
    'judgment-and-prose': CODE, 'reflect-judgment': CODE,
    'swarm-workers': WORKERS, 'reflect-tooling': WORKERS, 'fast-code': WORKERS,
    'hardest-tasks': ('fable', 'xhigh'),
}}
NATIVE_ROLES = {*NATIVE_DEFAULTS['claude-code'], 'long-running'}
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
BUDGET_STEPS = {'unlimited': 1, 'large': 0, 'medium': -1, 'small': -2}
THRESHOLDS = {'skipWhenLeft': 5, 'paceSlackHours': 24, 'floorPercent': 25, 'reservePerDay': 15}
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


def even_pace(window, now, slack_hours):
    """Return the percent left that spending evenly to slack_hours before the reset would leave, or None without a reset time and length."""
    resets, minutes = number(window.get('resets_at')), number(window.get('window_minutes'))
    if resets is None or minutes is None or minutes <= 0:
        return None
    return min(100, max(0, 100 * (resets - now - slack_hours * 3600) / (minutes * 60)))


def binding_line(window, now, settings):
    """Return (percent, name) of the line fast mode keeps the window above: even pace or the floor, whichever asks for more.

    Without a reset time the window has neither line and returns (None, None). Only a window a day or longer keeps a floor."""
    resets, minutes = number(window.get('resets_at')), number(window.get('window_minutes'))
    if resets is None:
        return None, None
    floor = min(100, settings['floorPercent'], settings['reservePerDay'] * (resets - now) / 86400) if minutes and minutes >= 1440 else 0
    pace = even_pace(window, now, settings['paceSlackHours'])
    return (pace, 'even pace leaves') if pace is not None and pace >= floor else (floor, 'floor')


def read_usage(sessions, now, settings):
    """Return the windows of the newest snapshot and its time, or None.

    Each window has its percent left, reset time, and binding line's percent and name."""
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
        if left is None:
            continue
        line, line_name = binding_line(window, now, settings)
        windows.append({'left': left, 'resets': number(window.get('resets_at')), 'line': line, 'lineName': line_name})
    # Windows alone decide: rate_limit_reached_type is an account-wide reason with no reset time,
    # and a live usage-limit error already sends the caller to its fallback.
    return {'windows': windows, 'seen': seen} if windows else None


def read_rate_limits():
    """Return the result of `codex app-server`'s account/rateLimits/read, or None."""
    # Bounding the read needs process groups, as review.py's runs do.
    if os.name != 'posix':
        return None
    requests = [
        {'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'pstack-target', 'version': '1'}}},
        {'method': 'initialized'},
        {'id': 2, 'method': 'account/rateLimits/read', 'params': {}},
    ]
    deadline = time.monotonic() + RESETS_TIMEOUT
    try:
        with subprocess.Popen(['codex', 'app-server'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True) as server:
            try:
                # The server exits on end of input before it answers, so input stays open until the reply.
                server.stdin.write(''.join(json.dumps(request) + '\n' for request in requests).encode())
                server.stdin.flush()
                pending = b''
                while select.select([server.stdout], [], [], max(0, deadline - time.monotonic()))[0]:
                    chunk = os.read(server.stdout.fileno(), 65536)
                    if not chunk:
                        return None
                    *lines, pending = (pending + chunk).split(b'\n')
                    for line in lines:
                        try:
                            message = table(json.loads(line))
                        except ValueError:
                            continue
                        if message.get('id') == 2:
                            return message.get('result')
                return None
            finally:
                # The whole group goes, so a launcher's child cannot outlive the read.
                with contextlib.suppress(OSError):
                    os.killpg(server.pid, signal.SIGKILL)
    except OSError:
        return None


def banked_expiries(result):
    """Return the expiry times of the available banked resets in an account/rateLimits/read result, or None."""
    summary = table(table(result).get('rateLimitResetCredits'))
    credits = summary.get('credits')
    if not isinstance(credits, list):
        # A count without detail rows says nothing about expiry, so only a zero count is a reading.
        return [] if number(summary.get('availableCount')) == 0 else None
    expiries = [credit.get('expiresAt', '') for credit in map(table, credits) if credit.get('status') == 'available']
    # Only an explicit null means never expiring; any other value that isn't a time makes the reading unknown.
    if any(expiry is not None and number(expiry) is None for expiry in expiries):
        return None
    return expiries


def fetch_reset_credits():
    """Ask Codex's app-server for the account's banked resets and return their expiry times, or None."""
    return banked_expiries(read_rate_limits())


def unexpired(value, now):
    if not isinstance(value, list):
        return None
    return [entry for entry in value if entry is None or (number(entry) is not None and entry > now)]


def codex_account(home):
    """Return the identity whose banked resets a cache entry holds: the Codex home and its signed-in account."""
    try:
        account = text(table(table(json.loads((home / 'auth.json').read_text())).get('tokens')).get('account_id'))
    except (OSError, ValueError):
        account = None
    return f'{home.resolve()}:{account}'


def reset_credits(cache, account, now):
    """Return the expiry times of the account's banked resets, None for one that never expires, or None when unknown."""
    try:
        cached = table(json.loads(cache.read_text()))
    except (OSError, ValueError):
        cached = {}
    fetched = number(cached.get('fetchedAt'))
    if cached.get('account') == account and fetched is not None and 0 <= now - fetched < RESETS_TTL:
        return unexpired(cached.get('expiries'), now)
    # A failed read is cached as unknown, so an offline machine pays the timeout once an hour
    # and a stale reading never outlives its hour.
    expiries = unexpired(fetch_reset_credits(), now)
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({'account': account, 'fetchedAt': now, 'expiries': expiries}))
    except OSError:
        pass
    return expiries


def lapsing(expiries, window):
    """Return the expiry times of banked resets that lapse before the window resets."""
    return [expiry for expiry in expiries if expiry is not None and expiry < window['resets']]


def first_lapse(expiries, window):
    """Return when the earliest banked reset that lapses before the window resets expires, as text."""
    return moment(min(lapsing(expiries, window))) or 'soon'


def check_speed(usage, read_banked):
    """Return (fast, the window furthest under its line or None, banked resets read or None).

    read_banked is called only when a window is under its line, so a check above every line reads nothing more."""
    under = [window for window in usage['windows'] if window['line'] is not None and window['left'] < window['line']]
    if not under:
        return True, None, None
    furthest = min(under, key=lambda window: window['left'] - window['line'])
    expiries = read_banked()
    if expiries is None:
        return False, furthest, None
    return all(lapsing(expiries, window) for window in under), furthest, expiries


def moment(stamp):
    try:
        return datetime.fromtimestamp(stamp, timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    except (OverflowError, OSError, ValueError, TypeError):
        return None


def describe(left, resets):
    until = moment(resets)
    return f'Codex usage {left}% left until {until}' if until else f'Codex usage {left}% left'


def has_mac_desktop():
    return sys.platform == 'darwin'


def capped(effort):
    # GPT models never run above xhigh.
    return 'xhigh' if effort in ('max', 'ultra') else effort


def thresholds(config):
    configured = table(config.get('codexUsage'))
    return {key: default if number(configured.get(key)) is None else configured[key] for key, default in THRESHOLDS.items()}


def speed_note(fast, window, expiries):
    """Return the note for a window under its line: why it runs at standard speed, or which lapsing reset keeps it fast."""
    under = f"{describe(round(window['left']), window['resets'])}, under the {round(window['line'])}% {window['lineName']}"
    if expiries is None:
        return f'Standard speed: {under}; banked resets unknown'
    lapse = lapsing(expiries, window)
    resets = f"{len(expiries)} banked reset{'' if len(expiries) == 1 else 's'}, {len(lapse)} expiring before then"
    if not fast:
        return f'Standard speed: {under}; {resets}'
    return f'A banked reset expiring {first_lapse(expiries, window)} keeps fast mode: {under}; {resets}. Redeem it once Codex usage runs out, and before it expires at the latest'


def budgeted(effort, budget):
    step = EFFORTS.index(effort) + BUDGET_STEPS.get(budget, 0)
    return EFFORTS[min(max(step, 0), len(EFFORTS) - 1)]


def resolve_native(parent, role, config, usage, read_banked):
    host = table(config.get(parent))
    roles = table(host.get('roles'))
    entry = table(roles.get(role))
    # Upstream sends trivial edits to its swarm workers model, so Claude Code's fast-code follows that entry.
    if not entry and parent == 'claude-code' and role == 'fast-code':
        entry = table(roles.get('swarm-workers'))
    model, effort = text(entry.get('model')), text(entry.get('effort'))
    default_model, default_effort = NATIVE_DEFAULTS.get(parent, {}).get(role, (None, None))
    if model in ('inherit-parent', 'auto'):
        model, default_effort = None, None
    elif model is None:
        model = default_model
    if effort not in EFFORTS and default_effort is not None:
        effort = budgeted(default_effort, text(host.get('budget')))
    target = {'role': role, 'run': parent, 'model': model}
    if parent == 'codex':
        effort = capped(effort)
        fast = usage is None or check_speed(usage, read_banked)[0]
        target['serviceTier'] = 'priority' if fast else 'default'
    target['effort'] = effort if effort in EFFORTS else None
    return target


def resolve(parent, role, config, codex_model, usage, read_banked):
    if role not in CROSS_VENDOR_ROLES:
        return resolve_native(parent, role, config, usage, read_banked)
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
        reason, expiries = describe(left, tightest['resets']), read_banked()
        if expiries and tightest['resets'] is not None and lapsing(expiries, tightest):
            reason += f'; a banked reset expiring {first_lapse(expiries, tightest)} lapses first, so redeem it to refill Codex'
        return {'role': role, 'run': 'fallback', 'reason': reason, 'usage': target['usage']}
    fast, window, expiries = check_speed(usage, read_banked)
    if expiries is not None:
        target['usage']['bankedResets'] = len(expiries)
    if not fast:
        target['serviceTier'] = 'default'
    if window is not None:
        target['note'] = speed_note(fast, window, expiries)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('role', choices=sorted({*CROSS_VENDOR_ROLES, *NATIVE_ROLES}))
    parser.add_argument('--parent', choices=['codex', 'claude-code'], required=True, help='The host running this session')
    parser.add_argument('--on-mac', action='store_true', help='A computer-use child runs on a linked macOS machine, not this one')
    args = parser.parse_args()
    if args.parent == 'codex' and args.role.startswith('computer-use'):
        parser.error('Codex runs computer use itself')
    config = load_config(Path(os.environ.get('PSTACK_CONFIG') or Path.home() / '.config' / 'pstack' / 'config.json'))
    home = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
    cache = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'pstack' / 'codex-reset-credits.json'
    if args.role.startswith('computer-use') and not (args.on_mac or has_mac_desktop()):
        print(json.dumps({'role': args.role, 'run': 'fallback', 'reason': f'Codex Computer Use needs a Mac desktop; this machine runs {sys.platform}'}))
        return 0
    now, codex_model, usage = time.time(), None, None
    other = 'codex' if args.parent == 'claude-code' else 'claude-code'
    runs_on = other if args.role in CROSS_VENDOR_ROLES else args.parent
    if runs_on == 'codex':
        codex_model = configured_codex_model(home)
        try:
            usage = read_usage(home / 'sessions', now, thresholds(config))
        except (OSError, ValueError):
            usage = None
    target = resolve(args.parent, args.role, config, codex_model, usage, lambda: reset_credits(cache, codex_account(home), now))
    print(json.dumps({key: value for key, value in target.items() if value is not None}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
