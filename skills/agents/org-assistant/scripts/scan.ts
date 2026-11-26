/**
 * One scan of one organisation: read the assistant thread and every source, gather what changed,
 * and carry out each step the wake policy names until one ends the scan. `references/scan.md`
 * describes the files and the failure rules this follows.
 *
 * Everything that decides a send (the batches, the gathered changes, and what today already sent)
 * lives in pending.json, written before snapshot.json: a crash between the two writes only makes
 * the next scan read the same events again, and their ids keep them from joining twice.
 */
import { join } from "node:path";

import { SourceError } from "./calls.ts";
import {
  type Change,
  type ChangeFields,
  type ChangeKind,
  change as makeChange,
  gather,
  muted,
  tier,
} from "./changes.ts";
import { EMPTY_LEDGER, type Ledger, ledgerParser } from "./ledger.ts";
import {
  EMPTY_PENDING,
  type Pending,
  type SentBatch,
  finishTry,
  forgetOld,
  freezeInline,
  freezeSent,
  known,
  pendingParser,
  startTry,
} from "./pending.ts";
import { type Ending, type Mode, type Thread, apply, holds, names, nextStep } from "./policy.ts";
import { type Profile, loadProfile } from "./profile.ts";
import {
  EMPTY_SNAPSHOT,
  type Health,
  type Snapshot,
  THREAD,
  healthLine,
  snapshotParser,
} from "./snapshot.ts";
import { type Context, type Fresh, scanSource } from "./sources/index.ts";
import { readThread, sendWake } from "./sources/t3.ts";
import { FileError, readJson, stateDir, withLock, writeJson, writeText } from "./store.ts";
import { type Local, iso, local, localIso } from "./time.ts";

export type ScanOptions = {
  mode: Mode;
  /** With `--since`, how far back a source with no snapshot yet counts changes, in milliseconds. */
  since: number | null;
};

const say = (line: string) => process.stderr.write(`org-assistant: ${line}\n`);

/** Scans one organisation; returns 1 when the unit should fail, else 0. */
export function scanOrg(org: string, now: Date, options: ScanOptions): number {
  try {
    const profile = loadProfile(org);
    const folder = stateDir(org);
    const scan = { org, profile, folder, now, ...options };
    // A dry run reads only, so it takes no lock and creates no folder.
    if (options.mode === "dry") return runScan(scan);
    const done = withLock(join(folder, ".lock"), () => runScan(scan));
    if (done !== "busy") return done;
    say(`${org}: another scan holds the lock; skipping this one`);
    return 0;
  } catch (error) {
    if (!(error instanceof FileError)) throw error;
    say(error.message);
    return 1;
  }
}

/** A failure recorded in a source's health entry; returns how many scans in a row it has failed. */
function failHealth(health: Record<string, Health>, name: string, error: SourceError): number {
  const old = health[name];
  const failures = (old?.ok === false ? old.failures : 0) + 1;
  health[name] = {
    ok: false,
    at: old?.at ?? null,
    failures,
    error: error.auth ? "auth" : "failed",
    message: error.message,
  };
  return failures;
}

/** Where an unexpected error was thrown, by its first stack frame: a file and line, never text. */
function where(cause: unknown): string {
  const frame = cause instanceof Error ? cause.stack?.match(/^\s+at .*:\d+:\d+\)?$/m) : null;
  return frame ? `, ${frame[0].trim()}` : "";
}

function counts(items: Change[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const item of items) out[item.kind] = (out[item.kind] ?? 0) + 1;
  return out;
}

/**
 * The message that wakes the assistant thread: the batch's id, why now, and its refs, never text.
 */
export function wakeMessage(
  org: string,
  batch: SentBatch,
  snapshot: Snapshot,
  zone: string,
): string {
  const named = batch.items.filter((item) => tier(item) !== "pulse");
  const pulse = counts(batch.items.filter((item) => tier(item) === "pulse"));
  const parts = named.slice(0, 12).map((item) => `${item.kind} ${item.ref}`);
  if (named.length > 12) parts.push(`${named.length - 12} more`);
  for (const [kind, count] of Object.entries(pulse).sort(([a], [b]) => (a < b ? -1 : 1))) {
    parts.push(`${count} ${kind}`);
  }
  const refs = parts.length > 0 ? `: ${parts.join(", ")}` : "";
  return (
    `<org-assistant org="${org}" batch="${batch.id}" kind="${batch.kind}" try="${batch.tries.length + 1}">\n` +
    `Use /org-assistant: post batch ${batch.id} from pending.json, then mark it delivered.\n` +
    `Why now: ${batch.reason}. ${batch.items.length} items${refs}.\n` +
    `Health: ${healthLine(snapshot, zone)}\n</org-assistant>\n`
  );
}

