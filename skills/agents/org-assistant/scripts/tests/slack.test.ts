/**
 * The Slack source, through the CLI: the waiting list of DMs and mentions, the reply that takes one
 * off it, the search watermarks and the scan's call budget, and the record parser a message body
 * can't fool.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import type { SlackMessage } from "./fakes.ts";
import { Org, slackTs } from "./helpers.ts";

test("a DM wakes the thread after 30 unanswered minutes, across two scans, once", (t) => {
  const org = new Org(t);
  org.startDay();
  const dm = { channel: "D0ALEX", ts: slackTs("10:00"), from: "U0ALEX" };
  org.world.slack.messages = [dm, { channel: "D0SAM", ts: slackTs("10:01"), from: "U0SAM" }];
  org.save();
  org.scan("10:05"); // five minutes old: kept waiting, no wake
  assert.equal(org.sent().length, 1);
  assert.deepEqual(
    org
      .waiting()
      .map((item) => item.channel)
      .sort(),
    ["D0ALEX", "D0SAM"],
  );
  org.world.slack.messages.push({ channel: "D0SAM", ts: slackTs("10:20"), from: "U0ME" });
  org.save();
  org.scan("11:05"); // the cursor moved past both; the waiting list still holds the unanswered one
  assert.deepEqual(org.kinds(org.lastSent()), [`slack.waiting slack:D0ALEX:${dm.ts}`]);
  assert.deepEqual(org.pending().sent?.items[0]?.detail, {
    via: "dm",
    channel: "D0ALEX",
    minutes: 65,
  });
  org.deliver();
  assert.deepEqual(org.found("12:05"), {}); // it woke the thread once, so it isn't news again
  assert.equal(org.sent().length, 2);
});

test("a reply found in the same scan as the DM wakes nothing", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = [
    { channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX" },
    { channel: "D0ALEX", ts: slackTs("09:25"), from: "U0ME" },
  ];
  org.save();
  org.scan("10:05");
  assert.equal(org.sent().length, 1);
  assert.deepEqual(org.waiting(), []);
});

test("a DM answered while the thread was busy leaves the gathered list before the wake", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = [{ channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX" }];
  org.threadIs("running");
  org.scan("10:05");
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["slack.waiting"],
  );
  org.world.slack.messages.push({ channel: "D0ALEX", ts: slackTs("10:15"), from: "U0ME" });
  org.threadIs("completed");
  org.scan("11:05");
  assert.equal(org.sent().length, 1);
});

test("a DM answered after an abandoned inline scan wakes nothing", (t) => {
  const org = new Org(t);
  org.startDay();
  const messages = org.world.slack.messages;
  messages.push({ channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX" });
  org.save();
  org.scan("10:05", { flags: ["--inline"] });
  messages.push({ channel: "D0ALEX", ts: slackTs("10:15"), from: "U0ME" });
  org.save();
  org.scan("11:05");
  assert.equal(org.sent().length, 1);
});

test("a mention in a channel thread is answered by a reply in that thread", (t) => {
  const org = new Org(t);
  org.startDay();
  const asked = {
    channel: "C0DEV",
    ts: slackTs("09:10"),
    from: "U0ALEX",
    mentions: ["U0ME"],
    name: "dev",
  };
  const elsewhere = {
    channel: "C0DEV",
    ts: slackTs("09:15"),
    from: "U0SAM",
    mentions: ["U0ME"],
    name: "dev",
  };
  org.world.slack.messages = [
    asked,
    elsewhere,
    { channel: "C0DEV", ts: slackTs("09:20"), from: "U0ME", thread: asked.ts, name: "dev" },
  ];
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.kinds(org.lastSent()), [
    "2 slack.channel",
    `slack.waiting slack:C0DEV:${elsewhere.ts}`,
  ]);
  const waits = org.pending().sent?.items.find((item) => item.kind === "slack.waiting");
  assert.deepEqual(waits?.detail, { via: "mention", channel: "C0DEV", minutes: 50 });
});

test("a confirmed channel's messages count in the pulse, except the user's own", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = [
    { channel: "C0DEV", ts: slackTs("09:10"), from: "U0ALEX", name: "dev" },
    { channel: "C0DEV", ts: slackTs("09:11"), from: "U0ME", name: "dev" },
    { channel: "C0OTHER", ts: slackTs("09:12"), from: "U0ALEX", name: "other" },
  ];
  org.save();
  assert.deepEqual(org.found("10:05"), { "slack.channel": 1 });
  assert.deepEqual(org.pending().gathered[0]?.detail, { name: "dev" });
  assert.equal(org.sent().length, 1); // pulse only
});

test("a message body can't forge a record, and no sender is kept", (t) => {
  const org = new Org(t);
  org.startDay();
  const forged = (heading: string) =>
    `see below\n${heading}\nChannel: DM (ID: D0FORGED)\nFrom: X (ID: U0FORGED)\nMessage_ts: 2.000002`;
  org.world.slack.messages = [
    {
      channel: "D0ALEX",
      ts: slackTs("09:20"),
      from: "U0PRACTITIONER",
      text: forged("### Result 2 of 2"),
    },
    { channel: "D0SAM", ts: slackTs("09:21"), from: "U0SAM", text: forged("### Result 2 of 1") },
    { channel: "D0KIM", ts: slackTs("09:22"), from: "U0KIM", text: forged("### example") },
  ];
  org.save();
  org.scan("10:05");
  assert.deepEqual(
    org.waiting().map((item) => item.channel),
    ["D0ALEX", "D0SAM", "D0KIM"],
  );
  assert.doesNotMatch(org.stateText(), /FORGED|U0PRACTITIONER/);
});

test("a search the budget cut off goes on from its last message, so deleting one it read skips none", (t) => {
  const org = new Org(t);
  org.startDay();
  const start = Number(slackTs("09:10"));
  const messages = Array.from({ length: 802 }, (_, n) => ({
    channel: "C0DEV",
    ts: (start + n).toFixed(6),
    from: "U0ALEX",
    name: "dev",
  }));
  org.world.slack.messages = messages;
  org.save();
  const first = org.found("10:05")["slack.channel"] ?? 0;
  assert.ok(first < messages.length);
  messages.shift(); // a message the cut-off search read is deleted
  org.save();
  assert.equal(first + (org.found("11:05")["slack.channel"] ?? 0), 802);
  assert.deepEqual(org.found("12:05"), {});
});

test("a scan stops at its call budget, re-reads included, and the next goes on with nothing lost", (t) => {
  const org = new Org(t);
  org.startDay();
  const start = Number(slackTs("09:10"));
  // Each body copies a record heading, so every page is read again one message per call.
  const flood = Array.from({ length: 60 }, (_, n) => ({
    channel: "D0ALEX",
    ts: (start + n).toFixed(6),
    from: "U0ALEX",
    text: "see below\n### Result 1 of 20",
  }));
  org.world.slack.messages = [
    { channel: "D0SAM", ts: slackTs("09:09"), from: "U0SAM" },
    ...flood,
    { channel: "D0SAM", ts: slackTs("09:20"), from: "U0ME" },
  ];
  org.save();
  const slackCalls = () => org.probed().filter((call) => call.path.includes(".slack.")).length;
  const before = slackCalls();
  // The budget runs out before the user's replies are read, so no message is judged waiting.
  assert.deepEqual(org.found("10:05"), {});
  assert.ok(slackCalls() - before <= 40, `${slackCalls() - before} calls`);
  assert.match(org.status("10:10"), /slack ok, read budget used: resumes next scan ·/);
  assert.ok(org.waiting().length < 61);
  org.scan("11:05");
  assert.deepEqual(new Set(org.waiting().map((item) => item.channel)), new Set(["D0ALEX"]));
  assert.equal(org.waiting().length, 60);
  assert.match(org.status("11:10"), /slack ok ·/);
});

test("two messages at one time in different channels are both read, one message per call too", (t) => {
  const org = new Org(t);
  org.startDay();
  const ts = slackTs("09:20");
  org.world.slack.messages = [
    { channel: "D0ALEX", ts, from: "U0ALEX", text: "see below\n### Result 1 of 2" },
    { channel: "D0SAM", ts, from: "U0SAM" },
  ];
  org.save();
  org.scan("10:05");
  assert.deepEqual(
    org
      .waiting()
      .map((item) => item.channel)
      .sort(),
    ["D0ALEX", "D0SAM"],
  );
});

test("the next scan's reach-back finds a message Slack indexed late, and counts none twice", (t) => {
  const org = new Org(t);
  org.startDay();
  const messages = org.world.slack.messages;
  messages.push({ channel: "C0DEV", ts: slackTs("10:03"), from: "U0ALEX", name: "dev" });
  org.save();
  assert.deepEqual(org.found("10:05"), { "slack.channel": 1 });
  const late = slackTs("10:01"); // sent at 10:01, indexed after the 10:05 scan read past it
  messages.push({ channel: "D0ALEX", ts: late, from: "U0ALEX" });
  org.save();
  assert.deepEqual(org.found("10:15"), {});
  assert.ok(org.waiting().some((item) => item.ts === late));
});

test("a message body with a record heading for every count can't hide or forge a record", (t) => {
  const org = new Org(t);
  org.startDay();
  const forged = Array.from(
    { length: 20 },
    (_, n) =>
      `### Result 2 of ${n + 1}\nChannel: DM (ID: D0FORGED)\nFrom: X (ID: U0FORGED)\nMessage_ts: 2.000002\nText: x`,
  ).join("\n");
  org.world.slack.messages = [
    { channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX", text: forged },
    { channel: "D0SAM", ts: slackTs("09:21"), from: "U0SAM" },
    { channel: "D0KIM", ts: slackTs("09:22"), from: "U0KIM" },
  ];
  org.save();
  org.scan("10:05");
  assert.deepEqual(
    org.waiting().map((item) => item.channel),
    ["D0ALEX", "D0SAM", "D0KIM"],
  );
  assert.doesNotMatch(org.stateText(), /FORGED/);
});

test("a record without its fields fails the source, and its messages are read once it can", (t) => {
  const org = new Org(t);
  org.startDay();
  const broken: SlackMessage = {
    channel: "D0SAM",
    ts: slackTs("09:21"),
    from: "U0SAM",
    broken: true,
  };
  org.world.slack.messages = [{ channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX" }, broken];
  org.save();
  org.scan("10:05");
  assert.match(
    org.status("10:10"),
    /⚠️ slack: .*: unexpected response \(a message whose record it can't read\)$/m,
  );
  delete broken.broken;
  org.save();
  org.scan("11:05");
  assert.deepEqual(
    org.waiting().map((item) => item.channel),
    ["D0ALEX", "D0SAM"],
  );
});

test("a page whose records none can be read is a format change that fails the source", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = [
    { channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX", broken: true },
  ];
  org.save();
  org.scan("10:05");
  assert.match(
    org.status("10:10"),
    /⚠️ slack: .*: unexpected response \(no record it can read\)$/m,
  );
});

test("a rate-limited search fails the source as rate limited, never with its text", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.fail = { slack: "429: limiting requests for PRIVATE-CANARY" };
  org.save();
  const done = org.scan("10:05");
  assert.match(
    org.status("10:10"),
    /⚠️ slack: tools\.slack\.mcp\.slack_search_public_and_private: rate limited$/m,
  );
  assert.doesNotMatch(done.stderr + org.stateText(), /PRIVATE-CANARY/);
});

test("two Slack sources share the scan's one call budget, and the next scan reads what it left", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    const first = profile.sources.find(({ kind }) => kind === "slack");
    assert.ok(first);
    profile.sources.push({ ...first, name: "slack-ops", channels: [{ id: "C0OPS" }] });
  });
  org.startDay();
  const start = Number(slackTs("09:10"));
  for (const channel of ["C0DEV", "C0OPS"]) {
    // Each first body copies a record heading, so its page is read again one message per call.
    org.world.slack.messages.push(
      ...Array.from({ length: 38 }, (_, n) => ({
        channel,
        from: "U0BOT",
        ts: (start + n).toFixed(6),
        ...(n === 0 ? { text: "see below\n### Result 1 of 20" } : {}),
      })),
    );
  }
  org.save();
  const slackCalls = () => org.probed().filter((call) => call.path.includes(".slack.")).length;
  let read = 0;
  const health: string[] = [];
  for (const clock of ["10:05", "11:05", "12:05"]) {
    const before = slackCalls();
    const report = org.report(clock);
    read += report.found["slack.channel"] ?? 0;
    health.push(
      report.health
        .split(" · ")
        .filter((part) => part.startsWith("slack"))
        .join(" · "),
    );
    assert.ok(slackCalls() - before <= 40, `${slackCalls() - before} calls at ${clock}`);
  }
  assert.equal(read, 76);
  // The second source's allowance ran out at the first scan, which is no stuck watermark.
  assert.deepEqual(health, [
    "slack ok · slack-ops ok, read budget used: resumes next scan",
    "slack ok · slack-ops ok",
    "slack ok · slack-ops ok",
  ]);
});

test("a copied record heading in a one-second burst is read again for its page alone, stranding none", (t) => {
  const org = new Org(t);
  const channels = Array.from({ length: 38 }, (_, n) => ({ id: `C0OPS${n}` }));
  org.writeProfile((profile) => {
    const slack = profile.sources.find(({ kind }) => kind === "slack");
    assert.ok(slack);
    slack.channels = channels;
  });
  org.startDay();
  const second = slackTs("09:10").split(".")[0];
  org.world.slack.messages = channels.map(({ id }, n) => ({
    channel: id,
    ts: `${second}.${String(n + 1).padStart(6, "0")}`,
    from: "U0BOT",
    ...(n === 0 ? { text: "see below\n### Result 1 of 20" } : {}),
  }));
  org.save();
  assert.deepEqual(org.found("10:05"), { "slack.channel": 38 });
  assert.match(org.status("10:10"), /slack ok ·/);
});

test("a second holding more messages than a scan reads says the watermark is stuck", (t) => {
  const org = new Org(t);
  org.startDay();
  const second = slackTs("09:10").split(".")[0];
  org.world.slack.messages = Array.from({ length: 900 }, (_, n) => ({
    channel: "C0DEV",
    ts: `${second}.${String(n + 1).padStart(6, "0")}`,
    from: "U0ALEX",
    name: "dev",
  }));
  org.save();
  org.scan("10:05");
  assert.match(org.status("10:10"), /slack ok, read budget used: resumes next scan ·/);
  org.scan("11:05");
  assert.match(org.status("11:10"), /slack ok, watermark stuck at 2026-11-26T09:10\+01:00: /);
});

/** `count` messages in `channel` from `from`, one a second from `clock`. */
const messages = (count: number, channel: string, from: string, clock: string): SlackMessage[] =>
  Array.from({ length: count }, (_, n) => ({
    channel,
    ts: (Number(slackTs(clock)) + n).toFixed(6),
    from,
  }));

