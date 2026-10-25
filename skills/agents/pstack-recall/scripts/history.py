#!/usr/bin/env python3
"""Discover and read repository-scoped Codex and Claude Code history."""

import argparse
from datetime import datetime, timezone
import fnmatch
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def git(repo, *args):
    environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    return subprocess.run(['git', '--no-optional-locks', '-C', str(repo), *args], capture_output=True, env=environment)


def workspaces(repo):
    repo = repo.resolve()
    result = git(repo, 'worktree', 'list', '--porcelain', '-z')
    if result.returncode:
        raise ValueError('Repository must be a Git working tree')
    roots = [Path(os.fsdecode(part[9:])).resolve() for part in result.stdout.split(b'\0') if part.startswith(b'worktree ')]
    if not roots:
        raise ValueError('Repository has no working trees')
    return roots[0], set(roots)


def workspace(value):
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        return None
    return Path(value).resolve()


def scoped_workspace(cwd, roots):
    if cwd in roots:
        return cwd
    if cwd is None or not any(cwd.is_relative_to(root) for root in roots):
        return None
    result = git(cwd, 'rev-parse', '--show-toplevel')
    if result.returncode:
        raise ValueError('Historical workspace inside this repository cannot be resolved')
    actual = Path(os.fsdecode(result.stdout).removesuffix('\n')).resolve()
    return actual if actual in roots else None


def object_record(value):
    if not isinstance(value, dict):
        raise ValueError('History record must be an object')
    return value


def codex_identity(path):
    with path.open(encoding='utf-8') as stream:
        first = stream.readline(4 * 1024 * 1024)
    item = object_record(json.loads(first))
    if item.get('type') != 'session_meta':
        raise ValueError('Unrecognized Codex session metadata')
    payload = object_record(item.get('payload', {}))
    return workspace(payload.get('cwd')), payload.get('id')


def claude_identity(path):
    with path.open(encoding='utf-8') as stream:
        for index, line in enumerate(stream):
            if index >= 100:
                break
            item = object_record(json.loads(line))
            if item.get('cwd'):
                return workspace(item['cwd']), item.get('sessionId')
    raise ValueError('Unrecognized Claude session metadata')


def history_files(directory, pattern):
    def failed(error):
        raise error
    for root, _, names in os.walk(directory, onerror=failed):
        for name in names:
            if fnmatch.fnmatchcase(name, pattern):
                yield Path(root) / name


def claude_workflow_journal(path):
    return path.name == 'journal.jsonl' and path.parent.parent.name == 'workflows'


def record_workspace(item, current):
    if item.get('type') == 'event_msg' and object_record(item.get('payload', {})).get('type') in ['task_started', 'turn_started']:
        return None
    if 'cwd' in item:
        current = workspace(item['cwd'])
        if current is None:
            raise ValueError('Explicit history workspace is invalid')
    if item.get('type') in ['session_meta', 'turn_context']:
        current = workspace(object_record(item.get('payload', {})).get('cwd'))
        if current is None:
            raise ValueError('History context has no valid workspace')
    return current


def session_workspaces(path, host, roots, cache):
    current, session_id = codex_identity(path) if host == 'codex' else claude_identity(path)
    seen = set()
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            item = object_record(json.loads(line))
            current = record_workspace(item, current)
            if current not in cache:
                cache[current] = scoped_workspace(current, roots)
            if cache[current] is not None:
                seen.add(cache[current])
    return session_id, seen


def index_history(repo, codex_home, claude_home, days):
    repo, roots = workspaces(repo)
    cutoff = time.time() - days * 86400
    sessions = []
    coverage = {}
    cache = {}
    hosts = [('codex', codex_home / 'sessions'), ('claude-code', claude_home / 'projects')]
    for host, directory in hosts:
        complete = directory.is_dir()
        reason = None if complete else 'History directory unavailable'
        try:
            directories = [directory] if complete else []
            archived = codex_home / 'archived_sessions'
            if host == 'codex' and archived.is_dir():
                directories.append(archived)
            paths = (path for folder in directories for path in history_files(folder, 'rollout-*.jsonl' if host == 'codex' else '*.jsonl'))
            for path in paths:
                if host == 'claude-code' and claude_workflow_journal(path):
                    continue
                try:
                    modified = path.stat().st_mtime
                    if modified < cutoff:
                        continue
                    session_id, seen = session_workspaces(path, host, roots, cache)
                    for scoped in sorted(seen):
                        sessions.append({'host': host, 'path': str(path.resolve()), 'id': session_id, 'cwd': str(scoped), 'mtime': modified, 'lastActivity': datetime.fromtimestamp(modified, timezone.utc).isoformat()})
                except (OSError, ValueError, TypeError):
                    complete = False
                    reason = 'Some history metadata could not be inspected'
        except OSError:
            complete = False
            reason = 'History traversal failed'
        coverage[host] = {'available': directory.is_dir(), 'complete': complete, 'reason': reason}
    sessions.sort(key=lambda item: item['mtime'], reverse=True)
    return {'repository': str(repo), 'generatedAt': time.time(), 'activityInspection': 'workspace-metadata', 'workspaces': sorted(map(str, roots)), 'days': days, 'coverage': coverage, 'sessions': sessions}


