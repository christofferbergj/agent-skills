/**
 * `.lock`: one scan of an organisation at a time, and a lock its process left behind is taken over.
 */
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, utimesSync, writeFileSync } from "node:fs";
import { test } from "node:test";

import { Org, utc } from "./helpers.ts";

function lock(org: Org, holder: string, age = 0): void {
  mkdirSync(org.statePath(""), { recursive: true });
  writeFileSync(org.statePath(".lock"), holder);
  const then = new Date(Date.now() - age);
  utimesSync(org.statePath(".lock"), then, then);
}

test("a scan skips while a running scan holds the lock, and writes nothing", (t) => {
  const org = new Org(t);
  lock(org, JSON.stringify({ pid: process.pid, started: new Date().toISOString() }));
  const done = org.cli(["scan", "acme"], utc("08:30"));
  assert.equal(done.code, 0);
  assert.match(done.stderr, /acme: another scan holds the lock; skipping this one/);
  assert.equal(existsSync(org.statePath("snapshot.json")), false);
  assert.equal(existsSync(org.statePath(".lock")), true);
});

test("a lock whose process no longer runs is taken over, and removed when the scan ends", (t) => {
  const org = new Org(t);
  const gone = spawnSync(process.execPath, ["-e", ""]).pid;
  lock(org, JSON.stringify({ pid: gone, started: "2026-11-26T07:00:00.000Z" }));
  org.scan("08:30");
  assert.ok(org.snapshot().last_scan);
  assert.equal(existsSync(org.statePath(".lock")), false);
});

test("an empty lock is stale only once it is old enough that its writer can't still be writing it", (t) => {
  const org = new Org(t);
  lock(org, "");
  assert.match(org.cli(["scan", "acme"], utc("08:30")).stderr, /another scan holds the lock/);
  lock(org, "", 60_000);
  org.scan("08:30");
  assert.ok(org.snapshot().last_scan);
});

test("a scan that fails its unit still removes its lock", (t) => {
  const org = new Org(t);
  org.world.t3.assistant = null;
  org.save();
  for (const clock of ["08:30", "09:05"]) org.scan(clock);
  org.scan("10:05", { code: 1 });
  assert.equal(existsSync(org.statePath(".lock")), false);
});

test("a dry run takes no lock, so it reads even while a scan runs", (t) => {
  const org = new Org(t);
  lock(org, JSON.stringify({ pid: process.pid, started: new Date().toISOString() }));
  const report = org.report("08:30", { flags: ["--dry-run"] });
  assert.equal(report.first, true);
  assert.equal(existsSync(org.statePath("snapshot.json")), false);
});
