"""project.py tick and tick.sh against fake `t3` and `gh` on PATH, which serve thread and PR
state from JSON files and record each `t3 thread send`. The rule under test: a change T3
doesn't tell the coordinator wakes it once, and an unchanged project wakes nothing.
Run: python3 -m unittest discover -s skills/agents/coordinator/scripts/tests"""
import json, os, pathlib, subprocess, sys, tempfile, time, unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = HERE / "project.py"

PROJECT = """# ◆ export

Coordinator: <t3-thread://v2/env/lead> · Checkout: {checkout} (on `main`)

## Goal

Ship the export.
Proof: #12 merged.
Follow-ups: none

## Workers

| Worker | Proof | Thread | Branch or PR | State | Waits on | Last side effect |
|---|---|---|---|---|---|---|
| build | #12 merged | <t3-thread://v2/env/w1> · task t1 | `export` · #12 | running | — | pushed abc |
| probe | report | <t3-thread://v2/env/w2> · task t2 | — | done | — | report |
| remote | report | <t3-thread://v2/other/w3> · task t3 | — | {remote} | — | launched |

## Listening

- Heartbeat: {heartbeat}
- Startup: none
- Watches: #12 (build), acme/app#7 (the user)
"""

FAKE_T3 = r"""#!/usr/bin/env python3
import json, os, sys
fake = os.environ["FAKE"]
if sys.argv[1:3] == ["thread", "show"]:
    threads = json.load(open(f"{fake}/threads.json"))
    if sys.argv[3] not in threads:
        sys.exit("Thread is no longer available.")
    print(json.dumps({"thread": threads[sys.argv[3]], "messages": []}))
elif sys.argv[1:3] == ["thread", "send"]:
    with open(f"{fake}/sent.jsonl", "a") as out:
        out.write(json.dumps({"to": sys.argv[3], "message": sys.stdin.read()}) + "\n")
    sys.exit(int(os.environ.get("SEND_CODE", "0")))
"""

FAKE_GH = r"""#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
repo = args[args.index("-R") + 1]
prs = json.load(open(os.environ["FAKE"] + "/prs.json"))
key = f"{repo}#{args[2]}"
with open(os.environ["FAKE"] + "/gh-calls.jsonl", "a") as out:
    out.write(json.dumps({"key": key}) + "\n")
if key not in prs:
    sys.exit("no pull requests found")
print(json.dumps(prs[key]))
"""


def thread(status="running", runs=1, items=10, asked=0, **more):
    return {"status": status, "runCount": runs, "itemCount": items, "pendingRequestCount": asked, **more}


