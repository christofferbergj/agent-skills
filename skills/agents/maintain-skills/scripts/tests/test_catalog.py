import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('catalog', Path(__file__).resolve().parents[1] / 'catalog.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CombinedCatalog(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / 'local'
        self.root.mkdir()
        self.upstream = self.base / 'matt'
        subprocess.run(['git', 'init', '-q', str(self.upstream)], check=True)
        initial = self.upstream / 'skills/engineering/alpha'
        initial.mkdir(parents=True)
        (initial / 'SKILL.md').write_text('initial source')
        (self.upstream / 'LICENSE').write_text('fixture MIT')
        self.commit('Initial')
        self.baseline = self.revision()
        self.directory = self.root / 'skills/engineering/alpha'
        (self.directory / 'agents').mkdir(parents=True)
        (self.directory / 'SKILL.md').write_text('---\nname: alpha\ndescription: Fixture behavior.\n---\nDo the fixture work.\n')
        (self.directory / 'agents/openai.yaml').write_text('interface:\n  display_name: Alpha\n')
        (self.directory / 'LICENSE').write_text('fixture MIT')
        (self.directory / 'UPSTREAM.md').write_text('Tracking policy: main\nImported from commit: `'+self.baseline+'`\nReviewed through commit: `'+self.baseline+'`\nLicense: MIT\nLocal adaptations: fixture\n')
        (self.root / 'README.md').write_text('[alpha](skills/engineering/alpha/SKILL.md)\n')
        (self.directory.parent / 'README.md').write_text('[alpha](alpha/SKILL.md)\n')
        self.definition = {'repository':'fixture','skillRoot':'skills','skills':[{'upstream':'skills/engineering/alpha','local':'alpha','directory':'skills/engineering/alpha'}],'excludedNames':{'teach':'User exclusion'},'excludedPathComponents':['personal'],'sharedPaths':['LICENSE','README.md']}
        self.registry = {'sources':{'matt':self.definition},'owners':{'domainArtifacts':'alpha'},'policy':'Preserve adaptations; review integration'}

    def tearDown(self):
        self.temporary.cleanup()

    def commit(self, title):
        subprocess.run(['git','-C',str(self.upstream),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.upstream),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm',title],check=True)

    def revision(self):
        return subprocess.check_output(['git','-C',str(self.upstream),'rev-parse','HEAD'],text=True).strip()

    def test_valid_packaging_and_callable_policy(self):
        self.assertTrue(catalog.validate(self.root,self.registry)['valid'])
        (self.directory/'agents/openai.yaml').write_text('policy:\n  allow_implicit_invocation: false\n')
        self.assertFalse(catalog.validate(self.root,self.registry)['valid'])

    def test_readme_listing_and_owned_reference_are_checked(self):
        (self.root/'README.md').write_text('alpha mentioned without an installable link\n')
        self.assertFalse(catalog.validate(self.root,self.registry)['valid'])
        (self.root/'README.md').write_text('[alpha](skills/engineering/alpha/SKILL.md)\n')
        (self.directory/'SKILL.md').write_text((self.directory/'SKILL.md').read_text()+'[foreign](../../../README.md)\n')
        self.assertFalse(catalog.validate(self.root,self.registry)['valid'])

    def test_inventory_finds_beta_additions_and_applies_all_exclusions(self):
        for path in ['skills/in-progress/beta','skills/productivity/teach','skills/personal/private']:
            directory=self.upstream/path;directory.mkdir(parents=True);(directory/'SKILL.md').write_text('candidate')
        self.commit('Add candidates')
        result=catalog.compare(self.root,self.registry,'matt',self.upstream,self.revision())
        self.assertEqual(result['added'],['skills/in-progress/beta'])
        self.assertEqual(len(result['excluded']),2)
        self.assertFalse(result['reviewComplete'])

    def test_removed_skill_stays_local_and_category_move_needs_review(self):
        moved=self.upstream/'skills/agents/alpha';moved.parent.mkdir(parents=True)
        (self.upstream/'skills/engineering/alpha').rename(moved)
        self.commit('Move category')
        result=catalog.compare(self.root,self.registry,'matt',self.upstream,self.revision())
        self.assertEqual(result['removed'],['skills/engineering/alpha'])
        self.assertEqual(result['possibleMoves'][0]['to'],'skills/agents/alpha')
        self.assertTrue((self.directory/'SKILL.md').exists())

    def test_changed_behavior_and_license_are_separate_review_inputs(self):
        (self.upstream/'skills/engineering/alpha/SKILL.md').write_text('changed behavior')
        (self.upstream/'LICENSE').write_text('changed license')
        self.commit('Change inputs')
        result=catalog.compare(self.root,self.registry,'matt',self.upstream,self.revision())
        self.assertEqual(result['skills'][0]['status'],'changed')
        self.assertIn('LICENSE',' '.join(result['sharedInputs'][0]['files']))

    def test_missing_baseline_is_blocked_instead_of_reset_to_head(self):
        (self.directory/'UPSTREAM.md').write_text('No reproducible baseline')
        result=catalog.compare(self.root,self.registry,'matt',self.upstream,self.baseline)
        self.assertEqual(result['skills'][0]['status'],'blocked')
        self.assertFalse(result['reviewComplete'])

    def test_shared_root_preserves_category_docs_shared_files_and_rename_endpoints(self):
        self.definition['sharedRoot'] = '.'
        category = self.upstream / 'skills/engineering/README.md'
        category.write_text('New category policy')
        (self.upstream / 'skills/shared-guidance.md').write_text('Shared behavior')
        source = self.upstream / 'skills/engineering/alpha/SKILL.md'
        source.rename(self.upstream / 'skills/moved-guidance.md')
        self.commit('Change shared inputs and move a file out of its owner')
        result = catalog.compare(self.root, self.registry, 'matt', self.upstream, self.revision())
        files = '\n'.join(result['sharedInputs'][0]['files'])
        for name in ['skills/engineering/README.md', 'skills/shared-guidance.md', 'skills/moved-guidance.md']:
            self.assertIn(name, files)
        self.assertEqual(result['skills'][0]['status'], 'removed')

    def test_checkpoint_never_writes_source_or_claims_integration_complete(self):
        before=(self.directory/'UPSTREAM.md').read_bytes()
        result=catalog.checkpoint(self.root,self.registry,{'matt':self.baseline},['alpha'],55,False)
        self.assertFalse(result['coverageComplete'])
        self.assertFalse(result['baselinesAdvancedByCheckpoint'])
        self.assertFalse(result['reviewComplete'])
        self.assertEqual((self.directory/'UPSTREAM.md').read_bytes(),before)
        result=catalog.checkpoint(self.root,self.registry,{'matt':self.baseline},['alpha'],55,True)
        self.assertTrue(result['coverageComplete'])
        self.assertFalse(result['reviewComplete'])

    def test_checkpoint_requires_each_source_and_known_skills(self):
        self.registry['sources']['pstack']={**self.definition,'skills':[]}
        with self.assertRaises(ValueError):catalog.checkpoint(self.root,self.registry,{'matt':self.baseline},[],10,False)
        with self.assertRaises(ValueError):catalog.checkpoint(self.root,self.registry,{'matt':self.baseline,'pstack':self.baseline},['unknown'],10,False)

    def test_pstack_manifest_has_one_authoritative_mapping(self):
        manifest=self.root/'pstack.json'
        manifest.write_text(json.dumps({'skills':[{'upstream':'source-alpha','local':'alpha','directory':'skills/engineering/alpha'}]}))
        self.registry['sources']={'pstack':{'manifest':'pstack.json','skillRoot':'pstack/skills'}}
        self.assertEqual(catalog.entries(self.root,self.registry)[0]['upstream'],'pstack/skills/source-alpha')


if __name__ == '__main__':
    unittest.main()
