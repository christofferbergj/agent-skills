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
import { DAY, fromSlackTs, isSlackTs, iso, local, localIso, sleep, slackTs } from "../time.ts";
import type { Adapter, Allowance, Context, Window } from "./index.ts";

const TOOL = "tools.slack.mcp.slack_search_public_and_private";
const LIMIT = 20;
/**
 * The calls one organisation's scan makes at most, across all its Slack sources, retries and
 * one-message re-reads included: four minutes at one call each six seconds.
 */
export const SLACK_CALLS = 40;
const FORGET = 3 * DAY; // a waiting message older than this leaves the list
const SEARCHES = ["dm", "mention", "channels"] as const;
type Search = (typeof SEARCHES)[number];
const COMMON = { response_format: "detailed", include_context: false };
/** Seconds a search read to its end reaches back the next time, for messages Slack indexed late. */
const OVERLAP = 600;
const RESULT = /^### Result (\d+) of (\d+)\s*$/gm;
const HEADER = /^## Messages \((\d+) results?\)/m;
const CHANNEL = /^Channel: (.*?)\s*\(ID: ([A-Z0-9]+)\)/m;
const FROM = /^From: .*\(ID: ([A-Z0-9]+)\)/m;
const TS = /^Message_ts: ([0-9]+\.[0-9]+)/m;
const THREAD = /[?&]thread_ts=([0-9]+\.[0-9]+)/;
const CURSOR = /`([A-Za-z0-9+/=_-]{8,})`/;
const BOTS = new Set(["U00", "USLACKBOT"]);

const seconds = (name: string, fallback: number) => Number(process.env[name] ?? fallback) * 1000;

/** A message by its identity: its channel and its timestamp, which another channel can share. */
const messageId = object({ channel: string, ts: slackTs });
type MessageId = Infer<typeof messageId>;

/**
 * Where a search goes on: from `from`, a Slack time, skipping the messages at or after it that it
 * has read, `seen`. A search read to its end goes on from OVERLAP before the scan began, for messages
 * Slack indexed late; one the budget cut off goes on from the latest message it read, seen or new.
 */
const cursor = object({ from: number, seen: array(messageId) });
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

type Message = MessageId & { from: string; thread: string | null; dm: boolean };

const refOf = (item: MessageId) => `slack:${item.channel}:${item.ts}`;

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
 * A search page: its messages, and the number of records it says it holds. `messages` is null when
 * a message body may have forged a record, since a body can hold anything, headings included: the
 * headings don't number 1 to that count in order, or a record lacks its fields. A page with records
 * none of which can be read is a format change, and fails the source.
 */
function readPage(text: string) {
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
  return { messages: numbered && messages.length === count ? messages : null, count };
}

/**
 * The message a one-message page holds, or null when the search has none left. Its first record is
 * the only real one, and everything after that record's `Text:` line is the message's own.
 */
