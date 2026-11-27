/**
 * `assistant.ts batch`, through the CLI: which batch it prints, each item's link from its ref and
 * the profile, a Slack conversation's waiting messages as one line, and the summed pulse line.
 */
import assert from "node:assert/strict";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { test } from "node:test";

import { type Change, change } from "../changes.ts";
import { EMPTY_PENDING, type Pending } from "../pending.ts";
import { Org, linearTime, slackTs, utc } from "./helpers.ts";

/** What `batch acme` prints at a Danish wall-clock time, with `args` after the organisation. */
function printed(org: Org, clock: string, args: string[] = []): string {
  const done = org.cli(["batch", "acme", ...args], utc(clock));
  assert.equal(done.code, 0, done.stderr);
  return done.stdout;
}

/** Gives the Linear and Slack sources their workspace slugs. */
function withWorkspaces(org: Org): void {
  org.writeProfile((profile) => {
    for (const source of profile.sources) {
      if (source.kind === "linear") source.workspace = "acme-eng";
      if (source.kind === "slack") source.workspace = "acme-chat";
    }
  });
}

/** A sent delta holding one change of each kind of ref. */
function everyRef(): Pending {
  const dm = slackTs("09:30");
  const items = [
    change("linear", "ticket.assigned", {
      ref: "ENG-103",
      at: utc("09:40"),
      detail: { type: "issueAssignedToYou" },
    }),
    change("github", "pr.review_requested", {
      ref: "example/web#12",
      at: utc("09:50"),
      detail: {},
    }),
    change("github", "issue.assigned", { ref: "example/web#13", at: utc("09:50"), detail: {} }),
    change("github", "release.awaited", {
      ref: "example/api@v1.1.0",
      at: utc("09:55"),
      detail: { prs: ["example/web#11"] },
    }),
    change("slack", "slack.waiting", {
      ref: `slack:D0ALEX:${dm}`,
      at: utc("09:30"),
      key: "waiting",
      detail: { via: "dm", channel: "D0ALEX", minutes: 35 },
    }),
    change("t3", "thread.finished", {
      ref: "t3:thr-1",
      at: utc("10:05"),
      detail: { status: "completed", link: "t3://thread/thr-1", items: 4, started: false },
    }),
  ];
  return delta(items);
}

/** A sent delta of `items`, frozen at 10:05. */
function delta(items: Change[]): Pending {
  return {
    ...EMPTY_PENDING,
    sent: {
      id: "acme-20261126-1005-2",
      kind: "delta",
      items,
      frozen_at: utc("10:05"),
      tries: [],
      reason: "a review request",
    },
    serial: 2,
  };
}

/** A DM waiting in `channel`, found by `source`, with the Slack timestamp `ts`. */
function waits(source: string, channel: string, ts: string): Change {
  return change(source, "slack.waiting", {
    ref: `slack:${channel}:${ts}`,
    at: new Date(Math.floor(Number(ts)) * 1000).toISOString(),
    key: "waiting",
    detail: { via: "dm", channel, minutes: 40 },
  });
}

function writePending(org: Org, pending: Pending): void {
  const file = org.statePath("pending.json");
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, JSON.stringify(pending));
}

test("each kind of ref becomes its link, from the workspaces the profile gives", (t) => {
  const org = new Org(t);
  withWorkspaces(org);
  writePending(org, everyRef());
  const ts = slackTs("09:30").replace(".", "");
  assert.equal(
    printed(org, "10:10"),
    [
      "Batch acme-20261126-1005-2 (delta, 6 changes): a review request",
      "- ticket.assigned · https://linear.app/acme-eng/issue/ENG-103 · 30 min ago · type: issueAssignedToYou",
      "- pr.review_requested · https://github.com/example/web/pull/12 · 20 min ago",
      "- issue.assigned · https://github.com/example/web/issues/13 · 20 min ago",
      "- release.awaited · https://github.com/example/api/releases/tag/v1.1.0 · 15 min ago · prs: https://github.com/example/web/pull/11",
      `- slack.waiting · https://acme-chat.slack.com/archives/D0ALEX/p${ts} · 40 min ago · 1 message waiting, via dm`,
      "- thread.finished · t3://thread/thr-1 · 5 min ago · status: completed, items: 4, started: false",
      "",
    ].join("\n"),
  );
});

