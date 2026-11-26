/**
 * ledger.json: the model's record, which the scan reads but never writes. Each command in COMMANDS
 * reads the ledger and, unless it only shows it, changes one thing, and the CLI replaces the file
 * atomically; running a command again, at any later time, leaves the ledger as its first run did.
 */
import {
  type Infer,
  type ObjectOf,
  type Parser,
  array,
  boolean,
  count,
  literal,
  oneOf,
  nullable,
  object,
  optional,
  parse,
  string,
  withDefault,
} from "./parse.ts";
import { MINUTE, type WrittenTime, instantOf, iso, written } from "./time.ts";

const KEEP = 50; // entries kept in each history list
const KEEP_LOG = 200;
/** A call that replaced another this recently makes a bare letter ambiguous. */
const CHANGED = 15 * MINUTE;
export const LOG_KINDS = ["told", "asked", "answered", "offered", "declined"] as const;
export const ANSWERS = ["depends", "unrelated"] as const;

const call = object({ id: string, text: string, since: string, replaced: nullable(string) });
const list = <T>(parser: (value: unknown, path: string) => T) => withDefault(array(parser), []);

export const ledgerParser = object({
  delivered: list(object({ batch: string, at: string })),
  quiet_until: nullable(string),
  paused_until: nullable(string),
  mutes: list(object({ ref: string, until: nullable(string) })),
  /** The one open call, numbered such as `c3`, and the queue behind it. */
  call: nullable(call),
  queue: list(object({ text: string, queued: string })),
  serial: withDefault(count, 0),
  /**
   * The call cleared last with nothing queued, which the next call names as the one it replaced.
   */
  cleared: nullable(string),
  dropped: list(
    object({
      id: string,
      text: string,
      since: string,
      replaced: nullable(string),
      dropped: string,
    }),
  ),
  started: list(object({ thread: string, ticket: string, at: string })),
  /** A PR that waits on another repository's release. */
  waits: list(object({ pr: string, on: string })),
  depends: list(object({ ticket: string, on: string })),
  leads: list(object({ ticket: string, on: string, answer: literal(...ANSWERS), at: string })),
  log: list(object({ at: string, kind: literal(...LOG_KINDS), text: string })),
});

export type Ledger = Infer<typeof ledgerParser>;
/** The ledger before its first command: every list empty, nothing held, no call. */
export const EMPTY_LEDGER: Ledger = parse(ledgerParser, {});

/** A ledger command the user's words can't carry out, such as setting a call while one is open. */
export class LedgerError extends Error {}

/** The time a command runs at, and the profile's timezone for times written without an offset. */
export type Context = { now: Date; zone: string };

type Shape = Record<string, Parser<unknown>>;
type Outcome = { out: string; ledger?: Ledger };

/** A command as the CLI runs it: its words in, what to print and the new ledger out. */
export type Command = {
  /** Positional argument names, in order. */
  args: string[];
  options: string[];
  help: string;
  /** Whether it can change the ledger, so the CLI runs it holding the ledger's lock. */
  writes: boolean;
  /** Throws a ShapeError when an argument or option doesn't fit, which the CLI reports as usage. */
  execute(
    ledger: Ledger,
    positionals: string[],
    options: Record<string, unknown>,
    context: Context,
  ): Outcome;
};

/**
 * A command whose positionals, named in `args` order, and options are read by one parser; an option
 * the command doesn't take fails it.
 */
function command<A extends Shape, O extends Shape>(spec: {
  args: A;
  options: O;
  help: string;
  run(ledger: Ledger, input: ObjectOf<A & O>, context: Context): Outcome;
}): Command {
  const names = Object.keys(spec.args);
  const input = object({ ...spec.args, ...spec.options }, { strict: true });
  return {
    args: names,
    options: Object.keys(spec.options),
    help: spec.help,
    writes: true,
    execute: (ledger, positionals, given, context) => {
      const named = Object.fromEntries(names.map((name, index) => [name, positionals[index]]));
      return spec.run(ledger, parse(input, { ...named, ...given }), context);
    },
  };
}

/** A command that takes no arguments and only shows the ledger, as `show` prints it. */
function view(help: string, show: (ledger: Ledger, now: Date) => string): Command {
  const run = (ledger: Ledger, _input: object, { now }: Context) => ({ out: show(ledger, now) });
  return { ...command({ args: {}, options: {}, help, run }), writes: false };
}

