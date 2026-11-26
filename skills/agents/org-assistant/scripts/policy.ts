/**
 * The wake policy: what one scan does next, as a pure function of the time, the schedule, the
 * pending batches, the ledger's holds, and the assistant thread. The scan calls `nextStep` until it
 * returns a step that ends the scan, carrying out each step between calls. `references/rules.md`
 * gives these rules for people.
 */
import { type Change, tier, urgent } from "./changes.ts";
import type { Ledger } from "./ledger.ts";
import type { Pending, SentBatch, Slot } from "./pending.ts";
import type { Schedule } from "./profile.ts";
import { type Clock, type Local, MINUTE, parseTime } from "./time.ts";

/** A scan from the timer, one inside the assistant's own run ("scan now"), or one that writes nothing. */
export type Mode = "timer" | "inline" | "dry";

/** The assistant thread as the scan read it. */
export type Thread =
  | { kind: "idle"; lastText: string }
  | { kind: "busy" }
  /** The profile names no thread yet. */
  | { kind: "absent" }
  | { kind: "unreadable" };

/** The ledger's quiet and pause, each the time it ends while it is still ahead, else null. */
export type Holds = { quiet: string | null; paused: string | null };

export function holds(ledger: Ledger, now: Date): Holds {
  const ahead = (until: string | null) => {
    const end = until === null ? null : parseTime(until);
    return end !== null && end > now ? until : null;
  };
  return { quiet: ahead(ledger.quiet_until), paused: ahead(ledger.paused_until) };
}

/** A pause holds every wake; quiet holds deltas and lets the overview through. */
function held(hold: Holds, kind: SentBatch["kind"]): boolean {
  return hold.paused !== null || (kind === "delta" && hold.quiet !== null);
}

/** Whether today's overview is owed by `at`: a weekday in the window, past `from`, outside a pause. */
export function overviewOwed(
  at: Local,
  schedule: Schedule,
  hold: Holds,
  from: Clock = schedule.overview,
): boolean {
  const [first, last] = schedule.window;
  return (
    at.isWeekday &&
    first <= at.clock &&
    at.clock <= last &&
    at.clock >= from &&
    hold.paused === null
  );
}

export type Situation = {
  at: Local;
  schedule: Schedule;
  /** The organisation's first scan, which records a baseline. */
  first: boolean;
  /** Whether this scan has read its sources yet. */
  read: boolean;
  pending: Pending;
  /** The batch ids the ledger marks delivered. */
  delivered: ReadonlySet<string>;
  hold: Holds;
} & ({ mode: "inline" } | { mode: "timer" | "dry"; thread: Thread });

export type Step =
  | { kind: "settle"; slot: Slot; reason: string }
  /** An inline batch nobody posted goes back to `gathered`. */
  | { kind: "release"; reason: string }
  /** A delta that quiet holds joins the overview that is due. */
  | { kind: "rejoin"; reason: string }
  | { kind: "read" }
  /** Ends the scan: freeze everything gathered as the inline batch this run posts. */
  | { kind: "inline"; reason: string }
  /** Ends the scan with no wake. */
  | { kind: "wait"; reason: string }
  /** Ends the scan failing the unit: the sent batch went undelivered too many times. */
  | { kind: "giveUp"; reason: string; failure: string }
  /** Ends the scan resending the undelivered batch. */
  | { kind: "resend"; reason: string }
  /** Ends the scan freezing `items` as a new batch and sending it. */
  | { kind: "wake"; batch: SentBatch["kind"]; items: Change[]; reason: string };

/** An inline batch nobody marked delivered within this long goes back to `gathered`. */
const INLINE_GRACE = 30 * MINUTE;
const IDLE: Thread = { kind: "idle", lastText: "" };

/** Whether a reply names a batch, so `acme-…-1` doesn't match the reply to `acme-…-14`. */
export function names(text: string, batch: string): boolean {
  const escaped = batch.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`\\bbatch ${escaped}(?![\\w-])`).test(text);
}

/**
 * The next step. Settling and rejoining come before the sources are read, so the reconciliation
 * of what stopped being true, such as an answered DM, and the mutes then apply to what rejoined.
 */
