/**
 * T3 Code, through the `t3` CLI: every thread in the organisation's projects, since the user does
 * their work through T3 agents, and the assistant thread itself, which the scan reads before it
 * wakes it and sends its wake to. A thread wakes the assistant on its status: it waits on the user,
 * failed, finished, or stalled; one that is new since the last scan is pulse. Keeps thread ids,
 * links, statuses, and counts, never titles or messages.
 */
import { SourceError, run, runJson } from "../calls.ts";
import type { Change, ChangeKind } from "../changes.ts";
import {
  type Infer,
  array,
  boolean,
  count,
  nullable,
  object,
  optional,
  record,
  string,
  withDefault,
} from "../parse.ts";
import type { Thread } from "../policy.ts";
import type { T3Source } from "../profile.ts";
import { HOUR, iso } from "../time.ts";
import type { Adapter, Context, Window } from "./index.ts";

/** A run still under way: the thread can't take a wake until it ends. */
const ACTIVE = new Set(["preparing", "queued", "starting", "running", "waiting"]);
/** The status a thread turns to, and the kind of change that turn is. */
const TURNS: Record<string, ChangeKind> = {
  waiting: "thread.waiting",
  failed: "thread.failed",
  completed: "thread.finished",
};
/** How long a running thread may go without a new item before it counts as stalled. */
const STALL = HOUR;
const QUIET = ["--log-level", "error"];

const listed = object({
  threadId: string,
  status: string,
  settled: boolean,
  archived: withDefault(boolean, false),
  snoozedUntil: nullable(string),
  /** Set on a thread another thread forked or delegated, which its parent's run covers. */
  parentThreadId: nullable(string),
  itemCount: count,
  latestRunId: nullable(string),
  createdAt: nullable(string),
  link: optional(string),
});
type Listed = Infer<typeof listed>;

const seenThread = object({
  status: string,
  items: count,
  /** When the scan first saw the thread at this status and item count. */
  since: string,
  /** Whether this stall was reported; a new item or status ends it. */
  stalled: boolean,
});
const section = object({ threads: record(seenThread) });
type Section = Infer<typeof section>;
type Seen = Infer<typeof seenThread>;

/** Whether a thread's changes reach the user: not settled, not snoozed, not a child of another. */
function watched(thread: Listed, now: Date): boolean {
  const snoozed = thread.snoozedUntil !== null && Date.parse(thread.snoozedUntil) > now.getTime();
  return !thread.settled && !snoozed && thread.parentThreadId === null;
}

function scan(source: T3Source, window: Window<Section>, ctx: Context) {
  const seen = window.kind === "resume" ? window.prev.threads : {};
  const now = iso(ctx.now);
  const started = new Map(ctx.ledger.started.map((entry) => [entry.thread, entry.ticket]));
  const threads: Section["threads"] = {};
  const watching = new Set<string>();
  const changes: Change[] = [];
  for (const project of source.projects) {
    const args = ["t3", "thread", "list", "--project", project.path, "--json", ...QUIET];
    for (const thread of runJson(args, `T3 threads in ${project.path}`, array(listed))) {
      const id = thread.threadId;
      if (id === ctx.thread || thread.archived) continue;
      const prev = seen[id];
      const same =
        prev !== undefined && prev.status === thread.status && prev.items === thread.itemCount;
      const record: Seen = {
        status: thread.status,
        items: thread.itemCount,
        since: same ? prev.since : now,
        stalled: same ? prev.stalled : false,
      };
      threads[id] = record;
      if (!watched(thread, ctx.now)) continue;
      watching.add(id);
      if (window.kind === "baseline") continue;
      // With no section yet, only a thread created since the window's start is new.
      const isNew =
        window.kind === "since"
          ? thread.createdAt !== null && Date.parse(thread.createdAt) >= window.since.getTime()
          : prev === undefined;
      if (window.kind === "since" && !isNew) continue;
      const ticket = started.get(id);
      const detail = {
        status: thread.status,
        link: thread.link ?? "",
        items: thread.itemCount,
        ...(ticket === undefined
          ? { started: false as const }
          : { started: true as const, ticket }),
      };
      const ref = `t3:${id}`;
      if (isNew) changes.push(ctx.change("thread.started", { ref, at: now, key: "new", detail }));
      const turned = TURNS[thread.status];
      if (turned !== undefined && (isNew || prev?.status !== thread.status)) {
        // Keyed by the run and its item count, so a replay after a crash adds it once, and the next
        // time the thread turns the same way gets a new key.
        const key = `${thread.status}:${thread.latestRunId}:${thread.itemCount}`;
        changes.push(ctx.change(turned, { ref, at: now, key, detail }));
      }
      if (
        thread.status === "running" &&
        same &&
        !prev.stalled &&
        ctx.now.getTime() - Date.parse(prev.since) >= STALL
      ) {
        record.stalled = true;
        changes.push(
          ctx.change("thread.stalled", { ref, at: now, key: `stalled@${prev.since}`, detail }),
        );
      }
    }
  }
  return {
    section: { threads },
    changes,
    // A gathered wait, failure, or stall stays only while the thread is still watched and as it was.
    still: (item: Change) => {
      const id = item.ref.slice("t3:".length);
      const current = threads[id];
      switch (item.kind) {
        case "thread.waiting":
        case "thread.failed":
          return watching.has(id) && current?.status === item.detail.status;
        case "thread.stalled":
          return (
            watching.has(id) && current?.status === "running" && current.items === item.detail.items
          );
        default:
          return true;
      }
    },
  };
}

export const t3: Adapter<T3Source, Section> = { section, scan };

const shown = object({
  thread: object({ status: string }),
  messages: withDefault(array(object({ role: string, text: nullable(string) })), []),
});

/** The assistant thread's state and, when it is idle, its last reply. */
export function readThread(id: string): Thread {
  let read: Infer<typeof shown>;
  try {
    read = runJson(
      ["t3", "thread", "show", id, "--json", "--messages", "1", ...QUIET],
      "the assistant thread",
      shown,
    );
  } catch (error) {
    if (error instanceof SourceError) return { kind: "unreadable" };
    throw error;
  }
  if (ACTIVE.has(read.thread.status)) return { kind: "busy" };
  const last = read.messages.at(-1);
  return { kind: "idle", lastText: last?.role === "assistant" ? (last.text ?? "") : "" };
}

/** Sends a wake to the assistant thread; whether `t3` took it. */
export function sendWake(id: string, message: string): boolean {
  return run(["t3", "thread", "send", id, "-"], { stdin: message }).code === 0;
}
