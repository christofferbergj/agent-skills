"""project.py on a project.md shaped like a real coordinator's: blank lines between some
decisions, a Result section, notes under the Workers table, and a learning that runs
into the Listening heading. Each edit changes only its own lines, and a phase end resets
only the phase's sections.
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


class Fixture:
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



class Project(Fixture, unittest.TestCase):
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



LISTENING = PROJECT[PROJECT.index("## Listening"):]
NEXT = ["--goal", "Fix what the audit found.", "--proof", "each finding merged"]


class Phase(Fixture, unittest.TestCase):
    def files(self):
        return sorted(p.name for p in self.dir.rglob("*") if p.is_file())

    def test_a_phase_archives_the_file_and_resets_only_the_phase(self):
        result = self.project("phase", "audit", "--result", "five reports", *NEXT)
        self.assertEqual(result.stdout, f"{self.dir}/phases/01-audit.md\n{self.dir}/project.md\n")
        self.assertEqual((self.dir / "phases/01-audit.md").read_bytes(), PROJECT.encode())
        self.assertEqual(self.text(), PROJECT[:PROJECT.index("## Goal")] + f"""## Goal

Fix what the audit found.
Proof: each finding merged
Follow-ups: none

## Phases

- {TODAY} · 01-audit: five reports · phases/01-audit.md

## Decisions

## Workers

| Worker | Proof | Thread | Branch or PR | State | Waits on | Last side effect |
|---|---|---|---|---|---|---|
| review-quality | — | <t3-thread://v2/e/q> · task t2 | — | running (slot 1) | — | launched |

Proofs:
- review: a ranked report.

## Learnings

