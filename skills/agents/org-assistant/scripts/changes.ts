/**
 * What a change is, and how soon each kind reaches the user. A change holds ids, kinds, states,
 * counts, and staff names only: never a ticket title, a message body, or anything about a
 * practitioner. `references/rules.md` gives the tiers for people; `KINDS` is the one table the scan
 * reads them from.
 */
import {
  type Infer,
  type Parser,
  ShapeError,
  array,
  boolean,
  count,
  literal,
  nullable,
  number,
  object,
  oneOf,
  optional,
  string,
  unknown,
} from "./parse.ts";

/** Now wakes at the next scan, batch at the next wake or batch slot, pulse never on its own. */
export type Tier = "now" | "batch" | "pulse";

const strict = { strict: true };

const none = object({}, strict);
/** An inbox notification, by its Linear type. */
const inbox = object({ type: nullable(string) }, strict);
const status = object({ field: literal("status"), to: nullable(string) }, strict);
/** Linear's tools don't say who changed a priority or due date. */
const field = object(
  {
    field: literal("priority", "due"),
    to: nullable(oneOf(number, string)),
    by: literal("unknown"),
  },
  strict,
);
const team = object({ team: string, who: string, finished: boolean }, strict);
const newInTeam = object({ team: string, who: string, new: literal(true) }, strict);
/** A T3 thread by its id, link, status, and item count; one the assistant started names its ticket. */
const thread = oneOf(
  object({ status: string, link: string, items: count, started: literal(false) }, strict),
  object(
    { status: string, link: string, items: count, started: literal(true), ticket: string },
    strict,
  ),
);

/**
 * Each kind's tier; `urgent` marks the kinds a weekend, or a day past its delta cap, still wakes
 * for: a person waiting on the user, a new assignment, a deadline within 24 hours. `detail` reads
 * what a change of the kind carries.
 */
export const KINDS = {
  "ticket.assigned": { tier: "now", urgent: true, detail: inbox },
  "ticket.unassigned": { tier: "now", urgent: false, detail: inbox },
  "ticket.changed": { tier: "now", urgent: false, detail: oneOf(inbox, status, field) },
  "ticket.mention": { tier: "now", urgent: true, detail: inbox },
  "ticket.comment": { tier: "now", urgent: false, detail: inbox },
  "ticket.unblocked": {
    tier: "now",
    urgent: false,
    detail: object({ blocker: string, to: nullable(string) }, strict),
  },
  "deadline.soon": { tier: "now", urgent: true, detail: object({ due: string }, strict) },
  "slack.waiting": {
    tier: "now",
    urgent: true,
    detail: object({ via: literal("dm", "mention"), channel: string, minutes: number }, strict),
  },
  "pr.review_requested": { tier: "now", urgent: true, detail: none },
  "pr.changes_requested": { tier: "now", urgent: false, detail: none },
  "pr.ci_failed": { tier: "now", urgent: false, detail: none },
  "issue.assigned": { tier: "now", urgent: true, detail: none },
  "release.awaited": { tier: "now", urgent: false, detail: object({ prs: array(string) }, strict) },
  "dependency.changed": {
    tier: "batch",
    urgent: false,
    detail: object(
      { blocks: string, before: nullable(string), to: nullable(string), owner: nullable(string) },
      strict,
    ),
  },
  "ticket.new_in_project": {
    tier: "batch",
    urgent: false,
    detail: object({ project: string }, strict),
  },
  /** An agent waits on the user. */
  "thread.waiting": { tier: "now", urgent: false, detail: thread },
  "thread.failed": { tier: "now", urgent: false, detail: thread },
  "thread.finished": { tier: "batch", urgent: false, detail: thread },
  /** Running an hour with no new item. */
  "thread.stalled": { tier: "batch", urgent: false, detail: thread },
  "ticket.moved": { tier: "pulse", urgent: false, detail: status },
  "linear.other": { tier: "pulse", urgent: false, detail: inbox },
  "pr.approved": { tier: "pulse", urgent: false, detail: none },
  "pr.opened": { tier: "pulse", urgent: false, detail: none },
  "pr.closed": { tier: "pulse", urgent: false, detail: none },
  "release.new": { tier: "pulse", urgent: false, detail: object({ prs: array(string) }, strict) },
  "issue.new": { tier: "pulse", urgent: false, detail: none },
  /** A thread that wasn't there at the last scan. */
  "thread.started": { tier: "pulse", urgent: false, detail: thread },
  "team.pulse": { tier: "pulse", urgent: false, detail: oneOf(team, newInTeam) },
  "slack.channel": { tier: "pulse", urgent: false, detail: object({ name: string }, strict) },
} satisfies Record<string, { tier: Tier; urgent: boolean; detail: Parser<unknown> }>;

