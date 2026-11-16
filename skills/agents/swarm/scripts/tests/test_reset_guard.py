import importlib.util
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
spec=importlib.util.spec_from_file_location('reset_guard',SCRIPTS/'reset_guard.py')
guard=importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
Window,Credit=guard.Window,guard.target.Credit

NOW=1_800_000_000
HOUR=3600
DAY=24*HOUR
WEEK_ENDS=NOW+3*DAY
WEEK=[Window(60,WEEK_ENDS)]


def credit(id,expires,kind='codexRateLimits'):
    return Credit(id,kind,expires)


class Decide(unittest.TestCase):
    def test_no_credits_does_nothing(self):
        self.assertEqual(guard.decide(WEEK,[],NOW,frozenset()),guard.Decision((),None,frozenset()))

    def test_a_reset_that_outlasts_the_week_or_never_expires_is_never_redeemed(self):
        for expires in (WEEK_ENDS+HOUR,None):
            decision=guard.decide([Window(0,WEEK_ENDS)],[credit('a',expires)],NOW,frozenset())
            self.assertEqual((decision.notices,decision.redeem),((),None),expires)

    def test_a_lapsing_reset_with_plenty_left_gets_one_heads_up(self):
        lapsing=credit('a',NOW+DAY)
        decision=guard.decide(WEEK,[lapsing],NOW,frozenset())
        self.assertEqual((decision.notices,decision.redeem,decision.warned),((lapsing,),None,{'a'}))
        again=guard.decide(WEEK,[lapsing],NOW,decision.warned)
        self.assertEqual((again.notices,again.redeem,again.warned),((),None,{'a'}))

    def test_a_lapsing_reset_is_redeemed_at_the_fallback_threshold(self):
        lapsing=credit('a',NOW+DAY)
        self.assertEqual(guard.decide([Window(5,WEEK_ENDS)],[lapsing],NOW,frozenset()).redeem,lapsing)
        self.assertIsNone(guard.decide([Window(6,WEEK_ENDS)],[lapsing],NOW,frozenset()).redeem)
        self.assertEqual(guard.decide([Window(4,NOW+HOUR),Window(60,WEEK_ENDS)],[lapsing],NOW,frozenset()).redeem,lapsing)

    def test_a_lapsing_reset_is_redeemed_within_the_margin_even_with_plenty_left(self):
        for expires,redeemed in [(NOW+3*HOUR,True),(NOW+3*HOUR+60,False),(NOW-1,False)]:
            decision=guard.decide([Window(90,WEEK_ENDS)],[credit('a',expires)],NOW,frozenset())
            self.assertEqual(decision.redeem is not None,redeemed,expires)

    def test_only_the_earliest_of_two_lapsing_resets_is_redeemed(self):
        early,late=credit('early',NOW+2*DAY),credit('late',NOW+DAY//2)
        decision=guard.decide([Window(3,WEEK_ENDS)],[early,late],NOW,frozenset())
        self.assertEqual((decision.redeem,decision.notices,decision.warned),(late,(early,),{'early','late'}))

    def test_another_reset_type_is_ignored(self):
        decision=guard.decide([Window(0,WEEK_ENDS)],[credit('a',NOW+HOUR,kind='otherLimits')],NOW,frozenset())
        self.assertEqual((decision.notices,decision.redeem),((),None))

    def test_announced_ids_no_longer_available_are_forgotten(self):
        self.assertEqual(guard.decide(WEEK,[credit('kept',None)],NOW,frozenset({'gone','kept'})).warned,{'kept'})


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
        print(json.dumps({'id': message['id'], 'result': {'outcome': 'reset'}}), flush=True)
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

    def tearDown(self):
        self.directory.cleanup()

    def run_guard(self,reply,*extra):
        read=reply if isinstance(reply,str) else json.dumps({'id':'ID','result':reply})
        out,err=StringIO(),StringIO()
        env={'PATH':f"{self.dir}:{os.environ['PATH']}",'FAKE_READ':read,'FAKE_LOG':str(self.log)}
        with patch.dict(os.environ,env),patch.object(sys,'argv',['reset_guard.py','--state',str(self.state),*extra]),patch.object(guard.time,'time',return_value=NOW),redirect_stdout(out),redirect_stderr(err):
            code=guard.main()
        return code,out.getvalue(),err.getvalue()

    def consumed(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_redeem_sends_the_credit_id_and_a_stable_idempotency_key(self):
        code,out,_=self.run_guard(reading(96,NOW+DAY))
        self.assertEqual(code,0)
        self.assertEqual(self.consumed(),[{'creditId':'credit-1','idempotencyKey':'reset-guard:credit-1'}])
        self.assertEqual(out,f'Redeemed the banked Codex reset expiring {guard.target.moment(NOW+DAY)}: 4% was left of the window ending {guard.target.moment(WEEK_ENDS)}.\n')

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

    def test_a_credit_list_shorter_than_the_count_warns_and_carries_on(self):
        code,out,err=self.run_guard(reading(96,NOW+DAY,count=3))
        self.assertEqual(code,0)
        self.assertIn('Codex lists 1 of 3 banked resets',err)
        self.assertTrue(out.startswith('Redeemed'),out)

    def test_banked_resets_without_a_window_reset_time_exit_1(self):
        reply=reading(96,NOW+DAY)
        reply['rateLimits']['primary']['resetsAt']=None
        code,out,err=self.run_guard(reply)
        self.assertEqual((code,out,self.consumed()),(1,'',[]))
        self.assertIn('no usage window with a reset time',err)

    def test_the_heads_up_is_printed_once_across_runs(self):
        code,out,_=self.run_guard(reading(10,NOW+DAY))
        self.assertEqual(code,0)
        self.assertIn('Heads-up: a banked Codex reset expires',out)
        self.assertIn('redeemed automatically at 5% left or 3 h before it expires',out)
        self.assertEqual(json.loads(self.state.read_text()),{'announced':['credit-1']})
        self.assertEqual(self.run_guard(reading(10,NOW+DAY)),(0,'',''))
        self.assertEqual(self.consumed(),[])

    def test_nothing_to_do_prints_nothing(self):
        self.assertEqual(self.run_guard(reading(96,WEEK_ENDS+DAY)),(0,'',''))
        self.assertFalse(self.state.exists())


if __name__=='__main__':
    unittest.main()
