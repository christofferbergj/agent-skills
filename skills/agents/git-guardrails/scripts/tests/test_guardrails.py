import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'block-dangerous-git.py'
spec = importlib.util.spec_from_file_location('guardrails', SCRIPT)
guardrails = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardrails)


class GitGuardrails(unittest.TestCase):
    def test_literal_dangerous_operations_include_git_options_and_shell_segments(self):
        for command in ['git push origin main', 'git -C /tmp/fixture push', 'git --no-pager push', 'git -c core.pager=cat push', 'git clean -df', 'git clean --force', 'git branch --delete --force feature', 'git branch -d -f feature', 'git branch -df feature', 'git reset --hard HEAD', 'git checkout -- .', 'git restore .', 'echo safe\ngit push', 'echo safe\n\ngit push', 'true && git push', 'env MODE=fixture git push', 'bash -c "git push origin main"', 'bash -lc "git push origin main"']:
            with self.subTest(command=command):
                self.assertIsNotNone(guardrails.denied(command))

    def test_quoted_mentions_and_read_only_git_commands_are_allowed(self):
        for command in ['echo "git push is denied"', 'git status --short', 'git -C /tmp/fixture diff --check', 'git clean -n', 'git branch --list', 'printf "%s" "git reset --hard"', 'git log --format="git push"']:
            with self.subTest(command=command):
                self.assertIsNone(guardrails.denied(command))

    def test_comments_keep_the_following_command_boundary(self):
        for command in ['echo safe # note\ngit push', '# note\ngit reset --hard', 'echo tag#value; git push', 'git pu\\\nsh', 'env -C /tmp git push', 'exec -a fixture git push']:
            with self.subTest(command=command):
                self.assertIsNotNone(guardrails.denied(command))

    def test_comment_text_and_quoted_hashes_are_not_executed(self):
        for command in ['echo safe # git push', 'echo "# git push"', 'echo "first\n# git push\nlast"', 'printf "%s" escaped\\#text', 'git log --format="# field"']:
            with self.subTest(command=command):
                self.assertIsNone(guardrails.denied(command))

    def test_both_hosts_receive_same_structured_denial_without_command_arguments(self):
        for host in ['codex', 'claude-code']:
            event={'session_id':'fixture','tool_name':'Bash','tool_input':{'command':'git push origin https://example.invalid/PRIVATE'}}
            result=subprocess.run(['python3',str(SCRIPT)],input=json.dumps(event),text=True,capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'],'deny')
            self.assertNotIn('PRIVATE',result.stdout+result.stderr)

    def test_malformed_input_fails_clearly_instead_of_allowing(self):
        for payload in ['not json', '[]', '{"tool_input":null}', '{"tool_input":{"command":[]}}']:
            result=subprocess.run(['python3',str(SCRIPT)],input=payload,text=True,capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'],'deny')


if __name__ == '__main__':
    unittest.main()