/** What one scan knows from the start and doesn't change. */
type Scan = {
  org: string;
  profile: Profile;
  now: Date;
  at: Local;
  /**
   * The organisation's first scan, which records a baseline; `--since` stands in for a snapshot.
   */
  first: boolean;
  since: number | null;
  ledger: Ledger;
};

/** What a scan changes as it goes, and the lines that will fail its unit. */
type State = { snapshot: Snapshot; pending: Pending; failed: string[] };

/** The assistant thread; one that can't be read counts as a failing source. */
function readAssistant(scan: Scan, state: State): { thread: Thread; state: State } {
  const id = scan.profile.thread;
  if (id === null) return { thread: { kind: "absent" }, state };
  const thread = readThread(id);
  const health = { ...state.snapshot.health };
  const failed = [...state.failed];
  if (thread.kind === "unreadable") {
    const failures = failHealth(health, THREAD, new SourceError("t3 thread show: failed"));
    say(`${scan.org}: can't read the assistant thread ${id}`);
    if (failures >= scan.profile.schedule.source_failures) {
      failed.push(`the assistant thread was unreadable ${failures} scans in a row`);
    }
  } else {
    delete health[THREAD];
  }
  return { thread, state: { ...state, snapshot: { ...state.snapshot, health }, failed } };
}

/**
 * Every source's changes, gathered. A source with no section yet counts from the earliest start it
 * was given, its first attempt or the start `--since` named, kept until it succeeds: one whose
 * sign-in failed from the start still reports what happened meanwhile.
 */
function readSources(scan: Scan, state: State): { found: Change[]; state: State } {
  const { org, profile, now, ledger } = scan;
  const { snapshot } = state;
  const sources = { ...snapshot.sources };
  const health = { ...snapshot.health };
  const starts = { ...snapshot.starts };
  const failed = [...state.failed];
  let gathered = state.pending.gathered;
  const found: Change[] = [];
  for (const source of profile.sources) {
    const { name } = source;
    const prev = sources[name];
    if (prev === undefined) {
      const asked = now.getTime() - (scan.since ?? 0);
      const kept = starts[name];
      starts[name] = iso(new Date(Math.min(asked, kept === undefined ? asked : Date.parse(kept))));
    }
    const fresh: Fresh = scan.first
      ? { kind: "baseline" }
      : { kind: "since", since: new Date(starts[name] ?? now) };
    const context: Context = {
      now,
      zone: profile.timezone,
      schedule: profile.schedule,
      ledger,
      thread: profile.thread,
      change: <K extends ChangeKind>(kind: K, fields: ChangeFields<K>) =>
        makeChange(name, kind, fields),
    };
    try {
      const result = scanSource(source, { prev, fresh, ctx: context });
      sources[name] = result.section;
      delete starts[name];
      health[name] = { ok: true, at: iso(now) };
      const { still } = result;
      // A change no longer true, such as a DM since answered, leaves the gathered list.
      if (still !== undefined)
        gathered = gathered.filter((item) => item.source !== name || still(item));
      found.push(...result.changes);
    } catch (error) {
      if (!(error instanceof SourceError)) throw error;
      const failures = failHealth(health, name, error);
      say(`${org}: ${name}: ${error.message}${where(error.cause)}`);
      if (failures >= profile.schedule.source_failures) {
        failed.push(`${name} failed ${failures} scans in a row`);
      }
    }
  }
  const kept = new Set([...profile.sources.map((source) => source.name), THREAD]);
  const pending = { ...state.pending, gathered };
  return {
    found,
    state: {
      snapshot: {
        sources,
        health: Object.fromEntries(Object.entries(health).filter(([name]) => kept.has(name))),
        starts,
        last_scan: iso(now),
      },
      pending: {
        ...pending,
        gathered: gather(gathered, found, known(pending)).filter(
          (item) => !muted(item, ledger.mutes, now),
        ),
      },
      failed,
    },
  };
}

