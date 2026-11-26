/**
 * A source or the assistant thread that fails, through the CLI: the unit fails on the third failed
 * scan in a row, nothing is lost meanwhile, and no error text reaches a file or the log.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import { SourceError } from "../calls.ts";
import { change } from "../changes.ts";
import { EMPTY_LEDGER } from "../ledger.ts";
import { object, parse, string } from "../parse.ts";
import { scheduleParser } from "../profile.ts";
import { type Context, scanWith } from "../sources/index.ts";
import { Org, THU, linearTime, slackTs } from "./helpers.ts";

test("an expired sign-in fails the unit on the third scan and loses nothing", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.fail = { linear: "auth" };
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("10:30"));
  org.save();
  org.scan("10:05");
  org.scan("11:05");
  assert.match(org.status("11:10"), /linear sign-in expired ×2/);
  const failed = org.scan("12:05", { code: 1 });
  assert.match(failed.stderr, /linear failed 3 scans in a row/);
  assert.equal(org.sent().length, 1);
  delete org.world.fail;
  org.save();
  org.scan("13:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.assigned ENG-103"]);
});

test("a source that never signed in reports what happened since its first attempt once it does", (t) => {
  const org = new Org(t);
  org.world.fail = { linear: "auth" };
  org.save();
  org.scan("08:30");
  org.scan("09:05");
  org.deliver();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:10"));
  delete org.world.fail;
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.assigned ENG-103"]);
});

test("a first scan with --since that a source fails keeps that source's lookback for the next", (t) => {
  const org = new Org(t);
  org.world.fail = { linear: "auth" };
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("08:00"));
  org.save();
  org.scan("10:05", { flags: ["--since", "24h"] });
  org.deliver();
  delete org.world.fail;
  org.save();
  assert.deepEqual(org.found("11:05"), { "ticket.assigned": 1 });
  assert.deepEqual(org.snapshot().starts, {});
});

test("a source error reaches no file or log with its text", (t) => {
  const org = new Org(t);
  org.scan("08:30");
  org.world.fail = { linear: "Could not load the ticket titled PRIVATE-CANARY" };
  org.save();
  const done = org.scan("09:05");
  const status = org.status("09:10");
  assert.doesNotMatch(done.stderr + done.stdout + status + org.stateText(), /PRIVATE-CANARY/);
  assert.match(status, /linear failing ×1/);
  assert.match(status, /⚠️ linear: tools\.linear\.get_notifications: failed$/m);
});

test("an unreadable thread fails the unit on the third scan", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.t3.assistant = null;
  org.save();
  org.scan("10:05");
  org.scan("11:05");
  const failed = org.scan("12:05", { code: 1 });
  assert.match(failed.stderr, /unreadable 3 scans in a row/);
});

test("a value no real source sends fails that source alone, and the scan goes on", (t) => {
  const org = new Org(t);
  org.startDay();
  const [ticket] = org.world.linear.mine;
  assert.ok(ticket);
  ticket.dueDate = "TBD";
  const [thread] = org.world.t3.threads;
  assert.ok(thread);
  thread.snoozedUntil = "soon";
  org.world.slack.messages = [
    { channel: "D0ALEX", ts: "99999999999999999999.1", from: "U0ALEX" },
    { channel: "D0SAM", ts: slackTs("09:20"), from: "U0SAM" },
  ];
  org.save();
  const report = org.report("10:05");
  assert.match(report.health, /^github ok · linear failing ×1 · slack ok · t3 failing ×1 · /);
  assert.match(
    org.status("10:10"),
    /⚠️ linear: tools\.linear\.list_issues: unexpected response at issues\[0\]\.dueDate$/m,
  );
  assert.match(
    org.status("10:10"),
    /⚠️ t3: T3 threads in \/invented\/project: unexpected response at \[0\]\.snoozedUntil$/m,
  );
  assert.deepEqual(
    org.waiting().map((item) => item.channel),
    ["D0SAM"],
  );
});

test("an adapter's unexpected error fails its source by the error's type, never its text", () => {
  const ctx: Context = {
    now: new Date(`${THU}T09:05:00Z`),
    zone: "Europe/Copenhagen",
    schedule: parse(scheduleParser, {}),
    ledger: EMPTY_LEDGER,
    thread: null,
    change: (kind, fields) => change("x", kind, fields),
  };
  const adapter = {
    section: object({ at: string }),
    scan: (): never => {
      throw new RangeError("Invalid time value while reading PRIVATE-CANARY");
    },
  };
  assert.throws(
    () => scanWith({ adapter, source: {}, prev: undefined, fresh: { kind: "baseline" }, ctx }),
    (error) => {
      assert.ok(error instanceof SourceError);
      assert.equal(error.message, "failed unexpectedly (RangeError)");
      return true;
    },
  );
});
