/**
 * The wake policy as a table: each row a situation and the one step `nextStep` takes from it, then
 * whole scans driven step by step with the same transitions the runner uses, for the order rules.
 */
import assert from "node:assert/strict";
import { test } from "node:test";

import { type Change, change, gather } from "../changes.ts";
import { parse } from "../parse.ts";
import { EMPTY_PENDING, type Pending, type SentBatch } from "../pending.ts";
import { type Mode, type Situation, type Step, type Thread, apply, nextStep } from "../policy.ts";
import { type Schedule, scheduleParser } from "../profile.ts";
import { clock, local } from "../time.ts";
import { FRI, SAT, THU, utc } from "./helpers.ts";

const ZONE = "Europe/Copenhagen";
const IDLE: Thread = { kind: "idle", lastText: "" };
const BATCH = "acme-20261126-1005-1";

const assigned = change("linear", "ticket.assigned", {
  ref: "ENG-1",
  at: utc("09:30"),
  detail: { type: "issueAssignedToYou" },
});
const comment = change("linear", "ticket.comment", {
  ref: "ENG-2",
  at: utc("09:31"),
  detail: { type: "issueNewComment" },
});
const fresh = change("linear", "ticket.new_in_project", {
  ref: "ENG-3",
  at: utc("09:32"),
  detail: { project: "P" },
});
const moved = change("linear", "ticket.moved", {
  ref: "ENG-4",
  at: utc("09:33"),
  detail: { field: "status", to: "Done" },
});

function sent(kind: SentBatch["kind"], tries = 1, items: Change[] = [comment]): SentBatch {
  const attempts = Array.from({ length: tries }, () => ({ at: utc("10:05"), ok: true }));
  return {
    id: BATCH,
    kind,
    items,
    frozen_at: utc("10:05"),
    tries: attempts,
    reason: "a change worth a wake",
  };
}

type Given = {
  clock?: string;
  day?: string;
  mode?: Mode;
  thread?: Thread;
  first?: boolean;
  read?: boolean;
  pending?: Partial<Pending>;
  meta?: Partial<Pending["meta"]>;
  delivered?: string[];
  quiet?: string;
  paused?: string;
  schedule?: Partial<Schedule>;
};

function situation(given: Given): Situation {
  const pending = { ...EMPTY_PENDING, ...given.pending };
  const base = {
    at: local(new Date(utc(given.clock ?? "10:05", given.day)), ZONE),
    schedule: { ...parse(scheduleParser, {}), ...given.schedule },
    first: given.first ?? false,
    read: given.read ?? true,
    pending: { ...pending, meta: { ...pending.meta, ...given.meta } },
    delivered: new Set(given.delivered),
    hold: { quiet: given.quiet ?? null, paused: given.paused ?? null },
  };
  return given.mode === "inline"
    ? { ...base, mode: "inline" }
    : { ...base, mode: given.mode ?? "timer", thread: given.thread ?? IDLE };
}

function summary(step: Step): string {
  switch (step.kind) {
    case "settle":
      return `settle ${step.slot}`;
    case "read":
      return "read";
    case "wake":
      return `wake ${step.batch}: ${step.items.map((item) => item.ref).join(" ")}`;
    case "giveUp":
      return `giveUp: ${step.failure}`;
    default:
      return `${step.kind}: ${step.reason}`;
  }
}

const today = { overview_on: THU, overview_id: "acme-20261126-0905-1" };

