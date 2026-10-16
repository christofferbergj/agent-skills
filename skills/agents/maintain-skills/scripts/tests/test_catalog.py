import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('catalog', Path(__file__).resolve().parents[1] / 'catalog.py')
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


class ActualLibraryCoverage(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[5]
        self.registry = json.loads((self.root / 'skills/agents/maintain-skills/catalog.json').read_text())
        self.inventory = catalog.inventory(self.root, self.registry)

    def test_every_actual_skill_and_source_family_is_accounted_for(self):
        self.assertTrue(self.inventory['valid'], self.inventory['problems'])
        self.assertEqual(self.inventory['repositorySkills'], 94)
        self.assertEqual(self.inventory['mappedSkills'], 86)
        self.assertEqual(len(self.inventory['sourceGroups']), 3)
        names = {item['name'] for item in self.inventory['skills']}
        self.assertTrue({'thermos', 'thermo-nuclear-review', 'thermo-nuclear-code-quality-review', 'test-audit', 'audit-agent-documentation', 'linting-alignment', 'maintain-skills', 'update-dependencies'} <= names)
        cursor = self.inventory['sourceGroups']['github.com/cursor/plugins@branch:main']
        self.assertIn('thermos', cursor['skills'])
        self.assertIn('pstack-mode', cursor['skills'])
        openclaw = self.inventory['sourceGroups']['github.com/openclaw/openclaw@branch:main']['records'][0]
        self.assertEqual(openclaw['baseline'], '71b5563397e95d67ad902f79a717559519010ac8')
        self.assertIsNone(openclaw['imported'])
        self.assertTrue(openclaw['historicalImportUnknown'])
        for path in ['.agents/skills/test-audit', '.agents/skills/test-audit/CAMPAIGN.md', '.agents/skills/test-audit/references/audit.md', 'docs/help/testing/writing-tests.md', '.agents/skills/openclaw-testing', 'LICENSE']:
            self.assertIn(path, openclaw['paths'])

    def test_old_eighty_six_skill_coverage_is_incomplete_but_all_ninety_four_can_finish(self):
        groups = self.inventory['sourceGroups']
        candidates = {key: group['records'][0]['baseline'] for key, group in groups.items()}
        reviews = {key: {'candidate': candidates[key], 'skills': group['skills'], 'inventoryReviewed': True, 'sharedInputsReviewed': True} for key, group in groups.items()}
        mapped = [entry['local'] for entry in catalog.entries(self.root, self.registry)]
        result = catalog.checkpoint(self.root, self.registry, candidates, mapped, 50, True, reviews)
        self.assertFalse(result['coverageComplete'])
        self.assertEqual(len(result['pending']), 8)
        self.assertIn('thermos', result['pending'])
        self.assertIn('test-audit', result['pending'])
        all_names = [item['name'] for item in self.inventory['skills']]
        result = catalog.checkpoint(self.root, self.registry, candidates, all_names, 50, True, reviews)
        self.assertTrue(result['coverageComplete'], result['problems'])
        self.assertEqual(len(result['completed']), 94)
        self.assertFalse(result['reviewComplete'])
        self.assertFalse(result['baselinesAdvancedByCheckpoint'])


if __name__ == '__main__':
    unittest.main()