export type ChangeKind = keyof typeof KINDS;
export type Detail<K extends ChangeKind> = Infer<(typeof KINDS)[K]["detail"]>;

type Item<K extends ChangeKind> = {
  /** The same however often the scan sees the same event, so a replay after a crash adds it once. */
  id: string;
  kind: K;
  /** What changed: a ticket id, `owner/repo#12`, `slack:<channel>:<ts>`, or `t3:<thread>`. */
  ref: string;
  at: string;
  /** The profile's name for the source that found it. */
  source: string;
  /** A wider thing a mute can name, such as `slack:<channel>`. */
  scope?: string;
  detail: Detail<K>;
};
/** A change of kind K, or of any kind in K when K is a union. */
export type ChangeOf<K extends ChangeKind> = K extends ChangeKind ? Item<K> : never;
export type Change = ChangeOf<ChangeKind>;

export type ChangeFields<K extends ChangeKind> = {
  ref: string;
  at: string;
  /**
   * What tells this event from another of the same kind and ref; the time by default. A count,
   * such as a team's moves, takes the scan window's start: one item per window, which the post sums.
   */
  key?: string;
  scope?: string;
  detail: Detail<K>;
};

export function change<K extends ChangeKind>(
  source: string,
  kind: K,
  fields: ChangeFields<K>,
): ChangeOf<K> {
  const { ref, at, key, scope, detail } = fields;
  const item: Item<K> = {
    id: `${kind}:${ref}:${key || at}`,
    kind,
    ref,
    at,
    source,
    ...(scope ? { scope } : {}),
    detail,
  };
  // An Item of a kind in K is a ChangeOf<K>; the compiler can't distribute a generic K to see it.
  return item as ChangeOf<K>;
}

function isKind(kind: string): kind is ChangeKind {
  return Object.hasOwn(KINDS, kind);
}

const base = object({
  id: string,
  kind: string,
  ref: string,
  at: string,
  source: string,
  scope: optional(string),
  detail: unknown,
});

/** A change read back from pending.json. */
export const changeParser: Parser<Change> = (value, path) => {
  const read = base(value, path);
  const kind = read.kind;
  if (!isKind(kind)) throw new ShapeError(`${path}.kind`, "is not a kind of change");
  const detail = KINDS[kind].detail(read.detail, `${path}.detail`);
  // The detail was read by its own kind's parser just above.
  return { ...read, kind, detail } as Change;
};

export function tier(item: Change): Tier {
  return KINDS[item.kind].tier;
}

export function urgent(item: Change): boolean {
  return KINDS[item.kind].urgent;
}

/** `items` plus each change in `found` whose id is neither gathered already nor in `skip`. */
export function gather(items: Change[], found: Change[], skip: ReadonlySet<string>): Change[] {
  const known = new Set([...items.map((item) => item.id), ...skip]);
  const out = [...items];
  for (const item of found) {
    if (known.has(item.id)) continue;
    known.add(item.id);
    out.push(item);
  }
  return out;
}

export type Mute = { ref: string; until: string | null };

/** A mute names a ref (`ENG-12`, `owner/repo#3`), a scope (`slack:C123`), or a kind, until a time. */
export function muted(item: Change, mutes: Mute[], now: Date): boolean {
  return mutes.some(
    (mute) =>
      (mute.until === null || Date.parse(mute.until) > now.getTime()) &&
      [item.ref, item.scope, item.kind].includes(mute.ref),
  );
}
