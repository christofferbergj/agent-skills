#!/usr/bin/env python3
"""Read-only worktree audit. Candidate status is advice, not permission to remove."""

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time


def git(repo, *args):
    environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    return subprocess.run(['git', '--no-optional-locks', '-C', str(repo), *args], capture_output=True, env=environment)


def audit(repo, base, activity=None, ownership=None):
    listing = git(repo, 'worktree', 'list', '--porcelain', '-z')
    base_result = git(repo, 'rev-parse', '--verify', base + '^{commit}')
    if listing.returncode or base_result.returncode:
        raise ValueError('Repository or base ref is unavailable')
    primary = None
    checkouts = []
    current = None
    for cell in listing.stdout.split(b'\0'):
        if cell.startswith(b'worktree '):
            current = {'path': str(Path(os.fsdecode(cell[9:])).resolve())}
            if primary is None:
                primary = current['path']
            checkouts.append(current)
        elif current is not None and cell == b'locked':
            current['locked'] = True
        elif current is not None and cell.startswith(b'locked '):
            current['locked'] = True
    if primary is None:
        raise ValueError('No working trees found')
    for evidence in [activity, ownership]:
        if evidence is not None and not isinstance(evidence, dict):
            raise ValueError('Evidence index must be an object')
    repository = str(Path(primary).resolve())
    now = time.time()
    def fresh(evidence):
        stamp = evidence.get('generatedAt') if evidence else None
        return isinstance(stamp, (int, float)) and now - 900 <= stamp <= now + 60
    base_revision = base_result.stdout.decode().strip()
    history_scoped = bool(activity and activity.get('repository') == repository)
    coverage = activity.get('coverage', {}) if history_scoped else {}
    if not isinstance(coverage, dict):
        raise ValueError('History coverage must be an object')
    sessions = activity.get('sessions') if history_scoped else None
    valid_sessions = isinstance(sessions, list) and all(isinstance(item, dict) and isinstance(item.get('cwd'), str) and isinstance(item.get('mtime'), (int, float)) and math.isfinite(item['mtime']) and 0 <= item['mtime'] <= now + 60 for item in sessions)
    history_complete = fresh(activity) and activity.get('activityInspection') == 'workspace-metadata' and valid_sessions and isinstance(activity.get('days'), (int, float)) and activity['days'] >= 4 and all(isinstance(coverage.get(host), dict) and coverage[host].get('complete') is True for host in ['codex', 'claude-code']) if history_scoped else False
    owner_scoped = bool(ownership and ownership.get('repository') == repository and fresh(ownership))
    owners = {}
    for item in ownership.get('worktrees', []) if owner_scoped else []:
        if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not Path(item['path']).is_absolute():
            raise ValueError('Ownership paths must be absolute')
        key = str(Path(item['path']).resolve())
        owners[key] = None if key in owners else item
    rows = []
    for checkout in checkouts:
        path = checkout['path']
        reasons = []
        if path == primary:
            reasons.append('primary checkout')
        if checkout.get('locked'):
            reasons.append('Git worktree is locked')
        status = git(path, 'status', '--porcelain', '--untracked-files=all', '--ignored=matching', '--ignore-submodules=none')
        if status.returncode:
            reasons.append('working state unavailable')
        elif status.stdout:
            reasons.append('tracked, untracked, or ignored files exist')
        indexed = git(path, 'ls-files', '-v', '-z')
        if indexed.returncode or any(cell[:1].islower() or cell.startswith(b'S ') for cell in indexed.stdout.split(b'\0') if cell):
            reasons.append('index flags can hide local changes or index state is unknown')
        staged = git(path, 'ls-files', '--stage', '-z')
        if staged.returncode or any(cell.startswith(b'160000 ') for cell in staged.stdout.split(b'\0')):
            reasons.append('submodules require direct preservation inspection')
        git_directory = git(path, 'rev-parse', '--absolute-git-dir')
        states = ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-apply', 'rebase-merge', 'BISECT_LOG', 'sequencer']
        if git_directory.returncode or any((Path(os.fsdecode(git_directory.stdout).removesuffix('\n')) / name).exists() for name in states):
            reasons.append('in-progress Git operation or unavailable administrative state')
        head = git(path, 'rev-parse', 'HEAD')
        merged = head.returncode == 0 and git(repo, 'merge-base', '--is-ancestor', head.stdout.decode().strip(), base_revision).returncode == 0
        if not merged:
            reasons.append('head not proved contained in selected base')
        if not history_complete:
            reasons.append('cross-host history coverage unknown or incomplete')
        if valid_sessions and any(item['cwd'] == path and item['mtime'] >= now - 4 * 86400 for item in sessions):
            reasons.append('recent scoped conversation activity')
        owner = owners.get(path) or {}
        if owner.get('kind') not in ['ordinary', 'managed'] or any(owner.get(key) is not False for key in ['active', 'pinned', 'shared']):
            reasons.append('inactive, unpinned, unshared ownership not established')
        rows.append({'path': path, 'head': head.stdout.decode().strip() if head.returncode == 0 else None, 'mergedIntoBase': merged, 'ownerKind': owner.get('kind'), 'bucket': 'hold' if reasons else 'candidate-for-final-inspection', 'reasons': reasons})
    return {'repository': repository, 'base': base, 'baseRevision': base_revision, 'readOnly': True, 'freshness': 'Local refs only; recheck current remote, task state, ownership, and contents before removal.', 'worktrees': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--activity-index', type=Path)
    parser.add_argument('--ownership-index', type=Path)
    args = parser.parse_args()
    try:
        activity = json.loads(args.activity_index.read_text()) if args.activity_index else None
        ownership = json.loads(args.ownership_index.read_text()) if args.ownership_index else None
        print(json.dumps(audit(args.repo, args.base, activity, ownership), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print(json.dumps({'error': 'Audit unavailable; retain checkouts pending direct inspection'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