const TABLE: [string, Given, string][] = [
  // Settling and rejoining, before the sources are read.
  [
    "the ledger marks the sent batch delivered",
    { read: false, pending: { sent: sent("delta") }, delivered: [BATCH] },
    "settle sent",
  ],
  [
    "the ledger marks the inline batch delivered",
    {
      read: false,
      pending: { inline: { ...sent("delta"), kind: "inline", reason: "scan now" } },
      delivered: [BATCH],
    },
    "settle inline",
  ],
  [
    "an inline batch unposted for 30 minutes goes back",
    {
      clock: "10:35",
      read: false,
      pending: { inline: { ...sent("delta"), kind: "inline", reason: "scan now" } },
    },
    "release: the inline batch went unposted",
  ],
  [
    "an inline batch 25 minutes old stays the run's to post",
    {
      clock: "10:30",
      read: false,
      pending: { inline: { ...sent("delta"), kind: "inline", reason: "scan now" } },
    },
    "read",
  ],
  [
    "a new inline scan takes back the last inline batch",
    {
      mode: "inline",
      read: false,
      pending: { inline: { ...sent("delta"), kind: "inline", reason: "scan now" } },
    },
    "release: the inline batch went unposted",
  ],
  [
    "an idle thread whose last reply names the batch has it",
    {
      read: false,
      thread: { kind: "idle", lastText: `Posted. (batch ${BATCH})` },
      pending: { sent: sent("delta") },
    },
    "settle sent",
  ],
  [
    "a reply naming a longer id that starts alike doesn't",
    {
      read: false,
      thread: { kind: "idle", lastText: `(batch ${BATCH}4)` },
      pending: { sent: sent("delta") },
    },
    "read",
  ],
  [
    "a busy thread's reply isn't read yet",
    { read: false, thread: { kind: "busy" }, pending: { sent: sent("delta") } },
    "read",
  ],
  [
    "a delta quiet holds joins the overview that is due",
    {
      clock: "09:05",
      day: FRI,
      read: false,
      quiet: `${FRI}T13:00:00Z`,
      pending: { sent: sent("delta") },
    },
    "rejoin: the held delta joins the overview",
  ],
  // The batch in flight, once the sources are read.
  [
    "a busy thread holds the resend",
    { thread: { kind: "busy" }, pending: { sent: sent("delta") } },
    "wait: the sent batch waits for the busy or unreadable thread",
  ],
  [
    "an unreadable thread holds it too",
    { thread: { kind: "unreadable" }, pending: { sent: sent("delta") } },
    "wait: the sent batch waits for the busy or unreadable thread",
  ],
  [
    "quiet holds a resent delta",
    { quiet: `${THU}T13:00:00Z`, meta: today, pending: { sent: sent("delta") } },
    "wait: the sent batch waits for the quiet or pause to end",
  ],
  [
    "pause holds a resent overview",
    { paused: `${FRI}T08:00:00Z`, pending: { sent: sent("overview") } },
    "wait: the sent batch waits for the quiet or pause to end",
  ],
  [
    "an undelivered batch on an idle thread goes once more",
    { pending: { sent: sent("delta", 1) } },
    "resend: resending the undelivered batch",
  ],
  [
    "after the retry the unit fails",
    { pending: { sent: sent("delta", 2) } },
    `giveUp: batch ${BATCH} undelivered after 2 wakes`,
  ],
  [
    "more retries in the schedule allow more",
    { schedule: { retries: 2 }, pending: { sent: sent("delta", 2) } },
    "resend: resending the undelivered batch",
  ],
  // New wakes.
  [
    "the inline scan freezes what it gathered",
    { mode: "inline" },
    "inline: inline batch for this run to post",
  ],
  [
    "the first scan records a baseline",
    { first: true, pending: { gathered: [assigned] } },
    "wait: the first scan records a baseline and wakes nothing",
  ],
  [
    "no thread yet: the timer sends nothing",
    { thread: { kind: "absent" }, meta: today, pending: { gathered: [assigned] } },
    "wait: the profile names no assistant thread yet",
  ],
  [
    "a dry run with no thread yet decides as if one were idle",
    { mode: "dry", thread: { kind: "absent" }, meta: today, pending: { gathered: [assigned] } },
    "wake delta: ENG-1",
  ],
  [
    "a pause holds everything",
    { paused: `${FRI}T08:00:00Z`, pending: { gathered: [assigned] } },
    `wait: paused until ${FRI}T08:00:00Z`,
  ],
  [
    "nothing wakes outside the window",
    { clock: "08:30", pending: { gathered: [assigned] } },
    "wait: outside the scan window",
  ],
  [
    "the weekday overview carries everything gathered",
    { clock: "09:05", pending: { gathered: [moved, fresh] } },
    "wake overview: ENG-4 ENG-3",
  ],
  ["the overview goes out late after a missed scan", { clock: "14:05" }, "wake overview: "],
  [
    "quiet lets the overview through",
    { clock: "09:05", quiet: `${THU}T13:00:00Z` },
    "wake overview: ",
  ],
  [
    "but holds a delta",
    { meta: today, quiet: `${THU}T13:00:00Z`, pending: { gathered: [assigned] } },
    `wait: quiet until ${THU}T13:00:00Z`,
  ],
  [
    "a now change wakes with everything gathered",
    { meta: today, pending: { gathered: [moved, comment] } },
    "wake delta: ENG-4 ENG-2",
  ],
  [
    "a busy thread holds a new wake",
    { meta: today, thread: { kind: "busy" }, pending: { gathered: [comment] } },
    "wait: a change worth a wake, held while the thread is busy or unreadable",
  ],
  [
    "a batched change waits for a slot",
    { meta: today, pending: { gathered: [fresh] } },
    "wait: nothing worth a wake yet",
  ],
  [
    "and goes at the slot",
    { clock: "13:05", meta: today, pending: { gathered: [fresh, moved] } },
    "wake delta: ENG-3 ENG-4",
  ],
  [
    "once per slot",
    {
      clock: "13:35",
      meta: { ...today, slots: { [THU]: [parse(clock, "13:00")] } },
      pending: { gathered: [fresh] },
    },
    "wait: nothing worth a wake yet",
  ],
  [
    "pulse alone never wakes",
    { clock: "13:05", meta: today, pending: { gathered: [moved] } },
    "wait: nothing worth a wake yet",
  ],
  [
    "a weekend wakes only for the urgent",
    { day: SAT, pending: { gathered: [comment, assigned, moved] } },
    "wake delta: ENG-1",
  ],
  [
    "and nothing else",
    { day: SAT, pending: { gathered: [comment, moved] } },
    "wait: weekend: nothing urgent",
  ],
  [
    "past the day's deltas only the urgent",
    { meta: { ...today, deltas: { [THU]: 6 } }, pending: { gathered: [comment, assigned] } },
    "wake delta: ENG-1",
  ],
  [
    "a smaller cap from the schedule",
    {
      schedule: { daily_deltas: 1 },
      meta: { ...today, deltas: { [THU]: 1 } },
      pending: { gathered: [comment] },
    },
    "wait: past 1 deltas today: nothing urgent",
  ],
];

