import importlib.util
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'worktree-audit.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class WorktreeAudit(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.root=Path(self.temporary.name).resolve()
        self.repo=self.root/'repo with spaces'
        self.checkout=self.root/'worktree with spaces'
        subprocess.run(['git','init','-q',str(self.repo)],check=True)
        subprocess.run(['git','-C',str(self.repo),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','Init'],check=True)
        subprocess.run(['git','-C',str(self.repo),'worktree','add','-q','-b','fixture',str(self.checkout)],check=True)
        self.history={'repository':str(self.repo),'generatedAt':time.time(),'activityInspection':'workspace-metadata','days':7,'coverage':{h:{'complete':True} for h in ['codex','claude-code']},'sessions':[]}
        self.owners={'repository':str(self.repo),'generatedAt':time.time(),'worktrees':[{'path':str(self.checkout),'kind':'ordinary','active':False,'pinned':False,'shared':False}]}

    def tearDown(self):
        self.temporary.cleanup()

    def result(self,history=None,owners=None):
        report=audit.audit(self.repo,'HEAD',history,owners)
        return next(row for row in report['worktrees'] if row['path']==str(self.checkout))

    def test_unknown_ownership_or_history_never_produces_candidate(self):
        self.assertEqual(self.result()['bucket'],'hold')
        self.assertEqual(self.result(self.history)['bucket'],'hold')
        self.assertEqual(self.result(None,self.owners)['bucket'],'hold')

    def test_only_clean_inactive_contained_checkout_is_candidate(self):
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'candidate-for-final-inspection')
        (self.checkout/'valuable.txt').write_text('untracked work')
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')
        self.assertTrue((self.checkout/'valuable.txt').exists())

    def test_active_pinned_or_recent_history_is_held(self):
        for key in ['active','pinned','shared']:
            self.owners['worktrees'][0][key]=True
            self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')
            self.owners['worktrees'][0][key]=False
        import time
        self.history['sessions']=[{'cwd':str(self.checkout),'mtime':time.time()}]
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')

    def test_foreign_evidence_cannot_establish_ownership(self):
        self.owners['repository']=str(self.root/'other')
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')

    def test_stale_or_short_activity_window_and_stale_ownership_are_held(self):
        for key,value in [('days',1),('generatedAt',time.time()-1000),('generatedAt',time.time()+600)]:
            history={**self.history,key:value}
            self.assertEqual(self.result(history,self.owners)['bucket'],'hold')
        self.owners['generatedAt']=time.time()-1000
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')

    def test_ignored_private_files_are_preserved(self):
        subprocess.run(['git','-C',str(self.checkout),'config','core.excludesFile',str(self.root/'ignore')],check=True)
        (self.root/'ignore').write_text('.env\n')
        private=self.checkout/'.env'
        private.write_text('fixture only')
        row=self.result(self.history,self.owners)
        self.assertEqual(row['bucket'],'hold')
        self.assertTrue(any('ignored' in reason for reason in row['reasons']))
        self.assertTrue(private.exists())

    def test_primary_locked_missing_and_uncontained_checkouts_are_held(self):
        report=audit.audit(self.repo,'HEAD',self.history,self.owners)
        self.assertEqual(report['worktrees'][0]['bucket'],'hold')
        subprocess.run(['git','-C',str(self.repo),'worktree','lock',str(self.checkout)],check=True)
        self.assertIn('Git worktree is locked',self.result(self.history,self.owners)['reasons'])
        subprocess.run(['git','-C',str(self.repo),'worktree','unlock',str(self.checkout)],check=True)
        subprocess.run(['git','-C',str(self.checkout),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','Uncontained'],check=True)
        self.assertFalse(self.result(self.history,self.owners)['mergedIntoBase'])
        self.checkout.rename(self.root/'missing')
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')

    def test_non_object_evidence_is_rejected(self):
        with self.assertRaises(ValueError):
            audit.audit(self.repo,'HEAD',[],self.owners)

    def test_incomplete_activity_and_conflicting_ownership_are_held(self):
        missing={key:value for key,value in self.history.items() if key!='sessions'}
        self.assertEqual(self.result(missing,self.owners)['bucket'],'hold')
        owner=self.owners['worktrees'][0]
        self.owners['worktrees']=[{**owner,'active':True},owner]
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')

    def test_index_flags_and_unfinished_operations_are_held(self):
        tracked=self.checkout/'tracked.txt'
        tracked.write_text('original')
        subprocess.run(['git','-C',str(self.checkout),'add','tracked.txt'],check=True)
        subprocess.run(['git','-C',str(self.checkout),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Tracked'],check=True)
        subprocess.run(['git','-C',str(self.repo),'merge','--ff-only','-q','fixture'],check=True)
        for flag in ['--assume-unchanged','--skip-worktree']:
            subprocess.run(['git','-C',str(self.checkout),'update-index',flag,'tracked.txt'],check=True)
            self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')
            subprocess.run(['git','-C',str(self.checkout),'update-index',flag.replace('--','--no-',1),'tracked.txt'],check=True)
        administrative=Path(subprocess.check_output(['git','-C',str(self.checkout),'rev-parse','--absolute-git-dir'],text=True).strip())
        (administrative/'MERGE_HEAD').write_text('fixture')
        self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')

    def test_unusable_activity_timestamps_are_held(self):
        for stamp in [float('nan'),float('inf'),time.time()+600,-1]:
            self.history['sessions']=[{'cwd':str(self.checkout),'mtime':stamp}]
            self.assertEqual(self.result(self.history,self.owners)['bucket'],'hold')


if __name__=='__main__':
    unittest.main()
