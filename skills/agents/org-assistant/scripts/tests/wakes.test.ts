/**
 * Which change wakes the thread and when, through the CLI: the overview, a change worth a wake, the
 * batch slots, the day's cap, weekends, quiet and pause, and the first scan's baseline.
 */
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

import { FRI, Org, SAT, THU, linearTime, slackTs, utc } from "./helpers.ts";

test("the first scan records a baseline and wakes nothing", (t) => {
  const org = new Org(t);
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("08:00"));
  org.save();
  const report = org.report("10:05");
  assert.equal(report.first, true);
  assert.equal(report.wake, null);
  assert.deepEqual(org.sent(), []);
  org.scan("11:05");
  assert.match(org.lastSent()?.message ?? "", /kind="overview"/);
  assert.deepEqual(org.batch(), []);
});

test("a wake tells the run the command that prints its batch", (t) => {
  const org = new Org(t);
  org.scan("08:30");
  org.scan("09:05");
  const id = org.pending().sent?.id;
  assert.ok(id);
  const message = org.lastSent()?.message ?? "";
  assert.ok(message.includes(`node scripts/assistant.ts batch acme ${id}`), message);
  assert.doesNotMatch(message, /pending\.json/);
});

test("a wake names each change worth one, counts the pulse, and carries each change once", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueCommentMention", "ENG-101", linearTime("09:40"));
  org.teamFinish("ENG-201", "09:20");
  org.world.github["example/api"]?.releases?.unshift({
    tagName: "v1.1.0",
    isDraft: false,
    publishedAt: utc("09:10"),
  });
  org.save();
  org.scan("10:05");
  const message = org.lastSent()?.message ?? "";
  assert.deepEqual(org.kinds(org.lastSent()), [
    "1 release.new",
    "1 team.pulse",
    "ticket.mention ENG-101",
  ]);
  assert.match(
    message,
    /^<org-assistant org="acme" batch="acme-20261126-1005-\d+" kind="delta" try="1">$/m,
  );
  assert.match(message, /^Why now: a change worth a wake\. 3 items: /m);
  assert.match(
    message,
    /^Health: github ok · linear ok · slack ok · t3 ok · scanned Thu 26 Nov 10:05$/m,
  );
  org.deliver();
  org.scan("11:05"); // the same sources again: nothing new, so nothing is sent
  assert.equal(org.sent().length, 2);
});

test("a batched change waits for the next batch slot", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.linear.team.ENG?.push({
    id: "ENG-301",
    status: "Todo",
    statusType: "unstarted",
    assignee: "Alex Example",
    assigneeId: "u-alex",
    createdAt: linearTime("10:00"),
    updatedAt: linearTime("10:00"),
    project: "Invented Project",
  });
  org.save();
  org.scan("11:05");
  org.scan("12:05");
  assert.equal(org.sent().length, 1);
  org.scan("13:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.new_in_project ENG-301"]);
});

test("a missed scan loses nothing and sends the overview late", (t) => {
  const org = new Org(t);
  org.scan("08:30");
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("08:40"));
  org.world.linear.team.ENG?.push({
    id: "ENG-302",
    status: "Todo",
    statusType: "unstarted",
    assignee: "Alex Example",
    assigneeId: "u-alex",
    createdAt: linearTime("11:00"),
    updatedAt: linearTime("11:00"),
    project: "Invented Project",
  });
  org.save();
  org.scan("14:05"); // the timer missed 09:05 to 13:05
  assert.equal(org.sent().length, 1);
  assert.match(org.sent()[0]?.message ?? "", /kind="overview"/);
  assert.deepEqual(org.kinds(org.sent()[0]), [
    "ticket.assigned ENG-103",
    "ticket.new_in_project ENG-302",
  ]);
  org.deliver();
  org.scan("15:05");
  assert.equal(org.sent().length, 1);
});

test("past the daily cap only urgent changes wake", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    profile.schedule = { daily_deltas: 1 };
  });
  org.startDay();
  org.note("n1", "issueStatusChanged", "ENG-101", linearTime("09:30"));
  org.save();
  org.scan("10:05"); // the day's one delta
  org.deliver();
  const [pr] = org.world.github["example/web"]?.mine ?? [];
  assert.ok(pr);
  Object.assign(pr, {
    statusCheckRollup: [{ status: "COMPLETED", conclusion: "FAILURE" }],
    updatedAt: utc("10:30"),
  });
  org.save();
  org.scan("11:05");
  assert.equal(org.sent().length, 2);
  org.note("n2", "issueCommentMention", "ENG-101", linearTime("11:30"));
  org.save();
  org.scan("12:05");
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.mention ENG-101"]);
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["pr.ci_failed"],
  );
});

test("weekends wake only for urgent changes", (t) => {
  const org = new Org(t);
  org.scan("08:30", { day: SAT });
  const [pr] = org.world.github["example/web"]?.mine ?? [];
  assert.ok(pr);
  Object.assign(pr, {
    statusCheckRollup: [{ status: "COMPLETED", conclusion: "FAILURE" }],
    updatedAt: utc("10:00", SAT),
  });
  org.save();
  org.scan("10:05", { day: SAT });
  assert.deepEqual(org.sent(), []);
  org.note("n1", "issueCommentMention", "ENG-101", linearTime("10:30", SAT));
  org.save();
  org.scan("11:05", { day: SAT });
  assert.deepEqual(org.kinds(org.lastSent()), ["ticket.mention ENG-101"]);
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["pr.ci_failed"],
  );
});

test("quiet lets the overview through, and pause holds a retry", (t) => {
  const org = new Org(t);
  org.scan("08:30");
  org.ledger(["quiet", `${THU}T14:00`]);
  org.scan("09:05");
  assert.match(org.lastSent()?.message ?? "", /kind="overview"/);
  org.ledger(["pause", "2026-11-30T09:00"]);
  org.scan("10:05");
  assert.equal(org.sent().length, 1);
});

test("a delta quiet holds overnight joins the next overview", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("21:30"));
  org.save();
  org.scan("22:05");
  org.ledger(["quiet", `${FRI}T14:00`], utc("08:00", FRI));
  org.scan("09:05", { day: FRI });
  assert.match(org.lastSent()?.message ?? "", /kind="overview"/);
  assert.ok(org.batch().includes("ticket.assigned ENG-103"));
});

test("a held delta rejoins the overview before mutes and answered messages are applied", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  const messages = org.world.slack.messages;
  messages.push({ channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX" });
  org.save();
  org.scan("10:05");
  org.ledger(["quiet", `${FRI}T14:00`], utc("10:10"));
  org.ledger(["mute", "ENG-103"], utc("10:10"));
  messages.push({ channel: "D0ALEX", ts: slackTs("10:15"), from: "U0ME" });
  org.save();
  org.scan("11:05");
  org.scan("09:05", { day: FRI });
  assert.equal(org.pending().sent?.kind, "overview");
  assert.deepEqual(org.batch(), []);
});

test("a dry run writes and sends nothing, and counts from --since on a first scan", (t) => {
  const org = new Org(t);
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  const report = org.report("10:05", { flags: ["--dry-run", "--since", "24h"] });
  assert.equal(report.wake, "overview");
  assert.ok(report.items.some((item) => item.kind === "ticket.assigned"));
  assert.match(report.would_send ?? "", /^<org-assistant org="acme"/);
  assert.deepEqual(org.sent(), []);
  assert.equal(existsSync(join(org.root, "state")), false);
});