""" + LISTENING)

    def test_a_parked_project_starts_again_and_numbers_the_next_archive(self):
        self.project("start", *NEXT, code=1)  # its phase is running
        self.project("phase", "audit", "--result", "five reports", "--park", "until the user asks")
        parked = self.text()
        self.assertIn(f"## Goal\n\nParked {TODAY}: until the user asks\nFollow-ups: none\n\n## Phases\n", parked)
        self.assertEqual(self.project("phase", "fixes", "--result", "r", *NEXT, code=1).stderr,
                         "the project is parked: start its next phase with start\n")
        self.assertEqual((self.text(), self.files()), (parked, ["01-audit.md", "project.md"]))
        self.project("start", *NEXT)
        self.assertIn("## Goal\n\nFix what the audit found.\nProof: each finding merged\nFollow-ups: none\n\n",
                      self.text())
        started = self.text().encode()
        self.project("phase", "fixes", "--result", "all merged", "--park", "done for now")
        self.assertEqual((self.dir / "phases/02-fixes.md").read_bytes(), started)
        self.assertIn(f"## Phases\n\n- {TODAY} · 01-audit: five reports · phases/01-audit.md\n"
                      f"- {TODAY} · 02-fixes: all merged · phases/02-fixes.md\n\n## Decisions", self.text())

    def test_a_retry_after_a_failed_write_reuses_its_archive(self):
        self.project("phase", "audit", "--result", "five reports", *NEXT)
        (self.dir / "project.md").write_text(PROJECT)  # as if the project.md write had failed
        self.project("phase", "audit", "--result", "five reports", *NEXT)
        self.assertEqual(self.files(), ["01-audit.md", "project.md"])
        self.assertIn("· 01-audit: five reports · phases/01-audit.md\n\n## Decisions", self.text())

    def test_a_repeated_phase_end_is_refused_without_a_second_archive(self):
        self.project("phase", "audit", "--result", "five reports", *NEXT)
        ended = self.text()
        self.assertEqual(self.project("phase", "audit", "--result", "five reports", *NEXT, code=1).stderr,
                         "phase 'audit' already ended with this goal: the project is in its next phase\n")
        self.assertEqual((self.text(), self.files()), (ended, ["01-audit.md", "project.md"]))

    def test_follow_ups_unknown_sections_and_unreadable_rows_carry(self):
        real = (PROJECT.replace("Follow-ups: none\n", "Follow-ups:\n- lockfile risk\n  wraps here\n\n- stray rows\n"
                                "* starred\n1. numbered\nunindented tail\n\n"
                                "### Milestones done\n\n- G1–G6\n")
                .replace("| done | — | report written |", "| done | report written |")
                .replace("## Learnings", "## Queue (cards for the user)\n\n- c1\n\n## Learnings"))
        (self.dir / "project.md").write_text(real)
        ended = self.project("phase", "audit", "--result", "five reports", "--park", "p")
        self.assertIn("kept 1 Workers rows whose cells don't match the header, so their State is unread:"
                      " review (pilot).", ended.stderr)
        self.assertIn(f"## Goal\n\nParked {TODAY}: p\nFollow-ups:\n- lockfile risk\n  wraps here\n\n- stray rows\n"
                      "* starred\n1. numbered\nunindented tail\n\n"
                      "## Phases\n", self.text())
        self.assertIn("| review (pilot) | a ranked report | <t3-thread://v2/e/r> · task t1 | — | done | report written |\n", self.text())
        self.assertIn("## Queue (cards for the user)\n\n- c1\n\n## Learnings\n\n## Listening", self.text())

    def test_a_delivery_line_carries_through_park_and_start(self):
        delivery = "Delivery: one-pr · integration feat/x from main@abc1234 · integrator integrate"
        (self.dir / "project.md").write_text(PROJECT.replace("Proof: five reports.\n", f"Proof: five reports.\n{delivery}\n"))
        self.project("phase", "audit", "--result", "five reports", "--park", "until the PR merges")
        self.assertIn(f"## Goal\n\nParked {TODAY}: until the PR merges\n{delivery}\nFollow-ups: none\n\n", self.text())
        self.project("start", *NEXT)
        self.assertIn(f"## Goal\n\nFix what the audit found.\nProof: each finding merged\n{delivery}\nFollow-ups: none\n\n",
                      self.text())

    def test_a_proof_inside_follow_ups_leaves_a_parked_project_parked(self):
        (self.dir / "project.md").write_text(PROJECT.replace("Follow-ups: none\n", "Follow-ups:\n- report\nProof: report received\n"))
        self.project("phase", "audit", "--result", "five reports", "--park", "later")
        self.project("phase", "again", "--result", "r", "--park", "later", code=1)
        self.project("start", *NEXT)

    def test_a_running_goal_that_starts_with_parked_is_running(self):
        self.project("phase", "audit", "--result", "five reports", "--goal", "Parked work is ready.", "--proof", "p")
        self.project("start", *NEXT, code=1)
        self.project("phase", "review", "--result", "r", "--park", "later")

    def test_an_archive_is_no_wider_than_its_source(self):
        (self.dir / "project.md").chmod(0o600)
        self.project("phase", "audit", "--result", "five reports", *NEXT)
        self.assertEqual((self.dir / "phases/01-audit.md").stat().st_mode & 0o777, 0o600)

    def test_a_reused_archive_narrows_to_its_source(self):
        (self.dir / "phases").mkdir()
        (self.dir / "phases/01-audit.md").write_text(PROJECT)
        (self.dir / "phases/01-audit.md").chmod(0o644)
        (self.dir / "project.md").chmod(0o600)
        self.project("phase", "audit", "--result", "five reports", *NEXT)
        self.assertEqual((self.dir / "phases/01-audit.md").stat().st_mode & 0o777, 0o600)

    def test_a_refused_phase_leaves_every_file_untouched(self):
        for args, code in [(["Bad_Slug", "--result", "r", *NEXT], 1),
                           (["audit", "--result", "two\nlines", *NEXT], 1),
                           (["audit", "--result", "ok\r## Listening", *NEXT], 1),
                           (["audit", "--result", "r", "--goal", "g", "--proof", "a\nb"], 1),
                           (["audit", "--result", "r", "--park", "p", "--goal", "g"], 2),
                           (["audit", "--result", "r", "--goal", "g"], 2),
                           (["audit", "--result", "r", "--proof", "p", "--park", "x"], 2)]:
            with self.subTest(args=args):
                self.project("phase", *args, code=code)
                self.assertEqual((self.text(), self.files()), (PROJECT, ["project.md"]))


if __name__ == "__main__":
    unittest.main()
