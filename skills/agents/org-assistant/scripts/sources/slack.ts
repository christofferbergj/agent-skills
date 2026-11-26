/**
 * Slack: direct messages and mentions the user hasn't answered, and a message count for each
 * confirmed channel. The waiting list is kept apart from the search cursors, so a message stays on
 * it across scans until the user answers or it has woken the thread once. Keeps channel, message,
 * and thread ids only: the search text is parsed for them and dropped, and so is the sender.
 */
import { Executor, LIMITED, SourceError, read } from "../calls.ts";
import type { Change } from "../changes.ts";
import {
  type Infer,
  array,
  boolean,
  nullable,
  number,
  object,
  optional,
  string,
} from "../parse.ts";
import type { SlackSource } from "../profile.ts";
import { DAY, type SlackTs, fromSlackTs, isSlackTs, iso, sleep, slackTs } from "../time.ts";
import type { Adapter, Context, Window } from "./index.ts";

const TOOL = "tools.slack.mcp.slack_search_public_and_private";
const PAGES = 10; // 20 messages a page
const LIMIT = 20;
const FORGET = 3 * DAY; // a waiting message older than this leaves the list
const SEARCHES = ["dm", "mention", "channels"] as const;
type Search = (typeof SEARCHES)[number];
const COMMON = { response_format: "detailed", include_context: false, limit: LIMIT };
/** Seconds each search reaches back before its cursor, for messages Slack indexed late. */
const OVERLAP = 600;
const RESULT = /^### Result (\d+) of (\d+)\s*$/gm;
const CHANNEL = /^Channel: (.*?)\s*\(ID: ([A-Z0-9]+)\)/m;
const FROM = /^From: .*\(ID: ([A-Z0-9]+)\)/m;
const TS = /^Message_ts: ([0-9]+\.[0-9]+)/m;
const THREAD = /[?&]thread_ts=([0-9]+\.[0-9]+)/;
const CURSOR = /`([A-Za-z0-9+/=_-]{8,})`/;
const BOTS = new Set(["U00", "USLACKBOT"]);

const HEADER = /^## Messages \((\d+) results?\)/m;
/** One message for each call when a page has to be read again; one page's re-read stops here. */
const REREAD = 2 * LIMIT;

const seconds = (name: string, fallback: number) => Number(process.env[name] ?? fallback) * 1000;

/**
 * Where a search's next run starts: OVERLAP before `at`, the time its last finished read began. A
 * read cut off at the page budget saves the `after` it asked from, the next page's cursor, and the
 * last message it reached, and goes on from there at the next scan; once that read is done, `at`
 * moves to `until`, when it began, so nothing it hadn't reached is skipped.
 */
const cursor = object({
  at: number,
  more: nullable(object({ after: string, page: string, last: nullable(slackTs), until: number })),
});
type Cursor = Infer<typeof cursor>;

const waiting = object({
  channel: string,
  ts: slackTs,
  /** The thread it was posted in, when it wasn't the thread's first message. */
  thread: nullable(string),
  dm: boolean,
  /** Whether it has woken the thread; it does once. */
  woke: boolean,
});
type Waiting = Infer<typeof waiting>;

const section = object({
  cursors: object({ dm: optional(cursor), mention: optional(cursor), channels: optional(cursor) }),
  waiting: array(waiting),
});
type Section = Infer<typeof section>;

const page = object({ results: string, pagination_info: optional(nullable(string)) });

type Message = { channel: string; ts: SlackTs; from: string; thread: string | null; dm: boolean };

/** A failed read of a page the tool sent, named by what failed only. */
const unreadable = (why: string) => new SourceError(`${TOOL}: unexpected response (${why})`);

/** A record's message, by ids only, from its field lines; null when it lacks one it needs. */
function messageOf(fields: string): Message | null {
  const channel = CHANNEL.exec(fields);
  const ts = TS.exec(fields)?.[1];
  if (channel === null || ts === undefined || !isSlackTs(ts)) return null;
  const thread = THREAD.exec(fields)?.[1] ?? null;
  const label = channel[1] ?? "";
  return {
    channel: channel[2] ?? "",
    ts,
    from: FROM.exec(fields)?.[1] ?? "",
    thread: thread !== ts ? thread : null,
    dm: label.startsWith("DM") || label.startsWith("Group DM"),
  };
}

/** A record's field lines: from its heading to its `Text:` line; the message body is never read. */
const fieldsOf = (text: string, from: number, to: number) =>
  text.slice(from, to).split("\nText:")[0] ?? "";

/**
 * A search page: its messages, the number of records it says it holds, and the next page's cursor.
 * `messages` is null when a message body may have forged a record, since a body can hold anything,
 * headings included: the headings don't number 1 to that count in order, or a record lacks its
 * fields. A page with records none of which can be read is a format change, and fails the source.
 */
