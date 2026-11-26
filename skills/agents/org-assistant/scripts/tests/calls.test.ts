/** The scan's ways out: what reaches Executor and the CLIs, and what a failure keeps of its text. */
import assert from "node:assert/strict";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { Executor, SourceError, failure, runJson } from "../calls.ts";
import { array, number, object, string } from "../parse.ts";

const FAKES = join(dirname(fileURLToPath(import.meta.url)), "fakes.ts");

/** An Executor on the fake probe, for a source that lists `listed` and an adapter that names `named`. */
function fakeExecutor(t: { after(fn: () => void): void }, listed: string[], named = listed) {
  const fake = mkdtempSync(join(tmpdir(), "org-assistant-calls-"));
  t.after(() => rmSync(fake, { recursive: true, force: true }));
  const previous = process.env.FAKE;
  process.env.FAKE = fake;
  t.after(() => (previous === undefined ? delete process.env.FAKE : (process.env.FAKE = previous)));
  const executor = new Executor(
    { command: [process.execPath, FAKES, "probe"], account: "acc", tools: listed },
    named,
  );
  return { executor, probed: () => existsSync(join(fake, "probe.jsonl")) };
}

test("the executor refuses a write tool even when the source lists it, and calls nothing", (t) => {
  const tool = "tools.linear.mark_notification";
  const { executor, probed } = fakeExecutor(t, [tool]);
  assert.throws(
    () => executor.call([{ path: tool, input: { id: "n1", read: true } }]),
    (error) => {
      assert.ok(error instanceof SourceError);
      assert.equal(error.message, `${tool} looks like a write, and the scan only reads`);
      return true;
    },
  );
  assert.equal(probed(), false);
});

test("the executor refuses a tool the adapter doesn't name, even when the source lists it", (t) => {
  const { executor, probed } = fakeExecutor(t, ["tools.linear.list_issues"], []);
  assert.throws(
    () => executor.call([{ path: "tools.linear.list_issues", input: {} }]),
    /is not in this source's tools/,
  );
  assert.equal(probed(), false);
});

test("a failure keeps its category and drops its text", () => {
  const cases: [unknown, string, boolean][] = [
    ["UNAUTHORIZED: PRIVATE-CANARY", "x: sign-in expired", true],
    [{ message: "token_revoked for PRIVATE-CANARY" }, "x: sign-in expired", true],
    ["429 Too Many Requests: PRIVATE-CANARY", "x: rate limited", false],
    ["HTTP 502 while reading PRIVATE-CANARY", "x: failed (HTTP 502)", false],
    ["PRIVATE-CANARY", "x: failed", false],
    [undefined, "x: failed", false],
  ];
  for (const [text, message, auth] of cases) {
    const error = failure("x", text);
    assert.equal(error.message, message);
    assert.equal(error.auth, auth);
  }
});

test("a CLI's JSON is read after a warning line, and an unknown shape fails naming the field only", () => {
  const print = (out: string) => [
    process.execPath,
    "-e",
    `process.stdout.write(${JSON.stringify(out)})`,
  ];
  assert.deepEqual(runJson(print("warning: old config\n[1, 2]\n"), "x", array(number)), [1, 2]);
  assert.throws(() => runJson(print('{"a": "PRIVATE-CANARY"}'), "x", object({ a: number })), {
    message: "x: unexpected response at a",
  });
  assert.throws(() => runJson(print("no json here"), "x", string), {
    message: "x: no JSON in its output",
  });
});