/**
 * `list` with `entry` in place of any entry with its key: "replace by key, then append". An entry
 * that matches the one there in every field but its time leaves the list as it is, so a repeat keeps
 * the first time and the entry's place.
 */
function upsert<T extends Record<string, string | null>>(
  list: T[],
  entry: T,
  key: (item: T) => string,
): T[] {
  const old = list.find((item) => key(item) === key(entry));
  const same = (field: string) => field === "at" || old?.[field] === entry[field];
  if (old !== undefined && Object.keys(entry).every(same)) return list;
  return [...list.filter((item) => key(item) !== key(entry)), entry];
}

/** A time the user gave, read in the profile's timezone unless it names an offset, as UTC. */
const utc = (time: WrittenTime, zone: string) => iso(instantOf(time, zone));

function showCall(ledger: Ledger, now: Date): string {
  const queued = `${ledger.queue.length} queued`;
  if (ledger.call === null) return `no open call · ${queued}`;
  const age = now.getTime() - Date.parse(ledger.call.since);
  const minutes = Math.floor(age / MINUTE);
  let line = `open call ${ledger.call.id} (${minutes} min old): ${ledger.call.text} · ${queued}`;
  if (ledger.call.replaced !== null && age < CHANGED) {
    line += `\n⚠️ It replaced another call ${minutes} min ago: ${ledger.call.replaced}. Ask which one a bare letter means.`;
  }
  return line;
}

/** Raises the oldest queued offer as the open call, numbering it. */
function openNext(ledger: Ledger, now: Date, replaced: string | null): Ledger {
  const [next, ...rest] = ledger.queue;
  if (next === undefined) return { ...ledger, call: null };
  const serial = ledger.serial + 1;
  return {
    ...ledger,
    serial,
    queue: rest,
    call: { id: `c${serial}`, text: next.text, since: iso(now), replaced },
  };
}

/** `call clear` and `call drop` settle the open call by its id; a repeat leaves the next alone. */
function settleCall(how: "clear" | "drop", help: string): Command {
  return command({
    args: { id: string },
    options: {},
    help,
    run: (ledger, { id }, { now }) => {
      const open = ledger.call;
      if (open === null || open.id !== id) return { out: showCall(ledger, now) };
      const dropped =
        how === "drop"
          ? [{ ...open, dropped: iso(now) }, ...ledger.dropped].slice(0, KEEP)
          : ledger.dropped;
      const recent = `${open.id}: ${open.text}`;
      const next = openNext({ ...ledger, dropped }, now, recent);
      const settled =
        next.call === null ? { ...next, cleared: how === "clear" ? recent : null } : next;
      return { out: showCall(settled, now), ledger: settled };
    },
  });
}

const untilOrOff = oneOf(literal("off"), written);

function hold(key: "quiet_until" | "paused_until", help: string): Command {
  return command({
    args: { until: untilOrOff },
    options: {},
    help,
    run: (ledger, input, { zone }) => {
      const until = input.until === "off" ? null : utc(input.until, zone);
      return { out: `${key}: ${until ?? "off"}`, ledger: { ...ledger, [key]: until } };
    },
  });
}

const answer = literal(...ANSWERS);
const logKind = literal(...LOG_KINDS);
const time = optional(written);
const flag = withDefault(boolean, false);

