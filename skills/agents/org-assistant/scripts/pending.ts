/**
 * pending.json: everything that decides a send. `sent` is the batch the last wake carried, frozen
 * with its tries until it is delivered; `inline` is the batch a "scan now" froze for its run;
 * `gathered` holds the changes since; `seen` the ids delivered in the last week, so the same events
 * never join a later batch; and `meta` what today already sent. Each function here returns the
 * pending state it was given with one change made.
 */
import { type Change, changeParser } from "./changes.ts";
import {
  type Infer,
  array,
  count,
  literal,
  nullable,
  object,
  record,
  string,
  boolean,
  withDefault,
} from "./parse.ts";
import type { Schedule } from "./profile.ts";
import { type Local, clock, instant, iso } from "./time.ts";

const tryParser = object({ at: instant, ok: nullable(boolean) });

const sent = object({
  /** An id no earlier batch had, such as `acme-20261126-1005-14`. */
  id: string,
  kind: literal("overview", "delta"),
  items: array(changeParser),
  frozen_at: string,
  /**
   * Each wake that carried it; `ok` is null while its send runs, so a crash mid-send still counts.
   */
  tries: array(tryParser),
  /** Why it woke the thread, for the wake message. */
  reason: string,
});

const inline = object({
  id: string,
  kind: literal("inline"),
  items: array(changeParser),
  frozen_at: string,
  reason: string,
});

const meta = object({
  /** The local date of today's overview, and its batch. */
  overview_on: nullable(string),
  overview_id: nullable(string),
  /**
   * Today's overview batch once it is settled, whether the ledger or the thread's last reply marked
   * it, so `status` counts it delivered either way.
   */
  overview_delivered: nullable(string),
  deltas: withDefault(record(count), {}),
  /** The batch slots today's wakes already covered. */
  slots: withDefault(record(array(clock)), {}),
});

export const pendingParser = object({
  sent: nullable(sent),
  inline: nullable(inline),
  gathered: withDefault(array(changeParser), []),
  /** Change id → when it was delivered. */
  seen: withDefault(record(string), {}),
  meta: withDefault(meta, {}),
  /** The last batch number, so each batch id is new. */
  serial: withDefault(count, 0),
});

export type SentBatch = Infer<typeof sent>;
export type InlineBatch = Infer<typeof inline>;
export type Meta = Infer<typeof meta>;
export type Pending = Infer<typeof pendingParser>;
export type Slot = "sent" | "inline";

export const EMPTY_PENDING: Pending = {
  sent: null,
  inline: null,
  gathered: [],
  seen: {},
  meta: { overview_on: null, overview_id: null, overview_delivered: null, deltas: {}, slots: {} },
  serial: 0,
};

/**
 * How long a delivered id is kept. A source that reports a change again while it holds stops before
 * this, so a change it reported once never joins a batch again.
 */
export const SEEN_FOR = 7 * 24 * 3_600_000;

/** Forgets the ids delivered more than a week ago. */
export function forgetOld(pending: Pending, now: Date): Pending {
  const since = now.getTime() - SEEN_FOR;
  return {
    ...pending,
    seen: Object.fromEntries(
      Object.entries(pending.seen).filter(([, at]) => Date.parse(at) >= since),
    ),
  };
}

/** Moves a delivered batch's ids into `seen`, so the same events never join a later batch. */
export function settle(pending: Pending, slot: Slot, now: Date): Pending {
  const batch = pending[slot];
  if (batch === null) return pending;
  const seen = { ...pending.seen };
  for (const item of batch.items) seen[item.id] = iso(now);
  const overview = batch.id === pending.meta.overview_id;
  return {
    ...pending,
    [slot]: null,
    seen,
    meta: overview ? { ...pending.meta, overview_delivered: batch.id } : pending.meta,
  };
}

/** Puts an undelivered batch's items back at the front of `gathered`. */
export function unfreeze(pending: Pending, slot: Slot): Pending {
  const batch = pending[slot];
  if (batch === null) return pending;
  const ids = new Set(batch.items.map((item) => item.id));
  return {
    ...pending,
    [slot]: null,
    gathered: [...batch.items, ...pending.gathered.filter((item) => !ids.has(item.id))],
  };
}

/** The ids a later scan must not gather again: delivered this week, or frozen in a batch. */
export function known(pending: Pending): Set<string> {
  const frozen = [pending.sent, pending.inline].flatMap((batch) => batch?.items ?? []);
  return new Set([...Object.keys(pending.seen), ...frozen.map((item) => item.id)]);
}

/** A new batch id, and the pending state with `items` taken out of `gathered`. */
function take(pending: Pending, org: string, at: Local, items: Change[]) {
  const serial = pending.serial + 1;
  const ids = new Set(items.map((item) => item.id));
  return {
    id: `${org}-${at.date.replaceAll("-", "")}-${at.clock.replace(":", "")}-${serial}`,
    rest: { ...pending, serial, gathered: pending.gathered.filter((item) => !ids.has(item.id)) },
  };
}

/** Freezes everything gathered as the batch a "scan now" run posts. */
export function freezeInline(pending: Pending, batch: { org: string; at: Local }): Pending {
  const { org, at } = batch;
  const items = pending.gathered;
  const { id, rest } = take(pending, org, at, items);
  return {
    ...rest,
    inline: { id, kind: "inline", items, frozen_at: iso(at.instant), reason: "scan now" },
  };
}

/**
 * Freezes the changes a wake carries as `sent`, and counts the wake in `meta` beside it, so the
 * batch and what today already sent are written together.
 */
export function freezeSent(
  pending: Pending,
  wake: {
    org: string;
    at: Local;
    schedule: Schedule;
    kind: SentBatch["kind"];
    items: Change[];
    reason: string;
  },
): Pending {
  const { org, at, schedule } = wake;
  const { id, rest } = take(pending, org, at, wake.items);
  const today = at.date;
  const old = rest.meta;
  const deltas =
    wake.kind === "delta" ? { [today]: (old.deltas[today] ?? 0) + 1 } : pick(old.deltas, today);
  const covered = schedule.batch_slots.filter((slot) => slot <= at.clock);
  const slots = { [today]: [...new Set([...(old.slots[today] ?? []), ...covered])].sort() };
  return {
    ...rest,
    sent: {
      id,
      kind: wake.kind,
      items: wake.items,
      frozen_at: iso(at.instant),
      tries: [],
      reason: wake.reason,
    },
    meta: {
      ...old,
      ...(wake.kind === "overview" ? { overview_on: today, overview_id: id } : {}),
      deltas,
      slots,
    },
  };
}

/** Only today's entry of a per-day count, if it has one. */
function pick<T>(byDay: Record<string, T>, today: string): Record<string, T> {
  const entry = byDay[today];
  return entry === undefined ? {} : { [today]: entry };
}

/** Records a wake of the sent batch before it goes out, so a crash mid-send still counts it. */
export function startTry(pending: Pending, at: Date): Pending {
  if (pending.sent === null) return pending;
  return {
    ...pending,
    sent: { ...pending.sent, tries: [...pending.sent.tries, { at: iso(at), ok: null }] },
  };
}

/** Records whether the wake's send went through. */
export function finishTry(pending: Pending, ok: boolean): Pending {
  if (pending.sent === null) return pending;
  const tries = pending.sent.tries.map((entry, index, all) =>
    index === all.length - 1 ? { ...entry, ok } : entry,
  );
  return { ...pending, sent: { ...pending.sent, tries } };
}
