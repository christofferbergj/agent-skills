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
  literal,
  nullable,
  number,
  object,
  optional,
  string,
} from "../parse.ts";
import type { SlackSource } from "../profile.ts";
import { DAY, fromSlackTs, iso, sleep } from "../time.ts";
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

const seconds = (name: string, fallback: number) => Number(process.env[name] ?? fallback) * 1000;

/**
 * Where a search's next run starts: `overlap` reaches back OVERLAP from `at`; `resume` continues a
 * cut-off search from its last message, with the same reach-back; `exact` starts at `at` itself,
 * when a cut-off search made no progress past its cursor, so a burst can't replay forever.
 */
const cursor = object({ at: number, reach: literal("overlap", "resume", "exact") });
type Cursor = Infer<typeof cursor>;

const waiting = object({
  channel: string,
  ts: string,
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

type Message = { channel: string; ts: string; from: string; thread: string | null; dm: boolean };

/**
 * Each record's field lines: from its `### Result N of M` heading up to its `Text:` line. A heading
 * counts only when it numbers on from the one before under the page's own total, so a message body
 * that copies a heading stays part of that message, and is never read.
 */
export function records(text: string): string[] {
  const headings: RegExpExecArray[] = [];
  let expected: number | null = null;
  let total: number | null = null;
  for (const match of text.matchAll(RESULT)) {
    const number = Number(match[1]);
    const of = Number(match[2]);
    if ((expected === null || (number === expected && of === total)) && number <= of) {
      headings.push(match);
      expected = number + 1;
      total = of;
    }
  }
  return headings.map((heading, index) => {
    const end = headings[index + 1]?.index ?? text.length;
    const body = text.slice(heading.index + heading[0].length, end);
    return body.split("\nText:")[0] ?? "";
  });
}

/** A search page as its messages, by ids only, and the next page's cursor. */
export function messages(
  text: string,
  pagination: string,
): { found: Message[]; next: string | null } {
  const found: Message[] = [];
  for (const block of records(text)) {
    const channel = CHANNEL.exec(block);
    const ts = TS.exec(block)?.[1];
    if (channel === null || ts === undefined) continue;
    const thread = THREAD.exec(block)?.[1] ?? null;
    const label = channel[1] ?? "";
    found.push({
      channel: channel[2] ?? "",
      ts,
      from: FROM.exec(block)?.[1] ?? "",
      thread: thread !== ts ? thread : null,
      dm: label.startsWith("DM") || label.startsWith("Group DM"),
    });
  }
  return { found, next: CURSOR.exec(pagination)?.[1] ?? null };
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
  return messages(got.results, got.pagination_info ?? "");
}

/**
 * Every message a search finds across up to PAGES pages, and whether it read them all: a page
 * shorter than the limit, or one with no next cursor, is the last. Oldest first means a cut-off
 * search misses only the newest messages, which the next scan reads from where this one stopped.
 */
function search(executor: Executor, input: Record<string, unknown>, order: "asc" | "desc" = "asc") {
  const args = { ...input, sort: "timestamp", sort_dir: order };
  const found: Message[] = [];
  let next: string | null = null;
  for (let count = 0; count < PAGES; count++) {
    const got = call(executor, next === null ? args : { ...args, cursor: next });
    found.push(...got.found);
    next = got.next;
    if (next === null || got.found.length < LIMIT) return { found, whole: true };
  }
  return { found, whole: false };
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
    dm: prev?.cursors.dm ?? { at: start, reach: "overlap" },
    mention: prev?.cursors.mention ?? { at: start, reach: "overlap" },
    channels: prev?.cursors.channels ?? { at: start, reach: "overlap" },
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
    const from = cursors[name];
    const after = from.reach === "exact" ? from.at : from.at - OVERLAP;
    const got = search(executor, { ...COMMON, ...filters[name], after: String(Math.trunc(after)) });
    found[name] = got.found;
    const last = got.found.at(-1);
    if (got.whole || last === undefined) {
      cursors[name] = { at: now, reach: "overlap" };
    } else {
      const reached = Number(last.ts);
      const stuck = from.reach !== "overlap" && reached <= from.at;
      cursors[name] = { at: Math.max(reached, from.at), reach: stuck ? "exact" : "resume" };
    }
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
