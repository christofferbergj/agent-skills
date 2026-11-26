"""assistant.py scan against fake Executor, gh, and t3 commands that serve recorded-shape
fixtures (fakes.py, fixtures/world.json) and record each call. No test reaches a live
source. The rules under test are references/scan.md's: which change wakes the thread and
when, a sent batch that stays frozen until delivered, one retry, and a unit that fails
after two undelivered wakes or three failed scans of a source.
Run: python3 -m unittest discover -s skills/agents/org-assistant/scripts/tests"""
from __future__ import annotations

import copy
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE.parent / "assistant.py"
WORLD = json.loads((HERE / "fixtures" / "world.json").read_text())
THU = "2026-11-26"  # a Thursday; Danish time is UTC+1 in November

PROFILE = """org = "acme"
name = "Acme"
timezone = "Europe/Copenhagen"
thread = "t-assistant"

[executor]
command = ["{python}", "{fakes}", "probe"]

[[sources]]
name = "linear"
kind = "linear"
account = "acc-linear"
teams = ["DEV", "BIZ"]
tools = [{linear_tools}]

[[sources]]
name = "slack"
kind = "slack"
account = "acc-slack"
me = "U0ME"
tools = ["tools.slack.mcp.slack_search_public_and_private"]
channels = [{{ id = "C0DEV", name = "dev" }}]

[[sources]]
name = "github"
kind = "github"
me = "me-login"
repos = [
  {{ repo = "example/web", mine = true, review_requests = true, issues = true }},
  {{ repo = "example/api", open_prs = true, releases = true }},
]

[[sources]]
name = "t3"
kind = "t3"
projects = [{{ path = "/invented/project" }}]
"""
LINEAR_TOOLS = '"tools.linear.get_notifications", "tools.linear.list_issues", "tools.linear.get_issue"'


def utc(local: str, day: str = THU) -> str:
    """A Danish wall-clock time on `day` as the UTC instant --now takes."""
    hour, minute = map(int, local.split(":"))
    return f"{day}T{hour - 1:02d}:{minute:02d}:00Z"


