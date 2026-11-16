from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS))
import reset_guard as guard
Window,Credit=guard.Window,guard.target.Credit

NOW=1_800_000_000
HOUR=3600
DAY=24*HOUR
WEEK_ENDS=NOW+3*DAY
WEEK=Window(60,WEEK_ENDS)


def credit(id,expires):
    return Credit(id,'codexRateLimits',expires)


def limits(*windows):
    return {'rateLimits':{'primary':windows[0],'secondary':windows[1] if len(windows)>1 else None}}


class ParseWeek(unittest.TestCase):
    def test_the_week_is_the_day_long_window_that_resets_last(self):
        day,week={'usedPercent':96,'windowDurationMins':1440,'resetsAt':NOW+HOUR},{'usedPercent':40,'windowDurationMins':10080,'resetsAt':WEEK_ENDS}
        self.assertEqual(guard.parse_week(limits(day,week)),Window(60,WEEK_ENDS))
        self.assertEqual(guard.parse_week(limits(week,day)),Window(60,WEEK_ENDS))

    def test_a_short_window_or_one_without_a_reset_time_is_no_week(self):
        self.assertIsNone(guard.parse_week(limits({'usedPercent':40,'windowDurationMins':300,'resetsAt':WEEK_ENDS})))
        self.assertIsNone(guard.parse_week(limits({'usedPercent':40,'windowDurationMins':10080,'resetsAt':None})))
        self.assertIsNone(guard.parse_week({}))


