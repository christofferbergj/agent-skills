/**
 * The harness every scan test shares: a scratch organisation `acme` whose profile points at the
 * fakes in fakes.ts, the invented world they serve, the CLI run as the timer would run it, and
 * builders for the situations the tests set up again and again. No test reaches a live source.
 */
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import type { TestContext } from "node:test";
import { fileURLToPath } from "node:url";

import { type Ledger, ledgerParser } from "../ledger.ts";
import { array, object, parse, string } from "../parse.ts";
import { type Pending, pendingParser } from "../pending.ts";
import { type Snapshot, snapshotParser } from "../snapshot.ts";
import type { TeamIssue, World } from "./fakes.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const CLI = join(HERE, "..", "assistant.ts");
const FAKES = join(HERE, "fakes.ts");
const WORLD = readFileSync(join(HERE, "fixtures", "world.json"), "utf8");

/** A Thursday; Danish time is UTC+1 in November. */
export const THU = "2026-11-26";
export const FRI = "2026-11-27";
export const SAT = "2026-11-28";

/** A Danish wall-clock time on `day`, in November, as the UTC instant `--now` takes. */
export function utc(clock: string, day = THU): string {
  const [hour = 0, minute = 0] = clock.split(":").map(Number);
  return new Date(Date.UTC(...ymd(day), hour - 1, minute)).toISOString().replace(".000Z", "Z");
}

/** The same time as Linear writes it, to the millisecond. */
export function linearTime(clock: string, day = THU): string {
  return utc(clock, day).replace("Z", ".000Z");
}

/** A Slack message timestamp at a Danish wall-clock time. */
export function slackTs(clock: string, day = THU): string {
  return (Date.parse(utc(clock, day)) / 1000).toFixed(6);
}

function ymd(day: string): [number, number, number] {
  const [year = 0, month = 1, date = 1] = day.split("-").map(Number);
  return [year, month - 1, date];
}

export type Ran = { code: number; stdout: string; stderr: string };
export type Report = {
  org: string;
  first: boolean;
  wake: string | null;
  reason: string;
  batch: string | null;
  items: { id: string; kind: string; ref: string }[];
  gathered: Record<string, number>;
  found: Record<string, number>;
  health: string;
  failed: string[];
  in_flight?: { id: string } | null;
  batch_items?: unknown[];
  would_send?: string | null;
};
export type Sent = { to: string; message: string };

/** The profile as JSON, for a test to change before it writes it. */
export type ProfileJson = {
  org?: string;
  name: string;
  timezone?: string;
  thread?: string;
  executor?: { command: string[] };
  schedule?: Record<string, unknown>;
  sources: Record<string, unknown>[];
};

export const LINEAR_TOOLS = [
  "tools.linear.get_notifications",
  "tools.linear.list_issues",
  "tools.linear.get_issue",
];

export class Org {
  readonly root: string;
  readonly fake: string;
  world: World;

  constructor(t: TestContext) {
    this.root = mkdtempSync(join(tmpdir(), "org-assistant-"));
    t.after(() => rmSync(this.root, { recursive: true, force: true }));
    this.fake = join(this.root, "fake");
    mkdirSync(join(this.fake, "bin"), { recursive: true });
    for (const name of ["gh", "t3"]) {
      const path = join(this.fake, "bin", name);
      writeFileSync(path, `#!/bin/sh\nexec "${process.execPath}" "${FAKES}" ${name} "$@"\n`);
      chmodSync(path, 0o755);
    }
    this.world = JSON.parse(WORLD);
    this.save();
    this.writeProfile();
  }

  /** Writes the world the fakes serve; call it after changing `world`. */
  save(): void {
    writeFileSync(join(this.fake, "world.json"), JSON.stringify(this.world));
  }

  profile(): ProfileJson {
    return {
      org: "acme",
      name: "Acme",
      timezone: "Europe/Copenhagen",
      thread: "t-assistant",
      executor: { command: [process.execPath, FAKES, "probe"] },
      sources: [
        {
          name: "linear",
          kind: "linear",
          account: "acc-linear",
          teams: ["ENG", "OPS"],
          tools: LINEAR_TOOLS,
        },
        {
          name: "slack",
          kind: "slack",
          account: "acc-slack",
          me: "U0ME",
          tools: ["tools.slack.mcp.slack_search_public_and_private"],
          channels: [{ id: "C0DEV", name: "dev" }],
        },
        {
          name: "github",
          kind: "github",
          me: "me-login",
          repos: [
            { repo: "example/web", mine: true, review_requests: true, issues: true },
            { repo: "example/api", open_prs: true, releases: true },
          ],
        },
        { name: "t3", kind: "t3", projects: [{ path: "/invented/project" }] },
      ],
    };
  }

  /** Writes acme's profile, as `edit` changes it. */
  writeProfile(edit: (profile: ProfileJson) => void = () => {}): void {
    const profile = this.profile();
    edit(profile);
    this.writeRaw("acme", JSON.stringify(profile, null, 1));
  }

  /** Writes an organisation's profile file as given, valid or not. */
  writeRaw(org: string, text: string): void {
    mkdirSync(join(this.root, "config", org), { recursive: true });
    writeFileSync(join(this.root, "config", org, "profile.json"), text);
  }

  cli(args: string[], now?: string): Ran {
    const done = spawnSync(process.execPath, [CLI, ...args, ...(now ? ["--now", now] : [])], {
      encoding: "utf8",
      env: {
        ...process.env,
        FAKE: this.fake,
        PATH: `${join(this.fake, "bin")}:${process.env.PATH}`,
        ORG_ASSISTANT_CONFIG: join(this.root, "config"),
        ORG_ASSISTANT_STATE: join(this.root, "state"),
        ORG_ASSISTANT_SLACK_SPACING: "0",
        ORG_ASSISTANT_SLACK_PAUSE: "0",
        ORG_ASSISTANT_LOCK_WAIT: "0",
      },
    });
    return { code: done.status ?? -1, stdout: done.stdout, stderr: done.stderr };
  }

