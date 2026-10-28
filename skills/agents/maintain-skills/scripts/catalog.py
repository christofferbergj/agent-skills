#!/usr/bin/env python3
"""Maintain every repository skill against its upstream sources.

Repository records (skill-local UPSTREAM.md files and catalog.json) hold decisions.
Machine-local state (source clones, checkpoints, run directories) holds verification
progress: begin takes the run lock, picks the mode, and opens a run folder; fetch
resolves candidates; compare --resume reuses verified progress; checkpoint records
it; prune bounds the retained runs; and release frees the lock.
"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

CATALOG = Path(__file__).resolve().parents[1] / 'catalog.json'
IGNORED = {'.git', '__pycache__', 'node_modules', '.pytest_cache'}
SHA = r'[0-9a-f]{40}'
URL = r'https?://[^\s)\]>]+'
RECORD_NAMES = ['UPSTREAM.md', 'PROVENANCE.md', 'ATTRIBUTION.md', 'SOURCE.md']
LOCK_STALE_MINUTES = 180  # Twice the longest run budget.
AUDIT_INTERVAL_DAYS = 7
REVIEW_EXPIRY_DAYS = 28
WORKTREES = ['library', 'process']
SOURCE_LABEL = re.compile(r'(?:source repository|canonical source|original source|^\s*[-*]?\s*(?:source|repository))\s*:', re.I)


def git(repository, *arguments):
    environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    environment['GIT_TERMINAL_PROMPT'] = '0'
    result = subprocess.run(['git', '--no-optional-locks', '-C', str(repository), *arguments], capture_output=True, env=environment)
    if result.returncode:
        detail = result.stderr.decode(errors='replace').strip().splitlines()
        raise ValueError('Required Git revision, path, or history is unavailable' + (': ' + detail[-1] if detail else ''))
    return result.stdout


def is_ancestor(repository, older, newer):
    try:
        git(repository, 'merge-base', '--is-ancestor', older, newer)
        return True
    except ValueError:
        return False


def name_status(repository, since, candidate, targets):
    return git(repository, 'diff', '--name-status', '--find-renames', since, candidate, '--', *targets).decode().splitlines()


def source_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Catalog path leaves the source repository')
    return path


def write_atomic(path, text):
    """Replace path in one step, so a crash leaves the old file or the new one, never a torn one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.' + str(os.getpid()) + '.tmp')
    temporary.write_text(text)
    os.replace(temporary, path)


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def parse_time(value):
    moment = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    return (moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def checkpoint_date(checkpoint):
    try:
        return parse_time(checkpoint['createdAt']).date()
    except (KeyError, TypeError, ValueError):
        return None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def files_under(directory):
    """Yield every file, and each symlinked directory as an entry of its own so a link never hides content."""
    for parent, children, files in os.walk(directory, followlinks=False):
        kept = []
        for name in sorted(children):
            if name in IGNORED:
                continue
            if (Path(parent) / name).is_symlink():
                yield Path(parent) / name
            else:
                kept.append(name)
        children[:] = kept
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


def policy_group(definition):
    """A catalog policy tracks its repository's branch, main unless it names one."""
    return group_key(repository_identity(definition['repository']), {'kind': 'branch', 'ref': definition.get('branch', 'main')})


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
    fidelity = re.search(r'Fidelity checked through:\s*`(' + SHA + r')`', block, re.I)
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
    return {'repository': 'https://' + identity + '.git', 'identity': identity, 'tracking': tracking, 'key': group_key(identity, tracking) if tracking else None, 'baseline': baseline, 'fidelity': fidelity[1] if fidelity else None, 'imported': imported[1] if imported else None, 'historicalImportUnknown': import_gap, 'paths': sorted(paths), 'primaryPaths': sorted(set(primary_paths)), 'sharedPaths': sorted(set(shared_paths)), 'record': record_path, 'problems': problems}


def discover_provenance(root, directory, front):
    candidates = [directory / name for name in RECORD_NAMES if (directory / name).is_file()]
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


def inventory(root, catalog, resume=None, now=None):
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
        # A mapped skill keeps its upstream name; a rename needs its recorded reason.
        upstream_name = Path(entry['upstream']).name
        reason = entry.get('renamed')
        if entry['local'] != upstream_name and not (isinstance(reason, str) and reason.strip()):
            problems.append(entry['local'] + ': renamed from ' + upstream_name + ' without a recorded reason')
        elif entry['local'] == upstream_name and 'renamed' in entry:
            problems.append(entry['local'] + ': records a rename reason but keeps the upstream name')
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
    # Only governing guidance and its owners invalidate local evidence; listings and the catalog do not.
    shared_context = {}
    for relative in catalog.get('contextPaths', []):
        path = source_path(root, relative)
        if path.is_file():
            shared_context[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    owners = catalog.get('owners', {})
    owner_names = {owners[role] for role in catalog.get('contextOwners', []) if role in owners}
    owner_fingerprints = {item['name']: item['fingerprint'] for item in skills if item['name'] in owner_names}
    context_fingerprint = digest([shared_context, owner_fingerprints])
    context_files = {**shared_context, **owner_fingerprints}
    result = {'schema': 2, 'contextFingerprint': context_fingerprint, 'contextFiles': context_files, 'repositorySkills': len(skills), 'mappedSkills': len(mapped), 'skills': skills, 'sourceGroups': groups, 'problems': problems, 'valid': not problems, 'catalogFingerprint': digest(catalog), 'fingerprint': digest([[item['directory'], item['fingerprint']] for item in skills])}
    # Records never confirmed complete in both directions await their first fidelity check.
    result['fidelityBacklog'] = sorted(item['name'] for item in skills if any(not record['fidelity'] for record in item['sources']))
    if resume is not None:
        previous = resume.get('skillFingerprints', {}) if isinstance(resume, dict) else {}
        result['changedSince'] = sorted(item['name'] for item in skills if previous.get(item['name']) != item['fingerprint'])
        if isinstance(resume, dict) and isinstance(resume.get('contextFiles'), dict):
            earlier = resume['contextFiles']
            result['contextChanged'] = sorted(name for name in set(earlier) | set(context_files) if earlier.get(name) != context_files.get(name))
        else:
            result['contextChanged'] = sorted(context_files) if isinstance(resume, dict) and resume.get('contextFingerprint') != context_fingerprint else []
        result['staleReviews'] = stale_reviews(resume, now)
    return result


def review_dates(resume):
    """Each locally reviewed skill's last review date; older checkpoints date every review by their creation."""
    if not isinstance(resume, dict):
        return {}
    fallback = checkpoint_date(resume)
    dates = resume.get('reviewedAt') if isinstance(resume.get('reviewedAt'), dict) else {}
    return {name: dates.get(name) or (fallback.isoformat() if fallback else None) for name in resume.get('locallyReviewed', resume.get('completed', []))}


def stale_reviews(resume, now=None):
    """Reviews older than the expiry, oldest first: an audit rechecks these against current tools."""
    today = (now or datetime.now(timezone.utc)).date()
    stale = []
    for name, date in review_dates(resume).items():
        try:
            reviewed = datetime.fromisoformat(date).date() if date else None
        except ValueError:
            reviewed = None
        if reviewed is None or (today - reviewed).days > REVIEW_EXPIRY_DAYS:
            stale.append((reviewed.isoformat() if reviewed else '', name))
    return [name for _, name in sorted(stale)]


def validate(root, catalog):
    discovered = inventory(root, catalog)
    problems = list(discovered['problems'])
    if 'contextPaths' not in catalog:
        problems.append('Catalog has no contextPaths')
    names = {item['name'] for item in discovered['skills']}
    for role, owner in catalog.get('owners', {}).items():
        if owner not in names:
            problems.append('Missing shared owner ' + role + ': ' + owner)
    for role in catalog.get('contextOwners', []):
        if role not in catalog.get('owners', {}):
            problems.append('Unknown context owner role: ' + role)
    for key, definition in catalog.get('sources', {}).items():
        if 'sharedReviewedThrough' in definition and not re.fullmatch(SHA, str(definition['sharedReviewedThrough'])):
            problems.append(key + ': sharedReviewedThrough must be a full commit SHA')
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
                    elif document.name not in ['README.md', *RECORD_NAMES, 'MAINTENANCE.md'] and not target.is_relative_to(directory):
                        problems.append(str(document.relative_to(root)) + ': invoke the reference owner instead of linking outside the skill: ' + label)
        except (OSError, ValueError, IndexError) as error:
            problems.append(name + ': ' + str(error))
    return {'valid': not problems, 'mappedSkills': discovered['mappedSkills'], 'repositorySkills': discovered['repositorySkills'], 'sources': len(discovered['sourceGroups']), 'problems': problems}


def excluded(path, definition):
    for prefix, reason in definition.get('excludedPaths', {}).items():
        prefix = prefix.rstrip('/')
        if path == prefix or path.startswith(prefix + '/'):
            return reason
    parts = Path(path).parts
    name = parts[-1]
    if name in definition.get('excludedNames', {}):
        return definition['excludedNames'][name]
    denied = {part.lower() for part in definition.get('excludedPathComponents', [])}
    if any(part.lower() in denied for part in parts):
        return 'Excluded personal directory'
    return None


def compare(root, catalog, source, upstream, candidate, resume=None):
    discovered = inventory(root, catalog)
    definitions = sources(root, catalog)
    if source in definitions:
        definition = definitions[source]
        key = policy_group(definition)
        group = discovered['sourceGroups'].get(key)
        if not group:
            raise ValueError('Suite source has no resolved local provenance')
        local_names = {entry['local'] for entry in definition.get('skills', [])}
        records = [record for record in group['records'] if record['local'] in local_names]
        policies = {source: definition}
    else:
        key = source
        group = discovered['sourceGroups'][source]
        records = group['records']
        policies = {name: definition for name, definition in definitions.items() if policy_group(definition) == key}
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
    # A prior checkpoint advances baselines only within this comparison; records keep their decisions.
    coverage = resume.get('sourceCoverage', {}).get(key, {}) if isinstance(resume, dict) and resume.get('schema') == 2 else {}
    prior = coverage.get('candidate')
    try:
        prior = git(upstream, 'rev-parse', '--verify', prior + '^{commit}').decode().strip() if re.fullmatch(SHA, str(prior)) else None
    except ValueError:
        prior = None
    verified = resume.get('skillFingerprints', {}) if prior else {}
    fingerprints = {item['name']: item['fingerprint'] for item in discovered['skills']}
    paths = git(upstream, 'ls-tree', '-r', '-z', '--name-only', candidate)
    actual = {str(Path(os.fsdecode(path)).parent) for path in paths.split(b'\0') if path.endswith(b'/SKILL.md') or path == b'SKILL.md'}
    changes = []
    for record in records:
        since, carried = record['baseline'], False
        try:
            if record['problems']:
                raise ValueError('; '.join(record['problems']))
            for primary in record['primaryPaths']:
                # Trees answer presence without blobs, so blobless clones stay offline.
                if not git(upstream, 'ls-tree', '--name-only', record['baseline'], '--', (primary + '/' if primary != '.' else '') + 'SKILL.md').strip():
                    raise ValueError('Recorded primary skill path is absent at the reviewed baseline: ' + primary)
            if prior and record['local'] in coverage.get('skills', []) and verified.get(record['local']) == fingerprints.get(record['local']) and is_ancestor(upstream, record['baseline'], prior):
                since, carried = prior, True
            delta = name_status(upstream, since, candidate, record['paths'])
            status = 'removed' if not any(primary in actual for primary in record['primaryPaths']) else 'changed' if delta else 'unchanged'
            changes.append({'local': record['local'], 'upstream': record['paths'], 'baseline': record['baseline'], 'since': since, 'carriedForward': carried, 'status': status, 'files': delta})
        except (OSError, ValueError) as error:
            changes.append({'local': record['local'], 'upstream': record['paths'], 'baseline': record['baseline'], 'since': since, 'carriedForward': carried, 'status': 'blocked', 'reason': str(error)})
    suite_results, shared = {}, []
    covered = {entry['local'] for definition in policies.values() for entry in definition.get('skills', [])}
    for name, definition in policies.items():
        skill_root = definition['skillRoot'].rstrip('/')
        prefix = skill_root + '/'
        suite_inventory = {path for path in actual if skill_root == '.' or path.startswith(prefix)}
        current = {path for path in suite_inventory if excluded(path, definition) is None}
        known = {entry['upstream'] for entry in definition.get('skills', [])}
        removed, added = known - suite_inventory, current - known
        moves = [{'from': old, 'to': candidates[0], 'decision': 'Verify continuity before changing identity or baseline'} for old in sorted(removed) if len(candidates := [new for new in added if Path(new).name == Path(old).name]) == 1]
        suite_results[name] = {'added': sorted(added), 'removed': sorted(removed), 'possibleMoves': moves, 'excluded': [{'path': path, 'reason': excluded(path, definition)} for path in sorted(suite_inventory - current)]}
        # One diff per policy from its shared review position, not from every record baseline.
        mapped = {entry['local'] for entry in definition.get('skills', [])}
        since, carried = definition.get('sharedReviewedThrough'), False
        try:
            if not since:
                baselines = sorted({record['baseline'] for record in records if record['local'] in mapped and record['baseline']})
                if not baselines:
                    raise ValueError('No reviewed-through revision for shared inputs')
                since = git(upstream, 'rev-list', '--no-walk=sorted', *baselines).decode().split()[0]
            since = git(upstream, 'rev-parse', '--verify', since + '^{commit}').decode().strip()
            if prior and coverage.get('sharedInputsReviewed') is True and is_ancestor(upstream, since, prior):
                since, carried = prior, True
            targets = [definition['sharedRoot']] if 'sharedRoot' in definition else definition.get('sharedPaths', [])
            delta = name_status(upstream, since, candidate, targets) if targets else []
            owned = known | suite_inventory
            unowned = [line for line in delta if any(not any(path.startswith(directory + '/') for directory in owned) for path in line.split('\t')[1:])]
            files = [line for line in unowned if not all(excluded(path, definition) for path in line.split('\t')[1:])]
            shared.append({'suite': name, 'since': since, 'carriedForward': carried, 'files': files, 'excludedFiles': len(unowned) - len(files)})
        except ValueError as error:
            shared.append({'suite': name, 'since': since, 'status': 'blocked', 'reason': str(error)})
    # Records outside every policy keep their declared plugin roots; a policy diff already covers the rest.
    scoped_inputs = {(record['baseline'], tuple(record['sharedPaths'])) for record in records if record['local'] not in covered and record['baseline'] and record['sharedPaths']}
    for baseline, targets in sorted(scoped_inputs):
        try:
            shared.append({'paths': list(targets), 'since': baseline, 'files': name_status(upstream, baseline, candidate, targets)})
        except ValueError as error:
            shared.append({'paths': list(targets), 'since': baseline, 'status': 'blocked', 'reason': str(error)})
    for change in changes:
        original = next((entry['upstream'] for definition in policies.values() for entry in definition.get('skills', []) if entry['local'] == change['local']), None)
        if original and original not in actual and change['status'] != 'blocked':
            change['status'] = 'removed'
    result = {'source': source, 'candidate': candidate, 'repository': group['repository'], 'tracking': group['tracking'], 'resumedFrom': prior, 'suites': suite_results, 'skills': changes, 'sharedInputs': shared}
    if policies:
        result['inventory'] = sorted(actual)
    if source in suite_results:
        result.update(suite_results[source])
    return result


def fetch(root, catalog, state, remotes=None):
    """Keep one blobless clone per repository identity and resolve each group's tracking choice."""
    remotes = remotes or {}
    groups = inventory(root, catalog)['sourceGroups']
    result, prepared = {'candidates': {}, 'checkouts': {}, 'errors': {}}, {}
    for key, group in sorted(groups.items()):
        identity, tracking = group['identity'], group['tracking']
        checkout = state / 'sources' / identity.replace('/', '-')
        try:
            if identity not in prepared:
                canonical = 'https://' + identity + '.git'
                # The override reaches the transport only; the clone keeps its canonical origin.
                rewrite = ['-c', 'url.' + remotes[identity] + '.insteadOf=' + canonical] if identity in remotes else []
                tags = ['--tags', '--force'] if any(other['identity'] == identity and other['tracking']['kind'] == 'tag' for other in groups.values()) else []
                try:
                    if checkout.exists():
                        if not (checkout / '.git').is_dir() or repository_identity(git(checkout, 'remote', 'get-url', 'origin').decode().strip()) != identity:
                            raise ValueError('Existing path is not a clone of ' + canonical + ': ' + str(checkout))
                        git(checkout, *rewrite, 'fetch', '--quiet', '--prune', *tags, 'origin')
                    else:
                        checkout.parent.mkdir(parents=True, exist_ok=True)
                        git(checkout.parent, *rewrite, 'clone', '--quiet', '--filter=blob:none', '--no-checkout', canonical, checkout.name)
                    prepared[identity] = None
                except ValueError as error:
                    prepared[identity] = str(error)
            if prepared[identity]:
                raise ValueError(prepared[identity])
            ref = {'branch': 'refs/remotes/origin/', 'tag': 'refs/tags/', 'commit': ''}[tracking['kind']] + tracking['ref']
            result['candidates'][key] = git(checkout, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()
            result['checkouts'][key] = str(checkout)
        except ValueError as error:
            result['errors'][key] = str(error)
    return result


def prune(state, keep):
    """Delete run directories beyond the newest N by name; files and symlinks are left alone."""
    if keep < 0:
        raise ValueError('Keep at least zero runs')
    runs = state / 'runs'
    if runs.is_symlink() or not runs.is_dir():
        return {'deleted': []}
    names = sorted(path.name for path in runs.iterdir() if path.is_dir() and not path.is_symlink())
    deleted = names[:max(len(names) - keep, 0)]
    for name in deleted:
        shutil.rmtree(runs / name)
    return {'deleted': deleted}


class Locked(Exception):
    def __init__(self, owner):
        super().__init__('locked')
        self.owner = owner if isinstance(owner, dict) else {}


def acquire_lock(state, run, now):
    """Take $STATE/lock with an atomic mkdir; a lock older than LOCK_STALE_MINUTES belongs to a dead run."""
    lock = state / 'lock'
    recovered = None
    try:
        lock.mkdir()
    except FileExistsError:
        owner = read_json(lock / 'owner.json')
        try:
            since = parse_time(owner['startedAt'])
        except (KeyError, TypeError, ValueError):
            since = None
        if since and now - since < timedelta(minutes=LOCK_STALE_MINUTES):
            raise Locked(owner)
        recovered = owner if isinstance(owner, dict) else {'unreadable': True}
        # Renaming first lets only one of two racing runs recreate the lock.
        stale = state / ('lock.stale.' + now.strftime('%Y%m%dT%H%M%S%fZ'))
        os.rename(lock, stale)
        shutil.rmtree(stale)
        try:
            lock.mkdir()
        except FileExistsError:
            raise Locked(read_json(lock / 'owner.json'))
    write_atomic(lock / 'owner.json', json.dumps({'run': str(run), 'startedAt': now.isoformat()}, indent=2) + '\n')
    return recovered


def leftovers(state):
    """Uncommitted changes and unpushed commits an interrupted run left in the reused worktrees."""
    found = {}
    for name in WORKTREES:
        worktree = state / 'worktrees' / name
        if not worktree.exists():
            continue
        try:
            changes = git(worktree, 'status', '--porcelain').decode().splitlines()
            unpushed = git(worktree, 'rev-list', 'HEAD', '--not', '--remotes').decode().split()
        except ValueError as error:
            found[name] = {'error': str(error)}
            continue
        if changes or unpushed:
            found[name] = {'changes': changes, 'unpushed': unpushed}
    return found


def begin(state, mode=None, now=None):
    """Open a run: take the lock, choose the mode, find the resume checkpoint, and gather carried state."""
    now = now or datetime.now(timezone.utc)
    state.mkdir(parents=True, exist_ok=True)
    runs = state / 'runs'
    earlier = sorted((path for path in runs.iterdir() if path.is_dir() and not path.is_symlink()), reverse=True) if runs.is_dir() else []
    audits = [checkpoint_date(data) for path in earlier if path.name.endswith('-audit') and isinstance(data := read_json(path / 'checkpoint.json'), dict) and data.get('coverageComplete') is True]
    last_audit = max((date for date in audits if date), default=None)
    if mode:
        reason = 'named'
    elif last_audit and (now.date() - last_audit).days < AUDIT_INTERVAL_DAYS:
        mode, reason = 'upstream', 'audit completed ' + last_audit.isoformat()
    else:
        mode, reason = 'audit', 'no completed audit in ' + str(AUDIT_INTERVAL_DAYS) + ' days'
    run = runs / (now.strftime('%Y-%m-%dT%H%M%SZ') + '-' + mode)
    recovered = acquire_lock(state, run, now)
    try:
        run.mkdir(parents=True)
        resume, skipped = None, []
        for path in earlier:
            if not (path / 'checkpoint.json').exists():
                continue
            data = read_json(path / 'checkpoint.json')
            if isinstance(data, dict) and data.get('schema') == 2:
                resume = (path / 'checkpoint.json', data)
                break
            skipped.append(str(path / 'checkpoint.json'))
        comments_since = None
        if resume:
            try:
                comments_since = (parse_time(resume[1]['createdAt']) - timedelta(minutes=float(resume[1].get('elapsedMinutes', 0)))).isoformat()
            except (KeyError, TypeError, ValueError):
                comments_since = None
        questions = read_json(state / 'questions.json') if (state / 'questions.json').exists() else []
        if questions is None:
            raise ValueError('Unreadable questions file: ' + str(state / 'questions.json'))
        result = {'run': str(run), 'mode': mode, 'modeReason': reason, 'startedAt': now.isoformat(), 'resume': str(resume[0]) if resume else None, 'skippedCheckpoints': skipped, 'commentsSince': comments_since, 'questions': questions}
        actions_path = state / 'next-actions.json'
        if actions_path.exists():
            actions = read_json(actions_path)
            if not isinstance(actions, list):
                raise ValueError('Unreadable next actions file: ' + str(actions_path))
            for action in actions:
                try:
                    carried = datetime.fromisoformat(action['firstCarried']).date()
                except (KeyError, TypeError, ValueError):
                    raise ValueError('Next action needs an item and a firstCarried date: ' + json.dumps(action))
                if last_audit and carried <= last_audit:
                    action['overdue'] = True
            result['nextActions'] = actions
        else:
            result['nextActions'] = []
            legacy = next((path / 'next-actions.md' for path in earlier if (path / 'next-actions.md').is_file()), None)
            if legacy:
                result['legacyNextActions'] = str(legacy)
        result['leftovers'] = leftovers(state)
        if recovered is not None:
            result['recoveredLock'] = recovered
        write_atomic(run / 'run.json', json.dumps({'startedAt': result['startedAt'], 'mode': mode}, indent=2) + '\n')
        write_atomic(run / 'begin.json', json.dumps(result, indent=2) + '\n')
        return result
    except BaseException:
        release(state, run)
        raise


def release(state, run):
    owner = read_json(state / 'lock' / 'owner.json')
    if not (state / 'lock').is_dir():
        return {'error': 'No run holds the lock'}
    holder = owner.get('run') if isinstance(owner, dict) else None
    if not holder or Path(holder).resolve() != Path(run).resolve():
        return {'error': 'The lock is held by ' + str(holder), 'heldBy': holder}
    shutil.rmtree(state / 'lock')
    return {'released': str(run)}


def suites_changed(report):
    return any(suite['added'] or suite['removed'] or suite['possibleMoves'] for suite in report['suites'].values())


def shared_changed(report):
    return any(entry.get('files') or entry.get('status') == 'blocked' for entry in report['sharedInputs'])


def compared_reviews(comparisons, candidates):
    """Turn compare reports into source reviews: unchanged skills, and empty inventories and shared inputs, need no decision."""
    reviews = {}
    for report in comparisons:
        key = group_key(repository_identity(report['repository']), report['tracking'])
        if candidates.get(key) != report['candidate']:
            raise ValueError('Comparison candidate differs from the checkpoint candidate for ' + key)
        review = reviews.setdefault(key, {'candidate': report['candidate'], 'skills': [], 'inventoryReviewed': True, 'sharedInputsReviewed': True})
        # A skill with several records in one group is acknowledged only when every row is unchanged.
        statuses = {}
        for change in report['skills']:
            statuses.setdefault(change['local'], set()).add(change['status'])
        review['skills'] = sorted(set(review['skills']) | {name for name, found in statuses.items() if found == {'unchanged'}})
        review['inventoryReviewed'] = review['inventoryReviewed'] and not suites_changed(report)
        review['sharedInputsReviewed'] = review['sharedInputsReviewed'] and not shared_changed(report)
    return reviews


def library_revision(root):
    try:
        return git(root, 'rev-parse', '--verify', 'HEAD').decode().strip()
    except ValueError:
        return None


def checkpoint(root, catalog, candidates, completed, elapsed_minutes, integration_validated, source_reviews=None, resume=None, comparisons=None, failed=None, context_reviewed=False, context_affected=(), now=None):
    current = inventory(root, catalog)
    packaging = validate(root, catalog)
    groups = current['sourceGroups']
    now = now or datetime.now(timezone.utc)
    # A group that failed to fetch keeps the prior candidate and stays pending until it fetches again.
    failed = sorted(failed or {})
    candidates = dict(candidates)
    for key in failed:
        prior = resume.get('sourceCoverage', {}).get(key, {}).get('candidate') or resume.get('candidates', {}).get(key) if isinstance(resume, dict) else None
        if not prior:
            raise ValueError('Failed source has no prior candidate to keep: ' + key)
        candidates[key] = prior
    if set(candidates) != set(groups) or any(not isinstance(value, str) or not re.fullmatch(SHA, value) for value in candidates.values()):
        raise ValueError('Checkpoint needs one immutable candidate SHA for each discovered repository/tracking group: ' + ', '.join(sorted(groups)))
    names = {item['name'] for item in current['skills']}
    if not set(completed) <= names or len(completed) != len(set(completed)) or not math.isfinite(elapsed_minutes) or elapsed_minutes < 0:
        raise ValueError('Unknown or duplicate completed skills or invalid elapsed time')
    reviews = compared_reviews(comparisons or [], candidates)
    # Explicit reviews record decided changes and override automatic acknowledgements.
    for key, review in (source_reviews or {}).items():
        automatic = reviews.get(key, {})
        if automatic and automatic['candidate'] != review.get('candidate'):
            raise ValueError('Source review candidate differs from its comparison for ' + key)
        reviews[key] = {**automatic, **review, 'skills': sorted(set(automatic.get('skills', [])) | set(review.get('skills', [])))}
    if not set(reviews) <= set(groups):
        raise ValueError('Unknown source review group')
    requested = set(completed)
    affected = set(context_affected)
    if not affected <= names:
        raise ValueError('Unknown skills in --context-affected')
    invalidated = []
    fingerprints = {item['name']: item['fingerprint'] for item in current['skills']}
    if resume is not None:
        if resume.get('schema') != 2 or 'skillFingerprints' not in resume or 'sourceCoverage' not in resume:
            raise ValueError('Legacy or incomplete checkpoint cannot establish current repository coverage; reconcile it against a fresh inventory')
        # A context change keeps a review only when the coordinator reviewed that change and the skill is unaffected.
        same_context = resume.get('contextFingerprint') == current['contextFingerprint']
        for name in resume.get('locallyReviewed', resume.get('completed', [])):
            if name in names and resume['skillFingerprints'].get(name) == fingerprints[name] and (same_context or (context_reviewed and name not in affected)):
                requested.add(name)
            else:
                invalidated.append(name)
        for key, group in groups.items():
            previous = resume['sourceCoverage'].get(key, {})
            if key not in reviews and previous.get('candidate') == candidates[key] and previous.get('fingerprint') == group['fingerprint'] and (same_context or context_reviewed):
                reviews[key] = previous if same_context else {**previous, 'skills': [name for name in previous.get('skills', []) if name not in affected]}
    coverage = {}
    for key, group in groups.items():
        review = reviews.get(key, {})
        reviewed_names = review.get('skills', [])
        if not isinstance(reviewed_names, list) or not set(reviewed_names) <= set(group['skills']) or len(reviewed_names) != len(set(reviewed_names)):
            raise ValueError('Unknown or duplicate skills in source review ' + key)
        matching = review.get('candidate') == candidates[key]
        coverage[key] = {'candidate': candidates[key], 'fingerprint': group['fingerprint'], 'skills': sorted(reviewed_names) if matching else [], 'pending': sorted(set(group['skills']) - set(reviewed_names)) if matching else group['skills'], 'inventoryReviewed': matching and review.get('inventoryReviewed') is True, 'sharedInputsReviewed': matching and review.get('sharedInputsReviewed') is True}
        if key in failed:
            coverage[key].update({'skills': [], 'pending': group['skills'], 'inventoryReviewed': False, 'sharedInputsReviewed': False})
    finished = []
    for item in current['skills']:
        invalid_packaging = any(problem.startswith(item['name'] + ':') or problem.startswith(item['directory'] + '/') for problem in packaging['problems'])
        if item['name'] in requested and not item['problems'] and not invalid_packaging and all(record['key'] and item['name'] in coverage[record['key']]['skills'] for record in item['sources']):
            finished.append(item['name'])
    pending = sorted(names - set(finished))
    source_pending = [key for key, review in coverage.items() if review['pending'] or not review['inventoryReviewed'] or not review['sharedInputsReviewed']]
    # Integration checks still hold when no skill or governing input changed since a validated checkpoint.
    integration_validated = integration_validated or (isinstance(resume, dict) and resume.get('integrationValidated') is True and resume.get('skillFingerprints') == fingerprints and resume.get('contextFingerprint') == current['contextFingerprint'])
    earlier_dates = review_dates(resume)
    today = now.date().isoformat()
    reviewed_at = {name: today if name in completed else earlier_dates.get(name) or today for name in sorted(requested)}
    return {'schema': 2, 'createdAt': now.isoformat(), 'libraryRevision': library_revision(root), 'inventoryFingerprint': current['fingerprint'], 'contextFingerprint': current['contextFingerprint'], 'contextFiles': current['contextFiles'], 'catalogFingerprint': current['catalogFingerprint'], 'skillFingerprints': fingerprints, 'candidates': candidates, 'failedSources': failed, 'locallyReviewed': sorted(requested), 'reviewedAt': reviewed_at, 'completed': sorted(finished), 'pending': pending, 'sourceCoverage': coverage, 'pendingSources': source_pending, 'invalidated': sorted(invalidated), 'problems': packaging['problems'], 'elapsedMinutes': elapsed_minutes, 'integrationValidated': integration_validated, 'coverageComplete': not pending and not source_pending and not packaging['problems'] and integration_validated}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--root', type=Path, help='Skill library repository root; begin, release, and prune need only --state')
    commands = parser.add_subparsers(dest='command', required=True, metavar='command')
    begin_parser = commands.add_parser('begin', help='Take the run lock, choose the mode, and open a run folder with the resume checkpoint and carried state')
    begin_parser.add_argument('--state', type=Path, required=True)
    begin_parser.add_argument('--mode', choices=['upstream', 'audit'], help='Run this mode instead of choosing by the last completed audit')
    begin_parser.add_argument('--now', help=argparse.SUPPRESS)
    release_parser = commands.add_parser('release', help='Free the run lock that begin took for --run')
    release_parser.add_argument('--state', type=Path, required=True)
    release_parser.add_argument('--run', type=Path, required=True)
    inventory_parser = commands.add_parser('inventory', help='Discover every skill, its provenance records, source groups, and fidelity backlog')
    inventory_parser.add_argument('--resume', type=Path, help='Prior checkpoint; lists skills whose files changed since it as changedSince')
    inventory_parser.add_argument('--output', type=Path)
    commands.add_parser('validate', help='Check packaging, listings, links, and catalog mappings')
    fetch_parser = commands.add_parser('fetch', help='Clone or update one blobless checkout per source and resolve candidate commits')
    fetch_parser.add_argument('--state', type=Path, required=True, help='Machine-local state directory; clones live under sources/')
    fetch_parser.add_argument('--remote', action='append', default=[], metavar='IDENTITY=URL', help='Fetch IDENTITY (such as github.com/owner/name) from URL without persisting it')
    fetch_parser.add_argument('--output', type=Path)
    compare_parser = commands.add_parser('compare', help='Diff one source group or catalog policy from reviewed baselines to a candidate; --resume carries checkpoint progress forward')
    compare_parser.add_argument('--source', help='Source group key or catalog source name')
    compare_parser.add_argument('--upstream', type=Path, help='Checkout whose origin is the source repository')
    compare_parser.add_argument('--candidate')
    compare_parser.add_argument('--fetch', type=Path, help='Fetch output; compares every fetched group instead of --source/--upstream/--candidate')
    compare_parser.add_argument('--output-dir', type=Path, help='With --fetch, write one <repository>-compare.json per group here')
    compare_parser.add_argument('--resume', type=Path, help='Prior checkpoint whose verified progress replaces record baselines')
    compare_parser.add_argument('--output', type=Path)
    checkpoint_parser = commands.add_parser('checkpoint', help='Record verification progress for the current candidates')
    checkpoint_parser.add_argument('--candidates', type=Path, required=True, help='Group-to-candidate map, or fetch output containing one')
    checkpoint_parser.add_argument('--completed', nargs='*', default=[])
    checkpoint_parser.add_argument('--source-reviews', type=Path, help='Decided source reviews per group; merged over --compare acknowledgements')
    checkpoint_parser.add_argument('--compare', type=Path, nargs='*', default=[], help='Compare reports whose unchanged skills and empty inventories or shared inputs count as reviewed')
    checkpoint_parser.add_argument('--resume', type=Path)
    checkpoint_parser.add_argument('--elapsed-minutes', type=float, required=True)
    checkpoint_parser.add_argument('--integration-validated', action='store_true')
    checkpoint_parser.add_argument('--context-reviewed', action='store_true', help='The context change since --resume was reviewed; earlier reviews survive it except for --context-affected')
    checkpoint_parser.add_argument('--context-affected', nargs='*', default=[], metavar='NAME')
    checkpoint_parser.add_argument('--output', type=Path, required=True)
    prune_parser = commands.add_parser('prune', help='Delete run directories under --state/runs beyond the newest --keep')
    prune_parser.add_argument('--state', type=Path, required=True)
    prune_parser.add_argument('--keep', type=int, required=True)
    arguments = parser.parse_args()
    # State-only commands run from a copy of this file streamed from the default branch, before any worktree is synced.
    if arguments.command not in {'begin', 'release', 'prune'} and not arguments.root:
        parser.error('--root is required for ' + arguments.command)
    try:
        if arguments.root:
            root = arguments.root.resolve()
            catalog = json.loads(arguments.catalog.read_text())
        if arguments.command == 'begin':
            try:
                result = begin(arguments.state.resolve(), arguments.mode, parse_time(arguments.now) if arguments.now else None)
            except Locked as error:
                print(json.dumps({'error': 'locked', 'heldBy': error.owner.get('run'), 'since': error.owner.get('startedAt')}))
                return 3
        elif arguments.command == 'release':
            result = release(arguments.state.resolve(), arguments.run.resolve())
        elif arguments.command == 'inventory':
            result = inventory(root, catalog, json.loads(arguments.resume.read_text()) if arguments.resume else None)
        elif arguments.command == 'validate':
            result = validate(root, catalog)
        elif arguments.command == 'fetch':
            remotes = {}
            for item in arguments.remote:
                identity, separator, url = item.partition('=')
                if not separator or not url:
                    raise ValueError('Remote override needs IDENTITY=URL: ' + item)
                remotes[repository_identity('https://' + identity)] = url
            result = fetch(root, catalog, arguments.state.resolve(), remotes)
        elif arguments.command == 'compare':
            resume = json.loads(arguments.resume.read_text()) if arguments.resume else None
            if arguments.fetch:
                if not arguments.output_dir:
                    raise ValueError('compare --fetch needs --output-dir')
                fetched = json.loads(arguments.fetch.read_text())
                result = {}
                for key, sha in sorted(fetched['candidates'].items()):
                    report = compare(root, catalog, key, Path(fetched['checkouts'][key]), sha, resume)
                    path = arguments.output_dir / (re.sub(r'[^A-Za-z0-9._-]+', '-', key) + '-compare.json')
                    write_atomic(path, json.dumps(report, indent=2, sort_keys=True) + '\n')
                    statuses = {}
                    for change in report['skills']:
                        statuses[change['status']] = statuses.get(change['status'], 0) + 1
                    result[key] = {'output': str(path), 'skills': statuses, 'suitesChanged': suites_changed(report), 'sharedChanged': shared_changed(report)}
            elif arguments.source and arguments.upstream and arguments.candidate:
                result = compare(root, catalog, arguments.source, arguments.upstream, arguments.candidate, resume)
            else:
                raise ValueError('compare needs --fetch with --output-dir, or --source, --upstream, and --candidate')
        elif arguments.command == 'prune':
            result = prune(arguments.state, arguments.keep)
        elif arguments.command == 'checkpoint':
            reviews = json.loads(arguments.source_reviews.read_text()) if arguments.source_reviews else None
            resume = json.loads(arguments.resume.read_text()) if arguments.resume else None
            candidates = json.loads(arguments.candidates.read_text())
            failed = {}
            # Accept fetch output directly: its candidates map is the input, and its errors stay pending.
            if isinstance(candidates.get('candidates'), dict):
                failed = candidates.get('errors') or {}
                candidates = candidates['candidates']
            result = checkpoint(root, catalog, candidates, arguments.completed, arguments.elapsed_minutes, arguments.integration_validated, reviews, resume, [json.loads(path.read_text()) for path in arguments.compare], failed, arguments.context_reviewed, arguments.context_affected)
        encoded = json.dumps(result, indent=2) + '\n'
        output = getattr(arguments, 'output', None)
        if output:
            write_atomic(output, encoded)
        print(encoded, end='')
        return 0 if result.get('valid', True) and not result.get('errors') and 'error' not in result else 1
    except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
        print(json.dumps({'error': str(error)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
