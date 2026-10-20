#!/usr/bin/env python3
"""Discover, validate, compare, and checkpoint every repository skill."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

CATALOG = Path(__file__).resolve().parents[1] / 'catalog.json'
IGNORED = {'.git', '__pycache__', 'node_modules', '.pytest_cache'}
SHA = r'[0-9a-f]{40}'
URL = r'https?://[^\s)\]>]+'
SOURCE_LABEL = re.compile(r'(?:source repository|canonical source|original source|^\s*[-*]?\s*(?:source|repository))\s*:', re.I)


def git(repository, *arguments):
    environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    result = subprocess.run(['git', '--no-optional-locks', '-C', str(repository), *arguments], capture_output=True, env=environment)
    if result.returncode:
        raise ValueError('Required Git revision, path, or history is unavailable')
    return result.stdout


def source_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Catalog path leaves the source repository')
    return path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def files_under(directory):
    for parent, children, files in os.walk(directory, followlinks=False):
        children[:] = sorted(name for name in children if name not in IGNORED and not (Path(parent) / name).is_symlink())
        for name in sorted(files):
            if name != '.DS_Store' and not name.endswith('.pyc'):
                yield Path(parent) / name


def sources(root, catalog):
    """Suite policies own addition/exclusion mappings, not repository coverage."""
    result = {}
    for key, original in catalog.get('sources', {}).items():
        definition = dict(original)
        if 'manifest' in definition:
            manifest = json.loads(source_path(root, definition['manifest']).read_text())
            definition['skills'] = [{**entry, 'upstream': definition['skillRoot'] + '/' + entry['upstream']} for entry in manifest['skills']]
        result[key] = definition
    return result


def entries(root, catalog):
    return [{**entry, 'source': key} for key, definition in sources(root, catalog).items() for entry in definition.get('skills', [])]


def markdown_targets(path):
    text = re.sub(r'`[^`]*`', '', path.read_text())
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#') and '<' not in target:
            yield target, (path.parent / target.split('#', 1)[0]).resolve()


def frontmatter(instruction):
    text = instruction.read_text()
    match = re.match(r'\A---\s*\n(.*?)\n---(?:\s*\n|\Z)', text, re.S)
    if not match:
        raise ValueError('Missing or invalid YAML frontmatter')
    return match[1]


def scalar(front, name):
    """Read the scalar subset used here; reject YAML non-string values."""
    match = re.search(r'^' + re.escape(name) + r':\s*([^\n]*)$', front, re.M)
    if not match:
        raise ValueError('Missing frontmatter field ' + name)
    value = match[1].strip()
    if value.startswith('"'):
        value = json.loads(value)
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1].replace("''", "'")
    elif value in {'|', '>', '|-', '>-', '|+', '>+'}:
        lines = front[match.end():].splitlines()
        value = '\n'.join(line.strip() for line in lines if line.startswith((' ', '\t')))
    elif not value or re.fullmatch(r'(?:null|true|false|yes|no|on|off|~|[-+]?\d+(?:\.\d+)?|\.nan|[-+]?\.inf)', value, re.I) or value[0] in '[{&*!':
        raise ValueError('Frontmatter field ' + name + ' must be a string')
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Frontmatter field ' + name + ' must be a nonempty string')
    return value


def repository_identity(url):
    url = url.strip().strip('`.,')
    if url.startswith('git@'):
        host, path = url[4:].split(':', 1)
    else:
        parsed = urlsplit(url)
        if parsed.scheme not in {'https', 'http', 'ssh', 'git'} or not parsed.hostname:
            raise ValueError('Unresolvable source repository: ' + url)
        host, path = parsed.hostname, parsed.path.lstrip('/')
    parts = path.rstrip('/').split('/')
    if host.lower() == 'github.com':
        parts = parts[:2]
    if len(parts) < 2 or not all(parts):
        raise ValueError('Unresolvable source repository: ' + url)
    repository = '/'.join(parts).removesuffix('.git')
    return host.lower() + '/' + (repository.lower() if host.lower() == 'github.com' else repository)


def tracking_policy(text):
    match = re.search(r'Tracking policy:\s*([^\n]+)', text, re.I)
    if not match:
        raise ValueError('Missing explicit tracking policy')
    policy = match[1]
    for kind, expression in [
        ('commit', r'(?:fixed|pinned|commit)\s+(?:at\s+)?`(' + SHA + r')`'),
        ('tag', r'tag\s+`([^`]+)`'),
        ('branch', r'(?:branch|upstream)\s+`([^`]+)`|`([^`]+)`\s+branch'),
    ]:
        found = re.search(expression, policy, re.I)
        if found:
            return {'kind': kind, 'ref': next(value for value in found.groups() if value)}
    quoted = re.findall(r'`([^`]+)`', policy)
    if len(quoted) == 1 and not re.search(r'\b(?:release|channel|fixed|pinned|tag)\b', policy, re.I):
        return {'kind': 'branch', 'ref': quoted[0]}
    if re.fullmatch(r'[\w./-]+\.?', policy):
        return {'kind': 'branch', 'ref': policy.rstrip('.')}
    raise ValueError('Unresolvable tracking policy: ' + policy)


def group_key(identity, tracking):
    return identity + '@' + tracking['kind'] + ':' + tracking['ref']


def github_paths(text, identity):
    result = []
    for url in re.findall(URL, text):
        try:
            if repository_identity(url) != identity:
                continue
        except ValueError:
            continue
        parsed = urlsplit(url)
        parts = parsed.path.strip('/').split('/')
        if len(parts) > 4 and parts[2] in {'blob', 'tree', 'raw'}:
            result.append('/'.join(parts[4:]).rstrip('.,'))
    return result


def provenance_blocks(text):
    declarations = []
    for match in re.finditer(r'^.*$', text, re.M):
        if SOURCE_LABEL.search(match[0]):
            urls = re.findall(URL, match[0])
            if urls:
                identities = {repository_identity(url) for url in urls}
                if len(identities) != 1:
                    raise ValueError('Ambiguous repositories on one source declaration')
                declarations.append((match.start(), identities.pop()))
    return [(identity, text[start:declarations[index + 1][0] if index + 1 < len(declarations) else len(text)]) for index, (start, identity) in enumerate(declarations)]


def source_record(identity, block, record_path):
    problems = []
    try:
        tracking = tracking_policy(block)
    except ValueError as error:
        tracking = None
        problems.append(str(error))
    reviewed = re.search(r'Reviewed through(?: commit)?:\s*(?:`(' + SHA + r')`|\[(' + SHA + r')\])', block, re.I)
    baseline = next((value for value in reviewed.groups() if value), None) if reviewed else None
    if not baseline:
        problems.append('Missing reproducible reviewed-through revision')
    imported = re.search(r'Imported from commit:\s*`(' + SHA + r')`', block, re.I)
    import_gap = bool(re.search(r'(?:original upstream import revision|import(?:ed)? revision):\s*(?:unrecorded|unknown)', block, re.I))
    if not imported and not import_gap:
        problems.append('Missing immutable import revision or documented historical import gap')
    credit = re.split(r'^## Local adaptations', block, maxsplit=1, flags=re.M | re.I)[0]
    declaration, _, details = credit.partition('\n')
    declared_paths = github_paths(declaration, identity)
    shared_paths = [path for path in declared_paths if Path(path).name != 'SKILL.md']
    paths = set(github_paths(details, identity)) | {path for path in declared_paths if Path(path).name == 'SKILL.md'}
    for line in credit.splitlines():
        if re.search(r'(?:supporting sources|upstream (?:files?|paths?)|original skill)', line, re.I):
            for path in re.findall(r'`([^`\s]+/[^`\s]+)`', line):
                if not path.startswith(('http', '/', '../')):
                    paths.add(path.rstrip('/'))
    # A skill directory includes its future scripts/references, not only today's SKILL.md.
    instruction_paths = [str(Path(path).parent) for path in paths if Path(path).name == 'SKILL.md']
    primary_paths = []
    for line in credit.splitlines():
        if re.search(r'Original skill(?: and resources)?:', line, re.I):
            primary_paths.extend(str(Path(path).parent) if Path(path).name == 'SKILL.md' else path for path in github_paths(line, identity))
    if not primary_paths:
        local_name = Path(record_path).parent.name
        primary_paths = [path for path in instruction_paths if Path(path).name == local_name] or instruction_paths
    paths = {str(Path(path).parent) if Path(path).name == 'SKILL.md' else path for path in paths}
    paths.add('LICENSE')
    if any(Path(path).is_absolute() or '..' in Path(path).parts for path in paths):
        problems.append('Upstream path leaves the source repository')
    if not primary_paths:
        problems.append('Missing concrete primary upstream skill path')
    if not any(path != 'LICENSE' for path in paths):
        problems.append('Missing concrete upstream skill or supporting paths')
    if not re.search(r'License:', block, re.I):
        problems.append('Missing license attribution')
    if 'Local adaptations' not in block:
        problems.append('Missing local adaptations to preserve')
    return {'repository': 'https://' + identity + '.git', 'identity': identity, 'tracking': tracking, 'key': group_key(identity, tracking) if tracking else None, 'baseline': baseline, 'imported': imported[1] if imported else None, 'historicalImportUnknown': import_gap, 'paths': sorted(paths), 'primaryPaths': sorted(set(primary_paths)), 'sharedPaths': sorted(set(shared_paths)), 'record': record_path, 'problems': problems}


def discover_provenance(root, directory, front):
    candidates = [directory / name for name in ['UPSTREAM.md', 'PROVENANCE.md', 'ATTRIBUTION.md', 'SOURCE.md'] if (directory / name).is_file()]
    if len(candidates) > 1:
        return [], [], ['Competing provenance records: ' + ', '.join(path.name for path in candidates)]
    if not candidates:
        candidates = [path for path in [directory / 'README.md', directory / 'SKILL.md'] if path.exists() and SOURCE_LABEL.search(path.read_text())]
    records, attributions, problems = [], [], []
    for path in candidates:
        text = path.read_text()
        try:
            blocks = provenance_blocks(text)
            if not blocks:
                problems.append('Source record has no resolvable repository: ' + str(path.relative_to(root)))
            records.extend(source_record(identity, block, str(path.relative_to(root))) for identity, block in blocks)
            for line in text.splitlines():
                if 'Attribution-only source:' in line:
                    urls = re.findall(URL, line)
                    if not urls:
                        problems.append('Attribution-only source has no repository URL')
                    attributions.extend({'identity': repository_identity(url), 'policy': 'attribution-only', 'record': str(path.relative_to(root))} for url in urls)
        except ValueError as error:
            problems.append(str(error))
    # Explicit ancestry cues are evidence even when the source record is absent.
    declared = {entry['identity'] for entry in records} | {entry['identity'] for entry in attributions}
    ancestry_urls = []
    if re.search(r'^\s*(?:credits?|sources?|upstream)\s*:', front, re.M | re.I):
        ancestry_urls.extend(re.findall(URL, front))
    for path in [directory / 'README.md', directory / 'SKILL.md', directory / 'CREDITS.md']:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if re.search(r'\b(?:adapted from|derived from|ported from|copied from|based on|original (?:author|source)|attribution|credits?)\b', line, re.I):
                ancestry_urls.extend(re.findall(URL, line))
    for url in ancestry_urls:
        parsed = urlsplit(url)
        if parsed.hostname == 'github.com' and len(parsed.path.strip('/').split('/')) < 2:
            continue  # Author profile links are credit, not a repository identity.
        try:
            identity = repository_identity(url.rstrip('"\''))
            if identity not in declared:
                problems.append('Unclassified attributed source ' + identity + ': record its own tracking/baseline or explicit attribution-only policy')
        except ValueError as error:
            problems.append(str(error))
    return records, attributions, problems


def inventory(root, catalog):
    skills, groups, problems = [], {}, []
    for instruction in sorted((root / 'skills').rglob('SKILL.md')):
        if any(part in IGNORED for part in instruction.relative_to(root).parts):
            continue
        directory = instruction.parent
        item = {'name': directory.name, 'directory': str(directory.relative_to(root)), 'sources': [], 'attributions': [], 'problems': []}
        try:
            front = frontmatter(instruction)
            name = scalar(front, 'name')
            item['name'] = name
            scalar(front, 'description')
            if directory.name != name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
                item['problems'].append('Directory or frontmatter name is invalid')
            item['sources'], item['attributions'], issues = discover_provenance(root, directory, front)
            item['problems'].extend(issues)
        except (OSError, ValueError, TypeError) as error:
            item['problems'].append(str(error))
        content = []
        for path in files_under(directory):
            if path.is_symlink():
                item['problems'].append('Skill resource is a symlink: ' + str(path.relative_to(directory)))
                continue
            content.append([str(path.relative_to(directory)), hashlib.sha256(path.read_bytes()).hexdigest(), bool(path.stat().st_mode & 0o111)])
        item['fingerprint'] = digest(content)
        item['classification'] = 'sourced' if item['sources'] else 'unresolved' if item['problems'] else 'local'
        for record in item['sources']:
            item['problems'].extend(record['identity'] + ': ' + problem for problem in record['problems'])
            if record['key']:
                group = groups.setdefault(record['key'], {'repository': record['repository'], 'identity': record['identity'], 'tracking': record['tracking'], 'skills': [], 'records': []})
                group['skills'].append(item['name'])
                group['records'].append({'local': item['name'], **record})
        skills.append(item)
    names = [item['name'] for item in skills]
    if len(names) != len(set(names)):
        problems.append('Duplicate installed skill names')
    definitions = sources(root, catalog)
    by_directory = {item['directory']: item for item in skills}
    mapped = entries(root, catalog)
    mapped_names = [entry['local'] for entry in mapped]
    if len(mapped_names) != len(set(mapped_names)):
        problems.append('Combined mapping contains duplicate installed names')
    for entry in mapped:
        item = by_directory.get(entry['directory'])
        if not item or item['name'] != entry['local']:
            problems.append('Missing or renamed mapped skill: ' + entry['local'])
        elif not item['sources']:
            item['problems'].append('Mapped upstream skill has no resolved source record')
        else:
            definition = definitions[entry['source']]
            identity = repository_identity(definition['repository'])
            if not any(record['identity'] == identity and entry['upstream'] in record['paths'] for record in item['sources']):
                item['problems'].append('Suite mapping conflicts with skill-local source identity/path')
    for key, group in groups.items():
        group['skills'] = sorted(set(group['skills']))
        group['fingerprint'] = digest([group['records'], [[item['name'], item['fingerprint']] for item in skills if item['name'] in group['skills']]])
    for item in skills:
        problems.extend(item['name'] + ': ' + problem for problem in item['problems'])
    shared_context = {}
    for path in [root / 'AGENTS.md', root / 'CLAUDE.md', root / 'README.md', root / 'CONTRIBUTING.md', root / 'docs/architecture.md', root / 'skills/README.md', *(root / 'skills').glob('*/README.md')]:
        if path.is_file():
            shared_context[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    owner_names = set(catalog.get('owners', {}).values())
    owner_fingerprints = {item['name']: item['fingerprint'] for item in skills if item['name'] in owner_names}
    context_fingerprint = digest([catalog, shared_context, owner_fingerprints])
    return {'schema': 2, 'contextFingerprint': context_fingerprint, 'repositorySkills': len(skills), 'mappedSkills': len(mapped), 'skills': skills, 'sourceGroups': groups, 'problems': problems, 'valid': not problems, 'catalogFingerprint': digest(catalog), 'fingerprint': digest([[item['directory'], item['fingerprint']] for item in skills])}


def validate(root, catalog):
    discovered = inventory(root, catalog)
    problems = list(discovered['problems'])
    names = {item['name'] for item in discovered['skills']}
    for role, owner in catalog.get('owners', {}).items():
        if owner not in names:
            problems.append('Missing shared owner ' + role + ': ' + owner)
    for item in discovered['skills']:
        name = item['name']
        directory = source_path(root, item['directory'])
        try:
            front = frontmatter(directory / 'SKILL.md')
            metadata = (directory / 'agents/openai.yaml').read_text()
            explicit = bool(re.search(r'^disable-model-invocation:\s*true\s*$', front, re.M))
            restricted = bool(re.search(r'^\s*allow_implicit_invocation:\s*false\s*$', metadata, re.M))
            if explicit != restricted:
                problems.append(name + ': host invocation policy differs')
            if not explicit and (re.search(r'^disable-model-invocation:', front, re.M) or re.search(r'^\s*allow_implicit_invocation:', metadata, re.M)):
                problems.append(name + ': callable dependencies must omit both invocation restrictions')
            if item['sources'] and not (directory / 'LICENSE').is_file():
                problems.append(name + ': missing retained license')
            for readme in [root / 'README.md', directory.parent / 'README.md']:
                if directory / 'SKILL.md' not in {target for _, target in markdown_targets(readme)}:
                    problems.append(name + ': missing linked listing in ' + str(readme.relative_to(root)))
            for document in directory.rglob('*.md'):
                if any(part in IGNORED for part in document.parts):
                    continue
                for label, target in markdown_targets(document):
                    if not target.exists():
                        problems.append(str(document.relative_to(root)) + ': broken link ' + label)
                    elif document.name not in ['README.md', 'UPSTREAM.md', 'PROVENANCE.md', 'ATTRIBUTION.md', 'SOURCE.md', 'MAINTENANCE.md', 'VALIDATION.md'] and not target.is_relative_to(directory):
                        problems.append(str(document.relative_to(root)) + ': invoke the reference owner instead of linking outside the skill: ' + label)
        except (OSError, ValueError, IndexError) as error:
            problems.append(name + ': ' + str(error))
    return {'valid': not problems, 'mappedSkills': discovered['mappedSkills'], 'repositorySkills': discovered['repositorySkills'], 'sources': len(discovered['sourceGroups']), 'problems': problems}


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
    discovered = inventory(root, catalog)
    definitions = sources(root, catalog)
    if source in definitions:
        definition = definitions[source]
        identity = repository_identity(definition['repository'])
        key = group_key(identity, {'kind': 'branch', 'ref': definition.get('branch', 'main')})
        group = discovered['sourceGroups'].get(key)
        if not group:
            raise ValueError('Suite source has no resolved local provenance')
        local_names = {entry['local'] for entry in definition.get('skills', [])}
        records = [record for record in group['records'] if record['local'] in local_names]
        policies = {source: definition}
    else:
        group = discovered['sourceGroups'][source]
        records = group['records']
        policies = {key: definition for key, definition in definitions.items() if repository_identity(definition['repository']) == group['identity'] and {'kind': 'branch', 'ref': definition.get('branch', 'main')} == group['tracking']}
    # Avoid comparing a valid SHA in a checkout for a different repository.
    try:
        remote = git(upstream, 'remote', 'get-url', 'origin').decode().strip()
    except ValueError:
        remote = None
    if not remote or repository_identity(remote) != group['identity']:
        raise ValueError('Upstream origin does not match the recorded source repository')
    candidate = git(upstream, 'rev-parse', '--verify', candidate + '^{commit}').decode().strip()
    if group['tracking']['kind'] == 'commit' and candidate != group['tracking']['ref']:
        raise ValueError('Candidate differs from the explicitly pinned source commit')
    paths = git(upstream, 'ls-tree', '-r', '-z', '--name-only', candidate)
    actual = {str(Path(os.fsdecode(path)).parent) for path in paths.split(b'\0') if path.endswith(b'/SKILL.md') or path == b'SKILL.md'}
    changes = []
    for record in records:
        try:
            if record['problems']:
                raise ValueError('; '.join(record['problems']))
            for primary in record['primaryPaths']:
                try:
                    git(upstream, 'cat-file', '-e', record['baseline'] + ':' + (primary + '/' if primary != '.' else '') + 'SKILL.md')
                except ValueError:
                    raise ValueError('Recorded primary skill path is absent at the reviewed baseline: ' + primary) from None
            delta = git(upstream, 'diff', '--name-status', '--find-renames', record['baseline'], candidate, '--', *record['paths']).decode().splitlines()
            status = 'removed' if not any(primary in actual for primary in record['primaryPaths']) else 'changed' if delta else 'unchanged'
            changes.append({'local': record['local'], 'upstream': record['paths'], 'baseline': record['baseline'], 'status': status, 'files': delta})
        except (OSError, ValueError) as error:
            changes.append({'local': record['local'], 'upstream': record['paths'], 'status': 'blocked', 'reason': str(error)})
    suite_results, shared = {}, []
    for key, definition in policies.items():
        skill_root = definition['skillRoot'].rstrip('/')
        prefix = skill_root + '/'
        suite_inventory = {path for path in actual if skill_root == '.' or path.startswith(prefix)}
        current = {path for path in suite_inventory if excluded(path, definition) is None}
        known = {entry['upstream'] for entry in definition.get('skills', [])}
        removed, added = known - suite_inventory, current - known
        moves = [{'from': old, 'to': candidates[0], 'decision': 'Verify continuity before changing identity or baseline'} for old in sorted(removed) if len(candidates := [new for new in added if Path(new).name == Path(old).name]) == 1]
        suite_results[key] = {'added': sorted(added), 'removed': sorted(removed), 'possibleMoves': moves, 'excluded': [{'path': path, 'reason': excluded(path, definition)} for path in sorted(suite_inventory - current)]}
        for baseline in sorted({record['baseline'] for record in records if record['baseline']}):
            try:
                targets = [definition['sharedRoot']] if 'sharedRoot' in definition else definition.get('sharedPaths', [])
                delta = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate, '--', *targets).decode().splitlines() if targets else []
                owned = known | suite_inventory
                files = [line for line in delta if any(not any(path.startswith(directory + '/') for directory in owned) for path in line.split('\t')[1:])]
                shared.append({'suite': key, 'baseline': baseline, 'files': files})
            except ValueError as error:
                shared.append({'suite': key, 'baseline': baseline, 'status': 'blocked', 'reason': str(error)})
    # Recorded plugin roots retain wrappers/manifests beyond individual skill directories.
    scoped_inputs = {(record['baseline'], tuple(record['sharedPaths'])) for record in records if record['baseline'] and record['sharedPaths']}
    for baseline, targets in sorted(scoped_inputs):
        try:
            delta = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate, '--', *targets).decode().splitlines()
            shared.append({'baseline': baseline, 'paths': list(targets), 'files': delta})
        except ValueError as error:
            shared.append({'baseline': baseline, 'paths': list(targets), 'status': 'blocked', 'reason': str(error)})
    # Generic sources still expose repository-wide shared changes, including unlisted support files.
    if not policies and not scoped_inputs:
        for baseline in sorted({record['baseline'] for record in records if record['baseline']}):
            try:
                delta = git(upstream, 'diff', '--name-status', '--find-renames', baseline, candidate).decode().splitlines()
                shared.append({'baseline': baseline, 'files': delta})
            except ValueError as error:
                shared.append({'baseline': baseline, 'status': 'blocked', 'reason': str(error)})
    for change in changes:
        original = next((entry['upstream'] for definition in policies.values() for entry in definition.get('skills', []) if entry['local'] == change['local']), None)
        if original and original not in actual and change['status'] != 'blocked':
            change['status'] = 'removed'
    result = {'source': source, 'candidate': candidate, 'repository': group['repository'], 'tracking': group['tracking'], 'inventory': sorted(actual), 'suites': suite_results, 'skills': changes, 'sharedInputs': shared, 'reviewComplete': False, 'policy': catalog.get('policy')}
    if source in suite_results:
        result.update(suite_results[source])
    return result


def checkpoint(root, catalog, candidates, completed, elapsed_minutes, integration_validated, source_reviews=None, resume=None):
    current = inventory(root, catalog)
    packaging = validate(root, catalog)
    groups = current['sourceGroups']
    if set(candidates) != set(groups) or any(not isinstance(value, str) or not re.fullmatch(SHA, value) for value in candidates.values()):
        raise ValueError('Checkpoint needs one immutable candidate SHA for each discovered repository/tracking group: ' + ', '.join(sorted(groups)))
    names = {item['name'] for item in current['skills']}
    if not set(completed) <= names or len(completed) != len(set(completed)) or not math.isfinite(elapsed_minutes) or elapsed_minutes < 0:
        raise ValueError('Unknown or duplicate completed skills or invalid elapsed time')
    reviews = dict(source_reviews or {})
    if not set(reviews) <= set(groups):
        raise ValueError('Unknown source review group')
    requested = set(completed)
    invalidated = []
    fingerprints = {item['name']: item['fingerprint'] for item in current['skills']}
    if resume is not None:
        if resume.get('schema') != 2 or 'skillFingerprints' not in resume or 'sourceCoverage' not in resume:
            raise ValueError('Legacy or incomplete checkpoint cannot establish current repository coverage; reconcile it against a fresh inventory')
        for name in resume.get('locallyReviewed', resume.get('completed', [])):
            if name in names and resume['skillFingerprints'].get(name) == fingerprints[name] and resume.get('contextFingerprint') == current['contextFingerprint']:
                requested.add(name)
            else:
                invalidated.append(name)
        for key, group in groups.items():
            previous = resume['sourceCoverage'].get(key, {})
            if key not in reviews and previous.get('candidate') == candidates[key] and previous.get('fingerprint') == group['fingerprint'] and resume.get('contextFingerprint') == current['contextFingerprint']:
                reviews[key] = previous
    coverage = {}
    for key, group in groups.items():
        review = reviews.get(key, {})
        reviewed_names = review.get('skills', [])
        if not isinstance(reviewed_names, list) or not set(reviewed_names) <= set(group['skills']) or len(reviewed_names) != len(set(reviewed_names)):
            raise ValueError('Unknown or duplicate skills in source review ' + key)
        matching = review.get('candidate') == candidates[key]
        coverage[key] = {'candidate': candidates[key], 'fingerprint': group['fingerprint'], 'skills': sorted(reviewed_names) if matching else [], 'pending': sorted(set(group['skills']) - set(reviewed_names)) if matching else group['skills'], 'inventoryReviewed': matching and review.get('inventoryReviewed') is True, 'sharedInputsReviewed': matching and review.get('sharedInputsReviewed') is True}
    finished = []
    for item in current['skills']:
        invalid_packaging = any(problem.startswith(item['name'] + ':') or problem.startswith(item['directory'] + '/') for problem in packaging['problems'])
        if item['name'] in requested and not item['problems'] and not invalid_packaging and all(record['key'] and item['name'] in coverage[record['key']]['skills'] for record in item['sources']):
            finished.append(item['name'])
    pending = sorted(names - set(finished))
    source_pending = [key for key, review in coverage.items() if review['pending'] or not review['inventoryReviewed'] or not review['sharedInputsReviewed']]
    return {'schema': 2, 'createdAt': datetime.now(timezone.utc).isoformat(), 'inventoryFingerprint': current['fingerprint'], 'contextFingerprint': current['contextFingerprint'], 'catalogFingerprint': current['catalogFingerprint'], 'skillFingerprints': fingerprints, 'candidates': candidates, 'locallyReviewed': sorted(requested), 'completed': sorted(finished), 'pending': pending, 'sourceCoverage': coverage, 'pendingSources': source_pending, 'invalidated': sorted(invalidated), 'problems': packaging['problems'], 'elapsedMinutes': elapsed_minutes, 'integrationValidated': integration_validated, 'coverageComplete': not pending and not source_pending and not packaging['problems'] and integration_validated, 'reviewComplete': False, 'baselinesAdvancedByCheckpoint': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--root', type=Path, required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['names', 'inventory', 'validate']:
        commands.add_parser(name)
    delta = commands.add_parser('compare')
    delta.add_argument('--source', required=True)
    delta.add_argument('--upstream', type=Path, required=True)
    delta.add_argument('--candidate', required=True)
    delta.add_argument('--output', type=Path)
    save = commands.add_parser('checkpoint')
    save.add_argument('--candidates', type=Path, required=True)
    save.add_argument('--completed', nargs='*', default=[])
    save.add_argument('--source-reviews', type=Path)
    save.add_argument('--resume', type=Path)
    save.add_argument('--elapsed-minutes', type=float, required=True)
    save.add_argument('--integration-validated', action='store_true')
    save.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    try:
        root = arguments.root.resolve()
        catalog = json.loads(arguments.catalog.read_text())
        if arguments.command == 'names':
            result = inventory(root, catalog)
            print('\n'.join(sorted(item['name'] for item in result['skills'])))
            return 0 if result['valid'] else 1
        if arguments.command == 'inventory':
            result = inventory(root, catalog)
        elif arguments.command == 'validate':
            result = validate(root, catalog)
        elif arguments.command == 'compare':
            result = compare(root, catalog, arguments.source, arguments.upstream, arguments.candidate)
        else:
            reviews = json.loads(arguments.source_reviews.read_text()) if arguments.source_reviews else None
            resume = json.loads(arguments.resume.read_text()) if arguments.resume else None
            result = checkpoint(root, catalog, json.loads(arguments.candidates.read_text()), arguments.completed, arguments.elapsed_minutes, arguments.integration_validated, reviews, resume)
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