export const COMMANDS: Record<string, Command> = {
  show: view("print the whole ledger", (ledger) => JSON.stringify(ledger, null, 1)),
  delivered: command({
    args: { batch: string },
    options: {},
    help: "mark a batch you posted delivered",
    run: (ledger, { batch }, { now }) => ({
      out: `batch ${batch} delivered`,
      ledger: ledger.delivered.some((entry) => entry.batch === batch)
        ? ledger
        : { ...ledger, delivered: [{ batch, at: iso(now) }, ...ledger.delivered].slice(0, KEEP) },
    }),
  }),
  quiet: hold("quiet_until", "hold deltas until a time in the profile's timezone, or off"),
  pause: hold("paused_until", "hold every wake until a time in the profile's timezone, or off"),
  mute: command({
    args: { ref: string },
    options: { until: time },
    help: "drop changes to a ticket, a PR, slack:<channel>, or a change kind, optionally --until a time",
    run: (ledger, { ref, until }, { zone }) => ({
      out: `muted ${ref}`,
      ledger: {
        ...ledger,
        mutes: upsert(
          ledger.mutes,
          { ref, until: until === undefined ? null : utc(until, zone) },
          (m) => m.ref,
        ),
      },
    }),
  }),
  unmute: command({
    args: { ref: string },
    options: {},
    help: "end a mute",
    run: (ledger, { ref }) => ({
      out: `unmuted ${ref}`,
      ledger: { ...ledger, mutes: ledger.mutes.filter((mute) => mute.ref !== ref) },
    }),
  }),
  "call show": view("the open call, its id and age, and the queue's length", showCall),
  "call set": command({
    args: { text: string },
    options: {},
    help: "open a call when none is open",
    run: (ledger, { text }, { now }) => {
      if (ledger.call?.text === text) return { out: showCall(ledger, now) };
      if (ledger.call !== null) {
        throw new LedgerError(
          `call ${ledger.call.id} is open; queue this one, or clear that call first`,
        );
      }
      const opened = openNext(
        { ...ledger, queue: [{ text, queued: iso(now) }, ...ledger.queue], cleared: null },
        now,
        ledger.cleared,
      );
      return { out: showCall(opened, now), ledger: opened };
    },
  }),
  "call queue": command({
    args: { text: string },
    options: {},
    help: "queue an offer behind the open call",
    run: (ledger, { text }, { now }) => {
      if (ledger.call?.text === text || ledger.queue.some((entry) => entry.text === text)) {
        return { out: showCall(ledger, now) };
      }
      const queued = { ...ledger, queue: [...ledger.queue, { text, queued: iso(now) }] };
      return { out: showCall(queued, now), ledger: queued };
    },
  }),
  "call clear": settleCall(
    "clear",
    "settle the call the user answered, by its id, raising the oldest queued offer",
  ),
  "call drop": settleCall("drop", "drop the call the overview leaves unanswered, by its id"),
  started: command({
    args: { thread: string },
    options: { ticket: string },
    help: "follow a thread you launched, with --ticket <id>",
    run: (ledger, { thread, ticket }, { now }) => ({
      out: `following ${thread} for ${ticket}`,
      ledger: {
        ...ledger,
        started: upsert(ledger.started, { thread, ticket, at: iso(now) }, (s) => s.thread),
      },
    }),
  }),
  finished: command({
    args: { thread: string },
    options: {},
    help: "stop following a thread",
    run: (ledger, { thread }) => ({
      out: `no longer following ${thread}`,
      ledger: { ...ledger, started: ledger.started.filter((entry) => entry.thread !== thread) },
    }),
  }),
  waits: command({
    args: { pr: string, on: string },
    options: {},
    help: "a PR that waits on another repository's release (owner/repo), or off",
    run: (ledger, { pr, on }) => ({
      out: `${pr} waits on ${on}`,
      ledger: {
        ...ledger,
        waits:
          on === "off"
            ? ledger.waits.filter((wait) => wait.pr !== pr)
            : upsert(ledger.waits, { pr, on }, (wait) => wait.pr),
      },
    }),
  }),
  depends: command({
    args: { ticket: string, on: string },
    options: { remove: flag },
    help: "a dependency the user confirmed, or --remove one",
    run: (ledger, { ticket, on, remove }) => {
      const pair = { ticket, on };
      const key = (entry: typeof pair) => `${entry.ticket} ${entry.on}`;
      return {
        out: `${ticket} ${remove ? "no longer depends" : "depends"} on ${on}`,
        ledger: {
          ...ledger,
          depends: remove
            ? ledger.depends.filter((entry) => key(entry) !== key(pair))
            : upsert(ledger.depends, pair, key),
        },
      };
    },
  }),
  lead: command({
    args: { ticket: string, on: string, answer },
    options: {},
    help: "the user's answer about a ticket that mentions another: depends or unrelated",
    run: (ledger, { ticket, on, answer }, { now }) => ({
      out: `lead ${ticket} → ${on}: ${answer}`,
      ledger: {
        ...ledger,
        leads: upsert(
          ledger.leads,
          { ticket, on, answer, at: iso(now) },
          (l) => `${l.ticket} ${l.on}`,
        ),
      },
    }),
  }),
  log: command({
    args: { kind: logKind, text: string },
    options: {},
    help: "what the user was told, asked, answered, offered, or declined, in ids and a few words",
    run: (ledger, { kind, text }, { now }) => {
      const [newest] = ledger.log;
      if (newest?.kind === kind && newest.text === text) return { out: `logged ${kind}` };
      return {
        out: `logged ${kind}`,
        ledger: {
          ...ledger,
          log: [{ at: iso(now), kind, text }, ...ledger.log].slice(0, KEEP_LOG),
        },
      };
    },
  }),
};
