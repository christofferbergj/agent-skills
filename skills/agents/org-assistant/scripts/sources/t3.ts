/**
 * T3 Code, through the `t3` CLI: threads in the organisation's projects that wait on the user, and
 * the threads the assistant started; and the assistant thread itself, which the scan reads before
 * it wakes it and sends its wake to. Keeps thread ids and statuses, never titles or messages.
 */
import { SourceError, run, runJson } from "../calls.ts";
import type { Change } from "../changes.ts";
import {
  type Infer,
  array,
  boolean,
  nullable,
  object,
  optional,
  record,
  string,
  withDefault,
} from "../parse.ts";
import type { Thread } from "../policy.ts";
import type { T3Source } from "../profile.ts";
import { iso } from "../time.ts";
import type { Adapter, Context, Window } from "./index.ts";

/** A run still under way: the thread can't take a wake until it ends. */
const ACTIVE = new Set(["preparing", "queued", "starting", "running", "waiting"]);
const DONE = new Set(["completed", "failed", "cancelled", "interrupted", "stopped"]);
const QUIET = ["--log-level", "error"];

const listed = object({
  threadId: string,
  status: string,
  settled: withDefault(boolean, false),
  archived: withDefault(boolean, false),
  updatedAt: nullable(string),
  link: optional(string),
});

const section = object({ threads: record(string) });
type Section = Infer<typeof section>;

function scan(source: T3Source, window: Window<Section>, ctx: Context) {
  const baseline = window.kind === "baseline";
  const seen = window.kind === "resume" ? window.prev.threads : {};
  const now = iso(ctx.now);
  const started = new Map(ctx.ledger.started.map((entry) => [entry.thread, entry]));
  const threads: Section["threads"] = {};
  const changes: Change[] = [];
  for (const project of source.projects) {
    const args = ["t3", "thread", "list", "--project", project.path, "--json", ...QUIET];
    for (const thread of runJson(args, `T3 threads in ${project.path}`, array(listed))) {
      const id = thread.threadId;
      if (id === ctx.thread || thread.archived) continue;
      const followed = started.get(id);
      if (thread.settled && followed === undefined) continue;
      threads[id] = thread.status;
      if (baseline || seen[id] === thread.status) continue;
      const ref = `t3:${id}`;
      const link = thread.link ?? "";
      if (followed !== undefined && DONE.has(thread.status)) {
        changes.push(
          ctx.change("thread.finished", {
            ref,
            at: now,
            key: `${thread.status}:${thread.updatedAt}`,
            detail: { status: thread.status, ticket: followed.ticket, link },
          }),
        );
      } else if (thread.status === "waiting") {
        const key = `waiting:${thread.updatedAt}`;
        changes.push(
          followed !== undefined
            ? ctx.change("thread.waiting", {
                ref,
                at: now,
                key,
                detail: { ticket: followed.ticket, link },
              })
            : ctx.change("thread.waits_on_you", { ref, at: now, key, detail: { link } }),
        );
      }
    }
  }
  return { section: { threads }, changes };
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
