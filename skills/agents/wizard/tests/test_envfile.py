import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('envfile', ROOT / 'envfile.py')
envfile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(envfile)


class DotenvValues(unittest.TestCase):
    def test_literal_values_round_trip_through_node_and_preserve_following_record(self):
        values=['', ' spaces ', "it's literal", 'a"b', "both '\" quotes", 'slash\\', '$literal', 'first\nsecond', 'first\nsecond\n', 'hash#value', 'with`backtick', 'single\' and ` tick', 'literal\\nsequence']
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'.env'
            for value in values:
                with self.subTest(value=value):
                    path.write_text('SENTINEL=kept\n')
                    envfile.upsert(path,'FIXTURE',value)
                    command=['node','-e','process.loadEnvFile(process.argv[1]); process.stdout.write(JSON.stringify({value:process.env.FIXTURE,sentinel:process.env.SENTINEL}))',str(path)]
                    environment={k:v for k,v in os.environ.items() if k not in ['FIXTURE','SENTINEL']}
                    result=json.loads(subprocess.check_output(command,env=environment,text=True))
                    self.assertEqual(result,{'value':value,'sentinel':'kept'})
                    self.assertEqual([v for k,_,v in envfile.records(path.read_text()) if k=='FIXTURE'],[value])

    def test_multiline_upsert_removes_whole_previous_record_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'.env'
            path.write_text("# keep\nFIXTURE='first\nFAKE_KEY=inside\nlast'\nSENTINEL=kept\nFIXTURE=duplicate\n")
            envfile.upsert(path,'FIXTURE',"it's new")
            first=path.read_bytes()
            envfile.upsert(path,'FIXTURE',"it's new")
            self.assertEqual(path.read_bytes(),first)
            self.assertNotIn('FAKE_KEY',path.read_text())
            self.assertIn('# keep\nSENTINEL=kept\n',path.read_text())

    def test_rejected_value_or_existing_quoting_never_changes_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'.env'
            path.write_text('SENTINEL=kept\n')
            before=path.read_bytes()
            for value in ["all '\"` quotes\nwith#hash",'carriage\rreturn','zero\0byte']:
                with self.assertRaises(ValueError):envfile.upsert(path,'FIXTURE',value)
                self.assertEqual(path.read_bytes(),before)
            path.write_text("FIXTURE='it'\\''s invalid'\nSENTINEL=kept\n")
            before=path.read_bytes()
            with self.assertRaises(ValueError):envfile.upsert(path,'FIXTURE','new')
            self.assertEqual(path.read_bytes(),before)

    def test_creation_permissions_and_existing_symlink_mode_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'real.env';link=Path(directory)/'.env'
            envfile.upsert(target,'FIXTURE','first')
            self.assertEqual(stat.S_IMODE(target.stat().st_mode),0o600)
            target.chmod(0o640);link.symlink_to(target)
            envfile.upsert(link,'FIXTURE','second')
            self.assertTrue(link.is_symlink())
            self.assertEqual(stat.S_IMODE(target.stat().st_mode),0o640)

    def test_bash_library_uses_helper_without_printing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'.env'
            library=(ROOT/'template.sh').read_text().split('run_wizard() {',1)[0]
            script=Path(directory)/'fixture.sh'
            script.write_text(library+'\nwrite_env FIXTURE "it\'s literal"\n')
            environment={**os.environ,'ENV_FILE':str(path),'WIZARD_ENV_HELPER':str(ROOT/'envfile.py')}
            result=subprocess.run(['bash',str(script)],env=environment,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertNotIn("it's literal",result.stdout+result.stderr)
            self.assertEqual([v for k,_,v in envfile.records(path.read_text()) if k=='FIXTURE'],["it's literal"])


if __name__ == '__main__':
    unittest.main()