/** `count` messages in a confirmed channel, one a second from `clock`: enough fill a scan's budget. */
const chatter = (clock: string, count: number): SlackMessage[] =>
  messages(count, "C0DEV", "U0ALEX", clock);

/** Whether any wake so far carried a waiting DM or mention. */
const wokeWaiting = (org: Org) =>
  org.sent().some(({ message }) => message.includes("slack.waiting"));

test("a busy channel doesn't keep a waiting DM from waking the thread", (t) => {
  const org = new Org(t);
  org.startDay();
  // 800 channel messages take more than the budget, but the replies are read before the channels.
  org.world.slack.messages = [
    { channel: "D0ALEX", ts: slackTs("09:10"), from: "U0ALEX" },
    ...chatter("09:20", 800),
  ];
  org.save();
  assert.equal(org.found("10:05")["slack.waiting"], 1);
  assert.ok((org.found("11:05")["slack.channel"] ?? 0) > 0);
});

test("a reply search the budget cut off still takes off the list a message a reply it read answers", (t) => {
  const org = new Org(t);
  org.startDay();
  // 800 of the user's replies take more than the budget; the first, oldest first, is the answer.
  org.world.slack.messages = [
    ...messages(1, "D0ALEX", "U0ALEX", "09:10"),
    ...messages(1, "D0ALEX", "U0ME", "09:15"),
    ...messages(800, "C0OTHER", "U0ME", "09:20"),
  ];
  org.save();
  const report = org.report("10:05");
  assert.match(report.health, /slack ok, read budget used/);
  assert.deepEqual(org.waiting(), []);
  org.scan("11:05");
  assert.equal(wokeWaiting(org), false);
});

