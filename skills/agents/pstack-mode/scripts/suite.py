#!/usr/bin/env python3
"""Validate the Pstack mapping, compare upstream inventories, and save checkpoints."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

MANIFEST = Path(__file__).resolve().parent.parent / 'suite.json'


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Required Git revision, path, or history is unavailable')
    return result.stdout


def field(text, name):
    found = re.search(r'^' + re.escape(name) + r':\s*(.+)$', text, re.M)
    if not found:
        raise ValueError('Missing frontmatter field ' + name)
    value = found[1].strip()
    return json.loads(value) if value.startswith('"') else value


def validate(root, manifest):
    problems = []
    entries = manifest['skills']
    names = [entry['local'] for entry in entries]
    if len(names) != len(set(names)) or len({entry['upstream'] for entry in entries}) != len(entries):
        problems.append('Suite mapping has duplicate names')
    for entry in entries:
        directory = root / entry['directory']
        name = entry['local']
        try:
            instruction = (directory/'SKILL.md').read_text()
            frontmatter = instruction.split('---', 2)[1]
            metadata = (directory/'agents/openai.yaml').read_text()
            if field(frontmatter, 'name') != name or directory.name != name:
                problems.append(name + ': directory/frontmatter mismatch')
            if not isinstance(field(frontmatter, 'description'), str):
                problems.append(name + ': description must be a string')
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name)>64:
                problems.append(name + ': invalid name')
            explicit = 'disable-model-invocation: true' in frontmatter
            if explicit != ('allow_implicit_invocation: false' in metadata):
                problems.append(name + ': invocation policy mismatch')
            if not explicit and ('disable-model-invocation:' in frontmatter or 'allow_implicit_invocation:' in metadata):
                problems.append(name + ': model-invoked dependencies must omit both restrictions')
            source = (directory/'UPSTREAM.md').read_text()
            for marker in ['Tracking policy:', 'Imported from commit:', 'Reviewed through commit:', 'License:', 'Local adaptations']:
                if marker not in source:
                    problems.append(name + ': missing provenance ' + marker)
            if not (directory/'LICENSE').exists():
                problems.append(name + ': missing retained license')
            for readme in [root/'README.md', directory.parent/'README.md']:
                if name not in readme.read_text():
                    problems.append(name + ': missing README listing ' + str(readme.relative_to(root)))
            for doc in directory.rglob('*.md'):
                for target in re.findall(r'\]\(([^)]+)\)', re.sub(r'`[^`]*`', '', doc.read_text())):
                    if '://' in target or target.startswith('#') or '<' in target:
                        continue
                    path = (doc.parent/target.split('#',1)[0]).resolve()
                    if not path.exists():
                        problems.append(str(doc.relative_to(root)) + ': broken link ' + target)
        except (OSError, ValueError, IndexError) as error:
            problems.append(name + ': ' + str(error))
    return {'valid': not problems, 'skills': len(entries), 'problems': problems}


def compare(root, upstream, candidate, manifest):
    candidate = git(upstream, 'rev-parse', '--verify', candidate+'^{commit}').strip()
    prefix = manifest['upstreamRoot']+'/skills/'
    paths = git(upstream, 'ls-tree', '-r', '--name-only', candidate, '--', prefix).splitlines()
    current = {p[len(prefix):].split('/')[0] for p in paths if p.startswith(prefix) and len(p[len(prefix):].split('/')) == 2 and p.endswith('/SKILL.md')}
    known = {entry['upstream'] for entry in manifest['skills']}
    changes = []
    for entry in manifest['skills']:
        try:
            record = (root/entry['directory']/'UPSTREAM.md').read_text()
            baseline = re.search(r'Reviewed through commit:\s*`([0-9a-f]{40})`', record)
            if not baseline:
                raise ValueError('Missing reviewed-through revision')
            baseline = baseline[1]
            changed = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate, '--', prefix+entry['upstream']).splitlines()
            changes.append({'local':entry['local'], 'upstream':entry['upstream'], 'baseline':baseline, 'status':'removed' if entry['upstream'] not in current else 'changed' if changed else 'unchanged', 'files':changed})
        except (OSError, ValueError) as error:
            changes.append({'local':entry['local'], 'upstream':entry['upstream'], 'status':'blocked', 'reason':str(error)})
    shared = []
    for baseline in sorted({entry['baseline'] for entry in changes if 'baseline' in entry}):
        files = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate, '--', 'pstack/agents', 'pstack/docs', 'pstack/.cursor-plugin', 'pstack/.claude-plugin', 'pstack/README.md', 'pstack/CHANGELOG.md', 'pstack/LICENSE').splitlines()
        shared.append({'baseline':baseline, 'files':files})
    return {'candidate':candidate, 'added':sorted(current-known), 'removed':sorted(known-current), 'skills':changes, 'sharedInputs':shared, 'policy':manifest['policy'], 'reviewComplete':False}


def checkpoint(manifest, candidate, completed, elapsed_minutes):
    names={entry['local'] for entry in manifest['skills']}
    if not set(completed)<=names or len(completed)!=len(set(completed)) or elapsed_minutes<0:
        raise ValueError('Checkpoint contains unknown/duplicate skills or invalid elapsed time')
    if not re.fullmatch(r'[0-9a-f]{40}',candidate):
        raise ValueError('Checkpoint candidate must be an immutable commit SHA')
    return {'schema':1, 'candidate':candidate, 'createdAt':datetime.now(timezone.utc).isoformat(), 'completed':sorted(completed), 'pending':sorted(names-set(completed)), 'elapsedMinutes':elapsed_minutes, 'reviewComplete':len(completed)==len(names), 'baselinesAdvancedByCheckpoint':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=MANIFEST)
    commands=parser.add_subparsers(dest='command',required=True)
    check=commands.add_parser('validate')
    check.add_argument('--root',type=Path,required=True)
    delta=commands.add_parser('compare')
    delta.add_argument('--root',type=Path,required=True)
    delta.add_argument('--upstream',type=Path,required=True)
    delta.add_argument('--candidate',required=True)
    save=commands.add_parser('checkpoint')
    save.add_argument('--candidate',required=True)
    save.add_argument('--completed',nargs='*',default=[])
    save.add_argument('--elapsed-minutes',type=float,required=True)
    for command in [check,delta,save]:
        command.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        manifest=json.loads(args.manifest.read_text())
        if args.command=='validate':
            result=validate(args.root.resolve(),manifest)
        elif args.command=='compare':
            result=compare(args.root.resolve(),args.upstream.resolve(),args.candidate,manifest)
        else:
            result=checkpoint(manifest,args.candidate,args.completed,args.elapsed_minutes)
        encoded=json.dumps(result,indent=2)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(encoded)
        print(encoded,end='')
        return 0 if result.get('valid',True) else 1
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps({'error':str(error),'reviewComplete':False}))
        return 2


if __name__=='__main__':
    sys.exit(main())
