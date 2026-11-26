/** The Linear source, through the CLI: how each inbox item and ticket change is classified. */
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
