/** The JSON profile: checked when it loads, so a broken profile fails only its own organisation. */
import assert from "node:assert/strict";
import { homedir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import { loadProfile } from "../profile.ts";
import { Org, utc } from "./helpers.ts";

/** Scans every organisation, and returns what the CLI printed to stderr. */
function scanAll(org: Org, code: number): string {
  const done = org.cli(["scan"], utc("08:30"));
  assert.equal(done.code, code, done.stderr);
  return done.stderr;
}

test("a profile that isn't valid JSON fails with its file and line", (t) => {
  const org = new Org(t);
  org.writeRaw("acme", '{"name": "Acme",\n"thread": }');
  const done = org.cli(["scan", "acme"], utc("10:05"));
  assert.equal(done.code, 1);
  assert.match(done.stderr, /acme\/profile\.json: not valid JSON \(line 2\)/);
});

test("one broken profile leaves the other organisations scanned", (t) => {
  const org = new Org(t);
  org.writeRaw(
    "aaa",
    JSON.stringify({
      name: "A",
      timezone: "Mars/Olympus",
      sources: [{ name: "x", kind: "t3", projects: [] }],
    }),
  );
  assert.match(scanAll(org, 1), /aaa\/profile\.json: timezone: unknown timezone/);
  assert.ok(org.snapshot().last_scan);
});

test("a profile with a list for a name fails only itself", (t) => {
  const org = new Org(t);
  org.writeRaw(
    "aaa",
    JSON.stringify({ name: "A", sources: [{ name: ["one"], kind: "t3", projects: [] }] }),
  );
  assert.match(scanAll(org, 1), /aaa\/profile\.json: sources\[0\]\.name: expected a string/);
  assert.ok(org.snapshot().last_scan);
});

test("a field the profile doesn't know is named, so a typo can't fall back to a default", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    profile.schedule = { daily_delta: 1 };
  });
  assert.match(scanAll(org, 1), /schedule\.daily_delta: is not a field it knows/);
});

test("each check a profile must pass names what is wrong", (t) => {
  const org = new Org(t);
  const cases: [string, (profile: ReturnType<Org["profile"]>) => void, RegExp][] = [
    ["no sources", (p) => void (p.sources = []), /sources: expected at least one source/],
    [
      "two sources, one name",
      (p) => void p.sources.push({ name: "t3", kind: "t3", projects: [] }),
      /two sources are named t3/,
    ],
    ["no executor", (p) => void delete p.executor, /the linear source needs the executor command/],
    ["another org", (p) => void (p.org = "other"), /org is other, but its folder is acme/],
    [
      "a window across midnight",
      (p) => void (p.schedule = { window: ["22:00", "02:00"] }),
      /schedule\.window: expected a start and an end/,
    ],
    [
      "a time out of range",
      (p) => void (p.schedule = { overview: "25:00" }),
      /schedule\.overview: expected a time of day/,
    ],
  ];
  for (const [name, edit, error] of cases) {
    org.writeProfile(edit);
    const done = org.cli(["scan", "acme"], utc("08:30"));
    assert.equal(done.code, 1, name);
    assert.match(done.stderr, error, name);
  }
});

test("a source of a kind with no adapter fails on every scan, and the others still scan", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => profile.sources.push({ name: "boards", kind: "azure-boards" }));
  const done = org.scan("08:30");
  assert.match(done.stderr, /boards: the Azure Boards adapter is not built yet/);
  assert.match(org.status("08:35"), /boards failing ×1 · github ok · linear ok/);
});

test("a loaded profile fills the schedule's defaults and reads ~ as the home folder", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => {
    profile.thread = "";
    profile.sources = [{ name: "t3", kind: "t3", projects: [{ path: "~/code/example" }] }];
    delete profile.executor;
  });
  process.env.ORG_ASSISTANT_CONFIG = join(org.root, "config");
  t.after(() => delete process.env.ORG_ASSISTANT_CONFIG);
  const profile = loadProfile("acme");
  assert.equal(profile.thread, null);
  assert.deepEqual(profile.schedule, {
    window: ["09:00", "23:59"],
    overview: "09:00",
    batch_slots: ["13:00", "17:00"],
    daily_deltas: 6,
    slack_wait_minutes: 30,
    retries: 1,
    source_failures: 3,
  });
  assert.deepEqual(profile.sources, [
    { name: "t3", kind: "t3", projects: [{ path: join(homedir(), "code/example"), options: [] }] },
  ]);
});

test("org finds the organisation by this thread's id, or else by the profile's own name", (t) => {
  const org = new Org(t);
  org.writeRaw(
    "aaa",
    JSON.stringify({
      name: "Other",
      thread: "t-other-assistant",
      sources: [{ name: "Acme", kind: "t3", projects: [] }],
    }),
  );
  const find = (args: string[], thread = "") =>
    org.cli(["org", ...args], undefined, { T3CODE_THREAD_ID: thread });
  assert.equal(find(["--name", "Acme"]).stdout, "acme\n");
  assert.equal(find(["--name", "Acme"], "t-other-assistant").stdout, "aaa\n");
  assert.equal(find([], "t-assistant").stdout, "acme\n");
  assert.equal(find(["--name", "Other"], "t-unknown").stdout, "aaa\n");
  const none = find(["--name", "Nobody"]);
  assert.equal(none.code, 1);
  assert.match(none.stderr, /no profile matches the name Nobody/);
  org.writeRaw("bbb", JSON.stringify({ ...org.profile(), org: "bbb", thread: "" }));
  const two = find(["--name", "Acme"]);
  assert.equal(two.code, 1);
  assert.match(two.stderr, /2 profiles match the name Acme: acme, bbb/);
  org.writeRaw("ccc", "{");
  assert.match(find(["--name", "Nobody"]).stderr, /can't read the profiles of ccc/);
});

test("org fails, naming it, when the profile this thread matches can't load, and picks no other", (t) => {
  const org = new Org(t);
  org.writeProfile((profile) => (profile.timezone = "Mars/Olympus"));
  org.writeRaw(
    "aaa",
    JSON.stringify({ ...org.profile(), org: "aaa", thread: "t-other-assistant" }),
  );
  const find = (thread: string) =>
    org.cli(["org", "--name", "Acme"], undefined, { T3CODE_THREAD_ID: thread });
  const mine = find("t-assistant");
  assert.equal(mine.code, 1);
  assert.match(mine.stderr, /acme\/profile\.json: timezone: unknown timezone/);
  assert.equal(mine.stdout, "");
  // By name, the broken profile still counts, so the name matches two.
  assert.match(find("t-unknown").stderr, /2 profiles match the name Acme: aaa, acme/);
  org.writeRaw("bbb", JSON.stringify({ ...org.profile(), org: "bbb", name: "B" }));
  assert.match(find("t-assistant").stderr, /2 profiles match this thread's id: acme, bbb/);
});
