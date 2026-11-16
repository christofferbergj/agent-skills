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

# Stands in for the Skills CLI: it records each call and writes the requested
# skills' current trees into the lock, except names listed under `lag`, which
# stay stale for that many calls, as GitHub can serve the previous tree.
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
    for name, tree in state['trees'].items():
        if skills != ['*'] and name not in skills:
            continue
        if state['lag'].get(name, 0) > 0:
            state['lag'][name] -= 1
            continue
        lock['skills'][name] = {'source': state['slug'], 'skillFolderHash': tree}
    lock_path.write_text(json.dumps(lock))
    state_path.write_text(json.dumps(state))
''')


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

    def install(self, hashes, lag=None, agents=('claude-code', 'codex')):
        skills = {name: {'source': SLUG, 'skillFolderHash': tree} for name, tree in hashes.items()}
        self.lock.write_text(json.dumps({'skills': skills, 'lastSelectedAgents': list(agents)}))
        self.state.write_text(json.dumps({
            'calls': [], 'lock': str(self.lock), 'slug': SLUG, 'trees': self.trees, 'lag': lag or {},
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
        agents = ['--global', '--yes', '--agent', 'claude-code', 'codex']
        self.assertEqual(self.calls(), [
            ['-y', 'skills@latest', 'add', SLUG, '--skill', '*', *agents],
            ['-y', 'skills@latest', 'add', SLUG, '--skill', 'beta', *agents],
        ])

    def test_refresh_fails_when_a_skill_stays_stale_after_the_retry(self):
        self.install({'alpha': OLD_TREE, 'beta': OLD_TREE}, lag={'beta': 2})
        code, output = self.run_check('--refresh')
        self.assertEqual(code, 1)
        self.assertIn('stale    beta', output)
        self.assertNotIn('stale    alpha', output)
        self.assertEqual(len(self.calls()), 2)

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
            f"Refresh with: npx -y skills@latest add {SLUG} --skill '*' --global --yes --agent claude-code codex",
            output,
        )


if __name__ == '__main__':
    unittest.main()
