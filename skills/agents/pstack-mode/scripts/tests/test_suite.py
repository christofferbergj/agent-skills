import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('suite',Path(__file__).resolve().parents[1]/'suite.py')
suite=importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)


class UpstreamReview(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.root=Path(self.temporary.name)
        self.source=self.root/'upstream'
        self.local=self.root/'local'
        self.local.mkdir()
        subprocess.run(['git','init','-q',str(self.source)],check=True)
        for name in ['a','b']:
            path=self.source/'pstack/skills'/name
            path.mkdir(parents=True)
            (path/'SKILL.md').write_text(name)
        (self.source/'pstack/LICENSE').write_text('fixture license')
        self.commit('Initial')
        self.baseline=self.revision()
        self.manifest={'upstreamRoot':'pstack','policy':'propose additions; preserve removals','skills':[{'upstream':n,'local':'pstack-'+n,'directory':'skills/pstack-'+n} for n in ['a','b']]}
        for entry in self.manifest['skills']:
            path=self.local/entry['directory']
            path.mkdir(parents=True)
            (path/'UPSTREAM.md').write_text('Reviewed through commit: `'+self.baseline+'`.\n')

    def tearDown(self):
        self.temporary.cleanup()

    def commit(self,message):
        subprocess.run(['git','-C',str(self.source),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.source),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm',message],check=True)

    def revision(self):
        return subprocess.check_output(['git','-C',str(self.source),'rev-parse','HEAD'],text=True).strip()

    def test_no_delta_does_not_claim_completed_review(self):
        result=suite.compare(self.local,self.source,self.baseline,self.manifest)
        self.assertEqual({s['status'] for s in result['skills']},{'unchanged'})
        self.assertFalse(result['reviewComplete'])

    def test_add_remove_change_and_license_inputs_are_discovered(self):
        (self.source/'pstack/skills/a/SKILL.md').write_text('changed behavior')
        (self.source/'pstack/skills/b/SKILL.md').unlink()
        (self.source/'pstack/skills/c').mkdir()
        (self.source/'pstack/skills/c/SKILL.md').write_text('new skill')
        (self.source/'pstack/LICENSE').write_text('changed fixture license')
        self.commit('Changes')
        result=suite.compare(self.local,self.source,self.revision(),self.manifest)
        self.assertEqual(result['added'],['c'])
        self.assertEqual(result['removed'],['b'])
        self.assertEqual([s['status'] for s in result['skills']],['changed','removed'])
        self.assertIn('pstack/LICENSE',' '.join(result['sharedInputs'][0]['files']))

    def test_partial_checkpoint_never_advances_source_baselines(self):
        before={p:p.read_bytes() for p in self.local.rglob('UPSTREAM.md')}
        result=suite.checkpoint(self.manifest,self.baseline,['pstack-a'],55)
        self.assertEqual(result['pending'],['pstack-b'])
        self.assertFalse(result['reviewComplete'])
        self.assertFalse(result['baselinesAdvancedByCheckpoint'])
        self.assertEqual(before,{p:p.read_bytes() for p in before})

    def test_unknown_completed_name_is_rejected(self):
        with self.assertRaises(ValueError):
            suite.checkpoint(self.manifest,self.baseline,['other'],55)


if __name__=='__main__':
    unittest.main()
