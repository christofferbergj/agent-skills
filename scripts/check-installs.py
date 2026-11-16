#!/usr/bin/env python3
"""Compare globally installed skills with this repository at a git ref.

Skills CLI records each installed skill's folder as a git tree hash in
~/.agents/.skill-lock.json, so an installed skill is current exactly when
that hash equals the tree at the ref. Reports stale, missing, unknown, and
retired installs, installs of the same name from another source, and entries
in ~/.claude/skills that load something other than the shared install.
Exits 1 when any is found. With --refresh, first runs the install it would
print for stale, missing, and unknown skills, rechecks, and reinstalls once
more the ones still outdated or reported failed; it also exits 1 when that
last install reports a failure.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

# Skills CLI agent keys, such as claude-code; anything else, such as --all, is not an agent.
AGENT = re.compile(r'[a-z0-9][a-z0-9-]*')


def git(*args):
    return subprocess.run(['git', *args], stdout=subprocess.PIPE, text=True, check=True).stdout


def install_command(slug, agents, skills=('*',)):
    """The install that refreshes these skills without prompts, or None when it would ask for the agents."""
    if isinstance(agents, list) and agents and all(isinstance(a, str) and AGENT.fullmatch(a) for a in agents):
        # Without --agent, --yes installs into every agent the CLI knows, some of which reject global skills.
        return ['npx', '-y', 'skills@latest', 'add', slug, '--skill', *skills, '--global', '--yes', '--agent', *agents]
    return None


def refresh_hint(slug, agents):
    """The install that refreshes every skill, with a note when it will ask for the agents."""
    command = install_command(slug, agents)
    if command:
        return f'Refresh with: {shlex.join(command)}'
    return (
        f"Refresh with: npx skills@latest add {slug} --skill '*' --global\n"
        'It asks for your agents, since the lock records no valid earlier choice.'
    )


def outdated(problems):
    """The skills an install fixes: stale, missing, and unknown ones."""
    return [line.split()[1] for line in problems if line.split()[0] in ('missing', 'stale', 'unknown')]


def install(command):
    """Run the install, print its failures, and return them as (skill or None, reason) pairs."""
    # Skills CLI records a skill once any agent's target succeeds and, without --json,
    # exits 0 when other targets fail; the --json report names each failed skill.
    command = [*command, '--json']
    print(f'Running: {shlex.join(command)}', flush=True)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        report = json.loads(result.stdout)
    except ValueError:
        report = None
    if isinstance(report, list) and all(isinstance(entry, dict) for entry in report):
        failures = [
            (entry.get('name'), str(entry.get('error') or entry.get('reason') or entry.get('status')))
            for entry in report
            if entry.get('status') != 'installed'
        ]
        if result.returncode and not failures:
            failures.append((None, f'the installer exited {result.returncode}'))
    else:
        failures = [(None, f'the installer exited {result.returncode} without a JSON report')]
        print((result.stdout + result.stderr)[-2000:].rstrip(), file=sys.stderr)
    for skill, reason in failures:
        print(f'Failed to install {skill or "skills"}: {reason}', file=sys.stderr)
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--ref', default='origin/main', help='git ref to compare with (default: origin/main; fetch first)')
    parser.add_argument('--refresh', action='store_true', help='install outdated skills, recheck, and retry the rest once')
    parser.add_argument('--retry-delay', type=float, default=15, help='seconds before the retry (default: 15)')
    parser.add_argument('--lock', type=Path, default=Path.home() / '.agents/.skill-lock.json')
    parser.add_argument('--shared-skills', type=Path, default=Path.home() / '.agents/skills')
    parser.add_argument('--claude-skills', type=Path, default=Path.home() / '.claude/skills')
    arguments = parser.parse_args()

    os.chdir(git('rev-parse', '--show-toplevel').strip())
    # Skills CLI records GitHub sources as owner/name.
    origin = git('remote', 'get-url', 'origin').strip().rstrip('/')
    match = re.search(r'github\.com[:/](.+?)(?:\.git)?$', origin)
    if not match:
        parser.error(f'origin is not a GitHub URL: {origin}')
    slug = match[1]
    trees = {}
    for path in git('ls-tree', '-r', '--name-only', arguments.ref, 'skills').splitlines():
        if path.endswith('/SKILL.md') and path.count('/') == 3:
            folder = path.rsplit('/', 1)[0]
            trees[folder.rsplit('/', 1)[1]] = (folder, git('rev-parse', f'{arguments.ref}:{folder}').strip())

    problems, lock = check(arguments, slug, trees)
    agents = lock.get('lastSelectedAgents')
    failures = []
    if arguments.refresh and install_command(slug, agents) and outdated(problems):
        failures = install(install_command(slug, agents))
        problems, lock = check(arguments, slug, trees)
        retry = sorted(set(outdated(problems)) | {skill for skill, _ in failures if skill})
        if retry or failures:
            # GitHub can serve the previous tree for a short while after a merge.
            time.sleep(arguments.retry_delay)
            failures = install(install_command(slug, agents, retry or ('*',)))
            problems, lock = check(arguments, slug, trees)
    problems += [f'failed   {skill or "install"}: {" ".join(reason.split())}' for skill, reason in failures]

    print('\n'.join(problems) or f'All {len(trees)} skills match {arguments.ref}.')
    if outdated(problems):
        print(f"\n{refresh_hint(slug, lock.get('lastSelectedAgents'))}")
    return 1 if problems else 0


def check(arguments, slug, trees):
    """Each install problem, and the lock it was read from."""
    lock = json.loads(arguments.lock.read_text())
    installed = lock.get('skills', {})
    problems = []
    for name, (folder, tree) in sorted(trees.items()):
        entry = installed.get(name)
        shared = arguments.shared_skills / name
        if entry is None or not (shared / 'SKILL.md').is_file():
            problems.append(f'missing  {name}')
        elif entry.get('source') != slug:
            problems.append(f'foreign  {name} is installed from {entry.get("source")}')
        elif not re.fullmatch(r'[0-9a-f]{40}', entry.get('skillFolderHash', '')):
            # Skills CLI falls back to another hash when it cannot read the GitHub tree.
            problems.append(f'unknown  {name} has no git tree hash in the lock; reinstall it to compare')
        elif entry['skillFolderHash'] != tree:
            problems.append(f'stale    {name}')
        shadow = arguments.claude_skills / name
        if shadow.exists() and shadow.resolve() != shared.resolve():
            problems.append(f'shadow   {name} loads {shadow.resolve()} instead of {shared}')
    for name, entry in sorted(installed.items()):
        if entry.get('source') == slug and name not in trees:
            problems.append(f'retired  {name} is installed but no longer in {arguments.ref}')
    return problems, lock


if __name__ == '__main__':
    sys.exit(main())
