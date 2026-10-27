import importlib.util
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('target',Path(__file__).resolve().parents[1]/'target.py')
target=importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)

NOW=1_800_000_000
# Thresholds differ from the script's defaults, so a resolver that ignored them would fail.
CONFIG={'codexUsage':{'fastWhileLeft':50,'skipWhenLeft':10},'claude-code':{'review':{'providerInstanceId':'codex','model':'gpt-fixture','effort':{'full':'max','delta':'high'},'serviceTier':'priority'},'computerUse':{'model':'gpt-fixture','effort':{'routine':'medium','hard':'high'},'serviceTier':'priority'}}}


def event(used,resets=NOW+3600,reached=None,secondary=None,stamp='2026-10-24T21:00:00Z',bucket='codex'):
    limits={'limit_id':bucket,'primary':{'used_percent':used,'window_minutes':10080,'resets_at':resets},'secondary':secondary,'rate_limit_reached_type':reached}
    return json.dumps({'timestamp':stamp,'type':'event_msg','payload':{'type':'token_count','rate_limits':limits}},separators=(',',':'))


class TargetResolution(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.home=Path(self.directory.name)
        self.day=self.home/'sessions'/'2026'/'10'/'24'
        self.day.mkdir(parents=True)
        self.config=self.home/'config.json'
        self.config.write_text(json.dumps(CONFIG))

    def tearDown(self):
        self.directory.cleanup()

    def log(self,name,*lines,mtime=NOW,day=None):
        path=(day or self.day)/name
        path.write_text(''.join(line+'\n' for line in lines))
        os.utime(path,(mtime,mtime))

    def run_target(self,role,parent='claude-code'):
        stream=StringIO()
        with patch.dict(os.environ,{'PSTACK_CONFIG':str(self.config),'CODEX_HOME':str(self.home)}),patch.object(sys,'argv',['target.py','--parent',parent,role]),patch.object(target.time,'time',return_value=NOW),redirect_stdout(stream):
            self.assertEqual(target.main(),0)
        return json.loads(stream.getvalue())

    def test_defaults_fill_effort_and_take_the_codex_configured_model(self):
        self.config.write_text('{}')
        (self.home/'config.toml').write_text('model = "gpt-configured"\n\n[profiles.other]\nmodel = "gpt-other"\n')
        self.log('a.jsonl',event(10))
        for role,effort in {'review-full':'xhigh','review-delta':'high','computer-use':'medium','computer-use-hard':'high'}.items():
            result=self.run_target(role)
            self.assertEqual((result['run'],result['model'],result['effort'],result.get('serviceTier')),('codex','gpt-configured',effort,None),role)

    def test_configured_entry_wins_and_gpt_effort_is_capped_at_xhigh(self):
        self.log('a.jsonl',event(10))
        result=self.run_target('review-full')
        self.assertEqual((result['providerInstanceId'],result['model'],result['effort'],result['serviceTier']),('codex','gpt-fixture','xhigh','priority'))
        self.assertEqual(result['usage']['left'],90)

    def test_configured_thresholds_step_down_to_standard_speed_and_then_the_fallback(self):
        for used,run,tier in [(49,'codex','priority'),(51,'codex','default'),(91,'fallback',None)]:
            self.log('a.jsonl',event(used))
            result=self.run_target('computer-use')
            self.assertEqual((result['run'],result.get('serviceTier')),(run,tier),used)
        self.assertIn('9% left until',result['reason'])

    def test_spent_window_falls_back_until_it_resets_whatever_the_reached_flag_says(self):
        self.log('a.jsonl',event(100,reached='rate_limit_reached'))
        self.assertEqual(self.run_target('review-full')['run'],'fallback')
        self.log('a.jsonl',event(100,resets=NOW-1,reached='rate_limit_reached',secondary={'used_percent':20,'window_minutes':300,'resets_at':NOW+60}))
        result=self.run_target('review-full')
        self.assertEqual((result['serviceTier'],result['usage']['left']),('priority',80))

    def test_tightest_window_decides(self):
        self.log('a.jsonl',event(10,secondary={'used_percent':70,'window_minutes':300,'resets_at':NOW+60}))
        result=self.run_target('review-full')
        self.assertEqual((result['usage']['left'],result['serviceTier']),(30,'default'))

    def test_newest_snapshot_wins_across_logs_even_when_another_log_was_written_later(self):
        self.log('busy.jsonl',event(10,stamp='2026-10-24T20:00:00Z'),'{"type":"response_item","payload":{"output":"long tool result"}}',mtime=NOW)
        self.log('other.jsonl',event(96,stamp='2026-10-24T20:30:00Z'),mtime=NOW-60)
        self.assertEqual(self.run_target('review-full')['run'],'fallback')

    def test_tail_parsing_skips_broken_lines_other_buckets_and_unreadable_entries(self):
        older=self.home/'sessions'/'2026'/'10'/'23'
        older.mkdir()
        self.log('a.jsonl',event(20),'x'*target.TAIL_BYTES,event(80,stamp='2026-10-24T21:10:00Z'),event(1,stamp='2026-10-24T21:20:00Z',bucket='codex_other'),event(5)[:-10],day=older,mtime=NOW-10)
        (self.home/'sessions'/'2026'/'10'/'25').mkdir()
        (self.day/'folder.jsonl').mkdir()
        (self.day/'broken.jsonl').symlink_to(self.home/'missing.jsonl')
        os.mkfifo(self.day/'pipe.jsonl')
        self.assertEqual(self.run_target('review-full')['usage']['left'],20)

    def test_invalid_config_and_log_values_fall_back_to_defaults(self):
        self.config.write_text(json.dumps({'codexUsage':{'fastWhileLeft':'40','skipWhenLeft':None},'claude-code':{'review':{'model':7,'effort':{'full':['xhigh']}}}}))
        (self.home/'config.toml').write_text('model = "gpt-configured"\n')
        self.log('a.jsonl',event(62,resets='soon'))
        result=self.run_target('review-full')
        self.assertEqual((result['model'],result['effort'],result['serviceTier'],result['usage']['left']),('gpt-configured','xhigh','default',38))
        self.config.write_text(json.dumps({'codexUsage':{'fastWhileLeft':10**400}}))
        self.log('a.jsonl',event(62,resets=10**400))
        self.assertEqual(self.run_target('review-full')['usage']['left'],38)
        self.config.write_text('{not json')
        self.assertEqual(self.run_target('review-delta')['effort'],'high')

    def test_unknown_usage_keeps_the_configured_speed(self):
        result=self.run_target('review-full')
        self.assertEqual((result['run'],result['serviceTier']),('codex','priority'))
        self.assertIn('unknown',result['note'])

    def test_codex_parent_reviews_with_claude_without_a_speed_and_runs_computer_use_itself(self):
        self.config.write_text(json.dumps({'codex':{'review':{'model':'claude-fixture','serviceTier':'priority'}}}))
        self.log('a.jsonl',event(99))
        result=self.run_target('review-delta',parent='codex')
        self.assertEqual((result['run'],result['model'],result['effort']),('claude-code','claude-fixture','high'))
        self.assertNotIn('serviceTier',result)
        self.assertNotIn('usage',result)
        with redirect_stderr(StringIO()),self.assertRaises(SystemExit):
            self.run_target('computer-use',parent='codex')

    def test_native_roles_run_on_the_parent_host_with_fast_roles_on_its_fast_model(self):
        self.config.write_text('{}')
        self.log('a.jsonl',event(99))
        self.assertEqual(self.run_target('how-explorer'),{'role':'how-explorer','run':'claude-code','model':'sonnet'})
        self.assertEqual(self.run_target('swarm-workers')['model'],'sonnet')
        self.assertEqual(self.run_target('feature-refactoring'),{'role':'feature-refactoring','run':'claude-code'})
        self.assertEqual(self.run_target('how-explorer',parent='codex'),{'role':'how-explorer','run':'codex','serviceTier':'default'})

    def test_configured_native_role_wins_and_inherit_aliases_keep_the_parent_model(self):
        self.config.write_text(json.dumps({'claude-code':{'roles':{'how-explorer':{'model':'haiku','effort':'low'},'swarm-workers':{'model':'inherit-parent'},'hardest-tasks':{'effort':'max'}}},'codex':{'roles':{'why-investigators':{'model':'gpt-small','effort':'ultra'}}}}))
        self.assertEqual(self.run_target('how-explorer'),{'role':'how-explorer','run':'claude-code','model':'haiku','effort':'low'})
        self.assertEqual(self.run_target('swarm-workers'),{'role':'swarm-workers','run':'claude-code'})
        self.assertEqual(self.run_target('hardest-tasks'),{'role':'hardest-tasks','run':'claude-code','effort':'max'})
        self.assertEqual(self.run_target('why-investigators',parent='codex'),{'role':'why-investigators','run':'codex','model':'gpt-small','serviceTier':'priority','effort':'xhigh'})

    def test_codex_native_roles_run_fast_while_usage_allows_and_claude_never_does(self):
        for used,tier in [(49,'priority'),(51,'default')]:
            self.log('a.jsonl',event(used))
            self.assertEqual(self.run_target('swarm-workers',parent='codex')['serviceTier'],tier,used)
            self.assertNotIn('serviceTier',self.run_target('swarm-workers'))
        (self.day/'a.jsonl').unlink()
        self.assertEqual(self.run_target('bug-fix',parent='codex')['serviceTier'],'priority')

    def test_unusable_role_values_fall_back_to_the_role_default(self):
        self.config.write_text(json.dumps({'claude-code':{'roles':{'how-explorer':{'model':None,'effort':'auto'},'fast-code':{'model':7,'effort':'ultra'},'bug-fix':{'effort':'inherit-parent'}}}}))
        self.assertEqual(self.run_target('how-explorer'),{'role':'how-explorer','run':'claude-code','model':'sonnet'})
        self.assertEqual(self.run_target('fast-code'),{'role':'fast-code','run':'claude-code','model':'sonnet'})
        self.assertEqual(self.run_target('bug-fix'),{'role':'bug-fix','run':'claude-code'})


if __name__=='__main__':
    unittest.main()