export function readPage(text: string, pagination: string) {
  const headings = [...text.matchAll(RESULT)];
  const header = HEADER.exec(text);
  const count = header === null ? headings.length : Number(header[1]);
  const records = headings.map((heading, index) =>
    messageOf(fieldsOf(text, heading.index, headings[index + 1]?.index ?? text.length)),
  );
  if (count > 0 && !records.some((record) => record !== null)) {
    throw unreadable("no record it can read");
  }
  const numbered =
    headings.length === count &&
    headings.every(
      (heading, index) => heading[1] === String(index + 1) && heading[2] === String(count),
    );
  const messages = records.filter((record) => record !== null);
  return {
    messages: numbered && messages.length === count ? messages : null,
    count,
    next: CURSOR.exec(pagination)?.[1] ?? null,
  };
}

/**
 * The message a one-message page holds, or null when the search has none left. Its first record is
 * the only real one, and everything after that record's `Text:` line is the message's own.
 */
export function onlyMessage(text: string): Message | null {
  const [first] = text.matchAll(RESULT);
  const header = HEADER.exec(text);
  if (first === undefined) {
    if (header === null || header[1] === "0") return null;
    throw unreadable("a page of one message with no record");
  }
  if ((header !== null && header[1] !== "1") || first[1] !== "1" || first[2] !== "1") {
    throw unreadable("a page of one message that holds more");
  }
  const message = messageOf(fieldsOf(text, first.index, text.length));
  if (message === null) throw unreadable("a message whose record it can't read");
  return message;
}

/**
 * One search call. Slack limits search bursts, so searches go one at a time, and a rate-limited
 * call waits and tries once more before it fails the source.
 */
function call(executor: Executor, input: Record<string, unknown>) {
  sleep(seconds("ORG_ASSISTANT_SLACK_SPACING", 6)); // at most 10 searches a minute
  let value: unknown;
  try {
    [value] = executor.call([{ path: TOOL, input }]);
  } catch (error) {
    if (!(error instanceof SourceError) || !LIMITED.test(error.message)) throw error;
    sleep(seconds("ORG_ASSISTANT_SLACK_PAUSE", 60));
    [value] = executor.call([{ path: TOOL, input }]);
  }
  const got = read(page, value, TOOL);
  return { results: got.results, pagination: got.pagination_info ?? "" };
}

/** Where a search goes on: the next page's cursor, and the last message it read. */
type Place = { page: string | null; last: SlackTs | null };
type Order = "asc" | "desc";

/** Whether `ts` comes after `last` in the search's order. */
const past = (ts: SlackTs, last: SlackTs | null, order: Order) =>
  last === null || (order === "asc" ? Number(ts) > Number(last) : Number(ts) < Number(last));

/**
 * The `count` messages of a page a body may have forged a record in, read again one per call from
 * the page's own cursor. Only messages past the last one read before the page count, so a cursor
 * that addresses pages rather than messages only costs more calls. A page that can't be read even
 * so fails the source, and the search's saved place stays where it was.
 */
function reread(
  executor: Executor,
  args: Record<string, unknown>,
  at: Place,
  count: number,
  order: Order,
): Message[] {
  const found: Message[] = [];
  let { page, last } = at;
  for (let calls = 0; found.length < count && calls < REREAD; calls++) {
    const got = call(executor, { ...args, limit: 1, ...(page === null ? {} : { cursor: page }) });
    const message = onlyMessage(got.results);
    if (message === null) break;
    if (past(message.ts, last, order)) {
      found.push(message);
      last = message.ts;
    }
    page = CURSOR.exec(got.pagination)?.[1] ?? null;
    if (page === null) break;
  }
  if (found.length < count) throw unreadable("a page it couldn't read one message at a time");
  return found;
}

/**
 * The messages a search finds on up to PAGES pages from `from`, and where it stopped: `next` is
 * null once a page shorter than the limit, or one with no next cursor, ended it. Oldest first means
 * a cut-off search misses only the newest messages, which the next scan reads from where this one
 * stopped.
 */
function search(
  executor: Executor,
  input: Record<string, unknown>,
  order: Order,
  from: Place,
): { found: Message[]; next: { page: string; last: SlackTs | null } | null } {
  const args = { ...input, sort: "timestamp", sort_dir: order };
  const found: Message[] = [];
  let at = from;
  for (let pages = 0; pages < PAGES; pages++) {
    const got = call(executor, at.page === null ? args : { ...args, cursor: at.page });
    const read = readPage(got.results, got.pagination);
    const messages = read.messages ?? reread(executor, args, at, read.count, order);
    found.push(...messages);
    const last = messages.at(-1)?.ts ?? at.last;
    if (read.next === null || read.count < LIMIT) return { found, next: null };
    at = { page: read.next, last };
  }
  return { found, next: at.page === null ? null : { page: at.page, last: at.last } };
}

