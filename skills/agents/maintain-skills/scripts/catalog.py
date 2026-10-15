#!/usr/bin/env python3
"""Inspect, validate, compare, and checkpoint the combined skill library."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

CATALOG = Path(__file__).resolve().parents[1] / 'catalog.json'


def git(repository, *arguments):
    environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    result = subprocess.run(
        ['git', '--no-optional-locks', '-C', str(repository), *arguments],
        capture_output=True, env=environment,
    )
    if result.returncode:
        raise ValueError('Required Git revision, path, or history is unavailable')
    return result.stdout


def source_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Catalog path leaves the source repository')
    return path


def sources(root, catalog):
    result = {}
    for key, definition in catalog['sources'].items():
        definition = dict(definition)
        if 'manifest' in definition:
            manifest = json.loads(source_path(root, definition['manifest']).read_text())
            definition['skills'] = [
                {**entry, 'upstream': definition['skillRoot'] + '/' + entry['upstream']}
                for entry in manifest['skills']
            ]
        result[key] = definition
    return result


def entries(root, catalog):
    return [
        {**entry, 'source': key}
        for key, definition in sources(root, catalog).items()
        for entry in definition['skills']
    ]


def markdown_targets(path):
    text = re.sub(r'`[^`]*`', '', path.read_text())
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#') and '<' not in target:
            yield target, (path.parent / target.split('#', 1)[0]).resolve()


def scalar(frontmatter, name):
    match = re.search(r'^' + re.escape(name) + r':\s*(.+)$', frontmatter, re.MULTILINE)
    if not match:
        raise ValueError('Missing frontmatter field ' + name)
    value = match[1].strip()
    return json.loads(value) if value.startswith('"') else value


def validate(root, catalog):
    problems = []
    mapped = entries(root, catalog)
    names = [entry['local'] for entry in mapped]
    if len(names) != len(set(names)):
        problems.append('Combined mapping contains duplicate installed names')
    discovered = {}
    for instruction in (root / 'skills').glob('*/*/SKILL.md'):
        try:
            front = instruction.read_text().split('---', 2)[1]
            name = scalar(front, 'name')
            if name in discovered:
                problems.append('Duplicate skill name: ' + str(name))
            discovered[name] = instruction.parent
        except (OSError, ValueError, IndexError):
            problems.append('Invalid skill frontmatter: ' + str(instruction.relative_to(root)))
    for role, owner in catalog['owners'].items():
        if owner not in discovered:
            problems.append('Missing shared owner ' + role + ': ' + owner)
    for entry in mapped:
        name = entry['local']
        directory = source_path(root, entry['directory'])
        try:
            front = (directory / 'SKILL.md').read_text().split('---', 2)[1]
            if scalar(front, 'name') != name or directory.name != name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
                problems.append(name + ': directory or frontmatter name is invalid')
            if not isinstance(scalar(front, 'description'), str):
                problems.append(name + ': description must be a string')
            metadata = (directory / 'agents/openai.yaml').read_text()
            explicit = 'disable-model-invocation: true' in front
            if explicit != ('allow_implicit_invocation: false' in metadata):
                problems.append(name + ': host invocation policy differs')
            if not explicit and ('disable-model-invocation:' in front or 'allow_implicit_invocation:' in metadata):
                problems.append(name + ': callable dependencies must omit both invocation restrictions')
            provenance = (directory / 'UPSTREAM.md').read_text()
            for marker in ['Tracking policy:', 'Imported from commit:', 'Reviewed through commit:', 'License:', 'Local adaptations']:
                if marker not in provenance:
                    problems.append(name + ': missing provenance ' + marker)
            if not (directory / 'LICENSE').is_file():
                problems.append(name + ': missing retained license')
            for readme in [root / 'README.md', directory.parent / 'README.md']:
                if directory / 'SKILL.md' not in {target for _, target in markdown_targets(readme)}:
                    problems.append(name + ': missing linked listing in ' + str(readme.relative_to(root)))
            for document in directory.rglob('*.md'):
                if '__pycache__' in document.parts or 'node_modules' in document.parts:
                    continue
                for label, target in markdown_targets(document):
                    if not target.exists():
                        problems.append(str(document.relative_to(root)) + ': broken link ' + label)
                    elif document.name not in ['README.md', 'UPSTREAM.md', 'MAINTENANCE.md', 'VALIDATION.md'] and not target.is_relative_to(directory):
                        problems.append(str(document.relative_to(root)) + ': invoke the reference owner instead of linking outside the skill: ' + label)
        except (OSError, ValueError, IndexError) as error:
            problems.append(name + ': ' + str(error))
    return {'valid': not problems, 'mappedSkills': len(mapped), 'repositorySkills': len(discovered), 'sources': len(catalog['sources']), 'problems': problems}


def excluded(path, definition):
    parts = Path(path).parts
    name = parts[-1]
    if name in definition.get('excludedNames', {}):
        return definition['excludedNames'][name]
    denied = {part.lower() for part in definition.get('excludedPathComponents', [])}
    if any(part.lower() in denied for part in parts):
        return 'Excluded personal directory'
    return None


def compare(root, catalog, source, upstream, candidate):
    definition = sources(root, catalog)[source]
    candidate = git(upstream, 'rev-parse', '--verify', candidate + '^{commit}').decode().strip()
    skill_root = definition['skillRoot'].rstrip('/')
    paths = git(upstream, 'ls-tree', '-r', '-z', '--name-only', candidate, '--', skill_root)
    inventory = {os.fsdecode(path).removesuffix('/SKILL.md') for path in paths.split(b'\0') if path.endswith(b'/SKILL.md')}
    current = {path for path in inventory if excluded(path, definition) is None}
    known = {entry['upstream'] for entry in definition['skills']}
    changes = []
    for entry in definition['skills']:
        try:
            record = source_path(root, entry['directory'] + '/UPSTREAM.md').read_text()
            baseline = re.search(r'Reviewed through commit:\s*`([0-9a-f]{40})`', record)
            if not baseline:
                raise ValueError('Reviewed-through source revision is missing')
            baseline = baseline[1]
            changed = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate, '--', entry['upstream']).decode().splitlines()
            changes.append({'local': entry['local'], 'upstream': entry['upstream'], 'baseline': baseline, 'status': 'removed' if entry['upstream'] not in inventory else 'changed' if changed else 'unchanged', 'files': changed})
        except (OSError, ValueError) as error:
            changes.append({'local': entry['local'], 'upstream': entry['upstream'], 'status': 'blocked', 'reason': str(error)})
    shared = []
    owned_directories = known | inventory
    for baseline in sorted({change['baseline'] for change in changes if 'baseline' in change}):
        if 'sharedRoot' in definition:
            delta = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate, '--', definition['sharedRoot']).decode().splitlines()
            files = [line for line in delta if any(not any(path.startswith(directory + '/') for directory in owned_directories) for path in line.split('\t')[1:])]
        else:
            files = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate, '--', *definition.get('sharedPaths', [])).decode().splitlines()
        shared.append({'baseline': baseline, 'files': files})
    removed = known - inventory
    added = current - known
    moves = []
    for old in sorted(removed):
        candidates = [new for new in added if Path(new).name == Path(old).name]
        if len(candidates) == 1:
            moves.append({'from': old, 'to': candidates[0], 'decision': 'Verify continuity before changing identity or baseline'})
    return {'source': source, 'candidate': candidate, 'added': sorted(added), 'removed': sorted(removed), 'possibleMoves': moves, 'excluded': [{'path': path, 'reason': excluded(path, definition)} for path in sorted(inventory - current)], 'skills': changes, 'sharedInputs': shared, 'reviewComplete': False, 'policy': catalog['policy']}


def checkpoint(root, catalog, candidates, completed, elapsed_minutes, integration_validated):
    definitions = sources(root, catalog)
    if set(candidates) != set(definitions) or any(not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value) for value in candidates.values()):
        raise ValueError('Checkpoint needs one immutable candidate SHA for each source')
    mapped = entries(root, catalog)
    names = {entry['local'] for entry in mapped}
    if not set(completed) <= names or len(completed) != len(set(completed)) or not 0 <= elapsed_minutes < float('inf'):
        raise ValueError('Unknown or duplicate completed skills or invalid elapsed time')
    pending = sorted(names - set(completed))
    return {'schema': 1, 'createdAt': datetime.now(timezone.utc).isoformat(), 'candidates': candidates, 'completed': sorted(completed), 'pending': pending, 'elapsedMinutes': elapsed_minutes, 'integrationValidated': integration_validated, 'coverageComplete': not pending and integration_validated, 'reviewComplete': False, 'baselinesAdvancedByCheckpoint': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--root', type=Path, required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('names')
    commands.add_parser('validate')
    delta = commands.add_parser('compare')
    delta.add_argument('--source', required=True)
    delta.add_argument('--upstream', type=Path, required=True)
    delta.add_argument('--candidate', required=True)
    delta.add_argument('--output', type=Path)
    save = commands.add_parser('checkpoint')
    save.add_argument('--candidates', type=Path, required=True)
    save.add_argument('--completed', nargs='*', default=[])
    save.add_argument('--elapsed-minutes', type=float, required=True)
    save.add_argument('--integration-validated', action='store_true')
    save.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    try:
        root = arguments.root.resolve()
        catalog = json.loads(arguments.catalog.read_text())
        if arguments.command == 'names':
            print('\n'.join(sorted(entry['local'] for entry in entries(root, catalog))))
            return 0
        if arguments.command == 'validate':
            result = validate(root, catalog)
        elif arguments.command == 'compare':
            result = compare(root, catalog, arguments.source, arguments.upstream, arguments.candidate)
        else:
            result = checkpoint(root, catalog, json.loads(arguments.candidates.read_text()), arguments.completed, arguments.elapsed_minutes, arguments.integration_validated)
        encoded = json.dumps(result, indent=2) + '\n'
        output = getattr(arguments, 'output', None)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(encoded)
        print(encoded, end='')
        return 0 if result.get('valid', True) else 1
    except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
        print(json.dumps({'error': str(error), 'reviewComplete': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