class Scan(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.fake = self.root / "fake"
        (self.fake / "bin").mkdir(parents=True)
        for name in ("gh", "t3"):
            path = self.fake / "bin" / name
            path.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{HERE / "fakes.py"}" {name} "$@"\n')
            path.chmod(0o755)
        self.world = copy.deepcopy(WORLD)
        self.save()
        self.write_profile()

    def write_profile(self, tools: str = LINEAR_TOOLS, extra: str = ""):
        folder = self.root / "config" / "acme"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "profile.toml").write_text(PROFILE.format(python=sys.executable, fakes=HERE / "fakes.py",
                                                            linear_tools=tools) + extra)

    def save(self):
        (self.fake / "world.json").write_text(json.dumps(self.world))

    def run_cli(self, *args, now: str | None = None):
        env = {**os.environ, "FAKE": str(self.fake), "PATH": f"{self.fake / 'bin'}:{os.environ['PATH']}",
               "ORG_ASSISTANT_CONFIG": str(self.root / "config"), "ORG_ASSISTANT_STATE": str(self.root / "state"),
               "ORG_ASSISTANT_SLACK_SPACING": "0", "ORG_ASSISTANT_SLACK_PAUSE": "0"}
        extra = ["--now", now] if now else []
        return subprocess.run([sys.executable, str(SCRIPT), *args, *extra], env=env, capture_output=True, text=True)

    def scan(self, local: str, day: str = THU, *flags, code: int = 0):
        done = self.run_cli("scan", "acme", *flags, now=utc(local, day))
        self.assertEqual(done.returncode, code, done.stderr)
        return done

    def sent(self) -> list[dict]:
        path = self.fake / "sent.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def state(self, name: str) -> dict:
        return json.loads((self.root / "state" / "acme" / name).read_text())

    def deliver(self, batch: str | None = None):
        batch = batch or self.state("pending.json")["sent"]["id"]
        done = self.run_cli("ledger", "acme", "delivered", batch)
        self.assertEqual(done.returncode, 0, done.stderr)
        return batch

    def kinds(self, message: dict) -> list[str]:
        """The `kind ref` pairs a wake message lists."""
        line = next(line for line in message["message"].splitlines() if line.startswith("Why now:"))
        return sorted(part.strip() for part in line.split("items: ", 1)[1].rstrip(".").split(", ")) \
            if "items: " in line else []

    def start_day(self):
        """A baseline before the window, then the weekday overview, delivered."""
        self.scan("08:30")
        self.assertEqual(self.sent(), [])
        self.scan("09:05")
        self.assertIn('kind="overview"', self.sent()[-1]["message"])
        self.deliver()

    def note(self, ident, kind, ticket, at):
        self.world["linear"]["notifications"].append(
            {"id": ident, "type": kind, "url": f"https://linear.app/example/issue/{ticket}/x", "createdAt": at})

    def test_each_change_is_classified_and_a_wake_carries_it_once(self):
        self.start_day()
        linear = self.world["linear"]
        self.note("n1", "issueAssignedToYou", "DEV-103", "2026-11-26T08:30:00.000Z")
        linear["mine"].append({**linear["mine"][1], "id": "DEV-103", "updatedAt": "2026-11-26T08:30:00.000Z"})
        self.note("n2", "issueCommentMention", "DEV-101", "2026-11-26T08:40:00.000Z")
        # Someone else moved DEV-101 (the inbox says so); the user moved DEV-102 themselves.
        self.note("n3", "issueStatusChanged", "DEV-101", "2026-11-26T08:45:00.000Z")
        for ref, status, at in (("DEV-101", "In Review", "08:45"), ("DEV-102", "In Progress", "08:50")):
            linear["issues"][ref]["stateHistory"].append(
                {"state": {"name": status}, "startedAt": f"{THU}T{at}:00.000Z", "endedAt": None})
            mine = next(i for i in linear["mine"] if i["id"] == ref)
            mine.update(status=status, updatedAt=f"{THU}T{at}:00.000Z")
        linear["team"]["DEV"][0].update(status="Done", statusType="completed", updatedAt=f"{THU}T08:20:00.000Z",
                                        completedAt=f"{THU}T08:20:00.000Z")
        linear["team"]["DEV"].append({"id": "DEV-300", "status": "Todo", "statusType": "unstarted", "assignee": "Sam Sample",
                                      "assigneeId": "u-sam", "createdAt": f"{THU}T08:25:00.000Z",
                                      "updatedAt": f"{THU}T08:25:00.000Z", "project": "Invented Project"})
        linear["issues"]["DEV-200"].update(status="Done", statusType="completed")
        web = self.world["github"]["example/web"]
        web["mine"][0].update(statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}],
                              updatedAt=f"{THU}T08:35:00Z")
        web["requested"] = [{"number": 12, "updatedAt": f"{THU}T08:36:00Z"}]
        self.world["github"]["example/api"]["releases"].insert(0, {"tagName": "v1.1.0", "isDraft": False,
                                                                   "publishedAt": f"{THU}T08:10:00Z"})
        self.save()
        self.scan("10:05")
        self.assertEqual(self.kinds(self.sent()[-1]), sorted([
            "ticket.assigned DEV-103", "ticket.mention DEV-101", "ticket.changed DEV-101", "ticket.moved DEV-102",
            "ticket.unblocked DEV-102", "ticket.new_in_project DEV-300", "team.pulse DEV", "pr.ci_failed example/web#11",
            "pr.review_requested example/web#12", "release.new example/api@v1.1.0"]))
        pulse = next(i for i in self.state("pending.json")["sent"]["items"] if i["kind"] == "team.pulse")
        self.assertEqual(pulse["detail"]["people"], {"Sam Sample": {"moved": 1, "finished": 1}})
        self.deliver()
        self.scan("11:05")  # the same sources again: nothing new, so nothing is sent
        self.assertEqual(len(self.sent()), 2)

    def test_a_batched_change_waits_for_the_next_slot(self):
        self.start_day()
        self.world["linear"]["team"]["DEV"].append(
            {"id": "DEV-301", "status": "Todo", "statusType": "unstarted", "assignee": "Alex Example", "assigneeId": "u-alex",
             "createdAt": f"{THU}T09:00:00.000Z", "updatedAt": f"{THU}T09:00:00.000Z", "project": "Invented Project"})
        self.save()
        self.scan("10:05")
        self.scan("12:05")
        self.assertEqual(len(self.sent()), 1)
        self.scan("13:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.new_in_project DEV-301"])

    def test_a_slack_message_wakes_after_30_unanswered_minutes_across_two_scans(self):
        self.start_day()
        dm = {"channel": "D0ALEX", "ts": "1795683600.000100", "from": "U0ALEX"}  # 10:00 Danish time
        answered = {"channel": "D0SAM", "ts": "1795683660.000100", "from": "U0SAM"}
        reply = {"channel": "D0SAM", "ts": "1795684800.000100", "from": "U0ME"}  # 10:20
        self.world["slack"]["messages"] = [dm, answered]
        self.save()
        self.scan("10:05")  # five minutes old: kept waiting, no wake
        self.assertEqual(len(self.sent()), 1)
        self.assertEqual(sorted(w["channel"] for w in self.state("snapshot.json")["sources"]["slack"]["waiting"]),
                         ["D0ALEX", "D0SAM"])
        self.world["slack"]["messages"].append(reply)
        self.save()
        self.scan("11:05")  # the cursor moved past both; the waiting list still holds the unanswered one
        self.assertEqual(self.kinds(self.sent()[-1]), ["slack.waiting slack:D0ALEX:1795683600.000100"])
        self.deliver()
        self.scan("12:05")  # it woke the thread once, so it doesn't again
        self.assertEqual(len(self.sent()), 2)

    def test_a_sent_batch_stays_frozen_while_in_flight(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "DEV-103", f"{THU}T08:30:00.000Z")
        self.save()
        self.scan("10:05")
        first = self.state("pending.json")["sent"]
        self.note("n2", "issueCommentMention", "DEV-101", f"{THU}T09:30:00.000Z")
        self.world["t3"]["assistant"]["status"] = "running"
        self.save()
        self.scan("11:05")  # busy: nothing sent, the batch unchanged, the new change gathered beside it
        pending = self.state("pending.json")
        self.assertEqual(len(self.sent()), 2)
        self.assertEqual(pending["sent"], first)
        self.assertEqual([i["ref"] for i in pending["gathered"]], ["DEV-101"])
        self.world["t3"]["assistant"]["status"] = "completed"
        self.save()
        self.scan("12:05")  # idle and undelivered: the same batch once more, still without the new change
        self.assertEqual(len(self.sent()), 3)
        self.assertIn(f'batch="{first["id"]}"', self.sent()[-1]["message"])
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.assigned DEV-103"])
        self.deliver(first["id"])
        self.scan("13:05")  # delivered: the next batch carries the change that waited
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention DEV-101"])

    def test_a_reply_that_names_the_batch_counts_as_delivered(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "DEV-103", f"{THU}T08:30:00.000Z")
        self.save()
        self.scan("10:05")
        batch = self.state("pending.json")["sent"]["id"]
        self.world["t3"]["assistant"]["last"] = f"Two things need you. (batch {batch})"
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 2)
        self.assertIsNone(self.state("pending.json")["sent"])

    def test_a_failed_wake_is_retried_once_then_fails_the_unit(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "DEV-103", f"{THU}T08:30:00.000Z")
        self.world["t3"]["send_code"] = 1
        self.save()
        self.scan("10:05")
        self.assertEqual(self.state("pending.json")["sent"]["tries"], [{"at": utc("10:05"), "ok": False}])
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 3)
        done = self.scan("12:05", code=1)
        self.assertIn("undelivered after 2 wakes", done.stderr)
        self.assertEqual(len(self.sent()), 3)

    def test_a_missed_scan_loses_nothing_and_sends_the_overview_late(self):
        self.scan("08:30")
        self.note("n1", "issueAssignedToYou", "DEV-103", f"{THU}T08:40:00.000Z")
        self.world["linear"]["team"]["DEV"].append(
            {"id": "DEV-302", "status": "Todo", "statusType": "unstarted", "assignee": "Alex Example", "assigneeId": "u-alex",
             "createdAt": f"{THU}T10:00:00.000Z", "updatedAt": f"{THU}T10:00:00.000Z", "project": "Invented Project"})
        self.save()
        self.scan("14:05")  # the timer missed 09:05 to 13:05
        self.assertEqual(len(self.sent()), 1)
        self.assertIn('kind="overview"', self.sent()[0]["message"])
        self.assertEqual(self.kinds(self.sent()[0]), ["ticket.assigned DEV-103", "ticket.new_in_project DEV-302"])
        self.deliver()
        self.scan("15:05")
        self.assertEqual(len(self.sent()), 1)

    def test_an_expired_sign_in_fails_the_unit_on_the_third_scan_and_loses_nothing(self):
        self.start_day()
        self.world["fail"] = {"linear": "auth"}
        self.note("n1", "issueAssignedToYou", "DEV-103", f"{THU}T09:30:00.000Z")
        self.save()
        self.scan("10:05")
        self.scan("11:05")
        self.assertIn("linear sign-in expired ×2", self.run_cli("status", "acme", now=utc("11:10")).stdout)
        done = self.scan("12:05", code=1)
        self.assertIn("linear failed 3 scans in a row", done.stderr)
        self.assertEqual(len(self.sent()), 1)
        del self.world["fail"]
        self.save()
        self.scan("13:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.assigned DEV-103"])

    def test_a_busy_thread_gets_nothing_until_it_is_idle(self):
        self.start_day()
        self.world["t3"]["assistant"]["status"] = "running"
        self.note("n1", "issueCommentMention", "DEV-101", f"{THU}T09:30:00.000Z")
        self.save()
        self.scan("10:05")
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 1)
        self.world["t3"]["assistant"]["status"] = "completed"
        self.save()
        self.scan("12:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention DEV-101"])

    def test_past_the_daily_cap_only_urgent_changes_wake(self):
        self.write_profile(extra="\n[schedule]\ndaily_deltas = 1\n")
        self.start_day()
        self.note("n1", "issueStatusChanged", "DEV-101", f"{THU}T08:30:00.000Z")
        self.save()
        self.scan("10:05")  # the day's one delta
        self.deliver()
        web = self.world["github"]["example/web"]
        web["mine"][0].update(statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}],
                              updatedAt=f"{THU}T09:30:00Z")
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 2)
        self.note("n2", "issueCommentMention", "DEV-101", f"{THU}T10:30:00.000Z")
        self.save()
        self.scan("12:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention DEV-101"])
        self.assertEqual([i["kind"] for i in self.state("pending.json")["gathered"]], ["pr.ci_failed"])

    def test_weekends_wake_only_for_urgent_changes(self):
        sat = "2026-11-28"
        self.scan("08:30", sat)
        web = self.world["github"]["example/web"]
        web["mine"][0].update(statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}],
                              updatedAt=f"{sat}T09:00:00Z")
        self.save()
        self.scan("10:05", sat)
        self.assertEqual(self.sent(), [])
        self.note("n1", "issueCommentMention", "DEV-101", f"{sat}T09:30:00.000Z")
        self.save()
        self.scan("11:05", sat)
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention DEV-101"])
        self.assertEqual([i["kind"] for i in self.state("pending.json")["gathered"]], ["pr.ci_failed"])

    def test_inline_scan_freezes_everything_for_the_run_and_wakes_nothing(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "DEV-103", f"{THU}T09:30:00.000Z")
        self.world["t3"]["assistant"]["status"] = "running"  # the run that asked for it
        self.save()
        done = self.scan("10:20", THU, "--inline")
        report = json.loads(done.stdout)
        self.assertEqual([i["ref"] for i in report["items"]], ["DEV-103"])
        self.assertEqual(len(self.sent()), 1)
        self.deliver(report["batch"])
        self.world["t3"]["assistant"]["status"] = "completed"
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 1)

    def test_a_dry_run_writes_and_sends_nothing(self):
        self.note("n1", "issueAssignedToYou", "DEV-103", f"{THU}T08:30:00.000Z")
        self.save()
        done = self.scan("10:05", THU, "--dry-run", "--since", "24h")
        report = json.loads(done.stdout)
        self.assertEqual(report["wake"], "overview")
        self.assertIn("ticket.assigned", [i["kind"] for i in report["items"]])
        self.assertEqual(self.sent(), [])
        self.assertFalse((self.root / "state").exists())

    def test_the_scan_calls_only_the_tools_its_profile_lists(self):
        self.write_profile('"tools.linear.get_notifications", "tools.linear.list_issues"')
        self.scan("08:30")
        calls = {json.loads(line)["path"] for line in (self.fake / "probe.jsonl").read_text().splitlines()}
        self.assertNotIn("tools.linear.get_issue", calls)
        self.assertIn("get_issue is not in this source's tools",
                      self.state("snapshot.json")["health"]["linear"]["message"])

if __name__ == "__main__":
    unittest.main()
