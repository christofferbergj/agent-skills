/**
 * `assistant.ts batch`: a frozen batch as the plain text the run posts from. Each item shows its
 * kind, its link, its age, and a short reading of its detail; a conversation's waiting Slack
 * messages make one line, and the team's moves and channel messages one pulse line. State holds no
 * message body or ticket title, so neither can show here.
 */
import type { Change, ChangeOf } from "./changes.ts";
import type { InlineBatch, SentBatch } from "./pending.ts";
import type { Source } from "./profile.ts";
import { MINUTE } from "./time.ts";

const TICKET = /^[A-Z][A-Z0-9]*-\d+$/;
const NUMBERED = /^([\w.-]+\/[\w.-]+)#(\d+)$/;
const RELEASE = /^([\w.-]+\/[\w.-]+)@(.+)$/;
const MESSAGE = /^slack:([A-Z0-9]+):(\d+)\.(\d+)$/;

/** The workspace slug the profile gives the source of `kind` that found `item`. */
function workspace(item: Change, sources: readonly Source[], kind: "linear" | "slack") {
  const found = sources.find((source) => source.name === item.source);
  return found?.kind === kind ? (found.workspace ?? null) : null;
}

/** The URL of what `item` names, or its ref when the profile gives no way to build one. */
export function link(item: Change, sources: readonly Source[]): string {
  const { ref } = item;
  if ("link" in item.detail) return item.detail.link || ref;
  if (TICKET.test(ref)) {
    const linear = workspace(item, sources, "linear");
    return linear === null ? ref : `https://linear.app/${linear}/issue/${ref}`;
  }
  const numbered = NUMBERED.exec(ref);
  if (numbered !== null) {
    const [, repo, number] = numbered;
    return `https://github.com/${repo}/${item.kind.startsWith("pr.") ? "pull" : "issues"}/${number}`;
  }
  const release = RELEASE.exec(ref);
  if (release !== null) {
    const [, repo, tag = ""] = release;
    return `https://github.com/${repo}/releases/tag/${encodeURIComponent(tag)}`;
  }
  const message = MESSAGE.exec(ref);
  if (message !== null) {
    const slack = workspace(item, sources, "slack");
    const [, channel, seconds, fraction] = message;
    return slack === null
      ? ref
      : `https://${slack}.slack.com/archives/${channel}/p${seconds}${fraction}`;
  }
  return ref;
}

/**
 * A message's place in time from the full Slack timestamp in its ref, since `at` keeps only the
 * second and two messages can share one.
 */
function sent(item: Change): bigint {
  const [, , seconds = "0", fraction = ""] = MESSAGE.exec(item.ref) ?? [];
  return BigInt(seconds + fraction.padEnd(6, "0"));
}

function reading(detail: Record<string, unknown>): string {
  return Object.entries(detail)
    .filter(([key]) => key !== "link")
    .map(([key, value]) => {
      const shown = Array.isArray(value) ? value.join(" ") || "none" : String(value ?? "none");
      return `${key}: ${shown}`;
    })
    .join(", ");
}

const plural = (count: number, word: string) => `${count} ${word}${count === 1 ? "" : "s"}`;

/** Adds one to `key`'s count, keeping first-seen order. */
function tally<K>(counts: Map<K, number>, key: K): void {
  counts.set(key, (counts.get(key) ?? 0) + 1);
}

/**
 * The batch as text: a header with its id, kind, and reason, then one line per item, a line per
 * Slack conversation with messages waiting, and one pulse line last.
 */
export function renderBatch(
  batch: SentBatch | InlineBatch,
  context: { now: Date; sources: readonly Source[]; delivered: boolean },
): string {
  const { now, sources } = context;
  const age = (at: string) =>
    `${Math.max(0, Math.floor((now.getTime() - Date.parse(at)) / MINUTE))} min ago`;
  const line = (item: Change, read: string) =>
    [item.kind, link(item, sources), age(item.at), ...(read === "" ? [] : [read])].join(" · ");
  /** Each item's line, or a conversation's waiting messages where its first one stood. */
  const rows: (string | ChangeOf<"slack.waiting">[])[] = [];
  const waiting = new Map<string, ChangeOf<"slack.waiting">[]>();
  const people = new Map<string, Map<"moved" | "finished" | "new", number>>();
  const channels = new Map<string, number>();
  for (const item of batch.items) {
    if (item.kind === "slack.waiting") {
      const conversation = waiting.get(item.detail.channel);
      if (conversation !== undefined) conversation.push(item);
      else {
        const first = [item];
        waiting.set(item.detail.channel, first);
        rows.push(first);
      }
    } else if (item.kind === "team.pulse") {
      const { detail } = item;
      const counts = people.get(detail.who) ?? new Map();
      tally(counts, "new" in detail ? "new" : detail.finished ? "finished" : "moved");
      people.set(detail.who, counts);
    } else if (item.kind === "slack.channel") tally(channels, item.detail.name);
    else rows.push(line(item, reading(item.detail)));
  }
  const shown = rows.map((row) => {
    if (typeof row === "string") return row;
    const oldest = row.reduce((a, b) => (sent(b) < sent(a) ? b : a));
    const via = [...new Set(row.map((item) => item.detail.via))].join(" and ");
    return line(oldest, `${plural(row.length, "message")} waiting, via ${via}`);
  });
  const pulse = [
    ...[...people].map(
      ([who, counts]) =>
        `${who} ${[...counts].map(([what, count]) => `${count} ${what}`).join(", ")}`,
    ),
    ...[...channels].map(([name, count]) => `#${name} ${plural(count, "message")}`),
  ];
  if (pulse.length > 0) shown.push(["pulse", ...pulse].join(" · "));
  const done = context.delivered ? ", already marked delivered" : "";
  const changes = plural(batch.items.length, "change");
  const header = `Batch ${batch.id} (${batch.kind}, ${changes}${done}): ${batch.reason}`;
  return [header, ...shown.map((row) => `- ${row}`)].join("\n");
}
