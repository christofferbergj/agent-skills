import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'catalog.py'
spec = importlib.util.spec_from_file_location('catalog', SCRIPT)
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)

REPOSITORY = 'https://github.com/example/library.git'
GROUP = 'github.com/example/library@branch:main'
OTHER = 'https://github.com/example/other.git'
OTHER_GROUP = 'github.com/example/other@branch:main'


class RepositoryCoverage(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / 'local'
        self.root.mkdir()
        self.upstream = self.base / 'upstream'
        subprocess.run(['git', 'init', '-q', str(self.upstream)], check=True)
        subprocess.run(['git', '-C', str(self.upstream), 'remote', 'add', 'origin', REPOSITORY], check=True)
        initial = self.upstream / 'skills/engineering/alpha'
        initial.mkdir(parents=True)
        (initial / 'SKILL.md').write_text('initial source')
        (self.upstream / 'LICENSE').write_text('fixture MIT')
        self.commit('Initial')
        subprocess.run(['git', '-C', str(self.upstream), 'branch', '-qM', 'main'], check=True)
        self.baseline = self.revision()
        self.definition = {
            'repository': REPOSITORY, 'branch': 'main', 'skillRoot': 'skills',
            'skills': [{'upstream': 'skills/engineering/alpha', 'local': 'alpha', 'directory': 'skills/engineering/alpha'}],
            'excludedNames': {'teach': 'User exclusion'}, 'excludedPathComponents': ['personal'],
            'sharedPaths': ['LICENSE', 'README.md'],
        }
        self.registry = {'sources': {'matt': self.definition}, 'owners': {}, 'policy': 'Preserve adaptations; review integration'}
        self.directory = self.add_skill('alpha', source=True)

    def tearDown(self):
        self.temporary.cleanup()

    def provenance(self, name='alpha', repository=REPOSITORY, tracking='upstream `main`', baseline=None):
        identity = catalog.repository_identity(repository)
        revision = baseline or self.baseline
        return (
            f'# {name} source\n\n'
            f'Canonical source: [source](https://{identity}).\n'
            f'Original skill: [source](https://{identity}/blob/{revision}/skills/engineering/{name}/SKILL.md).\n'
            f'Tracking policy: {tracking}\n'
            f'Imported from commit: `{revision}`\n'
            f'Reviewed through commit: `{revision}`\n'
            'License: MIT\n\n## Local adaptations\nPreserve local behavior.\n'
        )

    def add_skill(self, name, source=False, repository=REPOSITORY, category='engineering'):
        directory = self.root / 'skills' / category / name
        (directory / 'agents').mkdir(parents=True)
        (directory / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Fixture behavior.\n---\nDo the fixture work.\n')
        (directory / 'agents/openai.yaml').write_text(f'interface:\n  display_name: {name}\n')
        if source:
            (directory / 'LICENSE').write_text('fixture MIT')
            (directory / 'UPSTREAM.md').write_text(self.provenance(name, repository))
        for readme, target in [(self.root / 'README.md', f'skills/{category}/{name}/SKILL.md'), (directory.parent / 'README.md', f'{name}/SKILL.md')]:
            with readme.open('a') as output:
                output.write(f'[{name}]({target})\n')
        return directory

    def commit(self, title):
        subprocess.run(['git', '-C', str(self.upstream), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.upstream), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', title], check=True)

    def revision(self):
        return subprocess.check_output(['git', '-C', str(self.upstream), 'rev-parse', 'HEAD'], text=True).strip()

    def reviews(self, groups=None, candidate=None):
        groups = groups or catalog.inventory(self.root, self.registry)['sourceGroups']
        return {key: {'candidate': candidate or self.baseline, 'inventoryReviewed': True, 'sharedInputsReviewed': True, 'skills': group['skills']} for key, group in groups.items()}

    def checkpoint(self, completed=None, reviews=None, resume=None, candidates=None, integrated=True):
        return catalog.checkpoint(self.root, self.registry, candidates or {GROUP: self.baseline}, ['alpha'] if completed is None else completed, 55, integrated, reviews, resume)

    def test_valid_packaging_and_callable_policy(self):
        self.assertTrue(catalog.validate(self.root, self.registry)['valid'])
        (self.directory / 'agents/openai.yaml').write_text('policy:\n  allow_implicit_invocation: false\n')
        self.assertFalse(catalog.validate(self.root, self.registry)['valid'])
        self.assertFalse(self.checkpoint(reviews=self.reviews())['coverageComplete'])

    def test_readme_listing_and_owned_reference_are_checked(self):
        (self.root / 'README.md').write_text('alpha mentioned without a link\n')
        self.assertFalse(catalog.validate(self.root, self.registry)['valid'])
        (self.root / 'README.md').write_text('[alpha](skills/engineering/alpha/SKILL.md)\n')
        with (self.directory / 'SKILL.md').open('a') as output:
            output.write('[foreign](../../../README.md)\n')
        self.assertFalse(catalog.validate(self.root, self.registry)['valid'])

    def test_inventory_finds_beta_additions_and_applies_suite_exclusions(self):
        for path in ['skills/in-progress/beta', 'skills/productivity/teach', 'skills/personal/private']:
            directory = self.upstream / path
            directory.mkdir(parents=True)
            (directory / 'SKILL.md').write_text('candidate')
        self.commit('Add candidates')
        result = catalog.compare(self.root, self.registry, 'matt', self.upstream, self.revision())
        self.assertEqual(result['added'], ['skills/in-progress/beta'])
        self.assertEqual(len(result['excluded']), 2)
        self.assertEqual(len(result['inventory']), 4)
        self.assertFalse(result['reviewComplete'])
        self.add_skill('teach')
        self.assertIn('teach', [item['name'] for item in catalog.inventory(self.root, self.registry)['skills']])

    def test_removed_skill_stays_local_and_category_move_needs_review(self):
        moved = self.upstream / 'skills/agents/alpha'
        moved.parent.mkdir(parents=True)
        (self.upstream / 'skills/engineering/alpha').rename(moved)
        self.commit('Move category')
        result = catalog.compare(self.root, self.registry, 'matt', self.upstream, self.revision())
        self.assertEqual(result['removed'], ['skills/engineering/alpha'])
        self.assertEqual(result['possibleMoves'][0]['to'], 'skills/agents/alpha')
        self.assertEqual(result['skills'][0]['status'], 'removed')
        self.assertTrue((self.directory / 'SKILL.md').exists())

    def test_changed_behavior_license_and_support_resources_are_review_inputs(self):
        (self.upstream / 'skills/engineering/alpha/SKILL.md').write_text('changed behavior')
        (self.upstream / 'skills/engineering/alpha/support.py').write_text('support = True\n')
        (self.upstream / 'LICENSE').write_text('changed license')
        self.commit('Change inputs')
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.revision())
        self.assertEqual(result['skills'][0]['status'], 'changed')
        self.assertIn('support.py', ' '.join(result['skills'][0]['files']))
        self.assertIn('LICENSE', ' '.join(result['sharedInputs'][0]['files']))

    def test_missing_baseline_blocks_instead_of_resetting_to_head(self):
        record = self.directory / 'UPSTREAM.md'
        record.write_text(self.provenance().replace(f'Reviewed through commit: `{self.baseline}`', 'No reproducible reviewed baseline'))
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.baseline)
        self.assertEqual(result['skills'][0]['status'], 'blocked')
        self.assertFalse(self.checkpoint(reviews=self.reviews())['coverageComplete'])
        self.assertIn('alpha', self.checkpoint(reviews=self.reviews())['pending'])

    def test_missing_history_blocks_even_a_well_formed_baseline(self):
        (self.directory / 'UPSTREAM.md').write_text(self.provenance(baseline='f' * 40))
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.baseline)
        self.assertEqual(result['skills'][0]['status'], 'blocked')

    def test_nonexistent_historical_primary_path_is_blocked(self):
        record = self.directory / 'UPSTREAM.md'
        record.write_text(record.read_text().replace('/skills/engineering/alpha/SKILL.md', '/skills/engineering/typo/SKILL.md'))
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.baseline)
        self.assertEqual(result['skills'][0]['status'], 'blocked')
        self.assertIn('absent at the reviewed baseline', result['skills'][0]['reason'])

    def test_explicit_commit_pin_cannot_compare_a_different_candidate(self):
        record = self.directory / 'UPSTREAM.md'
        record.write_text(record.read_text().replace('upstream `main`', f'pinned commit `{self.baseline}`'))
        (self.upstream / 'LICENSE').write_text('new candidate')
        self.commit('Advance source')
        pinned_group = f'github.com/example/library@commit:{self.baseline}'
        with self.assertRaisesRegex(ValueError, 'pinned'):
            catalog.compare(self.root, self.registry, pinned_group, self.upstream, self.revision())
        self.assertEqual(catalog.compare(self.root, self.registry, pinned_group, self.upstream, self.baseline)['candidate'], self.baseline)

    def test_repository_root_upstream_skill_is_discovered(self):
        (self.upstream / 'SKILL.md').write_text('root skill')
        self.commit('Add root skill')
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.revision())
        self.assertIn('.', result['inventory'])

    def test_generic_repository_root_source_can_be_compared_and_accounted_for(self):
        (self.upstream / 'SKILL.md').write_text('root behavior')
        self.commit('Add root source')
        self.baseline = self.revision()
        self.registry['sources'] = {}
        record = self.directory / 'UPSTREAM.md'
        record.write_text(self.provenance().replace('/skills/engineering/alpha/SKILL.md', '/SKILL.md'))
        discovered = catalog.inventory(self.root, self.registry)
        self.assertTrue(discovered['valid'], discovered['problems'])
        source = discovered['sourceGroups'][GROUP]['records'][0]
        self.assertEqual(source['primaryPaths'], ['.'])
        self.assertIn('.', source['paths'])
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.baseline)
        self.assertEqual(result['skills'][0]['status'], 'unchanged')
        self.assertTrue(self.checkpoint(reviews=self.reviews())['coverageComplete'])
        (self.upstream / 'SKILL.md').write_text('changed root behavior')
        self.commit('Change root source')
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.revision())
        self.assertEqual(result['skills'][0]['status'], 'changed')
        self.assertIn('SKILL.md', ' '.join(result['skills'][0]['files']))

    def test_shared_root_preserves_category_docs_and_rename_endpoints(self):
        self.definition['sharedRoot'] = '.'
        (self.upstream / 'skills/engineering/README.md').write_text('New category policy')
        (self.upstream / 'skills/shared-guidance.md').write_text('Shared behavior')
        (self.upstream / 'skills/engineering/alpha/SKILL.md').rename(self.upstream / 'skills/moved-guidance.md')
        self.commit('Change shared inputs')
        result = catalog.compare(self.root, self.registry, 'matt', self.upstream, self.revision())
        files = '\n'.join(result['sharedInputs'][0]['files'])
        for name in ['skills/engineering/README.md', 'skills/shared-guidance.md', 'skills/moved-guidance.md']:
            self.assertIn(name, files)

    def test_checkpoint_needs_local_source_inventory_shared_and_integration_reviews(self):
        before = (self.directory / 'UPSTREAM.md').read_bytes()
        self.assertFalse(self.checkpoint()['coverageComplete'])
        self.assertFalse(self.checkpoint(completed=[], reviews=self.reviews())['coverageComplete'])
        review = self.reviews()
        for field in ['inventoryReviewed', 'sharedInputsReviewed']:
            partial = {GROUP: {**review[GROUP], field: False}}
            result = self.checkpoint(reviews=partial)
            self.assertFalse(result['coverageComplete'])
            self.assertEqual(result['pendingSources'], [GROUP])
        result = self.checkpoint(reviews=review, integrated=False)
        self.assertFalse(result['coverageComplete'])
        result = self.checkpoint(reviews=review)
        self.assertTrue(result['coverageComplete'])
        self.assertFalse(result['reviewComplete'])
        self.assertFalse(result['baselinesAdvancedByCheckpoint'])
        self.assertEqual((self.directory / 'UPSTREAM.md').read_bytes(), before)

    def test_candidates_are_required_for_discovered_sources_not_old_aliases(self):
        self.add_skill('beta', source=True, repository=OTHER)
        with self.assertRaises(ValueError):
            self.checkpoint()
        with self.assertRaises(ValueError):
            self.checkpoint(candidates={'matt': self.baseline})
        with self.assertRaises(ValueError):
            self.checkpoint(completed=['unknown'], candidates={GROUP: self.baseline, OTHER_GROUP: self.baseline})

    def test_future_local_and_sourced_skills_expand_coverage_without_catalog_edits(self):
        self.add_skill('local-only')
        self.add_skill('beta', source=True, repository=OTHER)
        discovered = catalog.inventory(self.root, self.registry)
        self.assertEqual(discovered['repositorySkills'], 3)
        self.assertEqual(discovered['mappedSkills'], 1)
        self.assertEqual(set(discovered['sourceGroups']), {GROUP, OTHER_GROUP})
        result = self.checkpoint(reviews=self.reviews(), candidates={GROUP: self.baseline, OTHER_GROUP: self.baseline})
        self.assertEqual(result['pending'], ['beta', 'local-only'])
        result = self.checkpoint(completed=['alpha', 'beta', 'local-only'], reviews=self.reviews(), candidates={GROUP: self.baseline, OTHER_GROUP: self.baseline})
        self.assertTrue(result['coverageComplete'])

    def test_a_mapped_skill_keeps_its_upstream_name_unless_a_rename_is_recorded(self):
        directory = self.add_skill('example-alpha', source=True)
        (directory / 'UPSTREAM.md').write_text(self.provenance('alpha'))
        self.definition['skills'] = [{'upstream': 'skills/engineering/alpha', 'local': 'example-alpha', 'directory': 'skills/engineering/example-alpha'}]
        self.assertIn('example-alpha: renamed from alpha without a recorded reason', catalog.validate(self.root, self.registry)['problems'])
        self.definition['skills'][0]['renamed'] = 'Collides with another installed alpha'
        self.assertTrue(catalog.validate(self.root, self.registry)['valid'])
        self.definition['skills'] = [{'upstream': 'skills/engineering/alpha', 'local': 'alpha', 'directory': 'skills/engineering/alpha', 'renamed': 'Stale reason'}]
        self.assertIn('alpha: records a rename reason but keeps the upstream name', catalog.validate(self.root, self.registry)['problems'])

    def test_unmapped_metadata_and_packaging_are_validated(self):
        directory = self.add_skill('local-only')
        for invalid in ['null', 'false', '23', '[list]', '{map: value}']:
            with self.subTest(invalid=invalid):
                (directory / 'SKILL.md').write_text(f'---\nname: local-only\ndescription: {invalid}\n---\n')
                self.assertFalse(catalog.validate(self.root, self.registry)['valid'])
                self.assertFalse(self.checkpoint(completed=['alpha', 'local-only'], reviews=self.reviews())['coverageComplete'])

    def test_unresolvable_provenance_is_not_local(self):
        directory = self.add_skill('beta')
        (directory / 'UPSTREAM.md').write_text('Original author: unknown. Import revision missing.')
        discovered = catalog.inventory(self.root, self.registry)
        beta = next(item for item in discovered['skills'] if item['name'] == 'beta')
        self.assertEqual(beta['classification'], 'unresolved')
        self.assertFalse(self.checkpoint(completed=['alpha', 'beta'], reviews=self.reviews())['coverageComplete'])

    def test_explicit_ancestry_without_a_source_record_stays_unresolved(self):
        directory = self.add_skill('beta')
        instruction = directory / 'SKILL.md'
        instruction.write_text(instruction.read_text() + '\nAdapted from [original](https://github.com/acme/skills/tree/main/skills/beta).\n')
        self.assertFalse(catalog.inventory(self.root, self.registry)['valid'])
        self.assertFalse(self.checkpoint(completed=['alpha', 'beta'], reviews=self.reviews())['coverageComplete'])

    def test_frontmatter_repository_credit_needs_explicit_classification(self):
        directory = self.add_skill('beta')
        instruction = directory / 'SKILL.md'
        instruction.write_text(instruction.read_text().replace('description: Fixture behavior.', 'description: Fixture behavior.\nmetadata:\n  credits:\n    url: https://github.com/example/other'))
        self.assertFalse(catalog.inventory(self.root, self.registry)['valid'])
        instruction.write_text(instruction.read_text().replace('https://github.com/example/other', 'https://gitlab.com/example/other.git'))
        self.assertFalse(catalog.inventory(self.root, self.registry)['valid'])

    def test_indirect_attribution_is_reported_without_inventing_an_import(self):
        instruction = self.directory / 'SKILL.md'
        instruction.write_text(instruction.read_text().replace('description: Fixture behavior.', 'description: Fixture behavior.\nmetadata:\n  credits:\n    url: https://github.com/example/other/blob/main/skills/beta/SKILL.md'))
        record = self.directory / 'UPSTREAM.md'
        record.write_text(record.read_text() + '\nAttribution-only source: https://github.com/example/other\nCanonical tracking remains the adapted source above.\n')
        discovered = catalog.inventory(self.root, self.registry)
        self.assertTrue(discovered['valid'])
        self.assertEqual(list(discovered['sourceGroups']), [GROUP])
        self.assertEqual(discovered['skills'][0]['attributions'][0]['identity'], 'github.com/example/other')

    def test_unknown_historical_import_with_markdown_review_baseline_is_valid(self):
        record = self.directory / 'UPSTREAM.md'
        text = self.provenance().replace(f'Imported from commit: `{self.baseline}`', 'Original upstream import revision: unrecorded. Preserve the historical gap.')
        text = text.replace(f'Reviewed through commit: `{self.baseline}`', f'Reviewed through: [{self.baseline}](https://github.com/example/library/commit/{self.baseline})')
        text = text.replace('License: MIT', f'Files reviewed: [support](https://github.com/example/library/blob/{self.baseline}/docs/support.md)\nLicense: MIT')
        record.write_text(text)
        (self.upstream / 'docs').mkdir()
        (self.upstream / 'docs/support.md').write_text('support changed')
        self.commit('Change documented support')
        discovered = catalog.inventory(self.root, self.registry)
        source = discovered['skills'][0]['sources'][0]
        self.assertTrue(discovered['valid'])
        self.assertIsNone(source['imported'])
        self.assertTrue(source['historicalImportUnknown'])
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.revision())
        self.assertIn('docs/support.md', ' '.join(result['skills'][0]['files']))

    def test_multiple_sources_must_each_complete_the_same_skill(self):
        record = self.directory / 'UPSTREAM.md'
        record.write_text(record.read_text() + '\n' + self.provenance(repository=OTHER))
        candidates = {GROUP: self.baseline, OTHER_GROUP: self.baseline}
        review = self.reviews()
        partial = {GROUP: review[GROUP]}
        result = self.checkpoint(reviews=partial, candidates=candidates)
        self.assertEqual(result['pending'], ['alpha'])
        self.assertIn(OTHER_GROUP, result['pendingSources'])
        self.assertTrue(self.checkpoint(reviews=review, candidates=candidates)['coverageComplete'])
        record.write_text(record.read_text().replace(f'Reviewed through commit: `{self.baseline}`', 'Reviewed through: unknown', 1))
        self.assertFalse(self.checkpoint(reviews=review, candidates=candidates)['coverageComplete'])

    def test_repository_aliases_collapse_but_tracking_choices_remain_separate(self):
        beta = self.add_skill('beta', source=True, repository='git@github.com:EXAMPLE/LIBRARY.git')
        self.assertEqual(len(catalog.inventory(self.root, self.registry)['sourceGroups']), 1)
        record = beta / 'UPSTREAM.md'
        record.write_text(record.read_text().replace('upstream `main`', 'upstream `release`'))
        discovered = catalog.inventory(self.root, self.registry)
        self.assertEqual(set(discovered['sourceGroups']), {GROUP, 'github.com/example/library@branch:release'})
        with self.assertRaises(ValueError):
            self.checkpoint(candidates={GROUP: self.baseline})

    def test_compare_rejects_an_unrelated_origin_even_with_available_commit(self):
        subprocess.run(['git', '-C', str(self.upstream), 'remote', 'set-url', 'origin', OTHER], check=True)
        with self.assertRaises(ValueError):
            catalog.compare(self.root, self.registry, GROUP, self.upstream, self.baseline)

    def test_resume_invalidates_changed_files_and_new_inventory_stays_pending(self):
        previous = self.checkpoint(reviews=self.reviews())
        self.assertTrue(previous['coverageComplete'])
        (self.directory / 'SKILL.md').write_text((self.directory / 'SKILL.md').read_text() + 'Changed behavior.\n')
        result = self.checkpoint(completed=[], resume=previous)
        self.assertEqual(result['pending'], ['alpha'])
        self.assertEqual(result['invalidated'], ['alpha'])
        self.assertFalse(result['coverageComplete'])
        fresh = self.checkpoint(reviews=self.reviews())
        self.add_skill('future')
        result = self.checkpoint(completed=[], resume=fresh)
        self.assertIn('future', result['pending'])
        self.assertFalse(result['coverageComplete'])

    def test_resume_invalidates_new_candidates_tracking_and_repository_guidance(self):
        previous = self.checkpoint(reviews=self.reviews())
        changed_candidate = 'f' * 40
        result = self.checkpoint(completed=[], resume=previous, candidates={GROUP: changed_candidate})
        self.assertEqual(result['pending'], ['alpha'])
        (self.root / 'AGENTS.md').write_text('New repository review requirements.\n')
        result = self.checkpoint(completed=[], resume=previous)
        self.assertEqual(result['pending'], ['alpha'])
        self.assertIn('alpha', result['invalidated'])
        record = self.directory / 'UPSTREAM.md'
        record.write_text(record.read_text().replace('upstream `main`', 'upstream `release`'))
        result = self.checkpoint(completed=[], resume=previous, candidates={'github.com/example/library@branch:release': self.baseline})
        self.assertFalse(result['coverageComplete'])

    def test_legacy_checkpoint_cannot_be_reused_as_complete(self):
        with self.assertRaisesRegex(ValueError, 'Legacy'):
            self.checkpoint(completed=[], resume={'schema': 1, 'completed': ['alpha'], 'coverageComplete': True})

    def test_source_completion_is_tied_to_candidate_and_known_skills(self):
        wrong = self.reviews(candidate='f' * 40)
        self.assertFalse(self.checkpoint(reviews=wrong)['coverageComplete'])
        wrong = self.reviews()
        wrong[GROUP]['skills'] = ['unknown']
        with self.assertRaises(ValueError):
            self.checkpoint(reviews=wrong)

    def test_manifest_remains_the_authoritative_suite_mapping(self):
        manifest = self.root / 'pstack.json'
        manifest.write_text(json.dumps({'skills': [{'upstream': 'source-alpha', 'local': 'alpha', 'directory': 'skills/engineering/alpha'}]}))
        self.registry['sources'] = {'pstack': {'repository': REPOSITORY, 'manifest': 'pstack.json', 'skillRoot': 'pstack/skills'}}
        self.assertEqual(catalog.entries(self.root, self.registry)[0]['upstream'], 'pstack/skills/source-alpha')

    def test_resume_invalidates_required_writing_owner_and_support(self):
        self.registry['owners']['agentWriting'] = 'writing-for-agents'
        self.registry['contextOwners'] = ['agentWriting']
        self.assertFalse(catalog.validate(self.root, self.registry)['valid'])
        writing = self.add_skill('writing-for-agents', category='agents')
        self.assertTrue(catalog.validate(self.root, self.registry)['valid'])
        mechanics = writing / 'SKILL-MECHANICS.md'
        mechanics.write_text('Original skill mechanics.\n')
        for path in [writing / 'SKILL.md', mechanics]:
            with self.subTest(path=path.name):
                previous = self.checkpoint(reviews=self.reviews())
                path.write_text(path.read_text() + 'Changed governing writing rule.\n')
                result = self.checkpoint(completed=[], resume=previous)
                self.assertIn('alpha', result['pending'])
                self.assertIn('alpha', result['invalidated'])
                self.assertNotEqual(previous['contextFingerprint'], result['contextFingerprint'])

    def test_resume_invalidates_required_repository_guidance(self):
        self.registry['contextPaths'] = ['AGENTS.md', 'CLAUDE.md', 'CONTRIBUTING.md', 'docs/architecture.md', 'skills/agents/maintain-skills/references/ADAPTATION.md']
        for relative in self.registry['contextPaths']:
            with self.subTest(path=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('Original governing policy.\n')
                previous = self.checkpoint(reviews=self.reviews())
                path.write_text('Changed governing policy.\n')
                result = self.checkpoint(completed=[], resume=previous)
                self.assertIn('alpha', result['pending'])
                self.assertIn('alpha', result['invalidated'])
                self.assertNotEqual(previous['contextFingerprint'], result['contextFingerprint'])

    def test_resume_preserves_matching_evidence_and_isolates_unrelated_skill_changes(self):
        directory = self.add_skill('unrelated-local')
        previous = self.checkpoint(completed=['alpha', 'unrelated-local'], reviews=self.reviews())
        matching = self.checkpoint(completed=[], resume=previous)
        self.assertTrue(matching['coverageComplete'])
        self.assertEqual(matching['invalidated'], [])
        instruction = directory / 'SKILL.md'
        instruction.write_text(instruction.read_text() + 'Changed unrelated behavior.\n')
        result = self.checkpoint(completed=[], resume=previous)
        self.assertEqual(result['completed'], ['alpha'])
        self.assertEqual(result['pending'], ['unrelated-local'])
        self.assertEqual(result['invalidated'], ['unrelated-local'])
        self.assertEqual(previous['contextFingerprint'], result['contextFingerprint'])


    def test_resume_ignores_listings_unrelated_owners_and_catalog(self):
        self.registry['owners'] = {'agentWriting': 'writing-for-agents', 'behaviorTests': 'tdd'}
        self.registry['contextOwners'] = ['agentWriting']
        self.add_skill('writing-for-agents', category='agents')
        tdd = self.add_skill('tdd')
        (self.root / 'skills/README.md').write_text('Library listing.\n')

        def append(path):
            with path.open('a') as output:
                output.write('Changed text.\n')
        changes = [
            ('README.md', lambda: append(self.root / 'README.md')),
            ('skills/README.md', lambda: append(self.root / 'skills/README.md')),
            ('category README', lambda: append(self.directory.parent / 'README.md')),
            ('non-writing owner', lambda: append(tdd / 'SKILL.md')),
            ('catalog', lambda: self.registry.update(policy='Changed policy')),
        ]
        for label, change in changes:
            with self.subTest(change=label):
                previous = self.checkpoint(completed=['alpha', 'tdd', 'writing-for-agents'], reviews=self.reviews())
                change()
                result = self.checkpoint(completed=[], resume=previous)
                self.assertIn('alpha', result['completed'])
                self.assertNotIn('alpha', result['invalidated'])
                self.assertEqual(previous['contextFingerprint'], result['contextFingerprint'])

    def test_excluded_paths_filter_additions_and_shared_lines(self):
        self.definition['sharedRoot'] = '.'
        self.definition['excludedPaths'] = {'automations/benny': 'Dormant workflows', 'assets/': 'README images', 'skills/in-progress/draft': 'Held draft'}
        for path in ['automations/benny/run.md', 'assets/logo.png', 'assets-guide/notes.md', 'docs/guide.md', 'skills/in-progress/draft/SKILL.md', 'skills/in-progress/beta/SKILL.md']:
            target = self.upstream / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(path)
        self.commit('Add excluded and kept inputs')
        result = catalog.compare(self.root, self.registry, 'matt', self.upstream, self.revision())
        self.assertEqual(result['added'], ['skills/in-progress/beta'])
        self.assertIn({'path': 'skills/in-progress/draft', 'reason': 'Held draft'}, result['excluded'])
        shared = result['sharedInputs'][0]
        self.assertEqual([line.split('\t')[1] for line in shared['files']], ['assets-guide/notes.md', 'docs/guide.md'])
        self.assertEqual(shared['excludedFiles'], 2)

    def test_policy_shares_one_diff_from_its_review_position(self):
        identity = catalog.repository_identity(REPOSITORY)
        declaration = f'Canonical source: [source](https://{identity}).'
        plugin = f'Canonical source: [source](https://{identity}), [plugin](https://{identity}/tree/main/plugin).'
        (self.upstream / 'plugin').mkdir()
        (self.upstream / 'plugin/manifest.json').write_text('{}')
        (self.upstream / 'README.md').write_text('Reviewed overview')
        (self.upstream / 'skills/engineering/beta').mkdir()
        (self.upstream / 'skills/engineering/beta/SKILL.md').write_text('beta source')
        self.commit('Add plugin and beta')
        reviewed = self.revision()
        (self.upstream / 'LICENSE').write_text('changed license')
        (self.upstream / 'plugin/manifest.json').write_text('{"changed": true}')
        self.commit('Change shared inputs')
        record = self.directory / 'UPSTREAM.md'
        record.write_text(record.read_text().replace(declaration, plugin))
        beta = self.add_skill('beta', source=True)
        (beta / 'UPSTREAM.md').write_text(self.provenance('beta', baseline=reviewed).replace(declaration, plugin))
        records = catalog.inventory(self.root, self.registry)['sourceGroups'][GROUP]['records']
        self.assertEqual({record['local']: record['sharedPaths'] for record in records}, {'alpha': ['plugin'], 'beta': ['plugin']})
        self.definition['sharedReviewedThrough'] = reviewed
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.revision())
        policy = [entry for entry in result['sharedInputs'] if 'suite' in entry]
        self.assertEqual([(entry['suite'], entry['since'], entry['files']) for entry in policy], [('matt', reviewed, ['M\tLICENSE'])])
        # Only the uncovered record keeps its own declared plugin diff.
        self.assertEqual([entry for entry in result['sharedInputs'] if 'paths' in entry], [{'paths': ['plugin'], 'since': reviewed, 'files': ['M\tplugin/manifest.json']}])
        del self.definition['sharedReviewedThrough']
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.revision())
        self.assertEqual([entry['since'] for entry in result['sharedInputs'] if 'suite' in entry], [self.baseline])

    def test_source_without_policy_compares_only_listed_paths(self):
        self.registry['sources'] = {}
        (self.upstream / 'docs').mkdir()
        (self.upstream / 'docs/unrelated.md').write_text('unrelated')
        self.commit('Change unlisted files')
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, self.revision())
        self.assertEqual(result['sharedInputs'], [])
        self.assertNotIn('inventory', result)
        self.assertEqual(result['skills'][0]['status'], 'unchanged')

    def advance_alpha_then_overview(self):
        (self.upstream / 'skills/engineering/alpha/SKILL.md').write_text('reviewed change')
        self.commit('Change alpha')
        verified = self.revision()
        (self.upstream / 'README.md').write_text('later overview')
        self.commit('Change overview')
        return verified, self.revision()

    def test_resume_carries_verified_skill_and_shared_progress_forward(self):
        verified, candidate = self.advance_alpha_then_overview()
        previous = self.checkpoint(reviews=self.reviews(candidate=verified), candidates={GROUP: verified})
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, candidate, previous)
        alpha = result['skills'][0]
        self.assertEqual((alpha['status'], alpha['baseline'], alpha['since'], alpha['carriedForward']), ('unchanged', self.baseline, verified, True))
        self.assertEqual(result['resumedFrom'], verified)
        self.assertEqual((result['sharedInputs'][0]['since'], result['sharedInputs'][0]['files']), (verified, ['A\tREADME.md']))
        fresh = catalog.compare(self.root, self.registry, GROUP, self.upstream, candidate)
        self.assertEqual((fresh['skills'][0]['status'], fresh['skills'][0]['since'], fresh['skills'][0]['carriedForward']), ('changed', self.baseline, False))

    def test_resume_falls_back_without_matching_verified_progress(self):
        verified, candidate = self.advance_alpha_then_overview()
        review = self.reviews(candidate=verified)
        unverified = self.checkpoint(reviews={GROUP: {**review[GROUP], 'skills': [], 'sharedInputsReviewed': False}}, candidates={GROUP: verified})
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, candidate, unverified)
        self.assertEqual((result['skills'][0]['status'], result['skills'][0]['since'], result['skills'][0]['carriedForward']), ('changed', self.baseline, False))
        self.assertEqual((result['sharedInputs'][0]['since'], result['sharedInputs'][0]['carriedForward']), (self.baseline, False))
        unknown = self.checkpoint(reviews=self.reviews(candidate='f' * 40), candidates={GROUP: 'f' * 40})
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, candidate, unknown)
        self.assertIsNone(result['resumedFrom'])
        self.assertEqual(result['skills'][0]['since'], self.baseline)
        previous = self.checkpoint(reviews=review, candidates={GROUP: verified})
        instruction = self.directory / 'SKILL.md'
        instruction.write_text(instruction.read_text() + 'Local change after the checkpoint.\n')
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, candidate, previous)
        self.assertEqual((result['skills'][0]['since'], result['skills'][0]['carriedForward']), (self.baseline, False))
        self.assertEqual(result['sharedInputs'][0]['since'], verified)

    def test_resume_never_moves_a_baseline_backwards(self):
        verified, candidate = self.advance_alpha_then_overview()
        (self.directory / 'UPSTREAM.md').write_text(self.provenance(baseline=verified))
        older = self.checkpoint(reviews=self.reviews(), candidates={GROUP: self.baseline})
        result = catalog.compare(self.root, self.registry, GROUP, self.upstream, candidate, older)
        self.assertEqual((result['skills'][0]['since'], result['skills'][0]['carriedForward']), (verified, False))

    def test_fetch_keeps_one_canonical_blobless_clone_and_reports_new_candidates(self):
        subprocess.run(['git', '-C', str(self.upstream), 'config', 'uploadpack.allowFilter', 'true'], check=True)
        state = self.base / 'state'
        remotes = {'github.com/example/library': self.upstream.as_uri()}
        checkout = state / 'sources/github.com-example-library'
        self.assertEqual(catalog.fetch(self.root, self.registry, state, remotes), {'candidates': {GROUP: self.baseline}, 'checkouts': {GROUP: str(checkout)}, 'errors': {}})

        def config(*arguments):
            return subprocess.run(['git', '-C', str(checkout), 'config', *arguments], capture_output=True, text=True).stdout.strip()
        self.assertEqual(config('remote.origin.url'), REPOSITORY)
        self.assertEqual(config('remote.origin.partialclonefilter'), 'blob:none')
        self.assertNotIn('insteadof', config('--local', '--list').lower())
        (self.upstream / 'README.md').write_text('new candidate')
        self.commit('Advance source')
        second = catalog.fetch(self.root, self.registry, state, remotes)
        self.assertEqual(second['candidates'], {GROUP: self.revision()})
        result = catalog.compare(self.root, self.registry, GROUP, checkout, second['candidates'][GROUP])
        self.assertEqual(result['skills'][0]['status'], 'unchanged')
        self.assertEqual(result['sharedInputs'][0]['files'], ['A\tREADME.md'])

    def test_fetch_reports_a_broken_remote_without_aborting_other_sources(self):
        self.add_skill('beta', source=True, repository=OTHER)
        registry = self.base / 'catalog.json'
        registry.write_text(json.dumps(self.registry))
        state = self.base / 'state'
        command = [sys.executable, str(SCRIPT), '--catalog', str(registry), '--root', str(self.root), 'fetch', '--state', str(state), '--remote', 'github.com/example/library=' + self.upstream.as_uri(), '--remote', 'github.com/example/other=' + (self.base / 'missing').as_uri()]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        result = json.loads(completed.stdout)
        self.assertEqual(result['candidates'], {GROUP: self.baseline})
        self.assertEqual(list(result['errors']), [OTHER_GROUP])

    def test_inventory_reports_fidelity_backlog_and_changes_since_a_checkpoint(self):
        self.assertEqual(catalog.inventory(self.root, self.registry)['fidelityBacklog'], ['alpha'])
        record = self.directory / 'UPSTREAM.md'
        record.write_text(record.read_text().replace('License: MIT', f'Fidelity checked through: `{self.baseline}`\nLicense: MIT'))
        self.assertEqual(catalog.inventory(self.root, self.registry)['fidelityBacklog'], [])
        previous = self.checkpoint(reviews=self.reviews())
        self.assertNotIn('changedSince', catalog.inventory(self.root, self.registry))
        self.assertEqual(catalog.inventory(self.root, self.registry, previous)['changedSince'], [])
        self.add_skill('beta')
        instruction = self.directory / 'SKILL.md'
        instruction.write_text(instruction.read_text() + 'Changed behavior.\n')
        self.assertEqual(catalog.inventory(self.root, self.registry, previous)['changedSince'], ['alpha', 'beta'])

    def test_checkpoint_counts_unchanged_comparisons_as_reviewed(self):
        beta = self.upstream / 'skills/engineering/beta'
        beta.mkdir(parents=True)
        (beta / 'SKILL.md').write_text('beta source')
        self.commit('Add beta')
        added = self.revision()
        self.definition['skills'].append({'upstream': 'skills/engineering/beta', 'local': 'beta', 'directory': 'skills/engineering/beta'})
        (self.add_skill('beta', source=True) / 'UPSTREAM.md').write_text(self.provenance('beta', baseline=added))
        (self.upstream / 'skills/engineering/alpha/SKILL.md').write_text('changed source')
        self.commit('Change alpha')
        candidate = self.revision()
        report = catalog.compare(self.root, self.registry, GROUP, self.upstream, candidate)
        quiet = catalog.checkpoint(self.root, self.registry, {GROUP: candidate}, ['alpha', 'beta'], 1, True, None, None, [report])
        self.assertEqual(quiet['sourceCoverage'][GROUP]['skills'], ['beta'])
        self.assertEqual(quiet['sourceCoverage'][GROUP]['pending'], ['alpha'])
        self.assertTrue(quiet['sourceCoverage'][GROUP]['sharedInputsReviewed'])
        decided = {GROUP: {'candidate': candidate, 'skills': ['alpha'], 'inventoryReviewed': True, 'sharedInputsReviewed': True}}
        merged = catalog.checkpoint(self.root, self.registry, {GROUP: candidate}, ['alpha', 'beta'], 1, True, decided, None, [report])
        self.assertEqual(merged['sourceCoverage'][GROUP]['skills'], ['alpha', 'beta'])
        self.assertTrue(merged['coverageComplete'])
        with self.assertRaises(ValueError):
            catalog.checkpoint(self.root, self.registry, {GROUP: self.baseline}, ['alpha'], 1, True, None, None, [report])

    def test_integration_validation_carries_only_while_nothing_changed(self):
        validated = self.checkpoint(reviews=self.reviews())
        self.assertTrue(validated['integrationValidated'])
        quiet = self.checkpoint(reviews=self.reviews(), resume=validated, integrated=False)
        self.assertTrue(quiet['integrationValidated'])
        self.assertTrue(quiet['coverageComplete'])
        instruction = self.directory / 'SKILL.md'
        instruction.write_text(instruction.read_text() + 'Changed behavior.\n')
        changed = self.checkpoint(reviews=self.reviews(), resume=validated, integrated=False)
        self.assertFalse(changed['integrationValidated'])

    def test_compare_cli_runs_every_fetched_group(self):
        registry = self.base / 'catalog.json'
        registry.write_text(json.dumps(self.registry))
        fetched = self.base / 'fetch.json'
        fetched.write_text(json.dumps({'candidates': {GROUP: self.baseline}, 'checkouts': {GROUP: str(self.upstream)}, 'errors': {}}))
        saved = subprocess.run([sys.executable, str(SCRIPT), '--catalog', str(registry), '--root', str(self.root), 'inventory', '--output', str(self.base / 'reports/inventory.json')], capture_output=True, text=True)
        self.assertEqual(saved.returncode, 0, saved.stdout + saved.stderr)
        self.assertEqual(json.loads((self.base / 'reports/inventory.json').read_text())['repositorySkills'], 1)
        result = subprocess.run([sys.executable, str(SCRIPT), '--catalog', str(registry), '--root', str(self.root), 'compare', '--fetch', str(fetched), '--output-dir', str(self.base / 'reports')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(result.stdout)[GROUP]
        self.assertEqual(summary['skills'], {'unchanged': 1})
        self.assertFalse(summary['sharedChanged'])
        report = json.loads((self.base / 'reports/github.com-example-library-compare.json').read_text())
        self.assertEqual(report['candidate'], self.baseline)

    def test_checkpoint_cli_accepts_fetch_output_as_candidates(self):
        registry = self.base / 'catalog.json'
        registry.write_text(json.dumps(self.registry))
        fetched = self.base / 'fetch.json'
        fetched.write_text(json.dumps({'candidates': {GROUP: self.baseline}, 'checkouts': {}, 'errors': {}}))
        output = self.base / 'checkpoint.json'
        result = subprocess.run([sys.executable, str(SCRIPT), '--catalog', str(registry), '--root', str(self.root), 'checkpoint', '--candidates', str(fetched), '--completed', 'alpha', '--elapsed-minutes', '1', '--output', str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(output.read_text())['candidates'], {GROUP: self.baseline})

    def test_prune_keeps_newest_runs_and_stays_inside_runs(self):
        state = self.base / 'state'
        runs = state / 'runs'
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'keep.txt').write_text('outside')
        (state / 'sources/clone').mkdir(parents=True)
        for name in ['2026-10-18T080000Z-upstream', '2026-10-19T080000Z-upstream', '2026-10-20T080000Z-upstream']:
            (runs / name).mkdir(parents=True)
            (runs / name / 'checkpoint.json').write_text('{}')
        (runs / '2026-10-18T080000Z-upstream/linked').symlink_to(outside)
        (runs / '2026-10-17T080000Z-link').symlink_to(outside)
        (runs / '2026-10-16T080000Z-notes.txt').write_text('file')
        self.assertEqual(catalog.prune(state, 1), {'deleted': ['2026-10-18T080000Z-upstream', '2026-10-19T080000Z-upstream']})
        self.assertEqual(sorted(path.name for path in runs.iterdir()), ['2026-10-16T080000Z-notes.txt', '2026-10-17T080000Z-link', '2026-10-20T080000Z-upstream'])
        self.assertEqual((outside / 'keep.txt').read_text(), 'outside')
        self.assertTrue((state / 'sources/clone').is_dir())
        linked = self.base / 'linked-state'
        linked.mkdir()
        (linked / 'runs').symlink_to(runs)
        self.assertEqual(catalog.prune(linked, 0), {'deleted': []})
        self.assertTrue((runs / '2026-10-20T080000Z-upstream').is_dir())

class ActualLibraryCoverage(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[5]
        self.registry = json.loads((self.root / 'skills/agents/maintain-skills/catalog.json').read_text())
        self.inventory = catalog.inventory(self.root, self.registry)

    def test_every_actual_skill_and_source_family_is_accounted_for(self):
        self.assertTrue(self.inventory['valid'], self.inventory['problems'])
        actual_names = {path.parent.name for path in (self.root / 'skills').rglob('SKILL.md')}
        self.assertEqual(self.inventory['repositorySkills'], len(actual_names))
        self.assertEqual(self.inventory['mappedSkills'], len(catalog.entries(self.root, self.registry)))
        names = {item['name'] for item in self.inventory['skills']}
        self.assertEqual(names, actual_names)
        self.assertTrue({'thermos', 'thermo-nuclear-review', 'thermo-nuclear-code-quality-review', 'test-audit', 'audit-agent-documentation', 'linting-alignment', 'maintain-skills', 'update-dependencies'} <= names)
        mapped = {entry['local']: entry['source'] for entry in catalog.entries(self.root, self.registry)}
        self.assertEqual({mapped.get(name) for name in ['thermos', 'thermo-nuclear-review', 'thermo-nuclear-code-quality-review']}, {'thermos'})
        cursor = self.inventory['sourceGroups']['github.com/cursor/plugins@branch:main']
        self.assertIn('thermos', cursor['skills'])
        self.assertIn('pstack-mode', cursor['skills'])
        openclaw = self.inventory['sourceGroups']['github.com/openclaw/openclaw@branch:main']['records'][0]
        source_record = self.root / 'skills/reviews/test-audit/UPSTREAM.md'
        reviewed = re.search(r'Reviewed through: \[([0-9a-f]{40})\]', source_record.read_text())
        self.assertIsNotNone(reviewed)
        self.assertEqual(openclaw['baseline'], reviewed[1])
        self.assertIsNone(openclaw['imported'])
        self.assertTrue(openclaw['historicalImportUnknown'])
        for path in ['.agents/skills/test-audit', '.agents/skills/test-audit/CAMPAIGN.md', '.agents/skills/test-audit/references/audit.md', 'docs/help/testing/writing-tests.md', '.agents/skills/openclaw-testing', 'LICENSE']:
            self.assertIn(path, openclaw['paths'])

    def test_every_documented_shared_owner_governs_checkpoint_reuse(self):
        owners = set(self.registry['owners'].values())
        architecture = (self.root / 'docs/architecture.md').read_text()
        documented = set(re.findall(r'^\|[^|\n]+\| `/([a-z0-9-]+)` +\|$', architecture, re.MULTILINE))
        self.assertEqual(documented, owners)
        adaptation = (self.root / 'skills/agents/maintain-skills/references/ADAPTATION.md').read_text()
        self.assertEqual(set(re.findall(r'^- /([a-z0-9-]+) ', adaptation, re.MULTILINE)), owners)

    def test_mapped_only_coverage_is_incomplete_but_all_repository_skills_can_finish(self):
        groups = self.inventory['sourceGroups']
        candidates = {key: group['records'][0]['baseline'] for key, group in groups.items()}
        reviews = {key: {'candidate': candidates[key], 'skills': group['skills'], 'inventoryReviewed': True, 'sharedInputsReviewed': True} for key, group in groups.items()}
        mapped = [entry['local'] for entry in catalog.entries(self.root, self.registry)]
        all_names = [item['name'] for item in self.inventory['skills']]
        result = catalog.checkpoint(self.root, self.registry, candidates, mapped, 50, True, reviews)
        self.assertFalse(result['coverageComplete'])
        self.assertEqual(set(result['pending']), set(all_names) - set(mapped))
        self.assertNotIn('thermos', result['pending'])
        self.assertIn('test-audit', result['pending'])
        result = catalog.checkpoint(self.root, self.registry, candidates, all_names, 50, True, reviews)
        self.assertTrue(result['coverageComplete'], result['problems'])
        self.assertEqual(set(result['completed']), set(all_names))
        self.assertFalse(result['reviewComplete'])
        self.assertFalse(result['baselinesAdvancedByCheckpoint'])


if __name__ == '__main__':
    unittest.main()