class Tick(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.root)])
        self.fake, self.dir = self.root / "fake", self.root / "coordinator" / "export"
        (self.fake / "bin").mkdir(parents=True)
        self.dir.mkdir(parents=True)
        for name, body in [("t3", FAKE_T3), ("gh", FAKE_GH)]:
            (self.fake / "bin" / name).write_text(body)
            (self.fake / "bin" / name).chmod(0o755)
        self.checkout = self.root / "check out"  # a space, as a real path may have
        subprocess.run(["git", "init", "-q", str(self.checkout)], check=True)
        subprocess.run(["git", "-C", str(self.checkout), "remote", "add", "origin", "git@github.com:acme/app.git"], check=True)
        self.write_project()
        self.threads = {"lead": thread("completed", 40), "w1": thread()}
        self.prs = {"acme/app#12": {"state": "OPEN", "isDraft": True}, "acme/app#7": {"state": "OPEN", "isDraft": False}}

    def write_project(self, heartbeat="tick", remote="done", rows=None):
        text = PROJECT.format(checkout=self.checkout, heartbeat=heartbeat, remote=remote)
        for old, new in (rows or {}).items():
            text = text.replace(old, new)
        (self.dir / "project.md").write_text(text)

    def tick(self, *args, code=0, send_code=0):
        (self.fake / "threads.json").write_text(json.dumps(self.threads))
        (self.fake / "prs.json").write_text(json.dumps(self.prs))
        env = {**os.environ, "FAKE": str(self.fake), "SEND_CODE": str(send_code),
               "PATH": f"{self.fake / 'bin'}:{os.environ['PATH']}"}
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.dir), "tick", *args],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, code, result.stderr)
        return result

    def sent(self):
        path = self.fake / "sent.jsonl"
        messages = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
        path.unlink(missing_ok=True)
        return messages

    def state(self):
        return json.loads((self.dir / "tick.json").read_text())

    def age(self, seconds):
        """Moves every saved time back, as if the last tick ran `seconds` ago."""
        state = self.state()
        for saved in state["threads"].values():
            saved["since"] -= seconds
        state["sent"] = {key: at - seconds for key, at in state["sent"].items()}
        (self.dir / "tick.json").write_text(json.dumps(state))

    def test_an_unchanged_project_wakes_nothing(self):
        for _ in range(3):
            self.tick("--send")
        self.assertEqual(self.sent(), [])

    def test_a_stopped_worker_wakes_the_coordinator_once_its_row_is_stale_for_a_tick(self):
        self.tick("--send")
        self.threads["w1"] = thread("failed", 1, 12)
        self.tick("--send")
        self.assertEqual(self.sent(), [], "a just-stopped thread waits a tick for T3's own delivery")
        self.tick("--send")
        [sent] = self.sent()
        self.assertEqual(sent["to"], "lead")
        self.assertTrue(sent["message"].startswith('<coordinator-tick project="export">\n'), sent["message"])
        self.assertIn("- build: its thread stopped (failed) while its row says running\n", sent["message"])
        self.assertIn(f"Read {self.dir / 'project.md'} and handle", sent["message"], "a fresh session finds the folder")
        self.tick("--send")
        self.assertEqual(self.sent(), [], "sent once an hour, not each tick")
        self.age(3600)
        self.tick("--send")
        self.assertEqual(len(self.sent()), 1, "still unfixed an hour later, so it repeats")

    def test_a_stopped_worker_whose_row_the_coordinator_fixed_wakes_nothing(self):
        self.tick("--send")
        self.threads["w1"] = thread("completed", 1, 12)
        self.tick("--send")
        self.write_project(rows={"| `export` · #12 | running |": "| `export` · #12 | done |"})
        self.tick("--send")
        self.assertEqual(self.sent(), [])

    def test_a_worker_with_no_new_item_for_an_hour_is_stalled(self):
        self.tick("--send")
        self.age(3000)
        self.tick("--send")
        self.assertEqual(self.sent(), [])
        self.age(700)
        self.tick("--send")
        [sent] = self.sent()
        self.assertIn("- build: no new thread item in 61 min\n", sent["message"])
        self.threads["w1"] = thread(items=11)
        self.tick("--send")
        self.assertEqual(self.sent(), [], "a new item ends the stall")

    def test_a_question_the_row_doesnt_show_wakes_it(self):
        self.tick("--send")
        self.threads["w1"] = thread("waiting", asked=1)
        self.tick("--send")
        self.tick("--send")
        [sent] = self.sent()
        self.assertIn("- build: its thread waits on 1 question(s) its row doesn't show\n", sent["message"])

    def test_a_pr_that_merges_or_turns_ready_wakes_it_once(self):
        self.write_project(rows={"- Watches: #12 (build), acme/app#7 (the user)": "- Watches: acme/app#7 (the user)"})
        self.tick("--send")
        self.prs["acme/app#12"] = {"state": "MERGED", "isDraft": False}
        self.prs["acme/app#7"] = {"state": "OPEN", "isDraft": True}
        self.tick("--send")
        [sent] = self.sent()
        self.assertIn("- acme/app#12: merged", sent["message"])
        self.assertIn("- acme/app#7: turned draft\n", sent["message"])
        self.tick("--send")
        self.assertEqual(self.sent(), [])

    def test_a_finished_pr_left_under_watches_repeats_until_unwatched(self):
        self.prs["acme/app#7"] = {"state": "MERGED", "isDraft": False}
        self.tick("--send")
        self.assertIn("- acme/app#7: merged, and still under Watches\n", self.sent()[0]["message"],
                      "even one that merged before the tick first saw it")
        self.tick("--send")
        self.assertEqual(self.sent(), [])
        self.age(3600)
        self.threads["w1"] = thread(items=11)  # the worker is busy, so only the watch repeats
        self.tick("--send")
        self.assertEqual(len(self.sent()), 1)
        self.write_project(rows={"- Watches: #12 (build), acme/app#7 (the user)": "- Watches: #12 (build)"})
        self.age(3600)
        self.threads["w1"] = thread(items=12)
        self.tick("--send")
        self.assertEqual(self.sent(), [])

    def test_one_pr_written_two_ways_or_in_a_range_is_checked_once_each(self):
        self.write_project(rows={"- Watches: #12 (build), acme/app#7 (the user)": "- Watches: #12, acme/app#12, app#12, #20–#22"})
        for n in (20, 21, 22):
            self.prs[f"acme/app#{n}"] = {"state": "OPEN", "isDraft": False}
        self.tick("--send")
        self.assertEqual(sorted(self.state()["prs"]), ["acme/app#12", "acme/app#20", "acme/app#21", "acme/app#22"])

    def test_a_repo_ref_without_a_known_owner_is_flagged(self):
        subprocess.run(["git", "-C", str(self.checkout), "remote", "remove", "origin"], check=True)
        self.write_project(rows={"- Watches: #12 (build), acme/app#7 (the user)": "- Watches: skills#246"})
        self.tick("--send")
        self.assertIn("- skills#246: the tick can't tell its repo from the checkout's origin, so write it as owner/repo#N\n", self.sent()[0]["message"])

    def test_a_failed_read_keeps_the_stall_clock(self):
        self.tick("--send")
        self.age(3060)
        del self.threads["w1"]
        self.tick("--send")
        self.sent()
        self.threads["w1"] = thread()
        self.age(600)
        self.tick("--send")
        self.assertIn("- build: no new thread item in 61 min\n", self.sent()[0]["message"])

    def test_a_pr_number_without_a_checkout_origin_is_flagged(self):
        subprocess.run(["rm", "-rf", str(self.checkout)], check=True)
        self.tick("--send")
        message = self.sent()[0]["message"]
        self.assertIn("- #12: the tick can't tell its repo from the checkout's origin, so write it as owner/repo#N\n", message)
        self.assertNotIn("acme/app#7:", message, "a full owner/repo#N needs no checkout")

    def test_a_reopened_pr_says_so(self):
        self.tick("--send")
        self.prs["acme/app#12"] = {"state": "CLOSED", "isDraft": True}
        self.tick("--send")
        self.sent()
        self.prs["acme/app#12"] = {"state": "OPEN", "isDraft": True}
        self.tick("--send")
        self.assertIn("- acme/app#12: reopened\n", self.sent()[0]["message"])

    def test_a_metadata_update_doesnt_reset_the_stall_clock(self):
        stamp = lambda ago: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - ago))
        self.threads["w1"] = thread(updatedAt=stamp(600))
        self.tick("--send")
        self.age(3060)
        self.threads["w1"] = thread(updatedAt=stamp(0))  # a title change, no new item
        self.tick("--send")
        self.assertIn("- build: no new thread item in 61 min\n", self.sent()[0]["message"])

    def test_a_worker_on_another_machine_gets_an_hourly_reminder(self):
        self.write_project(remote="running")
        self.tick("--send")
        [sent] = self.sent()
        self.assertIn("- remote: its thread is on another machine, so read its status with `t3_thread_read` "
                      "and environmentId other\n", sent["message"])

    def test_a_running_row_with_no_thread_link_is_flagged(self):
        self.write_project(rows={"<t3-thread://v2/env/w1> · task t1": "task t1"})
        self.tick("--send")
        self.assertIn("- build: its row says running but has no thread link to check\n", self.sent()[0]["message"])

    def test_links_paths_and_refs_parse_as_coordinators_write_them(self):
        self.write_project(rows={"<t3-thread://v2/env/w1> · task t1": "[build](t3-thread://v2/env/w1) · task t1",
                                 "- Watches: #12 (build), acme/app#7 (the user)": "- Watches: #12 (build), app#7 and acme/app#7"})
        self.tick("--send")
        calls = [json.loads(line) for line in (self.fake / "gh-calls.jsonl").read_text().splitlines()]
        self.assertEqual(sorted({call["key"] for call in calls}), ["acme/app#12", "acme/app#7"],
                         "#12 resolved through the origin of a checkout path with a space")
        self.assertEqual(list(self.state()["threads"]), ["w1"])

    def test_a_watches_line_that_says_none_names_no_pr(self):
        self.write_project(rows={"- Watches: #12 (build), acme/app#7 (the user)": "- Watches: none (#7 unwatched at handback)"})
        self.tick("--send")
        self.assertEqual(list(self.state()["prs"]), ["acme/app#12"])

    def test_a_live_row_the_tick_cant_parse_is_flagged(self):
        self.write_project(rows={"| probe | report | <t3-thread://v2/env/w2> · task t2 | — | done | — | report |":
                                 "| probe | report | <t3-thread://v2/env/w2> | running (round 2) |"})
        self.tick("--send")
        self.assertIn("- probe: its row's cells don't match the Workers header", self.sent()[0]["message"])
        self.write_project(rows={"| probe | report | <t3-thread://v2/env/w2> · task t2 | — | done | — | report |":
                                 "| probe | report | <t3-thread://v2/env/w2> | done | was running fine |"})
        self.age(3600)
        self.threads["w1"] = thread(items=11)
        self.tick("--send")
        self.assertEqual(self.sent(), [], "a done row that mentions running isn't live")

    def test_nothing_is_sent_while_the_coordinator_runs_but_workers_are_still_timed(self):
        self.tick("--send")
        self.threads["lead"] = thread("running", 41)
        self.threads["w1"] = thread("failed", 1, 12)
        self.prs["acme/app#12"] = {"state": "MERGED", "isDraft": False}
        self.tick("--send")
        self.tick("--send")
        self.assertEqual(self.sent(), [])
        self.assertEqual(self.state()["prs"]["acme/app#12"], ["OPEN", True], "a PR waits for the coordinator's turn to end")
        self.threads["lead"] = thread("completed", 41)
        self.tick("--send")
        [sent] = self.sent()
        self.assertIn("- build: its thread stopped (failed)", sent["message"], "its stop was timed while it ran")
        self.assertIn("- acme/app#12: merged", sent["message"])

    def test_a_stall_is_timed_from_the_threads_last_update(self):
        hour_ago = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 3660))
        self.threads["w1"] = thread(updatedAt=hour_ago)
        self.tick("--send")
        self.assertIn("- build: no new thread item in 61 min\n", self.sent()[0]["message"])

    def test_a_failed_send_keeps_the_state_so_the_next_tick_retries(self):
        self.tick("--send")
        self.prs["acme/app#12"] = {"state": "CLOSED", "isDraft": True}
        before = self.state()
        result = self.tick("--send", code=1, send_code=1)
        self.assertIn("t3 thread send failed", result.stderr)
        self.assertEqual(self.state(), before)
        self.sent()
        self.tick("--send")
        self.assertIn("- acme/app#12: closed", self.sent()[0]["message"])

    def test_with_the_heartbeat_off_send_does_nothing(self):
        self.write_project(heartbeat="none", remote="running")
        self.tick("--send")
        self.assertEqual((self.sent(), (self.dir / "tick.json").exists()), ([], False))

    def test_a_dry_run_prints_without_sending_or_saving(self):
        self.write_project(remote="running")
        result = self.tick()
        self.assertIn("the tick timer hasn't run in 20 minutes", result.stdout)
        self.assertIn("- remote: its thread is on another machine", result.stdout)
        self.assertEqual((self.sent(), (self.dir / "tick.json").exists()), ([], False))

    def test_a_dry_run_from_the_running_coordinator_still_checks_and_warns(self):
        self.threads["lead"] = thread("running", 41)
        self.write_project(remote="running")
        result = self.tick()
        self.assertIn("the tick timer hasn't run in 20 minutes", result.stdout)
        self.assertIn("- remote: its thread is on another machine", result.stdout)

    def test_failed_reads_are_named_on_stderr(self):
        del self.prs["acme/app#12"]
        self.assertIn("tick: can't read PR acme/app#12", self.tick("--send").stderr)
        del self.threads["lead"]
        self.assertIn("tick: can't read the coordinator's thread", self.tick("--send", code=1).stderr)

    def test_tick_sh_ticks_each_project_and_stamps_its_run(self):
        other = self.dir.parent / "parked"
        other.mkdir()
        (other / "project.md").write_text((self.dir / "project.md").read_text().replace("Heartbeat: tick", "Heartbeat: none"))
        self.write_project(remote="running")
        (self.fake / "threads.json").write_text(json.dumps(self.threads))
        (self.fake / "prs.json").write_text(json.dumps(self.prs))
        env = {**os.environ, "FAKE": str(self.fake), "PATH": f"{self.fake / 'bin'}:{os.environ['PATH']}"}
        subprocess.run([str(HERE / "tick.sh"), str(self.dir.parent)], env=env, check=True)
        self.assertEqual([m["to"] for m in self.sent()], ["lead"])
        self.assertLess(time.time() - (self.dir.parent / ".tick").stat().st_mtime, 60)
        self.assertFalse((other / "tick.json").exists())


    def test_a_log_line_before_the_cli_json_still_reads_the_thread(self):
        t3 = self.fake / "bin" / "t3"
        t3.write_text(FAKE_T3.replace('if sys.argv[1:3] == ["thread", "show"]:',
                                      'print("[04:13:56.902] WARN (#29): Database migration history diverges from this build; recorded migration ids are skipped, not reconciled by name. {")\n'
                                      'print("  divergent: [")\n'
                                      'print("    \\\'80:ScheduledTaskThreadMode (unknown to this build)\\\'")\n'
                                      'print("  ]")\n'
                                      'print("}")\n'
                                      'if sys.argv[1:3] == ["thread", "show"]:'))
        self.tick("--send")
        self.threads["w1"] = thread("failed", 1, 12)
        self.tick("--send")
        self.tick("--send")
        self.assertIn("- build: its thread stopped (failed)", self.sent()[0]["message"])

    def test_tick_sh_without_a_coordinator_folder_exits_cleanly(self):
        missing = self.root / "none"
        subprocess.run([str(HERE / "tick.sh"), str(missing)], check=True)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
