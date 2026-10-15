#!/usr/bin/env python3
"""Run a bounded, independent reviewer using the other vendor's CLI."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile


def run(args, *, cwd=None, timeout=20, input=None):
    process = subprocess.Popen(args, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=os.name == 'posix')
    try:
        stdout, stderr = process.communicate(input, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            if os.name == 'posix':
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            for stream in [process.stdin, process.stdout, process.stderr]:
                if stream:
                    stream.close()
            process.wait(timeout=1)
        raise
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)


def prepare(parent, repo):
    vendor = 'claude-code' if parent == 'codex' else 'codex'
    if os.name != 'posix':
        return vendor, None, 'Bounded reviewer process groups require a POSIX host'
    binary = shutil.which('claude' if vendor == 'claude-code' else 'codex')
    if not binary:
        return vendor, None, 'CLI is not installed'
    help_result = run([binary, '--help'] if vendor == 'claude-code' else [binary, 'exec', '--help'], cwd=repo)
    required = ['--safe-mode', '--strict-mcp-config', '--tools', '--permission-mode', '--permission-prompts', '--mcp-config', '--no-session-persistence', '--output-format'] if vendor == 'claude-code' else ['--sandbox', '--ephemeral', '--output-last-message', '--strict-config']
    advertised = set(re.findall(r'^\s*(?:-\w,\s*)?(--[a-z][a-z-]*)(?=[\s=,\[]|$)', help_result.stdout, re.MULTILINE))
    if help_result.returncode or any(flag not in advertised for flag in required):
        return vendor, None, 'Installed CLI lacks required review restrictions'
    if vendor == 'claude-code':
        auth = run([binary, 'auth', 'status'], cwd=repo)
        try:
            logged_in = auth.returncode == 0 and json.loads(auth.stdout).get('loggedIn') is True
        except (ValueError, AttributeError):
            logged_in = False
        if not logged_in:
            return vendor, None, 'CLI authentication is unavailable'
        return vendor, [binary, '-p', '--safe-mode', '--tools', 'Read,Glob,Grep', '--permission-mode', 'dontAsk', '--permission-prompts', 'none', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--no-session-persistence', '--output-format', 'json'], None
    if run([binary, 'login', 'status'], cwd=repo).returncode:
        return vendor, None, 'CLI authentication is unavailable'
    features = run([binary, 'features', 'list'], cwd=repo)
    supported = {line.split()[0] for line in features.stdout.splitlines() if line.split()}
    if features.returncode or not {'apps', 'plugins', 'hooks', 'browser_use', 'computer_use'} <= supported:
        return vendor, None, 'Installed CLI lacks required review feature controls'
    args = [binary, 'exec', '--strict-config', '--sandbox', 'read-only', '--ephemeral', '-c', 'approval_policy="never"', '-c', 'mcp_servers={}', '-c', 'features.apps=false', '-c', 'features.plugins=false', '-c', 'features.hooks=false', '-c', 'web_search="disabled"', '-c', 'features.browser_use=false', '-c', 'features.computer_use=false']
    return vendor, args, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent', choices=['codex', 'claude-code'], required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--prompt-file', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    result = {'vendor': None, 'status': 'unavailable', 'review': None, 'models': []}
    try:
        if not args.repo.is_dir() or args.timeout <= 0:
            raise ValueError('repo must exist and timeout must be positive')
        if not args.preflight and args.prompt_file is None:
            raise ValueError('--prompt-file is required unless --preflight is used')
        prompt = args.prompt_file.read_text() if not args.preflight else None
        vendor, command, reason = prepare(args.parent, args.repo.resolve())
        result['vendor'] = vendor
        if reason:
            result['reason'] = reason
        elif args.preflight:
            result['status'] = 'ready'
        else:
            with tempfile.TemporaryDirectory(prefix='pstack-review-') as temporary:
                final = Path(temporary) / 'final.txt'
                if vendor == 'codex':
                    command += ['--output-last-message', str(final), '-']
                completed = run(command, cwd=args.repo.resolve(), timeout=args.timeout, input=prompt)
                if completed.returncode:
                    result['reason'] = f'Reviewer exited with code {completed.returncode}; no independent verdict recorded'
                elif vendor == 'codex':
                    review = final.read_text().strip() if final.exists() else ''
                    if review:
                        result.update(status='completed', review=review)
                        model = re.search(r'^model:\s*(\S+)\s*$', completed.stderr, re.MULTILINE)
                        if model:
                            result['models'] = [model[1]]
                    else:
                        result['reason'] = 'Reviewer returned no final report'
                else:
                    response = json.loads(completed.stdout)
                    if not isinstance(response, dict) or response.get('is_error') or not isinstance(response.get('result'), str) or not response['result'].strip():
                        result['reason'] = 'Reviewer returned an error or empty result'
                    else:
                        result.update(status='completed', review=response['result'])
                        if isinstance(response.get('modelUsage'), dict):
                            result['models'] = sorted(response['modelUsage'])
    except subprocess.TimeoutExpired:
        result['reason'] = 'Reviewer timed out; no independent verdict recorded'
    except (OSError, ValueError) as error:
        result['reason'] = f'Reviewer unavailable: {type(error).__name__}'
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded)
        except OSError:
            result.update(status='unavailable', review=None, reason='Cannot write reviewer output')
            encoded = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    print(encoded, end='')
    return 0 if result['status'] in ['ready', 'completed'] else 2


if __name__ == '__main__':
    sys.exit(main())
