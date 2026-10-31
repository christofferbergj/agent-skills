"""project.py on a project.md shaped like a real coordinator's: blank lines between some
decisions, a Result section, notes under the Workers table, and a learning that runs
into the Listening heading. Each edit changes only its own lines.
Run: python3 -m unittest discover -s skills/agents/coordinator/scripts/tests"""
import pathlib, subprocess, sys, tempfile, unittest
from datetime import date

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "project.py"
TODAY = date.today().isoformat()

PROJECT = """# ◆ audit

Coordinator: <t3-thread://v2/e/c> · Checkout: ~/skills

## Goal

Audit the suite.
Plan: ~/plan.md
Proof: five reports.
Follow-ups: none

## Result (interim, 2026-10-30)

Shipped: #149.

## Decisions

- 2026-10-29 · coordinator: pilot is teammate-reviews.

- 2026-10-30 · the user: "a" to "merge #202" → merged 31ddd00.

## Workers

| Worker | Proof | Thread | Branch or PR | State | Waits on | Last side effect |
|---|---|---|---|---|---|---|
| review (pilot) | a ranked report | <t3-thread://v2/e/r> · task t1 | — | done | — | report written |
| review-quality | — | <t3-thread://v2/e/q> · task t2 | — | running (slot 1) | — | launched |

Proofs:
- review: a ranked report.

## Learnings

- 2026-10-29 · review: comment substance is good.
Follow-ups from r3: delete the transition hooks.
## Listening

- Heartbeat: scheduled-task:hb
- Reminder: scheduled-task:ci (20:00, one-time)
- Watches: none
"""


class Project(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.dir = pathlib.Path(temporary.name)
        (self.dir / "project.md").write_text(PROJECT)

    def project(self, *args, code=0, stdin=None):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.dir), *args], capture_output=True, text=True,
                                input=stdin)
        self.assertEqual(result.returncode, code, result.stderr)
        return result

    def text(self):
        return (self.dir / "project.md").read_text()

    def test_a_decision_goes_after_the_last_one(self):
        self.project("decide", "R5 asked: may a verifier record without a checkout? → a · source: the user: \"a\"")
        self.assertEqual(self.text(), PROJECT.replace(
            "merged 31ddd00.\n", f"merged 31ddd00.\n- {TODAY} · R5 asked: may a verifier record without a checkout?"
                                 " → a · source: the user: \"a\"\n"))

    def test_a_learning_from_stdin_keeps_a_blank_line_before_listening(self):
        self.project("learn", "-", stdin="r5: `a | b` names verify-work/SKILL.md\nand wraps\n")
        self.assertEqual(self.text(), PROJECT.replace(
            "transition hooks.\n## Listening",
            f"transition hooks.\n- {TODAY} · r5: `a | b` names verify-work/SKILL.md\n  and wraps\n\n## Listening"))

    def test_a_worker_row_changes_only_the_named_columns(self):
        self.project("worker", "review-quality", "--state", "done: #12 MERGED", "--last", "merged a1b2c3d, 15:40")
        self.assertEqual(self.text(), PROJECT.replace(
            "| running (slot 1) | — | launched |", "| done: #12 MERGED | — | merged a1b2c3d, 15:40 |"))
        self.project("worker", "review", "--waits", "the user's go | merge")  # matches `review (pilot)`
        self.assertIn("| review (pilot) | a ranked report | <t3-thread://v2/e/r> · task t1 | — | done | the user's go \\| merge |",
                      self.text())

    def test_a_new_row_without_a_state_is_refused_as_a_likely_typo(self):
        result = self.project("worker", "review-qualty", "--last", "pushed abc", code=1)
        self.assertEqual(result.stderr, "no Workers row matches 'review-qualty': a new row needs --state\n")
        self.assertEqual(self.text(), PROJECT)

    def test_a_worker_name_with_a_pipe_is_refused_so_its_row_stays_editable(self):
        result = self.project("worker", "api (pilot | checks)", "--state", "queued", code=1)
        self.assertEqual(result.stderr, "a worker name holds no |: 'api (pilot | checks)'\n")
        self.assertEqual(self.text(), PROJECT)

    def test_an_edit_keeps_the_files_mode(self):
        (self.dir / "project.md").chmod(0o644)
        self.project("decide", "x")
        self.assertEqual((self.dir / "project.md").stat().st_mode & 0o777, 0o644)

    def test_a_new_worker_row_goes_under_the_table(self):
        self.project("worker", "r5", "--proof", "#14 MERGED", "--thread", "<t3-thread://v2/e/5> · task t5",
                     "--state", "queued", "--waits", "slot")
        self.assertIn("| launched |\n| r5 | #14 MERGED | <t3-thread://v2/e/5> · task t5 | — | queued | slot | — |\n\nProofs:",
                      self.text())

    def test_a_state_outside_the_vocabulary_is_refused(self):
        for state in ["blocked", "in progress", "doneish", "replaced by"]:
            with self.subTest(state=state):
                result = self.project("worker", "review", "--state", state, code=1)
                self.assertIn("doesn't start with one of: queued, overdue", result.stderr)
        self.assertEqual(self.text(), PROJECT)
        for state in ["replaced by r5", "waiting (no slot), retry 1", "absorbed into r4"]:
            self.project("worker", "review", "--state", state)

    def test_a_row_short_of_a_cell_is_refused(self):
        short = PROJECT.replace("| running (slot 1) | — | launched |", "| running (slot 1) | launched |")
        (self.dir / "project.md").write_text(short)
        result = self.project("worker", "review-quality", "--last", "pushed abc", code=1)
        self.assertEqual(result.stderr, "the 'review-quality' row has 6 cells and the header 7: fix it by hand\n")
        self.assertEqual(self.text(), short)

    def test_listen_replaces_its_line_or_adds_one(self):
        self.project("listen", "Watches", "#1 (owner a)\n#2 (owner b)", code=1)
        self.project("listen", "Heartbeat", "none")
        self.project("listen", "Startup", "scheduled-task:st")
        self.assertEqual(self.text(), PROJECT.replace("- Heartbeat: scheduled-task:hb", "- Heartbeat: none")
                         .replace("- Watches: none\n", "- Watches: none\n- Startup: scheduled-task:st\n"))

    def test_init_writes_a_skeleton_the_edits_work_on(self):
        init = ["init", "--project", "p", "--coordinator", "<t3-thread://v2/e/c>", "--checkout", "~/p",
                "--goal", "Ship it.", "--proof", "a merged PR"]
        self.project(*init, code=1)  # it never overwrites
        self.assertEqual(self.text(), PROJECT)
        self.dir = self.dir / "new" / "p"  # a first start names a folder that doesn't exist yet
        self.project(*init)
        self.project("decide", "first")
        self.project("learn", "first")
        self.project("worker", "a", "--state", "running")
        text = self.text()
        self.assertTrue(text.startswith("# ◆ p\n\nCoordinator: <t3-thread://v2/e/c> · Checkout: ~/p\n\n## Goal\n\nShip it.\nProof: a merged PR\n"))
        self.assertIn(f"## Decisions\n\n- {TODAY} · first\n\n## Workers", text)
        self.assertIn("|---|---|---|---|---|---|---|\n| a | — | — | — | running | — | — |\n\n## Learnings", text)
        self.assertIn(f"## Learnings\n\n- {TODAY} · first\n\n## Listening\n\n- Heartbeat: none\n", text)


if __name__ == "__main__":
    unittest.main()