test("a gathered DM whose replies the budget left unread doesn't wake, and its answer then clears it", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = [{ channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX" }];
  org.threadIs("running");
  org.scan("10:05");
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["slack.waiting"],
  );
  // A bot's DMs spend the budget in the DM search, so the answer goes unread at the next scan.
  org.world.slack.messages.push(
    ...messages(1, "D0ALEX", "U0ME", "10:15"),
    ...messages(800, "D0BOT", "USLACKBOT", "10:20"),
  );
  org.threadIs("completed");
  org.scan("11:05");
  assert.equal(org.waiting().length, 1);
  assert.deepEqual(org.pending().gathered, []);
  org.scan("12:05");
  assert.equal(wokeWaiting(org), false);
  assert.deepEqual(org.waiting(), []);
});

test("a gathered DM a crash took from the pending list wakes once a scan reads its replies", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    profile.sources = profile.sources.filter(({ kind }) => kind === "slack");
  });
  org.startDay();
  org.world.slack.messages = messages(1, "D0ALEX", "U0ALEX", "09:20");
  org.threadIs("running");
  org.scan("10:05");
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["slack.waiting"],
  );
  // A bot's DMs spend the budget before the replies, so the gathered DM leaves; then the snapshot
  // is lost.
  const bots = messages(761, "D0BOT", "USLACKBOT", "10:20");
  org.world.slack.messages.push(...bots);
  org.save();
  org.crashAfterPending("11:05");
  assert.deepEqual(org.pending().gathered, []);
  org.world.slack.messages = org.world.slack.messages.filter((message) => !bots.includes(message));
  org.threadIs("completed");
  org.scan("12:05");
  assert.ok(wokeWaiting(org));
});

