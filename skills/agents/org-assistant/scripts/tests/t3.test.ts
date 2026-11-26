/**
 * The T3 source, through the CLI: each thread in the organisation's projects wakes the assistant on
 * its status, by the tiers in the kinds table, and only the threads the user wants to hear about.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import type { T3Thread } from "./fakes.ts";
import { Org, SAT, utc } from "./helpers.ts";

const LINK = "https://example.invalid/t-other";

/** The fixture's other thread, which the tests turn. */
function other(org: Org): T3Thread {
  const found = org.world.t3.threads.find((thread) => thread.threadId === "t-other");
  assert.ok(found);
  return found;
}

/** A thread in the organisation's project, as `t3 thread list` lists it. */
function thread(id: string, fields: Partial<T3Thread> = {}): T3Thread {
  return {
    threadId: id,
    status: "idle",
    settled: false,
    snoozed: false,
    snoozedUntil: null,
    parentThreadId: null,
    itemCount: 3,
    latestRunId: `r-${id}`,
    createdAt: utc("09:00"),
    updatedAt: utc("09:00"),
    link: `https://example.invalid/${id}`,
    ...fields,
  };
}

/** The fixture's other thread, completed at the start, ends a second run. */
function finishRun(org: Org): void {
  Object.assign(other(org), { status: "completed", itemCount: 20, latestRunId: "r-other-2" });
  org.save();
}

function turn(org: Org, status: string, itemCount?: number): void {
  Object.assign(other(org), { status, ...(itemCount === undefined ? {} : { itemCount }) });
  org.save();
}

