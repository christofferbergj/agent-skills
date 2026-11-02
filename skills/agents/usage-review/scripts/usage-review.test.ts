import assert from "node:assert/strict";
import { DatabaseSync } from "node:sqlite";
import { test } from "node:test";

import { endingOf, extract } from "./extract.ts";
import { classify, phraseCandidates, pickedLetter, rateOf, type Contract } from "./metrics.ts";
import { scan, type Rules } from "./public-check.ts";

/** A state database with only the columns the scripts read. */
function fixture() {
  const db = new DatabaseSync(":memory:");
  db.exec(`
    create table projection_projects (project_id text, title text);
    create table orchestration_v2_projection_threads (thread_id text, project_id text, deleted_at text, payload_json text);
    create table orchestration_v2_projection_runs (run_id text, thread_id text, status text, requested_at text, completed_at text, payload_json text);
    create table orchestration_v2_projection_messages (message_id text, thread_id text, run_id text, role text, created_at text, payload_json text);
    insert into projection_projects values ('p', 'demo');
  `);
  const thread = (id: string, lineage: string | null = null, createdBy = "user") =>
    db
      .prepare("insert into orchestration_v2_projection_threads values (?, 'p', null, ?)")
      .run(id, JSON.stringify({ createdBy, lineage: { relationshipToParent: lineage } }));
  const run = (
    id: string,
    threadId: string,
    status: string,
    at: string,
    done: string | null,
    userMessageId: string,
  ) =>
    db
      .prepare("insert into orchestration_v2_projection_runs values (?, ?, ?, ?, ?, ?)")
      .run(id, threadId, status, at, done, JSON.stringify({ userMessageId }));
  const message = (
    id: string,
    threadId: string,
    runId: string | null,
    role: string,
    at: string,
    text: string,
    source = "web",
    createdBy = role === "user" ? "user" : "agent",
  ) =>
    db
      .prepare("insert into orchestration_v2_projection_messages values (?, ?, ?, ?, ?, ?)")
      .run(
        id,
        threadId,
        runId,
        role,
        at,
        JSON.stringify({ text, createdBy, creationSource: source }),
      );
  return { db, thread, run, message };
}

const MENU =
  "Done the thing.\n\n**Next**\n\n- **`a` → watch #1** · _recommended_\n- `b` → /babysit-and-ship #1";

test("owner messages are typed as request, answer, steer, and unpaired", () => {
  const { db, thread, run, message } = fixture();
  thread("t");
  run("r1", "t", "completed", "2026-11-01T10:00:00Z", "2026-11-01T10:05:00Z", "u1");
  message("u1", "t", "r1", "user", "2026-11-01T10:00:00Z", "build it");
  message("a1", "t", "r1", "assistant", "2026-11-01T10:04:00Z", MENU);
  run("r2", "t", "completed", "2026-11-01T10:06:00Z", "2026-11-01T10:20:00Z", "u2");
  message("u2", "t", "r2", "user", "2026-11-01T10:06:00Z", "b");
  message("u3", "t", "r2", "user", "2026-11-01T10:10:00Z", "also update the docs");
  run("r4", "t", "cancelled", "2026-11-01T10:21:00Z", "2026-11-01T10:22:00Z", "u4");
  message("u4", "t", "r4", "user", "2026-11-01T10:21:00Z", "stop");
  run("r5", "t", "completed", "2026-11-01T10:30:00Z", "2026-11-01T10:31:00Z", "u5");
  message("u5", "t", "r5", "user", "2026-11-01T10:30:00Z", "try again");

  const rows = extract(db, "2026-11-01T00:00:00Z");
  assert.deepEqual(
    rows.map((r) => [r.messageId, r.interaction]),
    [
      ["u1", "request"],
      ["u2", "answer"],
      ["u3", "steer"],
      ["u4", "unpaired"],
      ["u5", "unpaired"],
    ],
  );
  assert.equal(rows[1].ending?.kind, "options");
  assert.equal(
    rows[3].previousRunStatus,
    "completed",
    "a finished run without a reply is never paired with an older one",
  );
  assert.equal(rows[4].previousRunStatus, "cancelled");
});