test("a DM whose replies take more than one scan's budget wakes once a scan reads them all", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = [
    ...messages(1, "D0ALEX", "U0ALEX", "09:10"),
    ...messages(761, "C0OTHER", "U0ME", "09:20"),
  ];
  org.save();
  assert.deepEqual(org.found("10:05"), {});
  assert.equal(org.waiting().length, 1);
  assert.deepEqual(org.found("11:05"), { "slack.waiting": 1 });
});

test("a budget that runs out before an ambiguous page is read again says so, not stuck", (t) => {
  const org = new Org(t);
  org.startDay();
  // 721 bot DMs take 37 calls, the mentions and the replies one each, so the channels get one.
  org.world.slack.messages = messages(721, "D0BOT", "USLACKBOT", "09:10");
  org.world.slack.messages.push({
    channel: "C0DEV",
    ts: slackTs("09:30"),
    from: "U0X",
    text: "pasted\n### Result 1 of 1",
  });
  org.save();
  org.scan("10:05");
  assert.match(org.status("10:10"), /slack ok, read budget used: resumes next scan ·/);
});

test("a budget that runs out re-reading the overlap of messages already seen says so, not stuck", (t) => {
  const org = new Org(t);
  org.startDay();
  const base = Number(slackTs("09:56"));
  org.world.slack.messages = Array.from({ length: 25 }, (_, n) => ({
    channel: "C0DEV",
    ts: (base + n * 20).toFixed(6),
    from: "U0ALEX",
  }));
  org.save();
  org.scan("10:05");
  // 730 DMs take 37 calls, the mentions and the replies one each, so the channels read one page of
  // 20 messages they read before, and the budget runs out.
  const dm = Number(slackTs("10:10"));
  org.world.slack.messages.push(
    ...Array.from({ length: 730 }, (_, n) => ({
      channel: "D0ALEX",
      ts: (dm + n * 4).toFixed(6),
      from: "U0ALEX",
    })),
  );
  org.save();
  org.scan("11:05");
  assert.match(org.status("11:10"), /slack ok, read budget used: resumes next scan ·/);
  const before = org.probed().length;
  org.scan("12:05");
  const channels = org
    .probed()
    .slice(before)
    .find((call) => String(call.input.filters).startsWith("in:<#"));
  assert.equal(channels?.input.after, String(base + 19 * 20));
});

