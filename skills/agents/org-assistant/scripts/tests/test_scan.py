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
teams = ["ENG", "OPS"]
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


def slack_ts(local: str, day: str = THU) -> str:
    """A Slack message timestamp at a Danish wall-clock time."""
    from datetime import datetime
    return f"{datetime.fromisoformat(utc(local, day).replace('Z', '+00:00')).timestamp():.6f}"


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

    def ledger(self, *args, now: str | None = None):
        done = self.run_cli("ledger", "acme", *(["--now", now] if now else []), *args)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.strip()

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

    def found(self, local: str, day: str = THU, *flags) -> dict:
        return json.loads(self.scan(local, day, *flags).stdout)["found"]

    def batch(self) -> list[str]:
        """The `kind ref` pairs of the batch the last wake froze."""
        return sorted(f"{i['kind']} {i['ref']}" for i in self.state("pending.json")["sent"]["items"])

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
        self.note("n1", "issueAssignedToYou", "ENG-103", "2026-11-26T08:30:00.000Z")
        linear["mine"].append({**linear["mine"][1], "id": "ENG-103", "updatedAt": "2026-11-26T08:30:00.000Z"})
        self.note("n2", "issueCommentMention", "ENG-101", "2026-11-26T08:40:00.000Z")
        # Someone else moved ENG-101 (the inbox says so); the user moved ENG-102 themselves.
        self.note("n3", "issueStatusChanged", "ENG-101", "2026-11-26T08:45:00.000Z")
        for ref, status, at in (("ENG-101", "In Review", "08:45"), ("ENG-102", "In Progress", "08:50")):
            linear["issues"][ref]["stateHistory"].append(
                {"state": {"name": status}, "startedAt": f"{THU}T{at}:00.000Z", "endedAt": None})
            mine = next(i for i in linear["mine"] if i["id"] == ref)
            mine.update(status=status, updatedAt=f"{THU}T{at}:00.000Z")
        linear["team"]["ENG"][0].update(status="Done", statusType="completed", updatedAt=f"{THU}T08:20:00.000Z",
                                        completedAt=f"{THU}T08:20:00.000Z")
        linear["team"]["ENG"].append({"id": "ENG-300", "status": "Todo", "statusType": "unstarted", "assignee": "Sam Sample",
                                      "assigneeId": "u-sam", "createdAt": f"{THU}T08:25:00.000Z",
                                      "updatedAt": f"{THU}T08:25:00.000Z", "project": "Invented Project"})
        linear["issues"]["ENG-200"].update(status="Done", statusType="completed")
        web = self.world["github"]["example/web"]
        web["mine"][0].update(statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}],
                              updatedAt=f"{THU}T08:35:00Z")
        web["requested"] = [{"number": 12, "updatedAt": f"{THU}T08:36:00Z"}]
        self.world["github"]["example/api"]["releases"].insert(0, {"tagName": "v1.1.0", "isDraft": False,
                                                                   "publishedAt": f"{THU}T08:10:00Z"})
        self.save()
        self.scan("10:05")
        self.assertIn("1 release.new, 1 team.pulse, 1 ticket.moved", self.sent()[-1]["message"])
        self.assertEqual(self.batch(), sorted([
            "ticket.assigned ENG-103", "ticket.mention ENG-101", "ticket.changed ENG-101", "ticket.moved ENG-102",
            "ticket.unblocked ENG-102", "ticket.new_in_project ENG-300", "team.pulse ENG-200", "pr.ci_failed example/web#11",
            "pr.review_requested example/web#12", "release.new example/api@v1.1.0"]))
        pulse = next(i for i in self.state("pending.json")["sent"]["items"] if i["kind"] == "team.pulse")
        self.assertEqual(pulse["detail"], {"team": "ENG", "who": "Sam Sample", "finished": True})
        self.deliver()
        self.scan("11:05")  # the same sources again: nothing new, so nothing is sent
        self.assertEqual(len(self.sent()), 2)

    def test_a_batched_change_waits_for_the_next_slot(self):
        self.start_day()
        self.world["linear"]["team"]["ENG"].append(
            {"id": "ENG-301", "status": "Todo", "statusType": "unstarted", "assignee": "Alex Example", "assigneeId": "u-alex",
             "createdAt": f"{THU}T09:00:00.000Z", "updatedAt": f"{THU}T09:00:00.000Z", "project": "Invented Project"})
        self.save()
        self.scan("10:05")
        self.scan("12:05")
        self.assertEqual(len(self.sent()), 1)
        self.scan("13:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.new_in_project ENG-301"])

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
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:30:00.000Z")
        self.save()
        self.scan("10:05")
        first = self.state("pending.json")["sent"]
        self.note("n2", "issueCommentMention", "ENG-101", f"{THU}T09:30:00.000Z")
        self.world["t3"]["assistant"]["status"] = "running"
        self.save()
        self.scan("11:05")  # busy: nothing sent, the batch unchanged, the new change gathered beside it
        pending = self.state("pending.json")
        self.assertEqual(len(self.sent()), 2)
        self.assertEqual(pending["sent"], first)
        self.assertEqual([i["ref"] for i in pending["gathered"]], ["ENG-101"])
        self.world["t3"]["assistant"]["status"] = "completed"
        self.save()
        self.scan("12:05")  # idle and undelivered: the same batch once more, still without the new change
        self.assertEqual(len(self.sent()), 3)
        self.assertIn(f'batch="{first["id"]}"', self.sent()[-1]["message"])
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.assigned ENG-103"])
        self.deliver(first["id"])
        self.scan("13:05")  # delivered: the next batch carries the change that waited
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention ENG-101"])

    def test_a_reply_that_names_the_batch_counts_as_delivered(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:30:00.000Z")
        self.save()
        self.scan("10:05")
        batch = self.state("pending.json")["sent"]["id"]
        self.world["t3"]["assistant"]["last"] = f"Earlier news. (batch {batch}1)"  # a longer id that starts alike
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 3)  # not that batch: resent
        self.world["t3"]["assistant"]["last"] = f"Two things need you. (batch {batch})"
        self.save()
        self.scan("12:05")
        self.assertEqual(len(self.sent()), 3)
        self.assertIsNone(self.state("pending.json")["sent"])

    def test_a_failed_wake_is_retried_once_then_fails_the_unit(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:30:00.000Z")
        self.world["t3"]["send_code"] = 1
        self.save()
        self.scan("10:05")
        self.assertEqual(self.state("pending.json")["sent"]["tries"], [{"at": utc("10:05"), "ok": False}])
        done = self.scan("11:05", code=1)  # the retry failed too: the unit fails now, not an hour later
        self.assertIn("last wake failed to send", done.stderr)
        done = self.scan("12:05", code=1)
        self.assertIn("undelivered after 2 wakes", done.stderr)
        self.assertEqual(len(self.sent()), 3)

    def test_a_missed_scan_loses_nothing_and_sends_the_overview_late(self):
        self.scan("08:30")
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:40:00.000Z")
        self.world["linear"]["team"]["ENG"].append(
            {"id": "ENG-302", "status": "Todo", "statusType": "unstarted", "assignee": "Alex Example", "assigneeId": "u-alex",
             "createdAt": f"{THU}T10:00:00.000Z", "updatedAt": f"{THU}T10:00:00.000Z", "project": "Invented Project"})
        self.save()
        self.scan("14:05")  # the timer missed 09:05 to 13:05
        self.assertEqual(len(self.sent()), 1)
        self.assertIn('kind="overview"', self.sent()[0]["message"])
        self.assertEqual(self.kinds(self.sent()[0]), ["ticket.assigned ENG-103", "ticket.new_in_project ENG-302"])
        self.deliver()
        self.scan("15:05")
        self.assertEqual(len(self.sent()), 1)

    def test_an_expired_sign_in_fails_the_unit_on_the_third_scan_and_loses_nothing(self):
        self.start_day()
        self.world["fail"] = {"linear": "auth"}
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T09:30:00.000Z")
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
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.assigned ENG-103"])

    def test_a_busy_thread_gets_nothing_until_it_is_idle(self):
        self.start_day()
        self.world["t3"]["assistant"]["status"] = "running"
        self.note("n1", "issueCommentMention", "ENG-101", f"{THU}T09:30:00.000Z")
        self.save()
        self.scan("10:05")
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 1)
        self.world["t3"]["assistant"]["status"] = "completed"
        self.save()
        self.scan("12:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention ENG-101"])

    def test_past_the_daily_cap_only_urgent_changes_wake(self):
        self.write_profile(extra="\n[schedule]\ndaily_deltas = 1\n")
        self.start_day()
        self.note("n1", "issueStatusChanged", "ENG-101", f"{THU}T08:30:00.000Z")
        self.save()
        self.scan("10:05")  # the day's one delta
        self.deliver()
        web = self.world["github"]["example/web"]
        web["mine"][0].update(statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}],
                              updatedAt=f"{THU}T09:30:00Z")
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 2)
        self.note("n2", "issueCommentMention", "ENG-101", f"{THU}T10:30:00.000Z")
        self.save()
        self.scan("12:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention ENG-101"])
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
        self.note("n1", "issueCommentMention", "ENG-101", f"{sat}T09:30:00.000Z")
        self.save()
        self.scan("11:05", sat)
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.mention ENG-101"])
        self.assertEqual([i["kind"] for i in self.state("pending.json")["gathered"]], ["pr.ci_failed"])

    def test_inline_scan_freezes_everything_for_the_run_and_wakes_nothing(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T09:30:00.000Z")
        self.world["t3"]["assistant"]["status"] = "running"  # the run that asked for it
        self.save()
        done = self.scan("10:20", THU, "--inline")
        report = json.loads(done.stdout)
        self.assertEqual([i["ref"] for i in report["items"]], ["ENG-103"])
        self.assertEqual(len(self.sent()), 1)
        self.deliver(report["batch"])
        self.world["t3"]["assistant"]["status"] = "completed"
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 1)

    def test_a_dry_run_writes_and_sends_nothing(self):
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:30:00.000Z")
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
    # Round-1 review findings, each failing on the first head.

    def test_a_crash_between_the_two_state_writes_sends_one_overview(self):
        self.scan("08:30")
        snapshot = self.root / "state" / "acme" / "snapshot.json"
        before = snapshot.read_bytes()
        self.scan("09:05")
        snapshot.write_bytes(before)  # as if the scan died after writing pending.json
        self.scan("10:05")
        self.deliver()
        self.scan("11:05")
        overviews = {m["message"].split('batch="')[1].split('"')[0] for m in self.sent() if 'kind="overview"' in m["message"]}
        self.assertEqual(len(overviews), 1)

    def test_an_inline_scan_leaves_the_batch_in_flight_frozen(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:30:00.000Z")
        self.save()
        self.scan("10:05")
        frozen = self.state("pending.json")["sent"]
        self.note("n2", "issueCommentMention", "ENG-101", f"{THU}T09:10:00.000Z")
        self.save()
        first = json.loads(self.scan("10:15", THU, "--inline").stdout)
        second = json.loads(self.scan("10:16", THU, "--inline").stdout)
        self.assertEqual(self.state("pending.json")["sent"], frozen)
        self.assertEqual(first["in_flight"]["id"], frozen["id"])
        self.assertEqual([i["ref"] for i in second["items"]], ["ENG-101"])
        self.assertEqual(len({frozen["id"], first["batch"], second["batch"]}), 3)

    def test_team_counts_made_while_a_batch_is_in_flight_wait_beside_it(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:30:00.000Z")
        team = self.world["linear"]["team"]["ENG"]
        team.append({"id": "ENG-201", "status": "Done", "statusType": "completed", "assignee": "Alex Example",
                     "assigneeId": "u-alex", "createdAt": "2026-11-20T08:00:00.000Z", "project": "Other Project",
                     "updatedAt": f"{THU}T08:30:00.000Z", "completedAt": f"{THU}T08:30:00.000Z"})
        self.save()
        self.scan("10:05")
        self.assertIn("team.pulse ENG-201", self.batch())
        team[0].update(status="Done", statusType="completed", updatedAt=f"{THU}T09:30:00.000Z",
                       completedAt=f"{THU}T09:30:00.000Z")
        self.world["t3"]["assistant"]["status"] = "running"
        self.save()
        self.scan("11:05")
        self.assertEqual(self.state("pending.json")["gathered"][0]["kind"], "team.pulse")

    def test_a_source_error_reaches_no_file_or_log_with_its_text(self):
        self.scan("08:30")
        self.world["fail"] = {"linear": "Could not load the ticket titled PRIVATE-CANARY"}
        self.save()
        done = self.scan("09:05")
        status = self.run_cli("status", "acme", now=utc("09:10")).stdout
        files = "".join(p.read_text() for p in (self.root / "state" / "acme").glob("*.json"))
        self.assertNotIn("PRIVATE-CANARY", done.stderr + done.stdout + status + files)
        self.assertIn("linear failing ×1", status)

    def test_quiet_lets_the_overview_through_and_pause_holds_a_retry(self):
        self.scan("08:30")
        self.ledger("quiet", f"{THU}T14:00")
        self.scan("09:05")
        self.assertIn('kind="overview"', self.sent()[-1]["message"])
        self.ledger("pause", "2026-11-30T09:00")
        self.scan("10:05")
        self.assertEqual(len(self.sent()), 1)

    def test_a_ticket_someone_closed_and_a_new_red_pr_both_wake(self):
        self.start_day()
        self.note("n1", "issueStatusChanged", "ENG-101", f"{THU}T08:30:00.000Z")
        self.world["linear"]["mine"][0].update(status="Canceled", statusType="canceled")
        self.world["github"]["example/web"]["mine"].append(
            {"number": 13, "isDraft": False, "reviewDecision": "CHANGES_REQUESTED", "updatedAt": f"{THU}T08:40:00Z",
             "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "FAILURE"}]})
        self.save()
        self.assertEqual(self.found("10:05"), {"ticket.changed": 1, "pr.ci_failed": 1, "pr.changes_requested": 1})

    def test_a_dm_answered_while_the_thread_was_busy_wakes_nothing(self):
        self.start_day()
        self.world["slack"]["messages"] = [{"channel": "D0ALEX", "ts": slack_ts("09:20"), "from": "U0ALEX"}]
        self.world["t3"]["assistant"]["status"] = "running"
        self.save()
        self.scan("10:05")
        self.world["slack"]["messages"].append({"channel": "D0ALEX", "ts": slack_ts("10:15"), "from": "U0ME"})
        self.world["t3"]["assistant"]["status"] = "completed"
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 1)

    def test_a_source_that_never_signed_in_reports_what_happened_once_it_does(self):
        self.world["fail"] = {"linear": "auth"}
        self.save()
        self.scan("08:30")
        self.scan("09:05")
        self.deliver()
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:10:00.000Z")
        del self.world["fail"]
        self.save()
        self.scan("10:05")
        self.assertEqual(self.kinds(self.sent()[-1]), ["ticket.assigned ENG-103"])

    def test_status_warns_when_no_overview_was_delivered_by_09_30(self):
        self.world["t3"]["assistant"]["status"] = "running"
        self.save()
        self.scan("08:30")
        self.scan("09:05")
        self.assertIn("No overview delivered today", self.run_cli("status", "acme", now=utc("09:35")).stdout)

    def test_an_unreadable_thread_fails_the_unit_on_the_third_scan(self):
        self.start_day()
        self.world["t3"]["assistant"] = None
        self.save()
        self.scan("10:05")
        self.scan("11:05")
        done = self.scan("12:05", code=1)
        self.assertIn("unreadable 3 scans in a row", done.stderr)

    def test_a_repeated_ledger_command_changes_nothing_more(self):
        self.scan("08:30")
        self.ledger("call", "set", "first offer")
        self.ledger("call", "queue", "second offer")
        self.ledger("call", "queue", "third offer")
        self.ledger("call", "clear", "c1")
        self.assertIn("second offer", self.ledger("call", "clear", "c1"))
        self.ledger("started", "t-new", "--ticket", "ENG-1")
        self.ledger("started", "t-new", "--ticket", "ENG-1")
        self.assertEqual(len(json.loads(self.ledger("show"))["started"]), 1)

    def test_a_call_that_replaced_another_within_15_minutes_says_so(self):
        self.scan("08:30")
        self.ledger("call", "set", "first offer", now=utc("10:00"))
        self.ledger("call", "queue", "second offer", now=utc("10:00"))
        self.ledger("call", "clear", "c1", now=utc("10:05"))
        self.assertIn("replaced another call", self.ledger("call", "show", now=utc("10:10")))
        self.assertNotIn("replaced another call", self.ledger("call", "show", now=utc("10:30")))

    def test_an_issue_assigned_again_within_a_week_wakes_again(self):
        self.start_day()
        issue = {"number": 5, "createdAt": f"{THU}T07:00:00Z", "updatedAt": f"{THU}T08:30:00Z",
                 "assignees": [{"login": "me-login"}]}
        self.world["github"]["example/web"]["issues"] = [issue]
        self.save()
        self.scan("10:05")
        self.deliver()
        issue.update(assignees=[], updatedAt=f"{THU}T09:30:00Z")
        self.save()
        self.scan("11:05")
        issue.update(assignees=[{"login": "me-login"}], updatedAt=f"{THU}T10:30:00Z")
        self.save()
        self.scan("12:05")
        self.assertEqual([self.kinds(m) for m in self.sent()[1:]], [["issue.assigned example/web#5"]] * 2)

    def test_a_malformed_profile_fails_with_its_line(self):
        (self.root / "config" / "acme" / "profile.toml").write_text('org = "acme"\nthread = \n')
        done = self.run_cli("scan", "acme", now=utc("10:05"))
        self.assertEqual(done.returncode, 1)
        self.assertIn("line 2", done.stderr)

    def test_one_broken_profile_leaves_the_other_organisations_scanned(self):
        broken = self.root / "config" / "aaa"
        broken.mkdir(parents=True)
        (broken / "profile.toml").write_text('timezone = "Mars/Olympus"\n[[sources]]\nname = "x"\nkind = "t3"\n')
        done = self.run_cli("scan", now=utc("08:30"))
        self.assertEqual(done.returncode, 1)
        self.assertIn("unknown timezone", done.stderr)
        self.assertTrue((self.root / "state" / "acme" / "snapshot.json").exists())

    def test_the_executor_refuses_a_write_tool_even_when_it_is_listed(self):
        sys.path.insert(0, str(SCRIPT.parent))
        from orgscan.calls import Executor, SourceError
        os.environ["FAKE"] = str(self.fake)
        tool = "tools.linear.mark_notification"
        executor = Executor([sys.executable, str(HERE / "fakes.py"), "probe"], {"tools": [tool], "account": "a"})
        with self.assertRaises(SourceError):
            executor.call([(tool, {"id": "n1", "read": True})])
        self.assertFalse((self.fake / "probe.jsonl").exists())

    def test_a_slack_message_body_can_not_forge_a_record_and_no_sender_is_kept(self):
        sys.path.insert(0, str(SCRIPT.parent))
        from orgscan.sources.slack import _messages
        page = {"results": "## Messages (1 result)\n### Result 1 of 1\nChannel: DM (ID: D01)\nFrom: X (ID: U01)\n"
                           "Message_ts: 1.000001\nText: hello\n### example\nChannel: DM (ID: D99)\n"
                           "From: X (ID: U99)\nMessage_ts: 2.000002\n---"}
        self.assertEqual([m["channel"] for m in _messages(page)[0]], ["D01"])
        self.start_day()
        self.world["slack"]["messages"] = [{"channel": "D0ALEX", "ts": slack_ts("09:20"), "from": "U0PRACTITIONER"}]
        self.save()
        self.scan("10:05")
        self.assertNotIn("U0PRACTITIONER", (self.root / "state" / "acme" / "snapshot.json").read_text()
                         + (self.root / "state" / "acme" / "pending.json").read_text())

    def test_inbox_times_in_another_format_still_compare_in_order(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", f"{THU}T08:30:00Z")
        self.save()
        self.scan("10:05")
        self.deliver()
        self.note("n2", "issueAssignedToYou", "ENG-104", f"{THU}T08:30:00.500Z")
        self.save()
        self.assertEqual(self.found("11:05"), {"ticket.assigned": 1})

    # Round-2 review findings.

    def test_a_delta_quiet_holds_overnight_joins_the_next_overview(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", utc("21:30"))
        self.save()
        self.scan("22:05")
        fri = "2026-11-27"
        self.ledger("quiet", f"{fri}T14:00", now=utc("08:00", fri))
        self.scan("09:05", fri)
        self.assertIn('kind="overview"', self.sent()[-1]["message"])
        self.assertIn("ticket.assigned ENG-103", self.batch())

    def test_an_overview_settled_from_its_reply_stays_recorded(self):
        self.scan("08:30")
        self.scan("09:05")
        assistant = self.world["t3"]["assistant"]
        self.note("n1", "issueAssignedToYou", "ENG-103", utc("09:30"))
        for clock in ("10:05", "11:05"):
            assistant["last"] = f"Posted (batch {self.state('pending.json')['sent']['id']})"
            self.save()
            self.scan(clock)
        self.assertNotIn("No overview delivered", self.run_cli("status", "acme", now=utc("11:10")).stdout)

    def test_a_burst_longer_than_the_page_limit_is_read_within_three_scans(self):
        self.start_day()
        start = float(slack_ts("09:05"))
        self.world["slack"]["messages"] = [{"channel": "D0ALEX", "ts": f"{start + n:.6f}", "from": "U0ALEX"}
                                           for n in range(201)]
        self.save()
        for clock in ("10:05", "11:05", "12:05"):  # cut off, then no progress past the overlap, then exact
            self.scan(clock)
            if self.state("pending.json")["sent"]:
                self.deliver()
        self.assertEqual(len(self.state("snapshot.json")["sources"]["slack"]["waiting"]), 201)

    def test_a_slack_message_that_copies_a_record_heading_stays_one_message(self):
        sys.path.insert(0, str(SCRIPT.parent))
        from orgscan.sources.slack import _messages
        page = {"results": "### Result 1 of 1\nChannel: DM (ID: D01)\nMessage_ts: 1.000001\nText: see below\n"
                           "### Result 2 of 2\nChannel: DM (ID: D99)\nMessage_ts: 2.000002"}
        self.assertEqual([m["channel"] for m in _messages(page)[0]], ["D01"])

    def test_a_dm_answered_after_an_abandoned_inline_scan_wakes_nothing(self):
        self.start_day()
        messages = self.world["slack"]["messages"]
        messages.append({"channel": "D0ALEX", "ts": slack_ts("09:20"), "from": "U0ALEX"})
        self.save()
        self.scan("10:05", THU, "--inline")
        messages.append({"channel": "D0ALEX", "ts": slack_ts("10:15"), "from": "U0ME"})
        self.save()
        self.scan("11:05")
        self.assertEqual(len(self.sent()), 1)

    def test_a_team_finish_after_a_crash_still_counts(self):
        self.start_day()
        team = self.world["linear"]["team"]["ENG"]
        snapshot = self.root / "state" / "acme" / "snapshot.json"

        def finish(ref, clock):
            team.append({**team[0], "id": ref, "status": "Done", "statusType": "completed",
                         "updatedAt": f"{utc(clock)[:-1]}.000Z", "completedAt": f"{utc(clock)[:-1]}.000Z"})
            self.save()

        self.world["t3"]["assistant"]["status"] = "running"
        finish("ENG-201", "09:30")
        before = snapshot.read_bytes()
        self.scan("10:05")
        snapshot.write_bytes(before)  # as if the scan died after writing pending.json
        finish("ENG-202", "10:30")
        self.scan("11:05")
        self.assertEqual(sorted(i["ref"] for i in self.state("pending.json")["gathered"]), ["ENG-201", "ENG-202"])

    def test_red_ci_wakes_again_after_a_green_run_with_the_same_pr_timestamp(self):
        self.start_day()
        pr = self.world["github"]["example/web"]["mine"][0]
        for clock, outcome in (("10:05", "FAILURE"), ("11:05", "SUCCESS"), ("12:05", "FAILURE")):
            pr["statusCheckRollup"] = [{"status": "COMPLETED", "conclusion": outcome}]
            self.save()
            self.scan(clock)
            if self.state("pending.json")["sent"]:
                self.deliver()
        self.assertEqual(len(self.sent()), 3)

    def test_a_profile_with_a_list_for_a_name_fails_only_itself(self):
        broken = self.root / "config" / "aaa"
        broken.mkdir(parents=True)
        (broken / "profile.toml").write_text('[[sources]]\nname = ["one"]\nkind = "t3"\n')
        done = self.run_cli("scan", now=utc("08:30"))
        self.assertEqual(done.returncode, 1)
        self.assertTrue((self.root / "state" / "acme" / "snapshot.json").exists())

    # Round-3 review findings.

    def test_a_reply_found_in_the_same_scan_as_the_dm_wakes_nothing(self):
        self.start_day()
        self.world["slack"]["messages"] = [{"channel": "D0ALEX", "ts": slack_ts("09:20"), "from": "U0ALEX"},
                                           {"channel": "D0ALEX", "ts": slack_ts("09:25"), "from": "U0ME"}]
        self.save()
        self.scan("10:05")
        self.assertEqual(len(self.sent()), 1)

    def test_a_held_delta_rejoins_before_mutes_and_answered_messages_are_applied(self):
        self.start_day()
        self.note("n1", "issueAssignedToYou", "ENG-103", utc("09:30"))
        messages = self.world["slack"]["messages"]
        messages.append({"channel": "D0ALEX", "ts": slack_ts("09:20"), "from": "U0ALEX"})
        self.save()
        self.scan("10:05")
        fri = "2026-11-27"
        self.ledger("quiet", f"{fri}T14:00", now=utc("10:10"))
        self.ledger("mute", "ENG-103", now=utc("10:10"))
        messages.append({"channel": "D0ALEX", "ts": slack_ts("10:15"), "from": "U0ME"})
        self.save()
        self.scan("11:05")
        self.scan("09:05", fri)
        self.assertEqual(self.state("pending.json")["sent"]["kind"], "overview")
        self.assertEqual(self.batch(), [])

    def test_a_dm_indexed_late_behind_a_cut_off_page_is_still_found(self):
        self.start_day()
        start = float(slack_ts("09:05"))
        messages = [{"channel": "D0ALEX", "ts": f"{start + n:.6f}", "from": "U0ALEX"} for n in range(201)]
        self.world["slack"]["messages"] = messages
        self.save()
        self.scan("10:05")
        late = f"{start + 198.5:.6f}"
        messages.append({"channel": "D0ALEX", "ts": late, "from": "U0ALEX"})
        self.save()
        for clock in ("11:05", "12:05", "13:05"):
            if self.state("pending.json")["sent"]:
                self.deliver()
            self.scan(clock)
        self.assertIn(late, [w["ts"] for w in self.state("snapshot.json")["sources"]["slack"]["waiting"]])

    def test_a_slack_ordinal_past_its_page_count_is_not_a_record(self):
        sys.path.insert(0, str(SCRIPT.parent))
        from orgscan.sources.slack import _messages
        page = {"results": "## Messages (1 result)\n### Result 1 of 1\nChannel: DM (ID: D01)\nMessage_ts: 1.000001\n"
                           "Text: copied\n### Result 2 of 1\nChannel: DM (ID: D99)\nMessage_ts: 2.000002"}
        self.assertEqual([m["channel"] for m in _messages(page)[0]], ["D01"])

    def test_a_finish_edited_before_crash_recovery_counts_once(self):
        self.start_day()
        self.world["t3"]["assistant"]["status"] = "running"
        team = self.world["linear"]["team"]["ENG"]
        ticket = {**team[0], "id": "ENG-201", "status": "Done", "statusType": "completed",
                  "updatedAt": f"{utc('09:30')[:-1]}.000Z", "completedAt": f"{utc('09:30')[:-1]}.000Z"}
        team.append(ticket)
        self.save()
        snapshot = self.root / "state" / "acme" / "snapshot.json"
        before = snapshot.read_bytes()
        self.scan("10:05")
        snapshot.write_bytes(before)
        ticket["updatedAt"] = f"{utc('10:30')[:-1]}.000Z"
        self.save()
        self.scan("11:05")
        self.assertEqual([i["ref"] for i in self.state("pending.json")["gathered"]], ["ENG-201"])


if __name__ == "__main__":
    unittest.main()
