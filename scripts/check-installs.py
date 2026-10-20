#!/usr/bin/env python3
"""Compare globally installed skills with this repository at a git ref.

Skills CLI records each installed skill's folder as a git tree hash in
~/.agents/.skill-lock.json, so an installed skill is current exactly when
that hash equals the tree at the ref. Reports stale, missing, unknown, and
retired installs, installs of the same name from another source, and entries
in ~/.claude/skills that load something other than the shared install.
Exits 1 when any is found.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def git(*args):
    return subprocess.run(['git', *args], stdout=subprocess.PIPE, text=True, check=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--ref', default='origin/main', help='git ref to compare with (default: origin/main; fetch first)')
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

    installed = json.loads(arguments.lock.read_text()).get('skills', {})
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

    print('\n'.join(problems) or f'All {len(trees)} skills match {arguments.ref}.')
    if any(line.split()[0] in ('missing', 'stale', 'unknown') for line in problems):
        print(f"\nRefresh with: npx skills@latest add {slug} --skill '*' --global")
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
