/**
 * T3 Code, through the `t3` CLI: every thread in the organisation's projects, since the user does
 * their work through T3 agents, and the assistant thread itself, which the scan reads before it
 * wakes it and sends its wake to. A thread wakes the assistant on its status and its run: it waits on
 * the user, failed, finished, or stalled; one that is new since the last scan is pulse. A finished or
 * failed run is reported once, when it ends, and stays news after the next run starts. A wait or a
 * stall is reported again at every scan while it holds, under the same id, so a gathered one leaves
 * once it stops holding, and one a failed read dropped comes back. Keeps thread ids, links,
 * statuses, run ids, and counts, never titles or messages.
 */
import { SourceError, run, runJson } from "../calls.ts";
import { type Change, type ChangeKind, standing } from "../changes.ts";
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
import { SEEN_FOR } from "../pending.ts";
import type { Thread } from "../policy.ts";
import type { T3Source } from "../profile.ts";
import { HOUR, iso, time } from "../time.ts";
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
/** A stall's key: when the scan first saw the thread at its status, run, and item count. */
const stallKey = (since: string) => `stalled@${since}`;

const listed = object({
  threadId: string,
  status: string,
  settled: boolean,
  archived: withDefault(boolean, false),
  snoozedUntil: nullable(time),
  /** Set on a thread another thread forked or delegated, which its parent's run covers. */
  parentThreadId: nullable(string),
  itemCount: count,
  latestRunId: nullable(string),
  createdAt: nullable(time),
  link: optional(string),
});
type Listed = Infer<typeof listed>;

const seenThread = object({
  status: string,
  items: count,
  /** The thread's latest run, so a second run that ends the same way still counts. */
  run: nullable(string),
  /** When the scan first saw the thread at this status, run, and item count. */
  since: string,
  /**
   * The turn or stall the scan reported for this status and run, by its key and when it reported it
   * first, which bounds how long a standing one is reported again.
   */
  turn: nullable(object({ key: string, at: string })),
});
const section = object({ threads: record(seenThread) });
type Section = Infer<typeof section>;
type Seen = Infer<typeof seenThread>;

/** Whether a thread's changes reach the user: not settled, not snoozed, not a child of another. */
function watched(thread: Listed, now: Date): boolean {
  const snoozed = thread.snoozedUntil !== null && thread.snoozedUntil > now;
  return !thread.settled && !snoozed && thread.parentThreadId === null;
}

function scan(source: T3Source, window: Window<Section>, ctx: Context) {
  const seen = window.kind === "resume" ? window.prev.threads : {};
  const now = iso(ctx.now);
  const started = new Map(ctx.ledger.started.map((entry) => [entry.thread, entry.ticket]));
  const threads: Section["threads"] = {};
  const watching = new Set<string>();
  const changes: Change[] = [];
  for (const [index, project] of source.projects.entries()) {
    const args = ["t3", "thread", "list", "--project", project.path, "--json", ...QUIET];
    // Named by its place in the profile: stderr reaches the journal and never names a path.
    for (const thread of runJson(args, `T3 threads in projects[${index}]`, array(listed))) {
      const id = thread.threadId;
      if (id === ctx.thread || thread.archived) continue;
      const prev = seen[id];
      const moved = prev?.status !== thread.status || prev.run !== thread.latestRunId;
      const same = prev !== undefined && !moved && prev.items === thread.itemCount;
      const record: Seen = {
        status: thread.status,
        items: thread.itemCount,
        run: thread.latestRunId,
        since: same ? prev.since : now,
        // A new status or run ends a turn, and a new item a stall, even while the thread is unwatched.
        turn: moved || (!same && thread.status === "running") ? null : prev.turn,
      };
      threads[id] = record;
      if (!watched(thread, ctx.now)) continue;
      watching.add(id);
      if (window.kind === "baseline") continue;
      // With no section yet, only a thread created since the window's start is new.
      const isNew =
        window.kind === "since"
          ? thread.createdAt !== null && thread.createdAt >= window.since
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
      // Keyed by the run and its item count, so a replay after a crash adds it once, and the next
      // time the thread turns the same way gets a new key.
      if (turned !== undefined && moved) {
        record.turn = {
          key: `${thread.status}:${thread.latestRunId}:${thread.itemCount}`,
          at: now,
        };
      }
      // An hour without a new item starts a stall, reported first at this scan.
      const running = thread.status === "running";
      if (running && same && ctx.now.getTime() - Date.parse(prev.since) >= STALL) {
        record.turn ??= { key: stallKey(record.since), at: now };
      }
      const kind = running ? "thread.stalled" : turned;
      // A standing one is reported again while it holds, until the pending state would forget it
      // was delivered; a finished or failed run only when it ends.
      const held = (turn: { at: string }) => ctx.now.getTime() - Date.parse(turn.at) < SEEN_FOR;
      if (kind !== undefined && record.turn !== null && (moved || standing({ kind }))) {
        if (held(record.turn)) {
          changes.push(ctx.change(kind, { ref, at: now, key: record.turn.key, detail }));
        }
      }
    }
  }
  return {
    section: { threads },
    changes,
    // A new thread, or a finished or failed run, stays gathered only while the thread is watched.
    still: (item: Change) => watching.has(item.ref.slice("t3:".length)),
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
