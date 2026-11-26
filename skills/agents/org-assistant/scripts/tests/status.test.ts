/** `assistant.ts status`, through the CLI: the health line and each warning, timed by the profile's schedule. */
import assert from "node:assert/strict";
import { test } from "node:test";

import { Org, THU, linearTime } from "./helpers.ts";

const NO_OVERVIEW = /No overview delivered today by/;
const STALE = /The last scan ran \d+ min ago: the timer may be stopped/;

test("status warns when no overview was delivered half an hour after it was due", (t) => {
  const org = new Org(t);
  org.threadIs("running");
  org.scan("08:30");
  org.scan("09:05");
  assert.doesNotMatch(org.status("09:25"), NO_OVERVIEW);
  assert.match(
    org.status("09:35"),
    /⚠️ No overview delivered today by 09:30: the scan or the thread may be broken\./,
  );
});

test("an overview settled from its reply counts as delivered", (t) => {
  const org = new Org(t);
  org.scan("08:30");
  org.scan("09:05");
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  for (const clock of ["10:05", "11:05"]) {
    org.replies(`Posted (batch ${org.pending().sent?.id})`);
    org.scan(clock);
  }
  assert.doesNotMatch(org.status("11:10"), NO_OVERVIEW);
});

test("a pause keeps the missing overview from warning", (t) => {
  const org = new Org(t);
  org.scan("08:30");
  org.ledger(["pause", "2026-11-30T09:00"]);
  org.scan("09:05");
  const status = org.status("09:35");
  assert.doesNotMatch(status, NO_OVERVIEW);
  assert.match(status, /^Paused until Mon 30 Nov 09:00$/m);
});

test("the old-stamp warning starts shortly after the window opens", (t) => {
  const org = new Org(t);
  org.scan("23:05", { day: "2026-11-25" });
  assert.doesNotMatch(org.status("09:10"), STALE); // last night's stamp, before today's first scan
  assert.match(org.status("09:20"), /⚠️ The last scan ran 615 min ago: the timer may be stopped\./);
});

test("the warnings' times come from the profile's schedule", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    profile.schedule = { window: ["10:00", "22:00"], overview: "10:00" };
  });
  org.threadIs("running");
  org.scan("08:30");
  assert.doesNotMatch(org.status("10:10"), STALE);
  const late = org.status("10:20");
  assert.match(late, STALE);
  assert.doesNotMatch(late, NO_OVERVIEW);
  assert.match(org.status("10:35"), /No overview delivered today by 10:30/);
});

test("status shows the batch in flight, what gathered since, and quiet", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  org.scan("10:05");
  org.ledger(["quiet", `${THU}T14:00`]);
  const id = org.pending().sent?.id;
  const status = org.status("10:10");
  assert.match(
    status,
    /^Health: github ok · linear ok · slack ok · t3 ok · scanned Thu 26 Nov 10:05$/m,
  );
  assert.match(status, new RegExp(`^In flight: batch ${id} \\(delta, 1 items, 1 wakes\\)$`, "m"));
  assert.match(status, /^Gathered since: 0 changes$/m);
  assert.match(status, /^Quiet until Thu 26 Nov 14:00$/m);
});

test("status before any scan says so", (t) => {
  const org = new Org(t);
  assert.match(org.status("10:00"), /^Health: no scan has run yet\n⚠️ The last scan ran never/);
});