  /** A scan of acme at a Danish wall-clock time, which must exit with `code`. */
  scan(clock: string, options: { day?: string; flags?: string[]; code?: number } = {}): Ran {
    const done = this.cli(["scan", "acme", ...(options.flags ?? [])], utc(clock, options.day));
    assert.equal(done.code, options.code ?? 0, done.stderr);
    return done;
  }

  report(clock: string, options: { day?: string; flags?: string[]; code?: number } = {}): Report {
    return JSON.parse(this.scan(clock, options).stdout);
  }

  found(clock: string, options: { day?: string } = {}): Record<string, number> {
    return this.report(clock, options).found;
  }

  status(clock: string, day = THU): string {
    const done = this.cli(["status", "acme"], utc(clock, day));
    assert.equal(done.code, 0, done.stderr);
    return done.stdout;
  }

  ledger(args: string[], now?: string): string {
    const done = this.cli(["ledger", "acme", ...args], now);
    assert.equal(done.code, 0, done.stderr);
    return done.stdout.trim();
  }

  /** Every wake the fake thread received. */
  sent(): Sent[] {
    return this.lines("sent.jsonl");
  }

  /** Every Executor call the fake probe received. */
  probed(): { path: string; input: Record<string, unknown> }[] {
    return this.lines("probe.jsonl");
  }

  private lines<T>(name: string): T[] {
    const path = join(this.fake, name);
    if (!existsSync(path)) return [];
    return readFileSync(path, "utf8")
      .trim()
      .split("\n")
      .map((line) => JSON.parse(line));
  }

  statePath(name: string): string {
    return join(this.root, "state", "acme", name);
  }

  /** Everything the scan and the ledger wrote, as one text, for checks on what it must never hold. */
  stateText(): string {
    const folder = join(this.root, "state", "acme");
    return readdirSync(folder)
      .map((name) => readFileSync(join(folder, name), "utf8"))
      .join("\n");
  }

  pending(): Pending {
    return parse(pendingParser, JSON.parse(readFileSync(this.statePath("pending.json"), "utf8")));
  }

  snapshot(): Snapshot {
    return parse(snapshotParser, JSON.parse(readFileSync(this.statePath("snapshot.json"), "utf8")));
  }

  ledgerState(): Ledger {
    return parse(ledgerParser, JSON.parse(readFileSync(this.statePath("ledger.json"), "utf8")));
  }

  /** The Slack messages still waiting for the user's answer. */
  waiting(): { channel: string; ts: string }[] {
    const section = object({ waiting: array(object({ channel: string, ts: string })) });
    return parse(section, this.snapshot().sources.slack).waiting;
  }

  /** Marks a batch delivered, the sent one by default, as the run does after posting it. */
  deliver(batch?: string): string {
    const id = batch ?? this.pending().sent?.id;
    assert.ok(id, "no batch is in flight");
    this.ledger(["delivered", id]);
    return id;
  }

  /** The `kind ref` pairs of the batch the last wake froze. */
  batch(): string[] {
    return (this.pending().sent?.items ?? []).map((item) => `${item.kind} ${item.ref}`).sort();
  }

  /** The `kind ref` pairs a wake message lists. */
  kinds(sent: Sent | undefined): string[] {
    const line = sent?.message.split("\n").find((entry) => entry.startsWith("Why now:")) ?? "";
    const listed = line.split("items: ")[1];
    return listed === undefined
      ? []
      : listed
          .replace(/\.$/, "")
          .split(", ")
          .map((part) => part.trim())
          .sort();
  }

  lastSent(): Sent | undefined {
    return this.sent().at(-1);
  }

  /** A baseline before the window, then the weekday overview, delivered. */
  startDay(day = THU): void {
    this.scan("08:30", { day });
    assert.deepEqual(this.sent(), []);
    this.scan("09:05", { day });
    assert.match(this.lastSent()?.message ?? "", /kind="overview"/);
    this.deliver();
  }

  /** A Linear inbox notification about `ticket`. */
  note(id: string, type: string, ticket: string, at: string): void {
    this.world.linear.notifications.push({
      id,
      type,
      url: `https://linear.app/example/issue/${ticket}/x`,
      createdAt: at,
    });
  }

  /** A ticket on the ENG team someone else finished at a Danish wall-clock time. */
  teamFinish(ref: string, clock: string): TeamIssue {
    const [first] = this.world.linear.team.ENG ?? [];
    assert.ok(first);
    const at = linearTime(clock);
    const ticket = {
      ...first,
      id: ref,
      status: "Done",
      statusType: "completed",
      updatedAt: at,
      completedAt: at,
    };
    this.world.linear.team.ENG?.push(ticket);
    this.save();
    return ticket;
  }

  /** A scan at `clock` that dies after writing pending.json, before snapshot.json. */
  crashAfterPending(clock: string, options: { day?: string } = {}): void {
    const path = this.statePath("snapshot.json");
    const before = readFileSync(path);
    this.scan(clock, options);
    writeFileSync(path, before);
  }

  /** Sets the assistant thread's status, such as `running`, and saves the world. */
  threadIs(status: string): void {
    assert.ok(this.world.t3.assistant);
    this.world.t3.assistant.status = status;
    this.save();
  }

  /** Sets the assistant thread's last reply, and saves the world. */
  replies(text: string): void {
    assert.ok(this.world.t3.assistant);
    this.world.t3.assistant.last = text;
    this.save();
  }
}