test("without a workspace, a ticket or a Slack message keeps its ref", (t) => {
  const org = new Org(t);
  writePending(org, everyRef());
  const lines = printed(org, "10:10").split("\n");
  assert.equal(lines[1], "- ticket.assigned · ENG-103 · 30 min ago · type: issueAssignedToYou");
  assert.equal(
    lines[5],
    `- slack.waiting · slack:D0ALEX:${slackTs("09:30")} · 40 min ago · 1 message waiting, via dm`,
  );
  assert.equal(
    lines[2],
    "- pr.review_requested · https://github.com/example/web/pull/12 · 20 min ago",
  );
});

test("a conversation links its oldest message by the full Slack timestamp, not the second", (t) => {
  const org = new Org(t);
  withWorkspaces(org);
  writePending(
    org,
    delta([waits("slack", "D1", "1800000000.200000"), waits("slack", "D1", "1800000000.100000")]),
  );
  const lines = printed(org, "10:10").split("\n");
  assert.match(lines[1] ?? "", /archives\/D1\/p1800000000100000 · .* · 2 messages waiting/);
});

test("the ids inside a detail are linked like refs", (t) => {
  const org = new Org(t);
  withWorkspaces(org);
  writePending(
    org,
    delta([
      change("linear", "ticket.unblocked", {
        ref: "ENG-102",
        at: utc("09:40"),
        detail: { blocker: "ENG-200", to: "Done" },
      }),
      change("linear", "dependency.changed", {
        ref: "ENG-200",
        at: utc("09:40"),
        detail: { blocks: "ENG-102", before: "In Progress", to: "Done", owner: "Sam Sample" },
      }),
      change("t3", "thread.waiting", {
        ref: "t3:thr-2",
        at: utc("10:05"),
        detail: {
          status: "waiting",
          link: "t3://thread/thr-2",
          items: 2,
          started: true,
          ticket: "ENG-102",
        },
      }),
    ]),
  );
  const ticket = (id: string) => `https://linear.app/acme-eng/issue/${id}`;
  const [, ...rows] = printed(org, "10:10").trim().split("\n");
  assert.deepEqual(rows, [
    `- ticket.unblocked · ${ticket("ENG-102")} · 30 min ago · blocker: ${ticket("ENG-200")}, to: Done`,
    `- dependency.changed · ${ticket("ENG-200")} · 30 min ago · blocks: ${ticket("ENG-102")}, before: In Progress, to: Done, owner: Sam Sample`,
    `- thread.waiting · t3://thread/thr-2 · 5 min ago · status: waiting, items: 2, started: true, ticket: ${ticket("ENG-102")}`,
  ]);
});

test("two Slack sources never merge a conversation or a channel's count", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    const [, slack] = profile.sources;
    assert.ok(slack);
    slack.workspace = "acme-chat";
    profile.sources.push({
      ...slack,
      name: "slack-ops",
      account: "acc-ops",
      workspace: "acme-ops",
    });
  });
  const message = (source: string, channel: string, name: string, ts: string) =>
    change(source, "slack.channel", {
      ref: channel,
      at: utc("09:30"),
      key: ts,
      detail: { name },
    });
  writePending(
    org,
    delta([
      waits("slack", "D0ALEX", "1795681800.000100"),
      waits("slack-ops", "D0ALEX", "1795681900.000100"),
      message("slack", "C0DEV", "dev", "1"),
      message("slack-ops", "C0DEV", "dev", "2"),
      message("slack-ops", "C0DEV", "dev", "3"),
      message("slack-ops", "C0RANDOM", "random", "4"),
    ]),
  );
  const [, ...rows] = printed(org, "10:10").trim().split("\n");
  assert.deepEqual(
    rows.map((row) => row.replace(/ · \d+ min ago/, "")),
    [
      "- slack.waiting · https://acme-chat.slack.com/archives/D0ALEX/p1795681800000100 · 1 message waiting, via dm",
      "- slack.waiting · https://acme-ops.slack.com/archives/D0ALEX/p1795681900000100 · 1 message waiting, via dm",
      "- pulse · #dev (slack) 1 message · #dev (slack-ops) 2 messages · #random 1 message",
    ],
  );
});

