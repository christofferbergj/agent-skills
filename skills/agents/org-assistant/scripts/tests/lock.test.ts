/**
 * The locks: one scan of an organisation at a time, and one ledger command at a time, held by the
 * kernel so nothing a dead process left keeps a later run out; and a scan of every organisation,
 * which runs each in a process of its own.
 */
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";
import { setTimeout as delay } from "node:timers/promises";

import { Org, utc } from "./helpers.ts";

const SKIPPED = /acme: another scan holds the lock; skipping this one/;

test("a scan skips while another holds the lock, and writes nothing", (t) => {
  const org = new Org(t);
  org.hold(t, ".lock");
  const done = org.cli(["scan", "acme"], utc("08:30"));
  assert.equal(done.code, 0);
  assert.match(done.stderr, SKIPPED);
  assert.equal(existsSync(org.statePath("snapshot.json")), false);
});

test("a lock file a dead scan left, even one naming a live process, keeps no scan out", (t) => {
  const org = new Org(t);
  mkdirSync(org.statePath(""), { recursive: true });
  const holder = { pid: process.pid, started: "2026-11-26T07:00:00.000Z" };
  writeFileSync(org.statePath(".lock"), JSON.stringify(holder));
  org.scan("08:30");
  assert.ok(org.snapshot().last_scan);
});

test("a scan killed while it holds the lock leaves the next one free to run", async (t) => {
  const org = new Org(t);
  org.world.t3.show_ms = 20_000;
  org.save();
  const scan = spawn(process.execPath, org.argv(["scan", "acme"], utc("08:30")), {
    env: org.env(),
    stdio: "ignore",
  });
  t.after(() => scan.kill("SIGKILL"));
  for (let tries = 0; !org.locked(".lock"); tries++) {
    assert.ok(tries < 200, "the scan never took its lock");
    await delay(50);
  }
  scan.kill("SIGKILL");
  await once(scan, "exit");
  delete org.world.t3.show_ms;
  org.save();
  assert.doesNotMatch(org.scan("08:30").stderr, SKIPPED);
  assert.ok(org.snapshot().last_scan);
});

test("a scan that fails its unit still lets go of its lock", (t) => {
  const org = new Org(t);
  org.world.t3.assistant = null;
  org.save();
  for (const clock of ["08:30", "09:05"]) org.scan(clock);
  org.scan("10:05", { code: 1 });
  assert.equal(org.locked(".lock"), false);
  assert.doesNotMatch(org.scan("11:05", { code: 1 }).stderr, SKIPPED);
});

test("a dry run takes no lock, so it reads even while a scan runs", (t) => {
  const org = new Org(t);
  org.hold(t, ".lock");
  const report = org.report("08:30", { flags: ["--dry-run"] });
  assert.equal(report.first, true);
  assert.equal(existsSync(org.statePath("snapshot.json")), false);
});

test("without flock the lock is a plain file: the scan says so, and one left behind keeps the next out", (t) => {
  const org = new Org(t);
  const noFlock = { PATH: join(org.fake, "bin") };
  const done = org.cli(["scan", "acme"], utc("08:30"), noFlock);
  assert.equal(done.code, 0, done.stderr);
  assert.match(done.stderr, /flock isn't on PATH, so .*\.lock is a plain file/);
  assert.ok(org.snapshot().last_scan);
  assert.equal(existsSync(org.statePath(".lock")), false);
  writeFileSync(org.statePath(".lock"), "");
  assert.match(org.cli(["scan", "acme"], utc("09:05"), noFlock).stderr, SKIPPED);
});

test("ledger commands run at once each land", async (t) => {
  const org = new Org(t);
  org.ledger(["log", "told", "first"]);
  const edits = Array.from({ length: 12 }, (_, n) =>
    spawn(process.execPath, org.argv(["ledger", "acme", "log", "told", `edit ${n}`]), {
      env: org.env({ ORG_ASSISTANT_LOCK_WAIT: "30" }),
      stdio: "ignore",
    }),
  );
  const codes = await Promise.all(edits.map(async (edit) => (await once(edit, "exit"))[0]));
  assert.deepEqual(
    codes,
    edits.map(() => 0),
  );
  assert.equal(org.ledgerState().log.length, 13);
});

test("a ledger command waits for the one before it, not for a scan", (t) => {
  const org = new Org(t);
  org.hold(t, ".lock");
  assert.equal(
    org.ledger(["delivered", "acme-20261126-1005-1"]),
    "batch acme-20261126-1005-1 delivered",
  );
  org.hold(t, ".ledger.lock");
  const done = org.cli(["ledger", "acme", "delivered", "acme-20261126-1105-2"]);
  assert.equal(done.code, 1);
  assert.match(done.stderr, /another ledger command holds it; run this again/);
});

test("a scan of every organisation runs each apart, so one whose state can't be written fails alone", (t) => {
  const org = new Org(t);
  org.writeRaw("aaa", JSON.stringify({ ...org.profile(), org: "aaa" }));
  mkdirSync(join(org.root, "state"), { recursive: true });
  writeFileSync(join(org.root, "state", "aaa"), "a file where aaa's state folder belongs");
  const done = org.cli(["scan"], utc("08:30"));
  assert.equal(done.code, 1);
  assert.match(done.stderr, /state\/aaa\/\.lock: can't be locked/);
  assert.ok(org.snapshot().last_scan);
});
