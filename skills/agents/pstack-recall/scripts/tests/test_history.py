import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('history',Path(__file__).resolve().parents[1]/'history.py')
history=importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)


class ScopedHistory(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.base=Path(self.temporary.name).resolve()
        self.repo=self.base/'selected repo'
        self.foreign=self.base/'foreign'
        for root in [self.repo,self.foreign]:
            root.mkdir()
            subprocess.run(['git','init','-q',str(root)],check=True)
        self.codex=self.base/'codex'
        self.claude=self.base/'claude'
        (self.codex/'sessions/2026/10/15').mkdir(parents=True)
        (self.claude/'projects').mkdir(parents=True)

    def tearDown(self):
        self.temporary.cleanup()

    def codex_session(self,name,cwd,rows=()):
        path=self.codex/'sessions/2026/10/15'/('rollout-'+name+'.jsonl')
        path.write_text('\n'.join(json.dumps(item) for item in [{'type':'session_meta','payload':{'cwd':str(cwd),'id':name}},*rows])+'\n')
        return path

    def message(self,text):
        return {'type':'response_item','payload':{'type':'message','role':'user','content':[{'type':'input_text','text':text}]}}

    def test_index_uses_both_hosts_but_never_includes_foreign_content(self):
        selected=self.codex_session('selected',self.repo,[self.message('selected')])
        self.codex_session('foreign',self.foreign,[self.message('FOREIGN PRIVATE TEXT')])
        directory=self.claude/'projects'/re.sub(r'[^a-zA-Z0-9]','-',str(self.repo))
        directory.mkdir()
        (directory/'conversation.jsonl').write_text(json.dumps({'type':'user','cwd':str(self.repo),'sessionId':'claude-selected','message':{'role':'user','content':'hello'}})+'\n')
        result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertEqual({s['host'] for s in result['sessions']},{'codex','claude-code'})
        self.assertNotIn('FOREIGN PRIVATE TEXT',json.dumps(result))
        self.assertNotIn(str(self.foreign),json.dumps(result))
        self.assertIn(str(selected),json.dumps(result))

    def test_claude_workflow_journal_is_not_a_coverage_gap(self):
        run=self.claude/'projects/project/session/subagents/workflows/run'
        run.mkdir(parents=True)
        (run/'journal.jsonl').write_text('\n'.join(json.dumps(item) for item in [{'type':'launched'},{'type':'started','agentId':'worker','key':'k','label':'l','phase':'p'}])+'\n')
        (run/'agent-worker.jsonl').write_text(json.dumps({'type':'user','cwd':str(self.repo),'sessionId':'worker','message':{'role':'user','content':'hello'}})+'\n')
        result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertTrue(result['coverage']['claude-code']['complete'])
        self.assertEqual([s['id'] for s in result['sessions']],['worker'])

    def test_foreign_read_is_rejected(self):
        path=self.codex_session('foreign',self.foreign,[self.message('PRIVATE')])
        with self.assertRaises(ValueError):
            history.read_session(path,self.repo,self.codex,self.claude,1000)

    def test_workspace_switch_excludes_foreign_turns_and_bounds_output(self):
        path=self.codex_session('selected',self.repo,[self.message('selected'),{'type':'turn_context','payload':{'cwd':str(self.foreign)}},self.message('PRIVATE'),{'type':'turn_context','payload':{'cwd':str(self.repo)}},self.message('123456789')])
        result=history.read_session(path,self.repo,self.codex,self.claude,12)
        text=''.join(m['text'] for m in result['messages'])
        self.assertNotIn('PRIVATE',text)
        self.assertEqual(len(text),12)
        self.assertTrue(result['truncated'])

    def test_subdirectory_is_scoped_but_nested_foreign_repository_is_not(self):
        directory=self.repo/'package'
        directory.mkdir()
        self.codex_session('package',directory)
        nested=self.repo/'nested'
        subprocess.run(['git','init','-q',str(nested)],check=True)
        self.codex_session('nested',nested)
        result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertEqual([s['id'] for s in result['sessions']],['package'])

    def test_unavailable_host_is_a_gap(self):
        result=history.index_history(self.repo,self.codex,self.base/'missing-claude',7)
        self.assertFalse(result['coverage']['claude-code']['complete'])

    def test_claude_subdirectory_and_hashed_project_names_use_metadata(self):
        package=self.repo/'package'
        package.mkdir()
        directory=self.claude/'projects/short-path-with-hash'
        directory.mkdir()
        path=directory/'conversation.jsonl'
        path.write_text(json.dumps({'type':'user','cwd':str(package),'sessionId':'nested','message':{'role':'user','content':'selected'}})+'\n')
        result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertEqual(result['sessions'][0]['id'],'nested')
        self.assertEqual(history.read_session(path,self.repo,self.codex,self.claude,100)['messages'][0]['text'],'selected')

    def test_malformed_records_report_incomplete_coverage(self):
        for payload in [[],None,{'type':'session_meta','payload':None}]:
            path=self.codex/'sessions/rollout-malformed.jsonl'
            path.write_text(json.dumps(payload)+'\n')
            result=history.index_history(self.repo,self.codex,self.claude,7)
            self.assertFalse(result['coverage']['codex']['complete'])
        selected=self.codex_session('selected',self.repo,[{'type':'response_item','payload':None}])
        with self.assertRaises(ValueError):
            history.read_session(selected,self.repo,self.codex,self.claude,100)

    def test_exact_character_limit_is_not_truncated_without_more_messages(self):
        path=self.codex_session('selected',self.repo,[self.message('12345')])
        self.assertFalse(history.read_session(path,self.repo,self.codex,self.claude,5)['truncated'])
        path=self.codex_session('selected',self.repo,[self.message('12345'),self.message('more')])
        self.assertTrue(history.read_session(path,self.repo,self.codex,self.claude,5)['truncated'])

    def test_linked_worktree_uses_canonical_repository_and_archived_sessions(self):
        subprocess.run(['git','-C',str(self.repo),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','Init'],check=True)
        linked=self.base/'linked'
        subprocess.run(['git','-C',str(self.repo),'worktree','add','-q','-b','linked',str(linked)],check=True)
        path=self.codex_session('archived',linked,[self.message('archived')])
        archived=self.codex/'archived_sessions'
        archived.mkdir()
        path=path.rename(archived/path.name)
        result=history.index_history(linked,self.codex,self.claude,7)
        self.assertEqual(result['repository'],str(self.repo))
        self.assertEqual(result['sessions'][0]['cwd'],str(linked))
        self.assertEqual(history.read_session(path,linked,self.codex,self.claude,100)['messages'][0]['text'],'archived')

    def test_index_tracks_workspace_switches_even_from_foreign_repository(self):
        subprocess.run(['git','-C',str(self.repo),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','--allow-empty','-qm','Init'],check=True)
        linked=self.base/'linked'
        subprocess.run(['git','-C',str(self.repo),'worktree','add','-q','-b','linked',str(linked)],check=True)
        path=self.codex_session('moving',self.foreign,[self.message('PRIVATE'),{'type':'turn_context','payload':{'cwd':str(self.repo)}},self.message('primary'),{'type':'turn_context','payload':{'cwd':str(linked)}},self.message('linked')])
        result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertEqual({s['cwd'] for s in result['sessions']},{str(self.repo),str(linked)})
        selected=history.read_session(path,self.repo,self.codex,self.claude,100)
        self.assertEqual([m['text'] for m in selected['messages']],['primary','linked'])

    def test_directory_permission_error_marks_coverage_incomplete(self):
        def unreadable(directory,onerror):
            onerror(PermissionError('fixture traversal denied'))
            yield
        with patch.object(history.os,'walk',side_effect=unreadable):
            result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertTrue(all(not value['complete'] for value in result['coverage'].values()))

    def test_deleted_subdirectory_is_a_coverage_gap(self):
        self.codex_session('deleted',self.repo/'no-longer-present')
        result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertFalse(result['coverage']['codex']['complete'])

    def test_removed_agent_worktree_counts_as_repository_activity(self):
        self.codex_session('agent',self.repo/'.claude/worktrees/agent-1/package')
        result=history.index_history(self.repo,self.codex,self.claude,7)
        self.assertTrue(result['coverage']['codex']['complete'])
        self.assertEqual([(s['id'],s['cwd']) for s in result['sessions']],[('agent',str(self.repo))])

    def test_trailing_repository_whitespace_is_preserved(self):
        root=self.base/'trailing repo '
        subprocess.run(['git','init','-q',str(root)],check=True)
        (root/'package').mkdir()
        self.codex_session('trailing',root/'package')
        result=history.index_history(root,self.codex,self.claude,7)
        self.assertEqual(result['sessions'][0]['cwd'],str(root))

    def test_explicit_invalid_workspace_and_malformed_text_are_rejected(self):
        for value in [None,'relative']:
            path=self.codex_session('invalid',self.repo,[{'type':'turn_context','payload':{'cwd':value}},self.message('must not leak')])
            with self.assertRaises(ValueError):
                history.read_session(path,self.repo,self.codex,self.claude,100)
        message=self.message('valid')
        message['payload']['content'][0]['text']=None
        path=self.codex_session('malformed-text',self.repo,[message])
        with self.assertRaises(ValueError):
            history.read_session(path,self.repo,self.codex,self.claude,100)

    def test_user_message_before_context_is_assigned_to_its_own_turn(self):
        start={'type':'event_msg','payload':{'type':'task_started'}}
        path=self.codex_session('turn-order',self.repo,[start,self.message('PRIVATE'),{'type':'turn_context','payload':{'cwd':str(self.foreign)}},start,self.message('selected'),{'type':'turn_context','payload':{'cwd':str(self.repo)}}])
        result=history.read_session(path,self.repo,self.codex,self.claude,100)
        self.assertEqual([m['text'] for m in result['messages']],['selected'])


if __name__=='__main__':
    unittest.main()
