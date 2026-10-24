import importlib.util
from contextlib import redirect_stdout
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
CONFIG={'codexUsage':{'fastWhileLeft':40,'skipWhenLeft':5},'claude-code':{'review':{'providerInstanceId':'codex','model':'gpt-fixture','effort':{'full':'max','delta':'high'},'serviceTier':'priority'},'computerUse':{'model':'gpt-fixture','effort':{'routine':'medium','hard':'high'},'serviceTier':'priority'}}}


def event(used,resets=NOW+3600,reached=None,secondary=None):
    limits={'limit_id':'codex','primary':{'used_percent':used,'window_minutes':10080,'resets_at':resets},'secondary':secondary,'rate_limit_reached_type':reached}
    return json.dumps({'timestamp':'2026-10-24T21:32:47Z','type':'event_msg','payload':{'type':'token_count','rate_limits':limits}})


class TargetResolution(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.home=Path(self.directory.name)
        self.day=self.home/'sessions'/'2026'/'10'/'24'
        self.day.mkdir(parents=True)

    def tearDown(self):
        self.directory.cleanup()

    def log(self,name,*lines,mtime=NOW):
        path=self.day/name
        path.write_text(''.join(line+'\n' for line in lines))
        os.utime(path,(mtime,mtime))

    def test_defaults_fill_effort_and_take_the_codex_configured_model(self):
        (self.home/'config.toml').write_text('model = "gpt-configured"\n\n[profiles.other]\nmodel = "gpt-other"\n')
        self.log('a.jsonl',event(10))
        expected={'review-full':'xhigh','review-delta':'high','computer-use':'medium','computer-use-hard':'high'}
        for role,effort in expected.items():
            result=target.resolve('claude-code',role,{},self.home,NOW)
            self.assertEqual((result['run'],result['model'],result['effort'],result['serviceTier']),('codex','gpt-configured',effort,None),role)

    def test_configured_entry_wins_and_gpt_effort_is_capped_at_xhigh(self):
        self.log('a.jsonl',event(10))
        result=target.resolve('claude-code','review-full',CONFIG,self.home,NOW)
        self.assertEqual((result['providerInstanceId'],result['model'],result['effort'],result['serviceTier']),('codex','gpt-fixture','xhigh','priority'))
        self.assertEqual(result['usage']['left'],90)

    def test_low_usage_drops_to_standard_speed_and_then_to_the_fallback(self):
        for used,run,tier in [(59,'codex','priority'),(61,'codex','default'),(96,'fallback',None)]:
            self.log('a.jsonl',event(used))
            result=target.resolve('claude-code','computer-use',CONFIG,self.home,NOW)
            self.assertEqual((result['run'],result.get('serviceTier')),(run,tier),used)
        self.assertIn('4% left until',result['reason'])

    def test_reached_limit_falls_back_and_a_passed_reset_counts_as_fresh(self):
        self.log('a.jsonl',event(20,reached='primary'))
        self.assertEqual(target.resolve('claude-code','review-full',CONFIG,self.home,NOW)['run'],'fallback')
        self.log('a.jsonl',event(99,resets=NOW-1))
        result=target.resolve('claude-code','review-full',CONFIG,self.home,NOW)
        self.assertEqual((result['serviceTier'],result['usage']['left']),('priority',100))

    def test_tightest_window_decides(self):
        self.log('a.jsonl',event(10,secondary={'used_percent':70,'window_minutes':300,'resets_at':NOW+60}))
        result=target.resolve('claude-code','review-full',CONFIG,self.home,NOW)
        self.assertEqual((result['usage']['left'],result['serviceTier']),(30,'default'))

    def test_newest_log_with_usage_is_read_from_its_tail(self):
        self.log('newest.jsonl','{"type":"session_meta"}',mtime=NOW)
        self.log('middle.jsonl',event(50),'x'*target.TAIL,event(80),'{"type":"response_item"}',event(5)[:-10],mtime=NOW-10)
        self.log('oldest.jsonl',event(1),mtime=NOW-20)
        self.assertEqual(target.resolve('claude-code','review-full',CONFIG,self.home,NOW)['usage']['left'],20)

    def test_unknown_usage_keeps_the_configured_speed(self):
        result=target.resolve('claude-code','review-full',CONFIG,self.home/'missing',NOW)
        self.assertEqual((result['run'],result['serviceTier']),('codex','priority'))
        self.assertIn('unknown',result['note'])

    def test_codex_parent_reviews_with_claude_and_keeps_computer_use(self):
        result=target.resolve('codex','review-delta',{'codex':{'review':{'model':'claude-fixture'}}},self.home,NOW)
        self.assertEqual((result['run'],result['model'],result['effort']),('claude-code','claude-fixture','high'))
        self.assertNotIn('usage',result)
        self.assertEqual(target.resolve('codex','computer-use',{},self.home,NOW)['run'],'self')

    def test_main_tolerates_a_broken_config_and_prints_one_json_object(self):
        config=self.home/'config.json'
        config.write_text('{not json')
        stream=StringIO()
        with patch.dict(os.environ,{'PSTACK_CONFIG':str(config),'CODEX_HOME':str(self.home)}),patch.object(sys,'argv',['target.py','--parent','claude-code','review-delta']),redirect_stdout(stream):
            self.assertEqual(target.main(),0)
        result=json.loads(stream.getvalue())
        self.assertEqual((result['run'],result['effort']),('codex','high'))
        self.assertNotIn('serviceTier',result)


if __name__=='__main__':
    unittest.main()