for (const [name, given, expected] of TABLE) {
  test(`policy: ${name}`, () => assert.equal(summary(nextStep(situation(given))), expected));
}

/**
 * The steps of one scan, carried out as the runner carries them out, until one ends it. `found` is
 * what the sources return when they are read.
 */
function drive(given: Given, found: Change[] = []): string[] {
  let s = situation({ ...given, read: false });
  const steps: string[] = [];
  for (;;) {
    const step = nextStep(s);
    steps.push(summary(step));
    const now = s.at.instant;
    if (step.kind === "settle" || step.kind === "release" || step.kind === "rejoin") {
      s = { ...s, pending: apply(step, s.pending, now) };
    } else if (step.kind === "read") {
      s = {
        ...s,
        read: true,
        pending: { ...s.pending, gathered: gather(s.pending.gathered, found, new Set()) },
      };
    } else return steps;
  }
}

test("a reply that names the batch settles it before the read, so the same scan can wake again", () => {
  const thread: Thread = { kind: "idle", lastText: `(batch ${BATCH})` };
  assert.deepEqual(drive({ thread, meta: today, pending: { sent: sent("delta") } }, [assigned]), [
    "settle sent",
    "read",
    "wake delta: ENG-1",
  ]);
});

test("a held delta rejoins before the read, so the overview carries it ahead of what the read finds", () => {
  const given: Given = {
    clock: "09:05",
    day: FRI,
    quiet: `${FRI}T13:00:00Z`,
    pending: { sent: sent("delta") },
  };
  assert.deepEqual(drive(given, [assigned]), [
    "rejoin: the held delta joins the overview",
    "read",
    "wake overview: ENG-2 ENG-1",
  ]);
});

test("the ledger settles the sent batch, then the inline one, before anything else", () => {
  const inline = {
    ...sent("delta"),
    id: "acme-20261126-1015-2",
    kind: "inline" as const,
    reason: "scan now",
  };
  assert.deepEqual(
    drive({ meta: today, delivered: [BATCH, inline.id], pending: { sent: sent("delta"), inline } }),
    ["settle sent", "settle inline", "read", "wait: nothing worth a wake yet"],
  );
});

test("an inline scan gives back the last inline batch, reads, and freezes everything", () => {
  const inline = { ...sent("delta"), kind: "inline" as const, reason: "scan now" };
  assert.deepEqual(drive({ mode: "inline", pending: { inline } }, [assigned]), [
    "release: the inline batch went unposted",
    "read",
    "inline: inline batch for this run to post",
  ]);
});