function onlyMessage(text: string): Message | null {
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

/** One search call: a page's text and its pagination line, or null once the budget is spent. */
type Ask = (input: Record<string, unknown>) => { results: string; pagination: string } | null;

/**
 * The source's search calls, out of the scan's one allowance. Slack limits search bursts, so the
 * calls go one at a time, and a rate-limited call waits a minute and tries once more, which costs a
 * call too, before it fails the source.
 */
function asker(executor: Executor, allowance: Allowance): Ask {
  return (input) => {
    for (let tries = 0; allowance.slackCalls > 0; tries++) {
      allowance.slackCalls -= 1;
      const pause = tries === 0 ? 0 : seconds("ORG_ASSISTANT_SLACK_PAUSE", 60);
      sleep(seconds("ORG_ASSISTANT_SLACK_SPACING", 6) + pause); // at most 10 searches a minute
      try {
        const got = read(page, executor.call([{ path: TOOL, input }])[0], TOOL);
        return { results: got.results, pagination: got.pagination_info ?? "" };
      } catch (error) {
        const limited = error instanceof SourceError && LIMITED.test(error.message);
        if (tries > 0 || !limited) throw error;
      }
    }
    return null;
  };
}

type Order = "asc" | "desc";

/**
 * The messages a search finds from `start` on, whether it read to its end before the budget ran
 * out, and the time of the latest message it read, seen or new, if any. A page a body may have forged a record in is read
 * again one message per call from that page's own cursor, where each page holds exactly one real
 * record, and the search then pages on from the page's next cursor. Slack's `after` takes whole
 * seconds, so a search starts at the second `start.from` falls in and skips what it has read; one
 * can't pass more messages within one second than the budget reads.
 */
function search(ask: Ask, input: Record<string, unknown>, order: Order, start: Cursor) {
  const args = { ...COMMON, ...input, after: String(Math.floor(start.from)), sort: "timestamp" };
  const taken = new Set(start.seen.map(refOf));
  const found: Message[] = [];
  let latest: number | null = null;
  const take = (message: Message) => {
    latest = Math.max(latest ?? -Infinity, Number(message.ts));
    if (Number(message.ts) < start.from || taken.has(refOf(message))) return;
    taken.add(refOf(message));
    found.push(message);
  };
  const call = (limit: number, cursor: string | null) => {
    const got = ask({ ...args, sort_dir: order, limit, ...(cursor === null ? {} : { cursor }) });
    return got && { results: got.results, next: CURSOR.exec(got.pagination)?.[1] ?? null };
  };
  const end = (ended: boolean) => ({ found, ended, latest });
  let cursor: string | null = null;
  for (;;) {
    const got = call(LIMIT, cursor);
    if (got === null) return end(false);
    const { messages, count } = readPage(got.results);
    if (messages !== null) messages.forEach(take);
    else {
      let one = cursor;
      for (let n = 0; n < count; n++) {
        const single = call(1, one);
        if (single === null) return end(false);
        const message = onlyMessage(single.results);
        if (message === null) return end(true);
        take(message);
        one = single.next;
        if (one === null) return end(true);
      }
    }
    if (got.next === null || count < LIMIT) return end(true);
    cursor = got.next;
  }
}

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
  const ask = asker(new Executor(source, [TOOL]), ctx.allowance);
  const me = source.me;
  const now = ctx.now.getTime() / 1000;
  const prev = window.kind === "resume" ? window.prev : null;
  const begin = {
    from: (window.kind === "since" ? window.since.getTime() / 1000 : now) - OVERLAP,
    seen: [],
  };
  const cursors: Record<Search, Cursor> = {
    dm: prev?.cursors.dm ?? begin,
    mention: prev?.cursors.mention ?? begin,
    channels: prev?.cursors.channels ?? begin,
  };
  const wait = ctx.schedule.slack_wait_minutes * 60;
  const list = (prev?.waiting ?? []).filter((item) => now - Number(item.ts) < FORGET / 1000);
  if (window.kind === "baseline") return { section: { cursors, waiting: list }, changes: [] };

  const filters: Record<Search, Record<string, unknown>> = {
    dm: { filters: "to:me", channel_types: "im,mpim" },
    mention: { keywords: [`<@${me}>`] },
    channels: { filters: source.channels.map((entry) => `in:<#${entry.id}>`).join(" ") },
  };
  // Each search goes on oldest first from where it stopped; once the budget runs out, the rest wait.
  const found: Record<Search, Message[]> = { dm: [], mention: [], channels: [] };
  let spent = false;
  let stuck: number | null = null;
  for (const name of SEARCHES) {
    if (spent || (name === "channels" && source.channels.length === 0)) continue;
    const start = cursors[name];
    const got = search(ask, filters[name], "asc", start);
    found[name] = got.found;
    spent = !got.ended;
    // The next scan reaches back OVERLAP once this one read to its end, else goes on from the
    // latest message it read, skipping the messages from there on it read.
    const from = got.ended ? now - OVERLAP : Math.max(start.from, got.latest ?? start.from);
    const seen = [...start.seen, ...got.found.map(({ channel, ts }) => ({ channel, ts }))];
    cursors[name] = { from, seen: seen.filter(({ ts }) => Number(ts) >= from) };
    // A search the budget cut off with all it read in the second it started at starts there again.
    if (spent && got.latest !== null && Math.floor(got.latest) === Math.floor(start.from)) {
      stuck = got.latest;
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
  const mine = spent
    ? null
    : search(ask, { filters: `from:<@${me}>` }, "desc", { from: oldest, seen: [] });
  spent ||= mine?.ended === false;
  const replies = mine?.found ?? [];
  // How far back the replies were read: all of them, down to the oldest a cut-off read reached, or
  // none when the budget left none to read them.
  const reached = mine?.ended ? -Infinity : Math.min(...replies.map(({ ts }) => Number(ts)));
  const changes: Change[] = [];
  const kept: Waiting[] = [];
  for (const item of list) {
    if (answered(item, replies)) continue;
    const age = now - Number(item.ts);
    if (Number(item.ts) < reached) {
      // A reply may be among those unread: no wake this scan, and its gathered change leaves, so the
      // next scan judges it again. Should it have woken the thread already, its change id is among
      // those delivered or frozen, so it joins no batch twice.
      kept.push({ ...item, woke: false });
    } else if (age >= wait && !item.woke) {
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
  const refs = new Set(kept.filter((item) => Number(item.ts) >= reached).map(refOf));
  return {
    section: { cursors, waiting: kept },
    changes,
    // A gathered DM or mention stays only while this scan read it as still unanswered.
    still: (item: Change) => item.kind !== "slack.waiting" || refs.has(item.ref),
    ...(stuck !== null
      ? {
          note: `watermark stuck at ${localIso(local(new Date(Math.floor(stuck) * 1000), ctx.zone))}: one second holds more messages than a scan reads`,
        }
      : spent
        ? { note: "read budget used: resumes next scan" }
        : {}),
  };
}

export const slack: Adapter<SlackSource, Section> = { section, scan };