test("a thread that turns waiting wakes the assistant at the next scan, with its id, link, and counts", (t) => {
  const org = new Org(t);
  org.startDay();
  turn(org, "running", 13);
  org.scan("10:05");
  assert.equal(org.sent().length, 1);
  turn(org, "waiting", 15);
  org.scan("11:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["thread.waiting t3:t-other"]);
  assert.deepEqual(org.pending().sent?.items[0]?.detail, {
    status: "waiting",
    link: LINK,
    items: 15,
    started: false,
  });
});

test("a thread that turns failed wakes the assistant at the next scan", (t) => {
  const org = new Org(t);
  org.startDay();
  turn(org, "failed");
  org.scan("10:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["thread.failed t3:t-other"]);
});

test("a thread that finished waits for the next batch slot", (t) => {
  const org = new Org(t);
  org.startDay();
  turn(org, "running", 13);
  org.scan("11:05");
  turn(org, "completed", 20);
  assert.deepEqual(org.found("12:05"), { "thread.finished": 1 });
  assert.equal(org.sent().length, 1);
  org.scan("13:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["thread.finished t3:t-other"]);
});

test("a thread running an hour with no new item is stalled, once per stall", (t) => {
  const org = new Org(t);
  org.startDay();
  turn(org, "running", 13);
  assert.deepEqual(org.found("10:05"), {});
  assert.deepEqual(org.found("10:35"), {}); // half an hour: still working
  assert.deepEqual(org.found("11:05"), { "thread.stalled": 1 });
  assert.deepEqual(org.found("12:05"), {});
  turn(org, "running", 14); // a new item ends the stall, so the batch slot finds it gone
  assert.deepEqual(org.found("13:05"), {});
  assert.equal(org.sent().length, 1);
  assert.deepEqual(org.found("14:05"), { "thread.stalled": 1 });
  assert.deepEqual(org.kinds(org.lastSent()), ["thread.stalled t3:t-other"]);
  assert.deepEqual(org.pending().sent?.items[0]?.detail, {
    status: "running",
    link: LINK,
    items: 14,
    started: false,
  });
});

test("a thread that ends a second run the same way between scans counts again", (t) => {
  const org = new Org(t);
  org.startDay();
  finishRun(org);
  assert.deepEqual(org.found("10:05"), { "thread.finished": 1 });
  Object.assign(other(org), { latestRunId: "r-other-3", itemCount: 30 });
  org.save();
  assert.deepEqual(org.found("11:05"), { "thread.finished": 1 });
  turn(org, "waiting", 34);
  org.scan("12:05");
  org.deliver();
  Object.assign(other(org), { latestRunId: "r-other-4", itemCount: 40 });
  org.save();
  assert.deepEqual(org.found("13:05"), { "thread.waiting": 1 });
});

test("a gathered change for a thread that has left the watch since is dropped before the wake", (t) => {
  const leave: [string, (thread: T3Thread) => void][] = [
    ["settled", (thread) => (thread.settled = true)],
    ["snoozed", (thread) => (thread.snoozedUntil = utc("18:00"))],
    ["archived", (thread) => (thread.archived = true)],
    ["made a child", (thread) => (thread.parentThreadId = "t-parent")],
  ];
  for (const [how, edit] of leave) {
    const org = new Org(t);
    org.startDay();
    org.world.t3.threads.push(thread("t-new"));
    finishRun(org);
    assert.deepEqual(org.found("10:05"), { "thread.finished": 1, "thread.started": 1 }, how);
    for (const entry of org.world.t3.threads) edit(entry);
    org.save();
    org.scan("11:05");
    assert.deepEqual(org.pending().gathered, [], how);
  }
  const org = new Org(t);
  org.startDay();
  finishRun(org);
  org.scan("10:05");
  org.world.t3.threads = org.world.t3.threads.filter((entry) => entry.threadId !== "t-other");
  org.save();
  org.scan("13:05");
  assert.deepEqual(org.pending().gathered, [], "gone");
  assert.equal(org.sent().length, 1);
});

test("a thread new since the last scan is pulse, and one that already waits wakes as waiting too", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.t3.threads.push(thread("t-new"));
  org.save();
  assert.deepEqual(org.found("10:05"), { "thread.started": 1 });
  assert.equal(org.sent().length, 1);
  org.world.t3.threads.push(thread("t-asks", { status: "waiting" }));
  org.save();
  org.scan("11:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["2 thread.started", "thread.waiting t3:t-asks"]);
});

test("only threads the user would want count: not the assistant's, a settled, snoozed, child, or archived one", (t) => {
  const org = new Org(t);
  const ahead = utc("18:00");
  const ended = utc("08:00");
  org.world.t3.threads.push(
    thread("t-settled", { settled: true }),
    thread("t-snoozed", { snoozed: true, snoozedUntil: ahead }),
    thread("t-woke", { snoozed: false, snoozedUntil: ended }),
    thread("t-child", { parentThreadId: "t-other" }),
    thread("t-archived", { archived: true }),
  );
  org.save();
  org.startDay();
  for (const entry of org.world.t3.threads) entry.status = "waiting";
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.kinds(org.lastSent()), [
    "thread.waiting t3:t-other",
    "thread.waiting t3:t-woke",
  ]);
});

test("a thread the assistant started carries started and its ticket", (t) => {
  const org = new Org(t);
  org.startDay();
  org.ledger(["started", "t-other", "--ticket", "ENG-101"]);
  turn(org, "waiting");
  org.scan("10:05");
  assert.deepEqual(org.pending().sent?.items[0]?.detail, {
    status: "waiting",
    link: LINK,
    items: 12,
    started: true,
    ticket: "ENG-101",
  });
});

test("a thread answered before the wake went out leaves the gathered list", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  turn(org, "waiting");
  org.scan("10:05");
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["thread.waiting"],
  );
  org.threadIs("completed");
  turn(org, "running", 14);
  org.scan("11:05");
  assert.equal(org.sent().length, 1);
  assert.deepEqual(org.pending().gathered, []);
});

test("a thread's turn read again after a crash joins once", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  turn(org, "waiting");
  org.crashAfterPending("10:05");
  org.scan("11:05");
  assert.deepEqual(
    org.pending().gathered.map((item) => `${item.kind} ${item.ref}`),
    ["thread.waiting t3:t-other"],
  );
});

test("a waiting thread doesn't wake the assistant on a weekend", (t) => {
  const org = new Org(t);
  org.scan("08:30", { day: SAT });
  turn(org, "waiting");
  assert.deepEqual(org.found("10:05", { day: SAT }), { "thread.waiting": 1 });
  assert.deepEqual(org.sent(), []);
});

test("with --since on a first scan, only threads created since count", (t) => {
  const org = new Org(t);
  org.world.t3.threads.push(thread("t-new", { status: "waiting", createdAt: utc("08:00") }));
  other(org).status = "waiting"; // created two days ago
  org.save();
  const report = org.report("10:05", { flags: ["--dry-run", "--since", "24h"] });
  assert.deepEqual(
    report.items
      .filter((item) => item.ref.startsWith("t3:"))
      .map((item) => `${item.kind} ${item.ref}`),
    ["thread.started t3:t-new", "thread.waiting t3:t-new"],
  );
});