/** Carries out each step the wake policy names, until one ends the scan. */
function drive(scan: Scan, mode: Mode, start: State) {
  let state = start;
  // An inline scan runs in the assistant thread's own run, so it doesn't read the thread.
  let thread: Thread | null = null;
  if (mode !== "inline") ({ thread, state } = readAssistant(scan, state));
  const delivered = new Set(scan.ledger.delivered.map((entry) => entry.batch));
  const hold = holds(scan.ledger, scan.now);
  let found: Change[] | null = null;
  for (;;) {
    const base = {
      at: scan.at,
      schedule: scan.profile.schedule,
      first: scan.first,
      read: found !== null,
      pending: state.pending,
      delivered,
      hold,
    };
    const step = nextStep(
      thread === null
        ? { ...base, mode: "inline" }
        : { ...base, mode: mode === "dry" ? "dry" : "timer", thread },
    );
    switch (step.kind) {
      case "settle":
      case "release":
      case "rejoin":
        state = { ...state, pending: apply(step, state.pending, scan.now) };
        break;
      case "read":
        ({ found, state } = readSources(scan, state));
        break;
      default: {
        const end: Ending = step;
        return { end, found: found ?? [], state };
      }
    }
  }
}

/** Freezes the batch the scan's last step names; returns the batch to send, if any. */
function finish(scan: Scan, end: Ending, state: State): { send: SentBatch | null; state: State } {
  const { org, at, profile } = scan;
  switch (end.kind) {
    case "inline":
      return { send: null, state: { ...state, pending: freezeInline(state.pending, { org, at }) } };
    case "giveUp":
      return { send: null, state: { ...state, failed: [...state.failed, end.failure] } };
    case "resend":
      return { send: state.pending.sent, state };
    case "wake": {
      const pending = freezeSent(state.pending, {
        org,
        at,
        schedule: profile.schedule,
        kind: end.batch,
        items: end.items,
        reason: end.reason,
      });
      return { send: pending.sent, state: { ...state, pending } };
    }
    case "wait":
      return { send: null, state };
  }
}

function runScan(
  options: ScanOptions & { org: string; profile: Profile; folder: string; now: Date },
): number {
  const { org, profile, folder, now, mode } = options;
  const zone = profile.timezone;
  const files = {
    snapshot: join(folder, "snapshot.json"),
    pending: join(folder, "pending.json"),
  };
  const stored = readJson(files.snapshot, snapshotParser);
  const scan: Scan = {
    org,
    profile,
    now,
    at: local(now, zone),
    first: stored === null && options.since === null,
    since: options.since,
    ledger: readJson(join(folder, "ledger.json"), ledgerParser) ?? EMPTY_LEDGER,
  };
  const start = {
    snapshot: stored ?? EMPTY_SNAPSHOT,
    pending: forgetOld(readJson(files.pending, pendingParser) ?? EMPTY_PENDING, now),
    failed: [],
  };
  const driven = drive(scan, mode, start);
  const { end, found } = driven;
  const { send, state } = finish(scan, end, driven.state);
  let { pending } = state;
  const { snapshot } = state;
  const failed = [...state.failed];

  const shown = mode === "inline" ? pending.inline : send;
  const report: Record<string, unknown> = {
    org,
    at: localIso(scan.at),
    first: scan.first,
    dry_run: mode === "dry",
    wake: send?.kind ?? null,
    reason: end.reason,
    batch: shown?.id ?? null,
    items: (shown?.items ?? []).map(({ id, kind, ref }) => ({ id, kind, ref })),
    gathered: counts(pending.gathered),
    found: counts(found),
    health: healthLine(snapshot, zone),
    failed,
  };
  if (mode === "inline") {
    report.batch_items = pending.inline?.items ?? [];
    report.in_flight = pending.sent;
  }
  const message = send === null ? null : wakeMessage(org, send, snapshot, zone);
  if (mode === "dry") {
    report.would_send = message;
    process.stdout.write(`${JSON.stringify(report, null, 1)}\n`);
    return failed.length > 0 ? 1 : 0;
  }

  writeJson(files.pending, pending);
  writeJson(files.snapshot, snapshot);
  writeText(join(folder, "scan.stamp"), `${iso(now)}\n`);
  const target = profile.thread;
  // The sources took minutes to read; the thread may have turned busy or answered meanwhile.
  if (send !== null && message !== null && target !== null && !moved(target, send.id)) {
    pending = startTry(pending, now);
    writeJson(files.pending, pending);
    const ok = sendWake(target, message);
    pending = finishTry(pending, ok);
    writeJson(files.pending, pending);
    if (!ok) {
      say(`${org}: t3 thread send failed`);
      if ((pending.sent?.tries.length ?? 0) >= 1 + profile.schedule.retries) {
        failed.push(`batch ${send.id}'s last wake failed to send`);
      }
    }
  }
  process.stdout.write(`${JSON.stringify(report)}\n`);
  for (const line of failed) say(`${org}: ${line}`);
  return failed.length > 0 ? 1 : 0;
}

/** Whether the thread turned busy, or named this batch, since the scan first read it. */
function moved(thread: string, batch: string): boolean {
  const now = readThread(thread);
  return now.kind !== "idle" || names(now.lastText, batch);
}