test("the corpus keeps owner messages in agent-created roots and drops subagents and server messages", () => {
  const { db, thread, message } = fixture();
  thread("root-by-agent", null, "agent");
  thread("child", "subagent");
  message("keep", "root-by-agent", null, "user", "2026-11-01T10:00:00Z", "hi");
  message("sub", "child", null, "user", "2026-11-01T10:00:00Z", "hi");
  message("prompt", "root-by-agent", null, "user", "2026-11-01T10:01:00Z", "scheduled", "server");
  message("old", "root-by-agent", null, "user", "2026-10-01T10:00:00Z", "hi");
  assert.deepEqual(
    extract(db, "2026-10-15T00:00:00Z").map((r) => r.messageId),
    ["keep"],
  );
});

test("endings read options, a plain next step, and Done", () => {
  const menu = endingOf(MENU);
  assert.equal(menu.kind, "options");
  assert.deepEqual(menu.kind === "options" && menu.options.map((o) => [o.letter, o.recommended]), [
    ["a", true],
    ["b", false],
  ]);
  assert.equal(endingOf("**Next**: I'll report when CI finishes.").kind, "next");
  assert.equal(endingOf("**Done**. Nothing open.").kind, "done");
});

test("picked letters come from bare letters, tweaks, and option phrasing", () => {
  assert.equal(pickedLetter("a"), "a");
  assert.equal(pickedLetter("B, but keep the name"), "b");
  assert.equal(pickedLetter("Do option A, then merge"), "a");
  assert.equal(pickedLetter("add a test"), null);
});

const contract: Contract = {
  rule: "babysit-b",
  opportunity: { offered: "babysit-and-ship" },
  success: { picked: "babysit-and-ship" },
  direction: "up",
};

test("a follow-up rate counts picks among the menus that offered the option", () => {
  const row = (text: string) => ({
    messageId: text,
    threadId: "t",
    project: null,
    at: "",
    interaction: "answer" as const,
    text,
    ending: endingOf(MENU),
  });
  assert.deepEqual(rateOf(contract, [row("b"), row("a"), row("my own words")]), {
    numerator: 1,
    opportunities: 3,
  });
});

test("follow-ups need minimum exposure and five points either way", () => {
  assert.equal(
    classify(contract, { numerator: 5, opportunities: 10 }, { numerator: 0, opportunities: 40 }),
    "insufficient-exposure",
  );
  assert.equal(
    classify(contract, { numerator: 8, opportunities: 40 }, { numerator: 4, opportunities: 40 }),
    "moved",
  );
  assert.equal(
    classify(contract, { numerator: 4, opportunities: 40 }, { numerator: 8, opportunities: 40 }),
    "wrong-way",
  );
  assert.equal(
    classify(contract, { numerator: 5, opportunities: 40 }, { numerator: 4, opportunities: 40 }),
    "unchanged",
  );
});

test("phrase candidates need enough messages across enough threads", () => {
  const rows = Array.from({ length: 12 }, (_, i) => ({
    messageId: `m${i}`,
    threadId: `t${i % 6}`,
    project: null,
    at: "",
    interaction: "request" as const,
    text: "please merge it when CI is green",
  }));
  const phrases = phraseCandidates(rows).map((c) => c.phrase);
  assert.ok(phrases.includes("merge it when ci"));
  assert.ok(
    !phrases.includes("merge it"),
    "a shorter phrase inside a longer one with the same count is dropped",
  );
  assert.deepEqual(phraseCandidates(rows.slice(0, 9)), []);
});

const rules: Rules = {
  allowedRepos: new Set(["christofferbergj/agent-skills", "mattpocock/skills"]),
  projectTitles: ["acme-portal"],
  privateNames: ["jane doe"],
};

test("the public check rejects each private identifier class by position only", () => {
  const text = [
    "see https://github.com/acme/secret-repo/pull/3",
    "fixes DEV-1234",
    "ask someone@acme.io",
    "in Acme-Portal today",
    "per Jane Doe",
  ].join("\n");
  assert.deepEqual(scan(text, "pr-body", rules), [
    { class: "github-url", where: "pr-body:1" },
    { class: "ticket-id", where: "pr-body:2" },
    { class: "email", where: "pr-body:3" },
    { class: "project-title", where: "pr-body:4" },
    { class: "private-name", where: "pr-body:5" },
  ]);
});

test("the public check allows upstream attribution, this repository, and standards ids", () => {
  const text =
    "from https://github.com/mattpocock/skills and https://github.com/christofferbergj/agent-skills/pull/60, UTF-8, ISO-8601, noreply@example.com";
  assert.deepEqual(scan(text, "file", rules), []);
});