const refOf = (item: { channel: string; ts: string }) => `slack:${item.channel}:${item.ts}`;

/** The user wrote after it in the same DM, or in the same channel thread. */
function answered(item: Waiting, mine: Message[]): boolean {
  return mine.some(
    (reply) =>
      reply.channel === item.channel &&
      Number(reply.ts) > Number(item.ts) &&
      (item.dm ||
        (reply.thread ?? reply.ts) === (item.thread ?? item.ts) ||
        reply.thread === item.ts),
  );
}

function scan(source: SlackSource, window: Window<Section>, ctx: Context) {
  const executor = new Executor(source, [TOOL]);
  const me = source.me;
  const now = ctx.now.getTime() / 1000;
  const prev = window.kind === "resume" ? window.prev : null;
  const start = window.kind === "since" ? window.since.getTime() / 1000 : now;
  const cursors: Record<Search, Cursor> = {
    dm: prev?.cursors.dm ?? { at: start, more: null },
    mention: prev?.cursors.mention ?? { at: start, more: null },
    channels: prev?.cursors.channels ?? { at: start, more: null },
  };
  const wait = ctx.schedule.slack_wait_minutes * 60;
  const list = (prev?.waiting ?? []).filter((item) => now - Number(item.ts) < FORGET / 1000);
  if (window.kind === "baseline") return { section: { cursors, waiting: list }, changes: [] };

  const filters: Record<Search, Record<string, unknown>> = {
    dm: { filters: "to:me", channel_types: "im,mpim" },
    mention: { keywords: [`<@${me}>`] },
    channels: { filters: source.channels.map((entry) => `in:<#${entry.id}>`).join(" ") },
  };
  const found: Record<Search, Message[]> = { dm: [], mention: [], channels: [] };
  for (const name of SEARCHES) {
    if (name === "channels" && source.channels.length === 0) continue;
    const { at, more } = cursors[name];
    const after = more?.after ?? String(Math.trunc(at - OVERLAP));
    const input = { ...COMMON, ...filters[name], after };
    const got = search(executor, input, "asc", {
      page: more?.page ?? null,
      last: more?.last ?? null,
    });
    found[name] = got.found;
    const until = more?.until ?? now;
    cursors[name] =
      got.next === null ? { at: until, more: null } : { at, more: { after, ...got.next, until } };
  }

  const known = new Set(list.map(refOf));
  for (const message of [...found.dm, ...found.mention]) {
    if (message.from === me || BOTS.has(message.from) || known.has(refOf(message))) continue;
    known.add(refOf(message));
    // The sender's id is needed only for the check above, so it stays out of the snapshot.
    list.push({
      channel: message.channel,
      ts: message.ts,
      thread: message.thread,
      dm: message.dm,
      woke: false,
    });
  }
  // The user's own messages since the oldest one still waiting, newest first: a cut-off read then
  // misses only the oldest replies, never the reply to a message that just arrived.
  const oldest = Math.min(...list.map((item) => Number(item.ts)), now - OVERLAP);
  const mine = search(
    executor,
    { ...COMMON, filters: `from:<@${me}>`, after: String(Math.trunc(oldest)) },
    "desc",
    { page: null, last: null },
  );
  const changes: Change[] = [];
  const kept: Waiting[] = [];
  for (const item of list) {
    if (answered(item, mine.found)) continue;
    const age = now - Number(item.ts);
    if (age >= wait && !item.woke) {
      changes.push(
        ctx.change("slack.waiting", {
          ref: refOf(item),
          at: iso(fromSlackTs(item.ts)),
          key: "waiting",
          scope: `slack:${item.channel}`,
          detail: {
            via: item.dm ? "dm" : "mention",
            channel: item.channel,
            minutes: Math.floor(age / 60),
          },
        }),
      );
      kept.push({ ...item, woke: true });
    } else {
      kept.push(item);
    }
  }
  const names = new Map(source.channels.map((entry) => [entry.id, entry.name ?? entry.id]));
  for (const message of found.channels) {
    const name = names.get(message.channel);
    if (name === undefined || message.from === me) continue;
    changes.push(
      ctx.change("slack.channel", {
        ref: message.channel,
        at: iso(fromSlackTs(message.ts)),
        key: message.ts,
        scope: `slack:${message.channel}`,
        detail: { name },
      }),
    );
  }
  const refs = new Set(kept.map(refOf));
  return {
    section: { cursors, waiting: kept },
    changes,
    // A gathered DM or mention stays only while it is still unanswered.
    still: (item: Change) => item.kind !== "slack.waiting" || refs.has(item.ref),
  };
}

export const slack: Adapter<SlackSource, Section> = { section, scan };