test("a DM that woke, whose gathered change a budget-out scan drops, wakes at the next scan that reads its replies", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = messages(1, "D0ALEX", "U0ALEX", "09:20");
  org.threadIs("running");
  org.scan("10:05");
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["slack.waiting"],
  );
  // A bot's DMs spend the budget in the DM search, so the replies go unread.
  org.world.slack.messages.push(...messages(800, "D0BOT", "USLACKBOT", "10:20"));
  org.save();
  org.scan("11:05");
  assert.deepEqual(
    org.pending().gathered.filter((item) => item.kind === "slack.waiting"),
    [],
  );
  org.threadIs("completed");
  org.scan("12:05");
  assert.ok(wokeWaiting(org));
});

test("a DM Slack indexed late is judged by the replies a cut-off search read before it waited", (t) => {
  const org = new Org(t);
  org.startDay();
  // 741 replies of the user's take more than the budget; the one at 09:59 answers the late DM.
  const replies = messages(741, "C0OTHER", "U0ME", "09:50");
  const answer = replies[540];
  assert.ok(answer);
  answer.channel = "D0ALEX";
  org.world.slack.messages = replies;
  org.save();
  org.scan("10:05");
  org.world.slack.messages.push(...messages(1, "D0ALEX", "U0ALEX", "09:58"));
  org.save();
  org.scan("11:05");
  assert.equal(wokeWaiting(org), false);
  assert.deepEqual(org.waiting(), []);
});

