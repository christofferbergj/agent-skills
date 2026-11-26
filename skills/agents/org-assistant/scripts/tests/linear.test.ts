/**
 * The Linear source, through the CLI: how each inbox item and ticket change is classified, and what
 * a read past its cap leaves out and says in the health line.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import { LINEAR_TOOLS, Org, THU, linearTime } from "./helpers.ts";

/** The `kind ref` pairs the last scan found, from its gathered list and the batch it froze. */
function caught(org: Org): string[] {
  const { sent, gathered } = org.pending();
  return [...(sent?.items ?? []), ...gathered].map((item) => `${item.kind} ${item.ref}`).sort();
}

test("each inbox item and ticket change is classified", (t) => {
  const org = new Org(t);
  org.startDay();
  const linear = org.world.linear;
  const [mine101, mine102] = linear.mine;
  assert.ok(mine101 && mine102);
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  linear.mine.push({ ...mine102, id: "ENG-103", updatedAt: linearTime("09:30") });
  org.note("n2", "issueCommentMention", "ENG-101", linearTime("09:40"));
  // Someone else moved ENG-101 (the inbox says so); the user moved ENG-102 themselves.
  org.note("n3", "issueStatusChanged", "ENG-101", linearTime("09:45"));
  for (const [ticket, status, clock] of [
    [mine101, "In Review", "09:45"],
    [mine102, "In Progress", "09:50"],
  ] as const) {
    linear.issues[ticket.id]?.stateHistory?.push({
      state: { name: status },
      startedAt: linearTime(clock),
      endedAt: null,
    });
    Object.assign(ticket, { status, updatedAt: linearTime(clock) });
  }
  const [sam] = linear.team.ENG ?? [];
  assert.ok(sam);
  Object.assign(sam, {
    status: "Done",
    statusType: "completed",
    updatedAt: linearTime("09:20"),
    completedAt: linearTime("09:20"),
  });
  linear.team.ENG?.push({
    id: "ENG-300",
    status: "Todo",
    statusType: "unstarted",
    assignee: "Sam Sample",
    assigneeId: "u-sam",
    createdAt: linearTime("09:25"),
    updatedAt: linearTime("09:25"),
    project: "Invented Project",
  });
  Object.assign(linear.issues["ENG-200"] ?? {}, { status: "Done", statusType: "completed" });
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.batch(), [
    "team.pulse ENG-200",
    "ticket.assigned ENG-103",
    "ticket.changed ENG-101",
    "ticket.mention ENG-101",
    "ticket.moved ENG-102",
    "ticket.new_in_project ENG-300",
    "ticket.unblocked ENG-102",
  ]);
  const pulse = org.pending().sent?.items.find((item) => item.kind === "team.pulse");
  assert.deepEqual(pulse?.detail, { team: "ENG", who: "Sam Sample", finished: true });
  const unblocked = org.pending().sent?.items.find((item) => item.kind === "ticket.unblocked");
  assert.deepEqual(unblocked?.detail, { blocker: "ENG-200", to: "Done" });
});

test("a priority or due date change counts as someone else's, and a deadline within 24 hours wakes once", (t) => {
  const org = new Org(t);
  org.startDay();
  const [ticket] = org.world.linear.mine;
  assert.ok(ticket);
  Object.assign(ticket, { priority: { value: 1, name: "Urgent" }, updatedAt: linearTime("09:30") });
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.batch(), ["ticket.changed ENG-101"]);
  assert.deepEqual(org.pending().sent?.items[0]?.detail, {
    field: "priority",
    to: 1,
    by: "unknown",
  });
  org.deliver();
  Object.assign(ticket, { dueDate: THU, updatedAt: linearTime("10:30") });
  org.save();
  org.scan("11:05");
  assert.deepEqual(org.batch(), ["deadline.soon ENG-101", "ticket.changed ENG-101"]);
  org.deliver();
  assert.deepEqual(org.found("12:05"), {});
});

test("a blocker of the user's ticket that moves is a batched dependency change, kept while unreadable", (t) => {
  const org = new Org(t);
  org.startDay();
  Object.assign(org.world.linear.issues["ENG-200"] ?? {}, {
    status: "In Review",
    updatedAt: linearTime("09:30"),
  });
  org.save();
  assert.deepEqual(org.found("10:05"), { "dependency.changed": 1 });
  const change = org.pending().gathered[0];
  assert.deepEqual(change?.detail, {
    blocks: "ENG-102",
    before: "In Progress",
    to: "In Review",
    owner: "Sam Sample",
  });
  org.world.unreadable = ["ENG-200"];
  org.save();
  org.scan("11:05");
  assert.equal(org.snapshot().health.linear?.ok, true); // one ticket it can't load doesn't stop the source
  delete org.world.unreadable;
  org.save();
  assert.deepEqual(org.found("12:05"), {}); // the last state it read stood in meanwhile
});

test("a ticket someone closed or took since the last scan still counts as the user's", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueStatusChanged", "ENG-101", linearTime("09:30"));
  Object.assign(org.world.linear.mine[0] ?? {}, { status: "Canceled", statusType: "canceled" });
  org.save();
  assert.deepEqual(org.found("10:05"), { "ticket.changed": 1 });
});

test("a comment on someone else's ticket is pulse, not news", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueNewComment", "ENG-999", linearTime("09:30"));
  org.save();
  assert.deepEqual(org.found("10:05"), { "linear.other": 1 });
  assert.equal(org.sent().length, 1);
});

test("inbox times in another format still compare in order", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", `${THU}T08:30:00Z`);
  org.save();
  org.scan("10:05");
  org.deliver();
  org.note("n2", "issueAssignedToYou", "ENG-104", `${THU}T08:30:00.500Z`);
  org.save();
  assert.deepEqual(org.found("11:05"), { "ticket.assigned": 1 });
});