def message_text(item):
    payload = object_record(item.get('payload', {}))
    if item.get('type') == 'response_item' and payload.get('type') == 'message':
        message = payload
    elif item.get('type') in ['user', 'assistant']:
        message = object_record(item.get('message', {}))
    else:
        return None
    role = message.get('role')
    if role not in ['user', 'assistant']:
        return None
    content = message.get('content', '')
    if isinstance(content, list):
        parts = [part.get('text', '') for part in content if isinstance(part, dict) and part.get('type') in ['text', 'input_text', 'output_text']]
        if any(not isinstance(text, str) for text in parts):
            raise ValueError('Message text must be a string')
        content = '\n'.join(parts)
    return {'role': role, 'text': content} if isinstance(content, str) and content else None


def read_session(path, repo, codex_home, claude_home, max_chars):
    repo, roots = workspaces(repo)
    path = path.resolve()
    codex_roots = [(codex_home / name).resolve() for name in ['sessions', 'archived_sessions']]
    claude_root = (claude_home / 'projects').resolve()
    if any(path.is_relative_to(root) for root in codex_roots):
        host = 'codex'
        current, session_id = codex_identity(path)
    elif path.is_relative_to(claude_root):
        host = 'claude-code'
        current, session_id = claude_identity(path)
    else:
        raise ValueError('Session is outside scoped history directories')
    _, seen = session_workspaces(path, host, roots, {})
    if not seen:
        raise ValueError('Session belongs to another repository')
    messages = []
    used = 0
    truncated = False
    cache = {}
    pending = []
    pending_chars = 0
    awaiting_context = False
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            item = object_record(json.loads(line))
            if host == 'codex' and item.get('type') == 'event_msg' and object_record(item.get('payload', {})).get('type') in ['task_started', 'turn_started']:
                pending = []
                pending_chars = 0
                awaiting_context = True
                current = None
                continue
            if awaiting_context and item.get('type') != 'turn_context':
                message = message_text(item)
                remaining = max_chars - used - pending_chars + 1
                if message and remaining > 0:
                    message['text'] = message['text'][:remaining]
                    pending.append(message)
                    pending_chars += len(message['text'])
                continue
            current = record_workspace(item, current)
            if awaiting_context:
                candidates = pending
                pending = []
                awaiting_context = False
            else:
                candidates = [message_text(item)]
            if current not in cache:
                cache[current] = scoped_workspace(current, roots)
            if cache[current] is None:
                continue
            for message in candidates:
                if not message:
                    continue
                remaining = max_chars - used
                if remaining <= 0:
                    truncated = True
                    break
                if len(message['text']) > remaining:
                    message['text'] = message['text'][:remaining]
                    truncated = True
                messages.append(message)
                used += len(message['text'])
                if truncated:
                    break
            if truncated:
                break
    return {'untrustedEvidence': True, 'host': host, 'session': session_id, 'path': str(path), 'repository': str(repo), 'messages': messages, 'truncated': truncated, 'unresolvedTurnContext': bool(awaiting_context and pending)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home()/'.codex')))
    parser.add_argument('--claude-home', type=Path, default=Path(os.environ.get('CLAUDE_CONFIG_DIR', Path.home()/'.claude')))
    parser.add_argument('--read', type=Path)
    parser.add_argument('--max-chars', type=int, default=20000)
    args = parser.parse_args()
    if args.days <= 0 or args.max_chars <= 0:
        parser.error('days and max-chars must be positive')
    try:
        result = read_session(args.read, args.repo, args.codex_home, args.claude_home, args.max_chars) if args.read else index_history(args.repo, args.codex_home, args.claude_home, args.days)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({'error': type(error).__name__, 'reason': 'Scoped history unavailable or session outside the requested repository'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