export function nextStep(s: Situation): Step {
  const { sent, inline } = s.pending;
  if (sent !== null && s.delivered.has(sent.id)) {
    return { kind: "settle", slot: "sent", reason: "the ledger marks the sent batch delivered" };
  }
  if (inline !== null && s.delivered.has(inline.id)) {
    return {
      kind: "settle",
      slot: "inline",
      reason: "the ledger marks the inline batch delivered",
    };
  }
  if (
    inline !== null &&
    (s.mode === "inline" || s.at.instant.getTime() - Date.parse(inline.frozen_at) >= INLINE_GRACE)
  ) {
    return { kind: "release", reason: "the inline batch went unposted" };
  }
  if (s.mode === "inline") {
    return s.read
      ? { kind: "inline", reason: "inline batch for this run to post" }
      : { kind: "read" };
  }
  if (sent !== null && s.thread.kind === "idle") {
    if (names(s.thread.lastText, sent.id)) {
      return {
        kind: "settle",
        slot: "sent",
        reason: "the thread's last reply already named the sent batch",
      };
    }
    if (held(s.hold, sent.kind) && overviewDue(s)) {
      return { kind: "rejoin", reason: "the held delta joins the overview" };
    }
  }
  if (!s.read) return { kind: "read" };
  // A dry run with no thread yet decides as if an idle thread were there.
  const thread = s.mode === "dry" && s.thread.kind === "absent" ? IDLE : s.thread;
  if (sent !== null) return inFlight(s, sent, thread);
  if (s.first)
    return { kind: "wait", reason: "the first scan records a baseline and wakes nothing" };
  if (thread.kind === "absent")
    return { kind: "wait", reason: "the profile names no assistant thread yet" };
  const wake = decide(s);
  if (wake.kind === "wake" && thread.kind !== "idle") {
    return { kind: "wait", reason: `${wake.reason}, held while the thread is busy or unreadable` };
  }
  return wake;
}

/** What happens to a sent batch still undelivered once the sources are read. */
function inFlight(s: Situation, sent: SentBatch, thread: Thread): Step {
  if (thread.kind !== "idle") {
    return { kind: "wait", reason: "the sent batch waits for the busy or unreadable thread" };
  }
  if (held(s.hold, sent.kind)) {
    return { kind: "wait", reason: "the sent batch waits for the quiet or pause to end" };
  }
  if (sent.tries.length >= 1 + s.schedule.retries) {
    return {
      kind: "giveUp",
      reason: "wakes stopped: the sent batch was never delivered",
      failure: `batch ${sent.id} undelivered after ${sent.tries.length} wakes`,
    };
  }
  return { kind: "resend", reason: "resending the undelivered batch" };
}

/** A weekday in the window, past the overview's time, with no overview frozen today. */
function overviewDue(s: Situation): boolean {
  return overviewOwed(s.at, s.schedule, s.hold) && s.pending.meta.overview_on !== s.at.date;
}

/** Whether the gathered changes wake the thread now, and with which of them. */
function decide(s: Situation): Extract<Step, { kind: "wake" | "wait" }> {
  const { at, schedule, hold } = s;
  const { gathered, meta } = s.pending;
  const wait = (reason: string) => ({ kind: "wait", reason }) as const;
  const wake = (batch: SentBatch["kind"], items: Change[], reason: string) =>
    ({ kind: "wake", batch, items, reason }) as const;
  if (hold.paused !== null) return wait(`paused until ${hold.paused}`);
  const [first, last] = schedule.window;
  if (at.clock < first || at.clock > last) return wait("outside the scan window");
  if (overviewDue(s)) return wake("overview", gathered, "the weekday overview");
  if (hold.quiet !== null) return wait(`quiet until ${hold.quiet}`);
  const worth = gathered.filter((item) => tier(item) !== "pulse");
  const capped = (meta.deltas[at.date] ?? 0) >= schedule.daily_deltas;
  if (!at.isWeekday || capped) {
    const why = at.isWeekday ? `past ${schedule.daily_deltas} deltas today` : "weekend";
    const pressing = worth.filter(urgent);
    return pressing.length > 0
      ? wake(
          "delta",
          pressing,
          `${why}: someone waits on you, a new assignment, or a deadline within 24 hours`,
        )
      : wait(`${why}: nothing urgent`);
  }
  if (worth.some((item) => tier(item) === "now"))
    return wake("delta", gathered, "a change worth a wake");
  const flushed = meta.slots[at.date] ?? [];
  if (
    worth.length > 0 &&
    schedule.batch_slots.some((slot) => slot <= at.clock && !flushed.includes(slot))
  ) {
    return wake("delta", gathered, "a batch slot");
  }
  return wait("nothing worth a wake yet");
}