test("a conversation's waiting messages make one line, linking the oldest", (t) => {
  const org = new Org(t);
  withWorkspaces(org);
  org.startDay();
  org.world.slack.messages = [
    ...["09:20", "09:22", "09:24"].map((clock) => ({
      channel: "D0ALEX",
      ts: slackTs(clock),
      from: "U0ALEX",
    })),
    { channel: "D0SAM", ts: slackTs("09:30"), from: "U0SAM" },
  ];
  org.save();
  org.scan("10:05");
  assert.equal(org.pending().sent?.items.length, 4);
  const [header, ...rows] = printed(org, "10:10").trim().split("\n");
  assert.match(header ?? "", /^Batch acme-\S+ \(delta, 4 changes\): /);
  assert.deepEqual(rows, [
    `- slack.waiting · https://acme-chat.slack.com/archives/D0ALEX/p${slackTs("09:20").replace(".", "")} · 50 min ago · 3 messages waiting, via dm`,
    `- slack.waiting · https://acme-chat.slack.com/archives/D0SAM/p${slackTs("09:30").replace(".", "")} · 40 min ago · 1 message waiting, via dm`,
  ]);
});

test("the team's moves and channel messages sum to one pulse line", (t) => {
  const org = new Org(t);
  const [sam] = org.world.linear.team.ENG ?? [];
  assert.ok(sam);
  sam.updatedAt = linearTime("08:45"); // the overview's scan sees it, so the next sees it move
  org.save();
  org.startDay();
  Object.assign(sam, { status: "In Review", updatedAt: linearTime("09:35") });
  org.teamFinish("ENG-201", "09:40");
  org.teamFinish("ENG-202", "09:45");
  org.world.slack.messages = ["09:30", "09:31", "09:50"].map((clock) => ({
    channel: "C0DEV",
    ts: slackTs(clock),
    from: "U0ALEX",
    name: "dev",
  }));
  org.save();
  org.scan("10:05", { flags: ["--inline"] });
  const [header, ...rows] = printed(org, "10:10").trim().split("\n");
  assert.match(header ?? "", /^Batch acme-\S+ \(inline, 6 changes\): scan now$/);
  assert.deepEqual(rows, ["- pulse · Sam Sample 1 moved, 2 finished · #dev 3 messages"]);
});

test("batch prints the sent batch by default, and either batch by its id", (t) => {
  const org = new Org(t);
  org.startDay();
  org.note("n1", "issueAssignedToYou", "ENG-103", linearTime("09:30"));
  org.save();
  org.scan("10:05");
  org.note("n2", "issueCommentMention", "ENG-101", linearTime("10:10"));
  org.save();
  org.scan("10:15", { flags: ["--inline"] });
  const { sent, inline } = org.pending();
  assert.ok(sent && inline);
  const header = (text: string) => text.split("\n")[0];
  assert.match(header(printed(org, "10:20")) ?? "", new RegExp(`^Batch ${sent.id} \\(delta, `));
  assert.match(
    header(printed(org, "10:20", [inline.id])) ?? "",
    new RegExp(`^Batch ${inline.id} \\(inline, 1 change\\): scan now$`),
  );
  org.deliver(sent.id);
  assert.match(
    header(printed(org, "10:20", [sent.id])) ?? "",
    /\(delta, 1 change, already marked delivered\)/,
  );
  const gone = org.cli(["batch", "acme", "acme-20261126-0000-99"], utc("10:20"));
  assert.equal(gone.code, 1);
  assert.match(gone.stderr, /no batch acme-20261126-0000-99 waits to be posted/);
});

test("with nothing frozen, batch says so", (t) => {
  const org = new Org(t);
  org.startDay();
  org.scan("10:05"); // settles the delivered overview
  assert.equal(printed(org, "10:10"), "No batch waits to be posted.\n");
});
