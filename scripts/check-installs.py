#!/usr/bin/env python3
"""Compare globally installed skills with this repository at a git ref.

Skills CLI records each installed skill's folder as a git tree hash in
~/.agents/.skill-lock.json, so an installed skill is current exactly when
that hash equals the tree at the ref. Reports stale, missing, and retired
installs, installs of the same name from another source, and copies in
~/.claude/skills that shadow the shared install. Exits 1 when any is found.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def git(*args):
    return subprocess.run(['git', *args], capture_output=True, text=True, check=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--ref', default='origin/main', help='git ref to compare with (default: origin/main; fetch first)')
    parser.add_argument('--lock', type=Path, default=Path.home() / '.agents/.skill-lock.json')
    parser.add_argument('--claude-skills', type=Path, default=Path.home() / '.claude/skills')
    arguments = parser.parse_args()

    os.chdir(git('rev-parse', '--show-toplevel').strip())
    # Skills CLI records GitHub sources as owner/name.
    slug = re.search(r'github\.com[:/](.+?)(?:\.git)?$', git('remote', 'get-url', 'origin').strip())[1]
    trees = {}
    for path in git('ls-tree', '-r', '--name-only', arguments.ref, 'skills').splitlines():
        if path.endswith('/SKILL.md') and path.count('/') == 3:
            folder = path.rsplit('/', 1)[0]
            trees[folder.rsplit('/', 1)[1]] = (folder, git('rev-parse', f'{arguments.ref}:{folder}').strip())

    installed = json.loads(arguments.lock.read_text()).get('skills', {})
    problems = []
    for name, (folder, tree) in sorted(trees.items()):
        entry = installed.get(name)
        if entry is None:
            problems.append(f'missing  {name}')
        elif entry.get('source') != slug:
            problems.append(f'foreign  {name} is installed from {entry.get("source")}')
        elif entry.get('skillFolderHash') != tree:
            problems.append(f'stale    {name}')
        shadow = arguments.claude_skills / name
        if shadow.exists() and not shadow.is_symlink():
            problems.append(f'shadow   {name} has a separate copy at {shadow}')
    for name, entry in sorted(installed.items()):
        if entry.get('source') == slug and name not in trees:
            problems.append(f'retired  {name} is installed but no longer in {arguments.ref}')

    print('\n'.join(problems) or f'All {len(trees)} skills match {arguments.ref}.')
    if any(line.split()[0] in ('missing', 'stale') for line in problems):
        print(f"\nRefresh with: npx skills@latest add {slug} --skill '*' --global")
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