class Decide(unittest.TestCase):
    def test_no_credits_does_nothing(self):
        self.assertEqual(guard.decide(WEEK,[],NOW,frozenset(),5,guard.MARGIN_HOURS),guard.Decision((),None))

    def test_a_reset_that_outlasts_the_week_is_never_redeemed(self):
        for expires in (WEEK_ENDS,WEEK_ENDS+HOUR):
            self.assertEqual(guard.decide(Window(0,WEEK_ENDS),[credit('a',expires)],NOW,frozenset(),5,guard.MARGIN_HOURS),guard.Decision((),None),expires)

    def test_a_lapsing_reset_with_plenty_left_gets_one_heads_up(self):
        lapsing=credit('a',NOW+DAY)
        self.assertEqual(guard.decide(WEEK,[lapsing],NOW,frozenset(),5,guard.MARGIN_HOURS),guard.Decision((lapsing,),None))
        self.assertEqual(guard.decide(WEEK,[lapsing],NOW,frozenset({'a'}),5,guard.MARGIN_HOURS),guard.Decision((),None))

    def test_a_lapsing_reset_is_redeemed_when_the_week_reaches_the_threshold(self):
        lapsing=credit('a',NOW+DAY)
        self.assertEqual(guard.decide(Window(5,WEEK_ENDS),[lapsing],NOW,frozenset(),5,guard.MARGIN_HOURS).redeem,lapsing)
        self.assertIsNone(guard.decide(Window(6,WEEK_ENDS),[lapsing],NOW,frozenset(),5,guard.MARGIN_HOURS).redeem)

    def test_a_lapsing_reset_is_redeemed_within_the_margin_even_with_plenty_left(self):
        for expires,redeemed in [(NOW+guard.MARGIN_HOURS*HOUR,True),(NOW+guard.MARGIN_HOURS*HOUR+60,False)]:
            decision=guard.decide(Window(90,WEEK_ENDS),[credit('a',expires)],NOW,frozenset(),5,guard.MARGIN_HOURS)
            self.assertEqual(decision.redeem is not None,redeemed,expires)

    def test_only_the_earliest_of_two_lapsing_resets_is_redeemed(self):
        early,late=credit('early',NOW+2*DAY),credit('late',NOW+DAY//2)
        self.assertEqual(guard.decide(Window(3,WEEK_ENDS),[early,late],NOW,frozenset(),5,guard.MARGIN_HOURS),guard.Decision((early,),late))


FAKE_CODEX='''\
#!/usr/bin/env python3
import json, os, sys
for line in sys.stdin:
    message = json.loads(line)
    if message.get('id') == 1:
        print(json.dumps({'id': 1, 'result': {}}), flush=True)
    elif message.get('method') == 'account/rateLimits/read':
        print(os.environ['FAKE_READ'].replace('"ID"', str(message['id'])), flush=True)
    elif message.get('method') == 'account/rateLimitResetCredit/consume':
        with open(os.environ['FAKE_LOG'], 'a') as log:
            log.write(json.dumps(message['params']) + '\\n')
        print(os.environ.get('FAKE_CONSUME', '{"id": "ID", "result": {"outcome": "reset"}}').replace('"ID"', str(message['id'])), flush=True)
'''


def row(expires,id='credit-1',**fields):
    return {'id':id,'resetType':'codexRateLimits','status':'available','grantedAt':NOW-DAY,'expiresAt':expires,**fields}


def reading(used,expires,rows=None,count=None):
    rows=[row(expires)] if rows is None else rows
    return {'rateLimits':{'limitId':'codex','primary':{'usedPercent':used,'windowDurationMins':10080,'resetsAt':WEEK_ENDS},'secondary':None},
            'rateLimitResetCredits':{'availableCount':len(rows) if count is None else count,'credits':rows}}


class Guard(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.dir=Path(self.directory.name)
        codex=self.dir/'codex'
        codex.write_text(FAKE_CODEX)
        codex.chmod(codex.stat().st_mode|stat.S_IEXEC)
        self.state=self.dir/'state'/'reset-guard.json'
        self.log=self.dir/'consumed.jsonl'
        self.config=self.dir/'config.json'

    def tearDown(self):
        self.directory.cleanup()

    def run_guard(self,reply,*extra,consume=None):
        read=reply if isinstance(reply,str) else json.dumps({'id':'ID','result':reply})
        out,err=StringIO(),StringIO()
        env={'PATH':f"{self.dir}:{os.environ['PATH']}",'FAKE_READ':read,'FAKE_LOG':str(self.log),'PSTACK_CONFIG':str(self.config)}
        if consume is not None:
            env['FAKE_CONSUME']=consume if isinstance(consume,str) else json.dumps({'id':'ID','result':consume})
        with patch.dict(os.environ,env),patch.object(sys,'argv',['reset_guard.py','--state',str(self.state),*extra]),patch.object(guard.time,'time',return_value=NOW),redirect_stdout(out),redirect_stderr(err):
            code=guard.main()
        return code,out.getvalue(),err.getvalue()

    def consumed(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_redeem_sends_the_credit_id_and_a_stable_idempotency_key(self):
        code,out,_=self.run_guard(reading(96,NOW+DAY))
        self.assertEqual(code,0)
        self.assertEqual(self.consumed(),[{'creditId':'credit-1','idempotencyKey':'reset-guard:credit-1'}])
        self.assertEqual(out,f'Redeemed the banked Codex reset expiring {guard.target.moment(NOW+DAY)}: 4% was left of the week ending {guard.target.moment(WEEK_ENDS)}.\n')

    def test_a_redeem_that_does_not_reset_codex_exits_1(self):
        for consume in ({'outcome':'noCredit'},{'outcome':'nothingToReset'},{'outcome':'cooldown_active'},{},json.dumps({'id':'ID','error':{'code':-32000,'message':'boom'}})):
            code,out,err=self.run_guard(reading(96,NOW+DAY),consume=consume)
            self.assertEqual((code,out),(1,''),consume)
            self.assertTrue(err.startswith('Could not redeem the banked Codex reset expiring'),err)
        self.assertEqual(len(self.consumed()),5)

    def test_a_failed_redeem_is_retried_and_only_heads_ups_are_remembered(self):
        reply=reading(96,None,[row(NOW+DAY),row(NOW+2*DAY,id='credit-2')])
        code,out,_=self.run_guard(reply,consume={'outcome':'noCredit'})
        self.assertEqual(code,1)
        self.assertTrue(out.startswith('Heads-up:'),out)
        code,out,_=self.run_guard(reply)
        self.assertEqual(code,0)
        self.assertTrue(out.startswith('Redeemed'),out)
        self.assertEqual([entry['creditId'] for entry in self.consumed()],['credit-1','credit-1'])
        self.assertEqual(json.loads(self.state.read_text()),{'announced':['credit-2']})

    def test_an_unwritable_state_file_still_redeems_then_exits_1(self):
        self.state.parent.mkdir()
        self.state.parent.chmod(0o500)
        code,out,err=self.run_guard(reading(96,None,[row(NOW+DAY),row(NOW+2*DAY,id='credit-2')]))
        self.assertEqual(code,1)
        self.assertEqual([entry['creditId'] for entry in self.consumed()],['credit-1'])
        self.assertIn('Redeemed the banked Codex reset',out)
        self.assertIn('Could not save the announced resets',err)

    def test_a_reset_already_redeemed_exits_0(self):
        code,out,err=self.run_guard(reading(96,NOW+DAY),consume={'outcome':'alreadyRedeemed'})
        self.assertEqual((code,err),(0,''))
        self.assertTrue(out.startswith('Codex had already redeemed the banked Codex reset expiring'),out)

    def test_dry_run_neither_redeems_nor_writes_state(self):
        code,out,_=self.run_guard(reading(96,NOW+DAY),'--dry-run')
        self.assertEqual((code,self.consumed(),self.state.exists()),(0,[],False))
        self.assertTrue(out.startswith('Dry run: would redeem the banked Codex reset expiring'),out)
        code,out,_=self.run_guard(reading(10,NOW+DAY),'--dry-run')
        self.assertTrue(out.startswith('Dry run: Heads-up:'),out)
        self.assertFalse(self.state.exists())

    def test_a_failed_or_unusable_read_exits_1(self):
        for reply in (json.dumps({'id':'ID','error':{'message':'not signed in'}}),{'rateLimitResetCredits':{'availableCount':2,'credits':None}}):
            code,out,err=self.run_guard(reply)
            self.assertEqual((code,out),(1,''),reply)
            self.assertTrue(err)
        self.assertEqual(self.consumed(),[])

    def test_a_reply_that_hides_a_resets_id_or_expiry_exits_1(self):
        expiry_missing={key:value for key,value in row(NOW+DAY).items() if key!='expiresAt'}
        missing_credits={'rateLimits':reading(96,NOW+DAY)['rateLimits']}
        for reply in (missing_credits,reading(96,None,[expiry_missing]),reading(96,None,[row(NOW+DAY,id=None)]),reading(96,None,[row('2026-11-17')])):
            code,out,err=self.run_guard(reply)
            self.assertEqual((code,out),(1,''),reply)
            self.assertIn("don't state each banked reset's id and expiry",err)
        self.assertEqual(self.consumed(),[])

    def test_used_expired_and_other_rows_are_ignored(self):
        rows=[row(NOW+HOUR,id='used',status='used'),row(NOW+HOUR,id='expired',status='expired'),row(NOW+HOUR,id='other',resetType='otherLimits'),row(NOW+DAY)]
        code,out,err=self.run_guard(reading(96,None,rows,count=2))
        self.assertEqual((code,err),(0,''))
        self.assertEqual([entry['creditId'] for entry in self.consumed()],['credit-1'])

    def test_a_credit_list_shorter_than_the_count_redeems_what_it_lists_then_exits_1(self):
        code,out,err=self.run_guard(reading(96,NOW+DAY,count=3))
        self.assertEqual(code,1)
        self.assertIn('Codex lists 1 of 3 banked resets',err)
        self.assertTrue(out.startswith('Redeemed'),out)

    def test_banked_resets_with_only_a_short_window_exit_1(self):
        reply=reading(98,NOW+DAY)
        reply['rateLimits']['primary']['windowDurationMins']=300
        code,out,err=self.run_guard(reply)
        self.assertEqual((code,out,self.consumed()),(1,'',[]))
        self.assertIn('no usage window a day or longer',err)

    def test_a_never_expiring_reset_with_only_a_short_window_is_quiet(self):
        reply=reading(98,None)
        reply['rateLimits']['primary']['windowDurationMins']=300
        self.assertEqual(self.run_guard(reply)[:2],(0,''))

    def test_banked_resets_without_a_window_reset_time_exit_1(self):
        reply=reading(96,NOW+DAY)
        reply['rateLimits']['primary']['resetsAt']=None
        code,out,err=self.run_guard(reply)
        self.assertEqual((code,out,self.consumed()),(1,'',[]))
        self.assertIn('no usage window a day or longer with a reset time',err)

    def test_the_heads_up_is_printed_once_across_runs(self):
        code,out,_=self.run_guard(reading(10,NOW+DAY))
        self.assertEqual(code,0)
        self.assertIn('Heads-up: a banked Codex reset expires',out)
        self.assertIn(f'redeemed automatically at 5% left or {guard.MARGIN_HOURS} h before it expires',out)
        self.assertEqual(json.loads(self.state.read_text()),{'announced':['credit-1']})
        self.assertEqual(self.run_guard(reading(10,NOW+DAY)),(0,'',''))
        self.assertEqual(self.consumed(),[])

    def test_the_threshold_defaults_to_the_configured_fallback_threshold(self):
        self.config.write_text(json.dumps({'codexUsage':{'skipWhenLeft':10}}))
        code,out,_=self.run_guard(reading(92,NOW+DAY))
        self.assertEqual((code,len(self.consumed())),(0,1))
        self.assertTrue(out.startswith('Redeemed the banked Codex reset'),out)

    def test_a_short_window_running_low_does_not_redeem(self):
        reply=reading(40,NOW+DAY)
        reply['rateLimits']['secondary']={'usedPercent':97,'windowDurationMins':300,'resetsAt':NOW+HOUR}
        code,out,_=self.run_guard(reply)
        self.assertEqual((code,self.consumed()),(0,[]))
        self.assertTrue(out.startswith('Heads-up:'),out)

    def test_a_reset_that_never_expires_has_expired_or_is_another_type_is_never_redeemed(self):
        rows=[row(None,id='never'),row(NOW-1,id='expired'),row(NOW+HOUR,id='other',resetType='otherLimits')]
        self.assertEqual(self.run_guard(reading(100,None,rows)),(0,'',''))
        self.assertEqual(self.consumed(),[])

    def test_announced_ids_no_longer_listed_are_forgotten(self):
        self.state.parent.mkdir()
        self.state.write_text(json.dumps({'announced':['gone','kept']}))
        self.assertEqual(self.run_guard(reading(10,None,[row(None,id='kept')])),(0,'',''))
        self.assertEqual(json.loads(self.state.read_text()),{'announced':['kept']})

    def test_nothing_to_do_prints_nothing(self):
        self.assertEqual(self.run_guard(reading(96,WEEK_ENDS+DAY)),(0,'',''))
        self.assertFalse(self.state.exists())


if __name__=='__main__':
    unittest.main()
