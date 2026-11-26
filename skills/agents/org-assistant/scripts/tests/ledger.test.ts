/** `assistant.ts ledger`, through the CLI: each command, and that a repeat changes nothing more. */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import { Org, THU, utc } from "./helpers.ts";

/** Runs a ledger command twice and returns the file after each run. */
function twice(org: Org, args: string[], now = utc("10:00")): [string, string] {
  org.ledger(args, now);
  const once = readFileSync(org.statePath("ledger.json"), "utf8");
  org.ledger(args, now);
  return [once, readFileSync(org.statePath("ledger.json"), "utf8")];
}

test("every ledger command run twice leaves the ledger as running it once did", (t) => {
  const org = new Org(t);
  for (const args of [
    ["delivered", "acme-20261126-1005-1"],
    ["quiet", `${THU}T14:00`],
    ["pause", "off"],
    ["mute", "ENG-7", "--until", `${THU}T18:00`],
    ["unmute", "ENG-8"],
    ["call", "set", "first offer"],
    ["call", "queue", "second offer"],
    ["started", "t-new", "--ticket", "ENG-1"],
    ["finished", "t-old"],
    ["waits", "example/web#11", "example/api"],
    ["depends", "ENG-1", "ENG-2"],
    ["depends", "ENG-3", "ENG-4", "--remove"],
    ["lead", "ENG-1", "ENG-5", "unrelated"],
    ["log", "told", "ENG-1 moved"],
  ]) {
    const [once, again] = twice(org, args);
    assert.equal(again, once, args.join(" "));
  }
  const ledger = org.ledgerState();
  assert.equal(ledger.started.length, 1);
  assert.equal(ledger.delivered.length, 1);
  assert.deepEqual(ledger.depends, [{ ticket: "ENG-1", on: "ENG-2" }]);
  assert.deepEqual(ledger.mutes, [{ ref: "ENG-7", until: "2026-11-26T17:00:00Z" }]);
});

test("the open call is settled by its id, and a repeat leaves the next call alone", (t) => {
  const org = new Org(t);
  org.ledger(["call", "set", "first offer"]);
  org.ledger(["call", "queue", "second offer"]);
  org.ledger(["call", "queue", "third offer"]);
  assert.match(
    org.ledger(["call", "clear", "c1"]),
    /^open call c2 \(0 min old\): second offer · 1 queued/,
  );
  assert.match(org.ledger(["call", "clear", "c1"]), /^open call c2 .*second offer/);
  assert.match(org.ledger(["call", "drop", "c2"]), /^open call c3 .*third offer · 0 queued/);
  assert.deepEqual(
    org.ledgerState().dropped.map((call) => call.id),
    ["c2"],
  );
  assert.equal(org.ledger(["call", "clear", "c3"]), "no open call · 0 queued");
});

test("a call can't be set while another is open", (t) => {
  const org = new Org(t);
  org.ledger(["call", "set", "first offer"]);
  const done = org.cli(["ledger", "acme", "call", "set", "another offer"]);
  assert.equal(done.code, 1);
  assert.match(done.stderr, /call c1 is open; queue this one, or clear that call first/);
});

test("a call that replaced another within 15 minutes says so", (t) => {
  const org = new Org(t);
  org.ledger(["call", "set", "first offer"], utc("10:00"));
  org.ledger(["call", "queue", "second offer"], utc("10:00"));
  org.ledger(["call", "clear", "c1"], utc("10:05"));
  assert.match(
    org.ledger(["call", "show"], utc("10:10")),
    /replaced another call 5 min ago: c1: first offer/,
  );
  assert.doesNotMatch(org.ledger(["call", "show"], utc("10:30")), /replaced another call/);
});

test("a call set after the last one was cleared names it as the call it replaced", (t) => {
  const org = new Org(t);
  org.ledger(["call", "set", "first offer"], utc("10:00"));
  org.ledger(["call", "clear", "c1"], utc("10:05"));
  assert.match(
    org.ledger(["call", "set", "next offer"], utc("10:06")),
    /^open call c2 .*\n⚠️ It replaced another call 0 min ago: c1: first offer/,
  );
});

test("quiet and pause read a time in the profile's timezone, and off ends them", (t) => {
  const org = new Org(t);
  assert.equal(org.ledger(["quiet", `${THU}T14:00`]), "quiet_until: 2026-11-26T13:00:00Z");
  assert.equal(
    org.ledger(["pause", "2026-11-30T09:00+01:00"]),
    "paused_until: 2026-11-30T08:00:00Z",
  );
  assert.equal(org.ledger(["quiet", "off"]), "quiet_until: off");
  assert.equal(org.ledgerState().quiet_until, null);
});

test("a ledger command with the wrong words is a usage error that changes nothing", (t) => {
  const org = new Org(t);
  for (const args of [
    ["call", "set"],
    ["lead", "ENG-1", "ENG-2", "maybe"],
    ["log", "shouted", "x"],
    ["started", "t-new"],
    ["quiet", "at two"],
    ["mute", "ENG-1", "--remove"],
    ["renamed"],
  ]) {
    const done = org.cli(["ledger", "acme", ...args]);
    assert.equal(done.code, 2, `${args.join(" ")}: ${done.stderr}`);
  }
  assert.throws(() => org.ledgerState());
});

test("ledger -h lists every command", (t) => {
  const org = new Org(t);
  const help = org.ledger(["-h"]);
  for (const name of [
    "delivered <batch>",
    "call clear <id>",
    "started <thread> [--ticket]",
    "lead <ticket> <on> <answer>",
  ]) {
    assert.ok(help.includes(name), name);
  }
});
