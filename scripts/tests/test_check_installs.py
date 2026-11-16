import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'check-installs.py'
SLUG = 'example/library'
OLD_TREE = '0' * 40

# Stands in for the Skills CLI in --json mode: it records each call, writes the
# requested skills' current trees into the lock, and prints a JSON report.
# Names under `lag` stay stale for that many calls, as GitHub can serve the
# previous tree. Names under `fail` are written to the lock but reported failed
# for that many calls, as the CLI does when one agent's target fails. With
# `text_exit`, it prints the failures as text and exits with that code instead.
FAKE_NPX = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys
    from pathlib import Path
    state_path = Path(os.environ['FAKE_NPX_STATE'])
    state = json.loads(state_path.read_text())
    args = sys.argv[1:]
    state['calls'].append(args)
    skills = args[args.index('--skill') + 1:args.index('--global')]
    lock_path = Path(state['lock'])
    lock = json.loads(lock_path.read_text())
    report = []
    for name, tree in state['trees'].items():
        if skills != ['*'] and name not in skills:
            continue
        if state['lag'].get(name, 0) > 0:
            state['lag'][name] -= 1
        else:
            lock['skills'][name] = {'source': state['slug'], 'skillFolderHash': tree}
        if state['fail'].get(name, 0) > 0:
            state['fail'][name] -= 1
            report.append({'name': name, 'status': 'failed', 'error': f'EACCES: permission denied, symlink {name}'})
        else:
            report.append({'name': name, 'status': 'installed'})
    lock_path.write_text(json.dumps(lock))
    state_path.write_text(json.dumps(state))
    failed = [entry for entry in report if entry['status'] == 'failed']
    if state['text_exit'] is not None:
        for entry in failed:
            print(f"Failed to install {entry['name']} for cursor: {entry['error']}")
        sys.exit(state['text_exit'])
    print(json.dumps(report))
    sys.exit(1 if failed else 0)
