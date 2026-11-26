/**
 * The batch's lifecycle through the CLI: a sent batch stays frozen until it is delivered, by the
 * ledger or the thread's own reply; an undelivered one goes once more, then fails the unit; and a
 * crash, a busy thread, or an inline scan between two scans loses nothing and sends nothing twice.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import { Org, linearTime, utc } from "./helpers.ts";

test("a sent batch stays frozen while in flight, and the next batch carries what waited", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  org.scan("10:05");
  const first = org.pending().sent;
  org.note("n2", "issueCommentMention", "ENG-101", linearTime("10:30"));
  org.threadIs("running");
  org.scan("11:05"); // busy: nothing sent, the batch unchanged, the new change gathered beside it
  assert.equal(org.sent().length, 2);
  assert.deepEqual(org.pending().sent, first);
  assert.deepEqual(
    org.pending().gathered.map((item) => item.ref),
    ["ENG-101"],
  );
  org.threadIs("completed");
  org.scan("12:05"); // idle and undelivered: the same batch once more, still without the new change
  assert.equal(org.sent().length, 3);
  assert.match(
    org.lastSent()?.message ?? "",
    new RegExp(`batch="${first?.id}" kind="delta" try="2"`),
  );
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.assigned ENG-103"]);
  org.deliver(first?.id);
  org.scan("13:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.mention ENG-101"]);
});

test("a reply that names the batch counts as delivered, and one that names a longer id doesn't", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  org.scan("10:05");
  const batch = org.pending().sent?.id;
  org.replies(`Earlier news. (batch ${batch}1)`);
  org.scan("11:05");
  assert.equal(org.sent().length, 3); // not that batch: resent
  org.replies(`Two things need you. (batch ${batch})`);
  org.scan("12:05");
  assert.equal(org.sent().length, 3);
  assert.equal(org.pending().sent, null);
});

test("a thread that turns busy while the sources are read gets the wake at the next scan", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.world.t3.shows = ["completed", "running"]; // idle when the scan starts, busy before it sends
  org.save();
  org.scan("10:05");
  assert.equal(org.sent().length, 1);
  assert.deepEqual(org.pending().sent?.tries, []);
  delete org.world.t3.shows;
  org.save();
  org.scan("11:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.assigned ENG-103"]);
  assert.match(org.lastSent()?.message ?? "", /try="1"/);
});

test("a failed wake is retried once, then fails the unit", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.world.t3.send_code = 1;
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.pending().sent?.tries, [{ at: utc("10:05"), ok: false }]);
  const retried = org.scan("11:05", { code: 1 }); // the retry failed too: the unit fails now, not an hour later
  assert.match(retried.stderr, /last wake failed to send/);
  const stopped = org.scan("12:05", { code: 1 });
  assert.match(stopped.stderr, /undelivered after 2 wakes/);
  assert.equal(org.sent().length, 3);
});

test("a crash between the two state writes sends one overview", (t) => {
  const org = new Org(t);
  org.scan("08:30");
  org.crashAfterPending("09:05");
  org.scan("10:05");
  org.deliver();
  org.scan("11:05");
  const overviews = new Set(
    org
      .sent()
      .filter((sent) => sent.message.includes('kind="overview"'))
      .map((sent) => /batch="([^"]+)"/.exec(sent.message)?.[1]),
  );
  assert.equal(overviews.size, 1);
});

test("a batch delivered after its scan crashed isn't sent again when the next scan replays its events", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  org.crashAfterPending("10:05");
  org.deliver();
  assert.deepEqual(org.found("11:05"), {}); // the same event, read again, is no news
  assert.equal(org.sent().length, 2);
  assert.deepEqual(org.pending().gathered, []);
});

test("a busy thread gets nothing until it is idle", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  org.note("n1", "issueCommentMention", "ENG-101", linearTime("10:30"));
  org.save();
  org.scan("10:05");
  org.scan("11:05");
  assert.equal(org.sent().length, 1);
  org.threadIs("completed");
  org.scan("12:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.mention ENG-101"]);
});

test("an inline scan freezes everything for the run and wakes nothing", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("10:30"));
  org.threadIs("running"); // the run that asked for it
  const report = org.report("10:20", { flags: ["--inline"] });
  assert.deepEqual(
    report.items.map((item) => item.ref),
    ["ENG-103"],
  );
  assert.equal(report.batch_items?.length, 1);
  assert.equal(org.sent().length, 1);
  org.deliver(report.batch ?? "");
  org.threadIs("completed");
  org.scan("11:05");
  assert.equal(org.sent().length, 1);
});

test("an inline scan leaves the batch in flight frozen and reports it", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  org.scan("10:05");
  const frozen = org.pending().sent;
  org.note("n2", "issueCommentMention", "ENG-101", linearTime("10:10"));
  org.save();
  const first = org.report("10:15", { flags: ["--inline"] });
  const second = org.report("10:16", { flags: ["--inline"] });
  assert.deepEqual(org.pending().sent, frozen);
  assert.equal(first.in_flight?.id, frozen?.id);
  assert.deepEqual(
    second.items.map((item) => item.ref),
    ["ENG-101"],
  );
  assert.equal(new Set([frozen?.id, first.batch, second.batch]).size, 3);
});

test("an inline batch stays frozen while its run goes on, so the run can still post it", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  const { batch } = org.report("10:05", { flags: ["--inline"] });
  org.scan("10:40"); // the run is still going, well past half an hour
  assert.equal(org.pending().inline?.id, batch);
  assert.deepEqual(org.pending().gathered, []);
  org.deliver(batch ?? "");
  org.threadIs("completed");
  org.scan("11:05");
  assert.equal(org.sent().length, 1);
  assert.equal(org.pending().inline, null);
});

test("an inline batch whose run ended without posting it goes back to gathered", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  org.scan("10:05", { flags: ["--inline"] });
  org.threadIs("completed");
  org.scan("10:10");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.assigned ENG-103"]);
});

test("an inline batch the thread's last reply names counts as posted", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  const { batch } = org.report("10:05", { flags: ["--inline"] });
  org.threadIs("completed");
  org.replies(`One thing needs you. (batch ${batch})`);
  org.scan("11:05");
  assert.equal(org.sent().length, 1);
  assert.equal(org.pending().inline, null);
});

test("team counts made while a batch is in flight wait beside it", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.teamFinish("ENG-201", "09:30");
  org.scan("10:05");
  assert.ok(org.batch().includes("team.pulse ENG-201"));
  const [sam] = org.world.linear.team.ENG ?? [];
  assert.ok(sam);
  Object.assign(sam, {
    status: "Done",
    statusType: "completed",
    updatedAt: linearTime("10:30"),
    completedAt: linearTime("10:30"),
  });
  org.threadIs("running");
  org.scan("11:05");
  assert.equal(org.pending().gathered[0]?.kind, "team.pulse");
});