test("a cut-off search goes on from the whole second it stopped in, so an answer indexed late there clears its DM", (t) => {
  const org = new Org(t);
  org.startDay();
  const start = Number(slackTs("09:45"));
  const cutoff = start + 759;
  const dm = { channel: "D0ALEX", ts: slackTs("09:20"), from: "U0ALEX" };
  // The budget reads 760 of the user's replies, the last half a second into its second.
  org.world.slack.messages = [
    dm,
    ...Array.from({ length: 761 }, (_, n) => ({
      channel: "C0OTHER",
      from: "U0ME",
      ts: (start + n + (n === 759 ? 0.5 : 0)).toFixed(6),
    })),
  ];
  org.save();
  org.report("10:05");
  // The answer, indexed after that scan, falls in that second before the last reply it read.
  org.world.slack.messages.push({
    channel: dm.channel,
    from: "U0ME",
    ts: (cutoff + 0.25).toFixed(6),
  });
  org.save();
  const report = org.report("11:05");
  assert.deepEqual(report.found, {});
  assert.equal(report.wake, null);
  assert.deepEqual(org.waiting(), []);
});

test("a DM Slack indexed late that the user answered before the last scan wakes nothing", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = messages(1, "D0ALEX", "U0ME", "10:02");
  org.save();
  org.scan("10:05");
  org.world.slack.messages.push(...messages(1, "D0ALEX", "U0ALEX", "10:01"));
  org.save();
  org.scan("11:05");
  assert.equal(wokeWaiting(org), false);
  assert.deepEqual(org.waiting(), []);
});

test("a gathered DM answered while Slack can't be read wakes nothing", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = messages(1, "D0ALEX", "U0ALEX", "09:20");
  org.threadIs("running");
  org.scan("10:05");
  assert.deepEqual(
    org.pending().gathered.map((item) => item.kind),
    ["slack.waiting"],
  );
  org.world.slack.messages.push(...messages(1, "D0ALEX", "U0ME", "10:15"));
  org.world.fail = { slack: "429: rate limit" };
  org.threadIs("completed");
  const report = org.report("11:05");
  assert.match(report.health, /slack failing ×1/);
  assert.equal(report.wake, null);
  assert.deepEqual(org.pending().gathered, []);
});

test("a gathered DM a failed Slack read dropped wakes once Slack reads it unanswered again", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.slack.messages = messages(1, "D0ALEX", "U0ALEX", "09:20");
  org.threadIs("running");
  org.scan("10:05");
  org.world.fail = { slack: "429: rate limit" };
  org.threadIs("completed");
  org.scan("11:05");
  assert.equal(wokeWaiting(org), false);
  delete org.world.fail;
  org.save();
  org.scan("12:05");
  assert.deepEqual(org.kinds(org.lastSent()), [`slack.waiting slack:D0ALEX:${slackTs("09:20")}`]);
});