''')


def refresh(*skills):
    """The arguments of the install --refresh runs for these skills."""
    return [
        '-y', 'skills@latest', 'add', SLUG, '--skill', *skills,
        '--global', '--yes', '--agent', 'claude-code', 'codex', '--json',
    ]


class Refresh(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / 'repo'
        for name in ('alpha', 'beta'):
            folder = self.repo / 'skills' / 'tools' / name
            folder.mkdir(parents=True)
            (folder / 'SKILL.md').write_text(f'---\nname: {name}\n---\n')
            shared = self.base / 'shared' / name
            shared.mkdir(parents=True)
            (shared / 'SKILL.md').write_text('installed\n')
        (self.base / 'claude').mkdir()
        self.git('init', '-q')
        self.git('remote', 'add', 'origin', f'https://github.com/{SLUG}.git')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'skills')
        self.trees = {
            name: self.git('rev-parse', f'HEAD:skills/tools/{name}').strip() for name in ('alpha', 'beta')
        }

        self.bin = self.base / 'bin'
        self.bin.mkdir()
        npx = self.bin / 'npx'
        npx.write_text(FAKE_NPX)
        npx.chmod(0o755)
        self.lock = self.base / 'skill-lock.json'
        self.state = self.base / 'npx-state.json'
        self.env = {**os.environ, 'PATH': f'{self.bin}{os.pathsep}{os.environ["PATH"]}', 'FAKE_NPX_STATE': str(self.state)}
        # The real Skills CLI must never run here, since it writes into the real agent folders.
        self.assertEqual(shutil.which('npx', path=self.env['PATH']), str(npx))

    def tearDown(self):
        self.temporary.cleanup()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], stdout=subprocess.PIPE, text=True, check=True).stdout

    def install(self, hashes, lag=None, fail=None, text_exit=None, agents=('claude-code', 'codex')):
        skills = {name: {'source': SLUG, 'skillFolderHash': tree} for name, tree in hashes.items()}
        self.lock.write_text(json.dumps({'skills': skills, 'lastSelectedAgents': list(agents)}))
        self.state.write_text(json.dumps({
            'calls': [], 'lock': str(self.lock), 'slug': SLUG, 'trees': self.trees,
            'lag': lag or {}, 'fail': fail or {}, 'text_exit': text_exit,
        }))

    def run_check(self, *extra):
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT), '--ref', 'HEAD', '--retry-delay', '0',
                '--lock', str(self.lock), '--shared-skills', str(self.base / 'shared'),
                '--claude-skills', str(self.base / 'claude'), *extra,
            ],
            cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        return result.returncode, result.stdout

    def calls(self):
        return json.loads(self.state.read_text())['calls']

    def test_refresh_installs_then_retries_only_the_skills_still_stale(self):
        self.install({'alpha': OLD_TREE, 'beta': OLD_TREE}, lag={'beta': 1})
        code, output = self.run_check('--refresh')
        self.assertEqual(code, 0, output)
        self.assertIn('All 2 skills match HEAD.', output)
        self.assertEqual(self.calls(), [refresh('*'), refresh('beta')])

    def test_refresh_fails_when_a_skill_stays_stale_after_the_retry(self):
        self.install({'alpha': OLD_TREE, 'beta': OLD_TREE}, lag={'beta': 2})
        code, output = self.run_check('--refresh')
        self.assertEqual(code, 1)
        self.assertIn('stale    beta', output)
        self.assertNotIn('stale    alpha', output)
        self.assertEqual(len(self.calls()), 2)

    def test_refresh_retries_the_skills_the_install_reported_failed(self):
        self.install({'alpha': OLD_TREE, 'beta': OLD_TREE}, lag={'beta': 1}, fail={'alpha': 1})
        code, output = self.run_check('--refresh')
        self.assertEqual(code, 0, output)
        self.assertIn('alpha: EACCES: permission denied, symlink alpha', output)
        self.assertIn('All 2 skills match HEAD.', output)
        self.assertEqual(self.calls(), [refresh('*'), refresh('alpha', 'beta')])

    def test_refresh_fails_when_the_retry_reports_a_failure_too(self):
        self.install({'alpha': OLD_TREE, 'beta': OLD_TREE}, fail={'alpha': 2})
        code, output = self.run_check('--refresh')
        self.assertEqual(code, 1, output)
        self.assertIn('failed   alpha: EACCES: permission denied, symlink alpha', output)
        self.assertNotIn('skills match', output)
        self.assertEqual(self.calls(), [refresh('*'), refresh('alpha')])

    def test_refresh_fails_when_the_install_prints_no_report(self):
        for text_exit in (0, 1):
            with self.subTest(text_exit=text_exit):
                self.install({'alpha': OLD_TREE, 'beta': OLD_TREE}, fail={'alpha': 2}, text_exit=text_exit)
                code, output = self.run_check('--refresh')
                self.assertEqual(code, 1, output)
                self.assertIn('Failed to install alpha for cursor: EACCES', output)
                self.assertEqual(self.calls(), [refresh('*'), refresh('*')])

    def test_refresh_installs_nothing_when_every_skill_matches(self):
        self.install(self.trees)
        code, output = self.run_check('--refresh')
        self.assertEqual((code, self.calls()), (0, []), output)

    def test_refresh_without_recorded_agents_only_prints_the_install(self):
        self.install({'alpha': OLD_TREE, 'beta': self.trees['beta']}, agents=())
        code, output = self.run_check('--refresh')
        self.assertEqual((code, self.calls()), (1, []))
        self.assertIn('It asks for your agents', output)

    def test_the_plain_check_only_prints_the_install(self):
        self.install({'alpha': OLD_TREE, 'beta': self.trees['beta']})
        code, output = self.run_check()
        self.assertEqual((code, self.calls()), (1, []))
        self.assertIn(
            f"Refresh with: npx -y skills@latest add {SLUG} --skill '*' --global --yes --agent claude-code codex\n",
            output,
        )


if __name__ == '__main__':
    unittest.main()
