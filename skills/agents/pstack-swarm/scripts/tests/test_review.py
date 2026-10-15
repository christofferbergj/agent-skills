import importlib.util
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('review',Path(__file__).resolve().parents[1]/'review.py')
review=importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewRestrictions(unittest.TestCase):
    def test_missing_other_cli_is_an_explicit_prerequisite(self):
        with patch.object(review.shutil,'which',return_value=None):
            vendor,command,reason=review.prepare('codex',Path('.'))
        self.assertEqual(vendor,'claude-code')
        self.assertIsNone(command)
        self.assertIn('not installed',reason)

    def test_claude_review_uses_read_tools_without_customizations(self):
        help_text='\n'.join(['--safe-mode', '--strict-mcp-config', '--tools', '--permission-mode', '--permission-prompts', '--mcp-config', '--no-session-persistence', '--output-format'])
        responses=[subprocess.CompletedProcess([],0,help_text,''),subprocess.CompletedProcess([],0,json.dumps({'loggedIn':True}),'')]
        with patch.object(review.shutil,'which',return_value='/fixture/claude'),patch.object(review,'run',side_effect=responses):
            vendor,command,reason=review.prepare('codex',Path('.'))
        self.assertIsNone(reason)
        self.assertEqual(command[command.index('--tools')+1],'Read,Glob,Grep')
        self.assertIn('--safe-mode',command)
        self.assertNotIn('--bare',command)
        self.assertNotIn('--dangerously-skip-permissions',command)

    def test_codex_review_disables_connectors_and_approvals(self):
        responses=[subprocess.CompletedProcess([],0,'--sandbox\n--ephemeral\n--output-last-message\n--strict-config',''),subprocess.CompletedProcess([],0,'logged in',''),subprocess.CompletedProcess([],0,'apps stable true\nplugins stable true\nhooks stable true\nbrowser_use stable true\ncomputer_use stable true','')]
        with patch.object(review.shutil,'which',return_value='/fixture/codex'),patch.object(review,'run',side_effect=responses):
            vendor,command,reason=review.prepare('claude-code',Path('.'))
        self.assertIsNone(reason)
        self.assertEqual(command[command.index('--sandbox')+1],'read-only')
        self.assertIn('mcp_servers={}',command)
        self.assertIn('features.plugins=false',command)
        self.assertIn('features.hooks=false',command)
        self.assertIn('approval_policy="never"',command)

    def test_unsupported_restriction_is_not_silently_dropped(self):
        with patch.object(review.shutil,'which',return_value='/fixture/claude'),patch.object(review,'run',return_value=subprocess.CompletedProcess([],0,'old CLI','')):
            _,command,reason=review.prepare('codex',Path('.'))
        self.assertIsNone(command)
        self.assertIn('required review restrictions',reason)

    def test_missing_codex_feature_control_requires_native_fallback(self):
        responses=[subprocess.CompletedProcess([],0,'--sandbox\n--ephemeral\n--output-last-message\n--strict-config',''),subprocess.CompletedProcess([],0,'logged in',''),subprocess.CompletedProcess([],0,'apps stable true\nplugins stable true','')]
        with patch.object(review.shutil,'which',return_value='/fixture/codex'),patch.object(review,'run',side_effect=responses):
            _,command,reason=review.prepare('claude-code',Path('.'))
        self.assertIsNone(command)
        self.assertIn('feature controls',reason)

    def test_non_posix_host_reports_unsupported_process_control(self):
        repo=Path('.')
        with patch.object(review.os,'name','nt'):
            _,command,reason=review.prepare('codex',repo)
        self.assertIsNone(command)
        self.assertIn('POSIX',reason)

    def invoke(self, parent, output, response):
        with tempfile.TemporaryDirectory() as directory:
            prompt=Path(directory)/'prompt.txt'
            prompt.write_text('Inspect the fixture')
            target=Path(directory)/'result.json'
            argv=['review.py','--parent',parent,'--repo',directory,'--prompt-file',str(prompt),'--output',str(target)]
            stream=StringIO()
            with patch.object(sys,'argv',argv),patch.object(review,'prepare',return_value=(output,['fixture'],None)),patch.object(review,'run',side_effect=response),redirect_stdout(stream):
                code=review.main()
            return code,json.loads(stream.getvalue()),json.loads(target.read_text())

    def test_claude_result_and_malformed_response_are_recorded(self):
        for payload,status in [({'result':'Evidence inspected','is_error':False},'completed'),([], 'unavailable'),({'result':[]},'unavailable')]:
            code,result,saved=self.invoke('codex','claude-code',[subprocess.CompletedProcess([],0,json.dumps(payload),'')])
            self.assertEqual(result['status'],status)
            self.assertEqual(saved,result)
            self.assertEqual(code,0 if status=='completed' else 2)

    def test_codex_final_report_and_failure_are_recorded(self):
        def completed(command,**kwargs):
            Path(command[command.index('--output-last-message')+1]).write_text('Independent report')
            return subprocess.CompletedProcess([],0,'','')
        code,result,_=self.invoke('claude-code','codex',completed)
        self.assertEqual(code,0)
        self.assertEqual(result['review'],'Independent report')
        code,result,_=self.invoke('claude-code','codex',[subprocess.CompletedProcess([],1,'','private diagnostic')])
        self.assertEqual(code,2)
        self.assertNotIn('private diagnostic',json.dumps(result))
        self.assertIsNone(result['review'])

    def test_missing_prompt_does_not_launch_cli_and_still_writes_status(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'result.json'
            argv=['review.py','--parent','codex','--repo',directory,'--output',str(target)]
            with patch.object(sys,'argv',argv),patch.object(review,'prepare') as prepare,redirect_stdout(StringIO()):
                self.assertEqual(review.main(),2)
            prepare.assert_not_called()
            self.assertEqual(json.loads(target.read_text())['status'],'unavailable')

    def test_timeout_is_bounded(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            review.run([sys.executable,'-c','import time; time.sleep(30)'],timeout=0.05)

    @unittest.skipUnless(os.name=='posix','Process-group behavior is POSIX-specific')
    def test_timeout_kills_descendant_in_reviewer_process_group(self):
        with tempfile.TemporaryDirectory() as directory:
            pidfile=Path(directory)/'child.pid'
            child='import time; time.sleep(30)'
            parent='import subprocess,sys,time; from pathlib import Path; child=subprocess.Popen([sys.executable,"-c",sys.argv[2]]); Path(sys.argv[1]).write_text(str(child.pid)); time.sleep(30)'
            with self.assertRaises(subprocess.TimeoutExpired):
                review.run([sys.executable,'-c',parent,str(pidfile),child],timeout=0.3)
            self.assertTrue(pidfile.exists())
            state=subprocess.run(['ps','-o','stat=','-p',pidfile.read_text()],capture_output=True,text=True).stdout.strip()
            self.assertTrue(not state or state.startswith('Z'),state)


if __name__=='__main__':
    unittest.main()
