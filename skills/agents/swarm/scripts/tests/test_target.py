import importlib.util
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('target',Path(__file__).resolve().parents[1]/'target.py')
target=importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)

NOW=1_800_000_000
WEEK=7*24*3600
# Half the weekly window is still to run, so even pace leaves 50%.
MIDWEEK=NOW+WEEK//2
# The threshold differs from the script's default, so a resolver that ignored it would fail.
CONFIG={'codexUsage':{'skipWhenLeft':10},'claude-code':{'review':{'providerInstanceId':'codex','model':'gpt-fixture','effort':{'full':'max','delta':'high'},'serviceTier':'priority'},'computerUse':{'model':'gpt-fixture','effort':{'routine':'medium','hard':'high'},'serviceTier':'priority'}}}


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
        self.credits=None
        self.fetches=0

    def tearDown(self):
        self.directory.cleanup()

    def log(self,name,*lines,mtime=NOW,day=None):
        path=(day or self.day)/name
        path.write_text(''.join(line+'\n' for line in lines))
        os.utime(path,(mtime,mtime))

    def fetch(self):
        self.fetches+=1
        return self.credits

    def run_target(self,role,parent='claude-code',now=NOW):
        stream=StringIO()
        with patch.dict(os.environ,{'PSTACK_CONFIG':str(self.config),'CODEX_HOME':str(self.home),'XDG_CACHE_HOME':str(self.home/'cache')}),patch.object(sys,'argv',['target.py','--parent',parent,role]),patch.object(target.time,'time',return_value=now),patch.object(target,'fetch_reset_credits',self.fetch),redirect_stdout(stream):
            self.assertEqual(target.main(),0)
        return json.loads(stream.getvalue())

    def test_defaults_fill_effort_and_take_the_codex_configured_model(self):
        self.config.write_text('{}')
        (self.home/'config.toml').write_text('model = "gpt-configured"\n\n[profiles.other]\nmodel = "gpt-other"\n')
        self.log('a.jsonl',event(10))
        for role,effort in {'review-full':'xhigh','review-delta':'high','computer-use':'medium','computer-use-hard':'high'}.items():
            result=self.run_target(role)
            self.assertEqual((result['run'],result['model'],result['effort'],result.get('serviceTier')),('codex','gpt-configured',effort,'priority'),role)

    def test_configured_entry_wins_and_gpt_effort_is_capped_at_xhigh(self):
        self.log('a.jsonl',event(10))
        result=self.run_target('review-full')
        self.assertEqual((result['providerInstanceId'],result['model'],result['effort'],result['serviceTier']),('codex','gpt-fixture','xhigh','priority'))
        self.assertEqual(result['usage']['left'],90)

    def test_even_pace_steps_down_to_standard_speed_and_the_threshold_to_the_fallback(self):
        for used,resets,run,tier in [(49,MIDWEEK,'codex','priority'),(51,MIDWEEK,'codex','default'),(85,NOW+3600,'codex','priority'),(91,NOW+3600,'fallback',None)]:
            self.log('a.jsonl',event(used,resets=resets))
            result=self.run_target('computer-use')
            self.assertEqual((result['run'],result.get('serviceTier')),(run,tier),used)
        self.assertIn('9% left until',result['reason'])

    def test_behind_pace_note_names_the_window_and_the_banked_resets(self):
        self.credits=[]
        self.log('a.jsonl',event(60,resets=MIDWEEK))
        note=self.run_target('review-full')['note']
        self.assertIn('40% left until',note)
        self.assertIn('under the 50% even pace leaves; 0 banked resets',note)

    def test_banked_resets_keep_fast_mode_in_full_when_they_outlast_the_window_and_pro_rata_before(self):
        # 40% left at midweek is 10 points behind pace; a reset lapsing within a tenth of the time left covers them.
        self.log('a.jsonl',event(60,resets=MIDWEEK))
        for credits,tier in [([None],'priority'),([MIDWEEK+1],'priority'),([NOW+WEEK//20],'priority'),([NOW+WEEK//40],'default'),([NOW-1],'default')]:
            self.credits=credits
            result=self.run_target('review-full')
            (self.home/'cache'/'pstack'/'codex-reset-credits.json').unlink()
            self.assertEqual(result['serviceTier'],tier,credits)
        self.assertEqual(result['usage']['bankedResets'],0)
        self.credits=[None]
        self.assertIn('Banked resets keep fast mode',self.run_target('review-full')['note'])

    def test_unknown_banked_resets_leave_a_window_behind_pace_at_standard_speed(self):
        self.log('a.jsonl',event(60,resets=MIDWEEK))
        result=self.run_target('review-full')
        self.assertEqual(result['serviceTier'],'default')
        self.assertIn('banked resets unknown',result['note'])
        self.assertNotIn('bankedResets',result['usage'])

    def test_banked_resets_are_read_only_behind_pace_and_cached_for_an_hour(self):
        self.credits=[None]
        self.log('a.jsonl',event(10,resets=MIDWEEK))
        self.run_target('review-full')
        self.assertEqual(self.fetches,0)
        self.log('a.jsonl',event(60,resets=MIDWEEK))
        self.run_target('review-full')
        self.run_target('swarm-workers',parent='codex',now=NOW+target.RESETS_TTL-1)
        self.assertEqual(self.fetches,1)
        # A failed refresh reads as unknown for its hour instead of renewing the old reading.
        self.credits=None
        result=self.run_target('review-full',now=NOW+target.RESETS_TTL)
        self.assertEqual((self.fetches,result['serviceTier']),(2,'default'))
        self.run_target('review-full',now=NOW+target.RESETS_TTL+1)
        self.assertEqual(self.fetches,2)

    def test_banked_resets_are_cached_per_codex_account(self):
        self.credits=[None]
        self.log('a.jsonl',event(60,resets=MIDWEEK))
        (self.home/'auth.json').write_text(json.dumps({'tokens':{'account_id':'account-a'}}))
        self.assertEqual(self.run_target('review-full')['serviceTier'],'priority')
        self.credits=[]
        (self.home/'auth.json').write_text(json.dumps({'tokens':{'account_id':'account-b'}}))
        self.assertEqual(self.run_target('review-full')['serviceTier'],'default')
        self.assertEqual(self.fetches,2)

    def test_every_window_behind_pace_must_be_covered(self):
        # The reset outlasts the 5-hour window but lapses a tenth of the way to the weekly reset.
        self.credits=[NOW+WEEK//20]
        self.log('a.jsonl',event(70,resets=MIDWEEK,secondary={'used_percent':70,'window_minutes':300,'resets_at':NOW+9000}))
        self.assertEqual(self.run_target('review-full')['serviceTier'],'default')

    def test_spent_window_falls_back_until_it_resets_whatever_the_reached_flag_says(self):
        self.log('a.jsonl',event(100,reached='rate_limit_reached'))
        self.assertEqual(self.run_target('review-full')['run'],'fallback')
        self.log('a.jsonl',event(100,resets=NOW-1,reached='rate_limit_reached',secondary={'used_percent':20,'window_minutes':300,'resets_at':NOW+60}))
        result=self.run_target('review-full')
        self.assertEqual((result['serviceTier'],result['usage']['left']),('priority',80))

    def test_any_window_behind_pace_decides(self):
        self.log('a.jsonl',event(10,secondary={'used_percent':70,'window_minutes':300,'resets_at':NOW+9000}))
        result=self.run_target('review-full')
        self.assertEqual((result['usage']['left'],result['serviceTier']),(30,'default'))
        self.log('a.jsonl',event(10,secondary={'used_percent':70,'window_minutes':300,'resets_at':NOW+60}))
        self.assertEqual(self.run_target('review-full')['serviceTier'],'priority')

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
        self.config.write_text(json.dumps({'codexUsage':{'skipWhenLeft':'40'},'claude-code':{'review':{'model':7,'effort':{'full':['xhigh']}}}}))
        (self.home/'config.toml').write_text('model = "gpt-configured"\n')
        # Without a reset time, the window has no pace to fall behind.
        self.log('a.jsonl',event(62,resets='soon'))
        result=self.run_target('review-full')
        self.assertEqual((result['run'],result['model'],result['effort'],result['serviceTier'],result['usage']['left']),('codex','gpt-configured','xhigh','priority',38))
        self.config.write_text(json.dumps({'codexUsage':{'skipWhenLeft':10**400}}))
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

    def test_native_roles_run_on_the_parent_host_with_fast_code_on_its_fast_model(self):
        self.config.write_text('{}')
        self.log('a.jsonl',event(99))
        self.assertEqual(self.run_target('fast-code'),{'role':'fast-code','run':'claude-code','model':'sonnet'})
        for role in ('how-explorer','why-investigators','reflect-tooling','swarm-workers'):
            self.assertEqual(self.run_target(role),{'role':role,'run':'claude-code'},role)
        self.assertEqual(self.run_target('feature-refactoring'),{'role':'feature-refactoring','run':'claude-code'})
        self.log('a.jsonl',event(99,resets=MIDWEEK))
        self.assertEqual(self.run_target('how-explorer',parent='codex'),{'role':'how-explorer','run':'codex','serviceTier':'default'})

    def test_configured_native_role_wins_and_inherit_aliases_keep_the_parent_model(self):
        self.config.write_text(json.dumps({'claude-code':{'roles':{'how-explorer':{'model':'haiku','effort':'low'},'swarm-workers':{'model':'inherit-parent'},'hardest-tasks':{'effort':'max'}}},'codex':{'roles':{'why-investigators':{'model':'gpt-small','effort':'ultra'}}}}))
        self.assertEqual(self.run_target('how-explorer'),{'role':'how-explorer','run':'claude-code','model':'haiku','effort':'low'})
        self.assertEqual(self.run_target('swarm-workers'),{'role':'swarm-workers','run':'claude-code'})
        self.assertEqual(self.run_target('hardest-tasks'),{'role':'hardest-tasks','run':'claude-code','effort':'max'})
        self.assertEqual(self.run_target('why-investigators',parent='codex'),{'role':'why-investigators','run':'codex','model':'gpt-small','serviceTier':'priority','effort':'xhigh'})

    def test_codex_native_roles_run_fast_while_usage_allows_and_claude_never_does(self):
        for used,tier in [(49,'priority'),(51,'default')]:
            self.log('a.jsonl',event(used,resets=MIDWEEK))
            self.assertEqual(self.run_target('swarm-workers',parent='codex')['serviceTier'],tier,used)
            self.assertNotIn('serviceTier',self.run_target('swarm-workers'))
        (self.day/'a.jsonl').unlink()
        self.assertEqual(self.run_target('bug-fix',parent='codex')['serviceTier'],'priority')

    def test_unusable_role_values_fall_back_to_the_role_default(self):
        self.config.write_text(json.dumps({'claude-code':{'roles':{'how-explorer':{'model':None,'effort':'auto'},'fast-code':{'model':7,'effort':'ultra'},'bug-fix':{'effort':'inherit-parent'}}},'codex':{'roles':{'swarm-workers':{'serviceTier':'flex'}}}}))
        self.assertEqual(self.run_target('how-explorer'),{'role':'how-explorer','run':'claude-code'})
        self.assertEqual(self.run_target('fast-code'),{'role':'fast-code','run':'claude-code','model':'sonnet'})
        self.assertEqual(self.run_target('bug-fix'),{'role':'bug-fix','run':'claude-code'})
        self.assertEqual(self.run_target('swarm-workers',parent='codex')['serviceTier'],'priority')


FAKE_CODEX='''\
#!/usr/bin/env python3
import json, os, subprocess, sys, time
for line in sys.stdin:
    message = json.loads(line)
    if message.get('id') == 1:
        print(json.dumps({'id': 1, 'result': {}}), flush=True)
    elif message.get('id') == 2:
        if os.environ.get('FAKE_CODEX') == 'hang':
            time.sleep(30)
        if os.environ.get('FAKE_CODEX') == 'orphan':
            # A launcher's child keeps the reply pipe open after the launcher is killed.
            subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
            time.sleep(30)
        print('not json', flush=True)
        print(os.environ['FAKE_CODEX'], flush=True)
'''


class AppServerRead(unittest.TestCase):
    TIMEOUT=2

    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        codex=Path(self.directory.name)/'codex'
        codex.write_text(FAKE_CODEX)
        codex.chmod(codex.stat().st_mode|stat.S_IEXEC)

    def tearDown(self):
        self.directory.cleanup()

    def read(self,reply):
        payload=reply if isinstance(reply,str) else json.dumps({'id':2,'result':{'rateLimitResetCredits':reply}})
        with patch.dict(os.environ,{'PATH':f"{self.directory.name}:{os.environ['PATH']}",'FAKE_CODEX':payload}),patch.object(target,'RESETS_TIMEOUT',self.TIMEOUT):
            return target.fetch_reset_credits()

    def test_available_resets_return_their_expiry_times(self):
        credits=[{'status':'available','expiresAt':NOW},{'status':'redeemed','expiresAt':NOW},{'status':'available','expiresAt':None}]
        self.assertEqual(self.read({'availableCount':2,'credits':credits}),[NOW,None])

    def test_expiry_the_reply_does_not_state_reads_as_unknown(self):
        self.assertIsNone(self.read({'availableCount':2,'credits':None}))
        self.assertIsNone(self.read(None))
        self.assertIsNone(self.read({'availableCount':1,'credits':[{'status':'available','expiresAt':'2026-11-06T00:00:00Z'}]}))
        self.assertIsNone(self.read({'availableCount':1,'credits':[{'status':'available'}]}))
        self.assertEqual(self.read({'availableCount':0,'credits':None}),[])

    def test_errors_hangs_and_a_missing_cli_read_as_unknown(self):
        self.assertIsNone(self.read(json.dumps({'id':2,'error':{'message':'not signed in'}})))
        self.assertIsNone(self.read('hang'))
        started=time.monotonic()
        self.assertIsNone(self.read('orphan'))
        # Killing only the launcher leaves its child holding the pipe, so the read overruns the timeout.
        self.assertLess(time.monotonic()-started,self.TIMEOUT+0.5)
        with patch.dict(os.environ,{'PATH':self.directory.name+'/missing'}):
            self.assertIsNone(target.fetch_reset_credits())


if __name__=='__main__':
    unittest.main()
