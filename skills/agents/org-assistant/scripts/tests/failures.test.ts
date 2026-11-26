/**
 * A source or the assistant thread that fails, through the CLI: the unit fails on the third failed
 * scan in a row, nothing is lost meanwhile, and no error text reaches a file or the log.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import { Org, linearTime } from "./helpers.ts";

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
