import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { DatabaseSync } from "node:sqlite";
import { test } from "node:test";

const SCRIPT = join(import.meta.dirname, "session-start.ts");
const SESSION = JSON.stringify({
  session_id: "s1",
  hook_event_name: "SessionStart",
  source: "startup",
});

const NO_T3 = join(tmpdir(), "no-t3-state.sqlite");

function stdout(args: string[], stateDb = NO_T3) {
  const result = spawnSync(process.execPath, [SCRIPT, ...args], {
    input: SESSION,
    encoding: "utf8",
    env: { ...process.env, T3_STATE_DB: stateDb },
  });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout;
}

function run(...args: string[]) {
  return JSON.parse(stdout(args));
}

/** A T3 state database whose one provider thread records session s1 under the given thread. */
function t3State(threadId: string) {
  const path = join(mkdtempSync(join(tmpdir(), "t3-state-")), "statev2.sqlite");
  const db = new DatabaseSync(path);
  db.exec(
    "create table orchestration_v2_projection_provider_threads (thread_id text, payload_json text)",
  );
  db.prepare("insert into orchestration_v2_projection_provider_threads values (?, ?)").run(
    threadId,
    JSON.stringify({ nativeThreadRef: { nativeId: "s1" } }),
  );
  db.close();
  return path;
}

test("loads the skill's rules within both hosts' hook limits", () => {
  const output = run();
  const context: string = output.hookSpecificOutput.additionalContext;

  assert.equal(output.hookSpecificOutput.hookEventName, "SessionStart");
  assert.equal(output.systemMessage, undefined);
  assert.match(context, /\*\*Next\*\*/);
  assert.doesNotMatch(context, /^name: next-options/m);
  assert.doesNotMatch(context, /## Setup|references\/setup\.md/);
  assert.ok(context.length <= 8_000, `${context.length} characters`);
});

test("loads reply-shape's rules under its own name and within the same limit", () => {
  const output = run(join(import.meta.dirname, "..", "..", "reply-shape", "SKILL.md"));
  const context: string = output.hookSpecificOutput.additionalContext;

  assert.equal(output.systemMessage, undefined);
  assert.match(context, /^These are the user's reply rules from the reply-shape skill\./);
  assert.match(context, /## Decision card/);
  assert.doesNotMatch(context, /^name: reply-shape/m);
  assert.doesNotMatch(context, /## Setup/);
  assert.ok(context.length <= 8_000, `${context.length} characters`);
});

test("warns instead of failing the session when the rules are missing", () => {
  const output = run(join(import.meta.dirname, "missing.md"));

  assert.match(output.systemMessage, /missing\.md/);
  assert.equal(output.hookSpecificOutput.additionalContext, output.systemMessage);
});

test("skips a T3 delegated task, whose parent reads its report", () => {
  assert.equal(stdout([], t3State("thread:delegated-task:review-1")), "");
});

test("loads the rules in a T3 thread the user talks to", () => {
  const output = JSON.parse(stdout([], t3State("a72e6690-e831-4a9c-b2fa-33af8b371226")));

  assert.match(output.hookSpecificOutput.additionalContext, /\*\*Next\*\*/);
});

test("loads the rules when T3's schema has changed", () => {
  const path = join(mkdtempSync(join(tmpdir(), "t3-state-")), "statev2.sqlite");
  new DatabaseSync(path).close();

  assert.match(run().hookSpecificOutput.additionalContext, /\*\*Next\*\*/);
  assert.match(JSON.parse(stdout([], path)).hookSpecificOutput.additionalContext, /\*\*Next\*\*/);
});
