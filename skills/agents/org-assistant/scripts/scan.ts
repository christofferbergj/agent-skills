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
import { type Ledger, ledgerParser } from "./ledger.ts";
import { parse } from "./parse.ts";
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
  settle,
  startTry,
  unfreeze,
} from "./pending.ts";
import { type Mode, type Step, type Thread, holds, names, nextStep } from "./policy.ts";
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
import {
  FileError,
  parseFile,
  readJson,
  stateDir,
  withLock,
  writeJson,
  writeText,
} from "./store.ts";
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
    // A dry run reads only, so it takes no lock and creates no folder.
    if (options.mode === "dry") return runScan(org, profile, folder, now, options);
    const wait = Number(process.env.ORG_ASSISTANT_LOCK_WAIT ?? 60) * 1000;
    const done = withLock(folder, wait, () => runScan(org, profile, folder, now, options));
    if (done !== "busy") return done;
    say(`${org}: another scan holds the lock; skipping this one`);
    return 0;
  } catch (error) {
    if (!(error instanceof FileError)) throw error;
    say(error.message);
    return 1;
  }
}

function load<T>(
  folder: string,
  name: string,
  parser: (value: unknown, path: string) => T,
  empty: T,
) {
  const file = join(folder, name);
  const value = readJson(file);
  return {
    file,
    loaded: value !== undefined,
    value: value === undefined ? empty : parseFile(file, parser, value),
  };
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

function counts(items: Change[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const item of items) out[item.kind] = (out[item.kind] ?? 0) + 1;
  return out;
}

/** The message that wakes the assistant thread: the batch's id, why now, and its refs, never text. */
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

function runScan(
  org: string,
  profile: Profile,
  folder: string,
  now: Date,
  options: ScanOptions,
): number {
  const { mode } = options;
  const zone = profile.timezone;
  const schedule = profile.schedule;
  const at: Local = local(now, zone);
  const snapshotFile = load(folder, "snapshot.json", snapshotParser, EMPTY_SNAPSHOT);
  const pendingFile = load(folder, "pending.json", pendingParser, EMPTY_PENDING);
  const ledger: Ledger = load(folder, "ledger.json", ledgerParser, parse(ledgerParser, {})).value;
  // `--since` stands in for a snapshot from that long ago.
  const first = !snapshotFile.loaded && options.since === null;
  let snapshot = snapshotFile.value;
  let pending: Pending = forgetOld(pendingFile.value, now);
  const failed: string[] = [];
  const delivered = new Set(ledger.delivered.map((entry) => entry.batch));
  const hold = holds(ledger, now);

  /** The assistant thread; one that can't be read counts as a failing source. */
  const readAssistant = (): Thread => {
    if (profile.thread === null) return { kind: "absent" };
    const thread = readThread(profile.thread);
    const health = { ...snapshot.health };
    if (thread.kind === "unreadable") {
      const failures = failHealth(health, THREAD, new SourceError("t3 thread show: failed"));
      say(`${org}: can't read the assistant thread ${profile.thread}`);
      if (failures >= schedule.source_failures) {
        failed.push(`the assistant thread was unreadable ${failures} scans in a row`);
      }
    } else {
      delete health[THREAD];
    }
    snapshot = { ...snapshot, health };
    return thread;
  };

  /**
   * Every source's changes. A source with no snapshot yet counts from its first attempt, so one
   * whose sign-in failed from the start still reports what happened meanwhile.
   */
  const readSources = (): Change[] => {
    const found: Change[] = [];
    const sources = { ...snapshot.sources };
    const health = { ...snapshot.health };
    const starts = { ...snapshot.starts };
    for (const source of profile.sources) {
      const { name } = source;
      const prev = sources[name];
      if (prev === undefined) starts[name] ??= iso(now);
      const fresh: Fresh =
        options.since !== null
          ? { kind: "since", since: new Date(now.getTime() - options.since) }
          : first
            ? { kind: "baseline" }
            : { kind: "since", since: new Date(starts[name] ?? iso(now)) };
      const context: Context = {
        now,
        zone,
        schedule,
        ledger,
        thread: profile.thread,
        change: <K extends ChangeKind>(kind: K, fields: ChangeFields<K>) =>
          makeChange(name, kind, fields),
      };
      try {
        const result = scanSource(source, prev, fresh, context);
        sources[name] = result.section;
        delete starts[name];
        health[name] = { ok: true, at: iso(now) };
        const { still } = result;
        if (still !== undefined) {
          // A change no longer true, such as a DM since answered, leaves the gathered list.
          pending = {
            ...pending,
            gathered: pending.gathered.filter((item) => item.source !== name || still(item)),
          };
        }
        found.push(...result.changes);
      } catch (error) {
        if (!(error instanceof SourceError)) throw error;
        const failures = failHealth(health, name, error);
        say(`${org}: ${name}: ${error.message}`);
        if (failures >= schedule.source_failures)
          failed.push(`${name} failed ${failures} scans in a row`);
      }
    }
    const kept = new Set([...profile.sources.map((source) => source.name), THREAD]);
    snapshot = {
      sources,
      health: Object.fromEntries(Object.entries(health).filter(([name]) => kept.has(name))),
      starts,
      last_scan: iso(now),
    };
    const gathered = gather(pending.gathered, found, known(pending));
    pending = { ...pending, gathered: gathered.filter((item) => !muted(item, ledger.mutes, now)) };
    return found;
  };

  const thread = mode === "inline" ? null : readAssistant();
  let found: Change[] | null = null;
  const step = ((): Exclude<Step, { kind: "settle" | "release" | "rejoin" | "read" }> => {
    for (;;) {
      const base = { at, schedule, first, read: found !== null, pending, delivered, hold };
      const next = nextStep(
        thread === null
          ? { ...base, mode: "inline" }
          : { ...base, mode: mode === "dry" ? "dry" : "timer", thread },
      );
      switch (next.kind) {
        case "settle":
          pending = settle(pending, next.slot, now);
          break;
        case "release":
          pending = unfreeze(pending, "inline");
          break;
        case "rejoin":
          pending = unfreeze(pending, "sent");
          break;
        case "read":
          found = readSources();
          break;
        default:
          return next;
      }
    }
  })();

  let send: SentBatch | null = null;
  switch (step.kind) {
    case "inline":
      pending = freezeInline(pending, org, at);
      break;
    case "giveUp":
      failed.push(step.failure);
      break;
    case "resend":
      send = pending.sent;
      break;
    case "wake":
      pending = freezeSent(pending, org, at, schedule, {
        kind: step.batch,
        items: step.items,
        reason: step.reason,
      });
      send = pending.sent;
      break;
    case "wait":
      break;
  }

  const shown = mode === "inline" ? pending.inline : send;
  const report: Record<string, unknown> = {
    org,
    at: localIso(at),
    first,
    dry_run: mode === "dry",
    wake: send?.kind ?? null,
    reason: step.reason,
    batch: shown?.id ?? null,
    items: (shown?.items ?? []).map(({ id, kind, ref }) => ({ id, kind, ref })),
    gathered: counts(pending.gathered),
    found: counts(found ?? []),
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

  writeJson(pendingFile.file, pending);
  writeJson(snapshotFile.file, snapshot);
  writeText(join(folder, "scan.stamp"), `${iso(now)}\n`);
  const target = profile.thread;
  // The sources took minutes to read; the thread may have turned busy or answered meanwhile.
  if (send !== null && message !== null && target !== null && !moved(target, send.id)) {
    pending = startTry(pending, now);
    writeJson(pendingFile.file, pending);
    const ok = sendWake(target, message);
    pending = finishTry(pending, ok);
    writeJson(pendingFile.file, pending);
    if (!ok) {
      say(`${org}: t3 thread send failed`);
      if ((pending.sent?.tries.length ?? 0) >= 1 + schedule.retries) {
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
