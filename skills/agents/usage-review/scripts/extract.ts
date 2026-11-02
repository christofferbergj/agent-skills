/**
 * Reads the owner's messages from T3 Code's state database for /usage-review.
 * Writes one JSON line per owner message, typed by how it relates to the runs around it.
 *
 * Usage: extract.ts --out <file.jsonl> [--days 7 | --since <ISO>] [--db <path>]
 */
import { DatabaseSync } from "node:sqlite";
import { mkdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { parseArgs } from "node:util";

export type Interaction = "request" | "steer" | "answer" | "unpaired";

export interface MenuOption {
  readonly letter: string;
  readonly text: string;
}

export type Ending =
  | { readonly kind: "options"; readonly options: readonly MenuOption[] }
  | { readonly kind: "next" | "done" | "none" };

export interface OwnerMessage {
  readonly messageId: string;
  readonly threadId: string;
  readonly project: string | null;
  readonly at: string;
  readonly interaction: Interaction;
  readonly text: string;
  /** Status of the run before an `unpaired` message, which left no final reply. */
  readonly previousRunStatus?: string;
  /** How the answered run's final assistant message ended; only on `answer`. */
  readonly ending?: Ending;
  readonly assistantWords?: number;
}

const OPTION = /^\s*[-*]\s*\**`?([a-d])`?\s*(?:→|->)\s*(.*)$/i;

export function stateDbPath(flag?: string): string {
  return flag ?? process.env.T3_STATE_DB ?? join(homedir(), ".t3", "userdata", "statev2.sqlite");
}

/** Reads the lettered options, plain next step, or Done from a reply's last lines. */
export function endingOf(reply: string): Ending {
  const tail = reply.split("\n").slice(-25);
  const options = tail.flatMap((line) => {
    const match = line.match(OPTION);
    if (!match) return [];
    const text = match[2].replace(/\*\*|`|·\s*_recommended_/g, "").trim();
    return [{ letter: match[1].toLowerCase(), text }];
  });
  if (options.length > 0) return { kind: "options", options };
  const joined = tail.join("\n");
  if (/\*\*Next\*\*:/.test(joined)) return { kind: "next" };
  if (/^\s*\**Done\b/m.test(joined)) return { kind: "done" };
  return { kind: "none" };
}

interface MessageRow {
  id: string;
  threadId: string;
  project: string | null;
  at: string;
  runId: string | null;
  text: string;
}

interface RunRow {
  runId: string;
  status: string;
  completedAt: string | null;
}

/**
 * Owner messages are typed by message provenance, whatever created the thread: the owner wrote
 * them in the web or mobile client, outside subagent and delegated-task threads. The window
 * applies to message time, so older threads still active in it count.
 */
export function extract(db: DatabaseSync, since: string): OwnerMessage[] {
  const messages = db
    .prepare(
      `select m.message_id id, m.thread_id threadId, p.title project, m.created_at at, m.run_id runId,
              json_extract(m.payload_json, '$.text') text
       from orchestration_v2_projection_messages m
       join orchestration_v2_projection_threads t on t.thread_id = m.thread_id
       left join projection_projects p on p.project_id = t.project_id
       where m.role = 'user' and m.created_at >= ?
         and json_extract(m.payload_json, '$.createdBy') = 'user'
         and json_extract(m.payload_json, '$.creationSource') in ('web', 'mobile')
         and t.deleted_at is null
         and coalesce(json_extract(t.payload_json, '$.lineage.relationshipToParent'), '') <> 'subagent'
       order by m.thread_id, m.created_at, m.message_id`,
    )
    .all(since) as unknown as MessageRow[];
  // A message starts the run that names it; one sent while a run is active joins that run instead.
  const startedBy = db.prepare(
    `select json_extract(payload_json, '$.userMessageId') = ? started
     from orchestration_v2_projection_runs where run_id = ?`,
  );
  const previousRun = db.prepare(
    `select run_id runId, status, completed_at completedAt from orchestration_v2_projection_runs
     where thread_id = ? and requested_at <= ?
       and coalesce(json_extract(payload_json, '$.userMessageId'), '') <> ?
     order by ordinal desc limit 1`,
  );
  const finalReply = db.prepare(
    `select json_extract(payload_json, '$.text') text from orchestration_v2_projection_messages
     where run_id = ? and role = 'assistant' order by created_at desc, message_id desc limit 1`,
  );

  return messages.map((message) => {
    const base = {
      messageId: message.id,
      threadId: message.threadId,
      project: message.project,
      at: message.at,
      text: message.text ?? "",
    };
    const own = message.runId
      ? (startedBy.get(message.id, message.runId) as { started: number | null } | undefined)
      : undefined;
    if (own && !own.started) return { ...base, interaction: "steer" };
    const run = previousRun.get(message.threadId, message.at, message.id) as RunRow | undefined;
    if (!run) return { ...base, interaction: "request" };
    if (run.completedAt === null || run.completedAt > message.at)
      return { ...base, interaction: "steer" };
    const reply = (finalReply.get(run.runId) as { text: string | null } | undefined)?.text;
    if (!reply) return { ...base, interaction: "unpaired", previousRunStatus: run.status };
    return {
      ...base,
      interaction: "answer",
      ending: endingOf(reply),
      assistantWords: reply.split(/\s+/).filter(Boolean).length,
    };
  });
}

if (import.meta.main) {
  const { values } = parseArgs({
    options: {
      days: { type: "string", default: "7" },
      since: { type: "string" },
      db: { type: "string" },
      out: { type: "string" },
    },
  });
  if (!values.out)
    throw new Error(
      "usage: extract.ts --out <file.jsonl> [--days 7 | --since <ISO>] [--db <path>]",
    );
  // Stored times are all UTC with milliseconds, so the window compares as text in that form.
  const since = new Date(
    values.since ?? Date.now() - Number(values.days) * 86_400_000,
  ).toISOString();
  const db = new DatabaseSync(stateDbPath(values.db), { readOnly: true, timeout: 5_000 });
  try {
    const rows = extract(db, since);
    mkdirSync(dirname(values.out), { recursive: true });
    writeFileSync(values.out, rows.map((row) => JSON.stringify(row)).join("\n") + "\n");
    const counts = Object.groupBy(rows, (row) => row.interaction);
    const summary = Object.fromEntries(Object.entries(counts).map(([k, v]) => [k, v?.length]));
    console.log(
      JSON.stringify({
        since,
        messages: rows.length,
        threads: new Set(rows.map((r) => r.threadId)).size,
        ...summary,
      }),
    );
  } finally {
    db.close();
  }
}
