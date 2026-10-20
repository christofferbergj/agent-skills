import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { test } from "node:test";

const SCRIPT = join(import.meta.dirname, "session-start.ts");
const SESSION = JSON.stringify({
  session_id: "s1",
  hook_event_name: "SessionStart",
  source: "startup",
});

function run(...args: string[]) {
  const result = spawnSync(process.execPath, [SCRIPT, ...args], {
    input: SESSION,
    encoding: "utf8",
  });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
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

test("warns instead of failing the session when the rules are missing", () => {
  const output = run(join(import.meta.dirname, "missing.md"));

  assert.match(output.systemMessage, /missing\.md/);
  assert.equal(output.hookSpecificOutput.additionalContext, output.systemMessage);
});