test("the scan calls only the tools its profile lists", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    const [linear] = profile.sources;
    assert.ok(linear);
    linear.tools = LINEAR_TOOLS.filter((tool) => !tool.endsWith("get_issue"));
  });
  org.scan("08:30");
  assert.ok(org.probed().every((call) => call.path !== "tools.linear.get_issue"));
  const health = org.snapshot().health.linear;
  assert.equal(
    health?.ok === false && health.message,
    "tools.linear.get_issue is not in this source's tools",
  );
});

test("a team finish after a crash still counts", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  org.teamFinish("ENG-201", "09:30");
  org.crashAfterPending("10:05");
  org.teamFinish("ENG-202", "10:30");
  org.scan("11:05");
  assert.deepEqual(caught(org), ["team.pulse ENG-201", "team.pulse ENG-202"]);
});

test("a finish edited before crash recovery counts once", (t) => {
  const org = new Org(t);
  org.startDay();
  org.threadIs("running");
  const ticket = org.teamFinish("ENG-201", "09:30");
  org.crashAfterPending("10:05");
  ticket.updatedAt = linearTime("10:30");
  org.save();
  org.scan("11:05");
  assert.deepEqual(caught(org), ["team.pulse ENG-201"]);
});

/** `clock` plus `seconds`, as Linear writes the time. */
const later = (clock: string, seconds: number) =>
  new Date(Date.parse(linearTime(clock)) + seconds * 1000).toISOString();

/** The health line's entry for Linear, from what `status` prints. */
const health = (org: Org, clock: string) =>
  /^Health: .*?\blinear ([^·]*)/m.exec(org.status(clock))?.[1]?.trim();

test("an inbox read past the cap reads the newest items, says so, and next time reads only newer ones", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.linear.page_size = 1; // twenty pages then hold 20 items
  // 21 items at one time: the read past the cap takes 20, and the 21st stays unread.
  for (let n = 0; n < 21; n++) org.note(`n${n}`, "issueSubscribed", "ENG-999", linearTime("09:10"));
  org.save();
  assert.deepEqual(org.found("10:05"), { "linear.other": 20 });
  assert.equal(health(org, "10:10"), "ok, inbox capped at 1,000: older items unread");
  org.note("n-new", "issueAssignedToYou", "ENG-103", linearTime("10:30"));
  org.save();
  assert.deepEqual(org.found("11:05"), { "ticket.assigned": 1 });
  assert.equal(health(org, "11:10"), "ok");
  assert.deepEqual(org.found("12:05"), {});
});

test("a scan after a read past the cap starts the inbox from its first page", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.linear.page_size = 1;
  for (let n = 0; n < 25; n++) org.note(`n${n}`, "issueSubscribed", "ENG-999", later("09:10", n));
  org.save();
  org.scan("10:05");
  const before = org.probed().length;
  org.scan("11:05");
  const [first] = org
    .probed()
    .slice(before)
    .filter((call) => call.path.endsWith("notifications"));
  assert.deepEqual(first?.input, { limit: 50 });
});

test("a status change whose inbox item is past the cap counts once, as the user's own", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.linear.page_size = 1;
  const [ticket] = org.world.linear.mine;
  assert.ok(ticket);
  org.world.linear.issues[ticket.id]?.stateHistory?.push({
    state: { name: "In Review" },
    startedAt: linearTime("09:30"),
    endedAt: null,
  });
  Object.assign(ticket, { status: "In Review", updatedAt: linearTime("09:30") });
  org.note("n-status", "issueStatusChanged", ticket.id, linearTime("09:30"));
  for (let n = 0; n < 20; n++) org.note(`n${n}`, "issueSubscribed", "ENG-999", later("09:40", n));
  org.save();
  assert.deepEqual(org.found("10:05"), { "linear.other": 20, "ticket.moved": 1 });
  assert.deepEqual(org.found("11:05"), {});
});

test("an assigned list past the cap says so, and keeps the tickets it didn't reach", (t) => {
  const org = new Org(t);
  org.startDay();
  const [template] = org.world.linear.mine;
  assert.ok(template);
  org.world.linear.page_size = 2;
  const more = Array.from({ length: 40 }, (_, n) => ({ ...template, id: `ENG-${500 + n}` }));
  org.world.linear.mine.unshift(...more);
  org.save();
  org.scan("10:05");
  assert.equal(
    health(org, "10:10"),
    "ok, assigned tickets capped at 5,000: the rest kept as last read",
  );
  org.note("n1", "issueNewComment", "ENG-101", linearTime("10:30"));
  org.save();
  assert.deepEqual(org.found("11:05"), { "ticket.comment": 1 });
});

test("a team read past the cap says so, and the next scan reads on from its time", (t) => {
  const org = new Org(t);
  org.startDay();
  const [sam] = org.world.linear.team.ENG ?? [];
  assert.ok(sam);
  org.world.linear.page_size = 2;
  const created = { createdAt: linearTime("09:30"), updatedAt: linearTime("09:30") };
  const tickets = Array.from({ length: 41 }, (_, n) => ({
    ...sam,
    ...created,
    id: `ENG-${600 + n}`,
  }));
  org.world.linear.team.ENG?.push(...tickets);
  org.save();
  assert.deepEqual(org.found("10:05"), { "team.pulse": 40 });
  assert.equal(health(org, "10:10"), "ok, team ENG capped at 5,000: the rest unread");
  assert.deepEqual(org.found("11:05"), {});
  assert.equal(health(org, "11:10"), "ok");
});
