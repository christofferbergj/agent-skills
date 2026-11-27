/**
 * `assistant.ts batch`: a frozen batch as the plain text the run posts from. Each item shows its
 * kind, its link, its age, and a short reading of its detail; a conversation's waiting Slack
 * messages make one line, and the team's moves and channel messages one pulse line. State holds no
 * message body or ticket title, so neither can show here.
 */
import type { Change, ChangeOf } from "./changes.ts";
import { type Ledger, deliveredNote } from "./ledger.ts";
import type { InlineBatch, SentBatch } from "./pending.ts";
import type { LinearSource, SlackSource, Source } from "./profile.ts";
import { minutesAgo } from "./time.ts";

const TICKET = /^[A-Z][A-Z0-9]*-\d+$/;
const NUMBERED = /^([\w.-]+\/[\w.-]+)#(\d+)$/;
const RELEASE = /^([\w.-]+\/[\w.-]+)@(.+)$/;
const MESSAGE = /^slack:([A-Z0-9]+):(\d+)\.(\d+)$/;

/**
 * The workspace slug for a link of `kind` to a ref the source `from` found: that source's own when
 * it is of `kind`. A ref nested in a change's detail, such as a started thread's ticket, may name
 * another kind's thing, and then takes the profile's only source of that kind. A source no longer
 * in the profile gives none, so a frozen change never takes another source's workspace.
 */
function workspace(
  from: string,
  sources: readonly Source[],
  kind: "linear" | "slack",
  nested: boolean,
): string | null {
  const ofKind = sources.filter(
    (source): source is LinearSource | SlackSource => source.kind === kind,
  );
  const own = ofKind.find((source) => source.name === from);
  if (own !== undefined) return own.workspace ?? null;
  const [only, ...more] = ofKind;
  const origin = sources.some((source) => source.name === from);
  return nested && origin && more.length === 0 ? (only?.workspace ?? null) : null;
}

/**
 * The URL of `ref`, found by the source `from`, or null when the profile gives no way to build one;
 * `pull` reads `owner/repo#n` as a PR rather than an issue, and `nested` marks a ref
 * from a change's detail.
 */
function urlOf(
  ref: string,
  from: string,
  sources: readonly Source[],
  options: { pull: boolean; nested: boolean },
): string | null {
  if (TICKET.test(ref)) {
    const linear = workspace(from, sources, "linear", options.nested);
    return linear === null ? null : `https://linear.app/${linear}/issue/${ref}`;
  }
  const numbered = NUMBERED.exec(ref);
  if (numbered !== null) {
    const [, repo, number] = numbered;
    return `https://github.com/${repo}/${options.pull ? "pull" : "issues"}/${number}`;
  }
  const release = RELEASE.exec(ref);
  if (release !== null) {
    const [, repo, tag = ""] = release;
    return `https://github.com/${repo}/releases/tag/${encodeURIComponent(tag)}`;
  }
  const message = MESSAGE.exec(ref);
  if (message !== null) {
    const slack = workspace(from, sources, "slack", options.nested);
    const [, channel, seconds, fraction] = message;
    return slack === null
      ? null
      : `https://${slack}.slack.com/archives/${channel}/p${seconds}${fraction}`;
  }
  return null;
}

/**
 * A ref as the post names it and the ledger takes it, with its URL after it when there is one, such
 * as `example/web#11 <https://github.com/example/web/pull/11>`.
 */
const cite = (ref: string, url: string | null) => (url ? `${ref} <${url}>` : ref);

/** What `item` names, cited with its URL: a T3 thread's own link, or its ref's. */
function link(item: Change, sources: readonly Source[]): string {
  if ("link" in item.detail) return cite(item.ref, item.detail.link);
  const pull = item.kind.startsWith("pr.");
  return cite(item.ref, urlOf(item.ref, item.source, sources, { pull, nested: false }));
}

/** The detail fields that hold refs: tickets, and the PRs a release names. */
const REFS: ReadonlySet<string> = new Set(["blocks", "blocker", "ticket", "prs"]);

/**
 * Whether message `a` was sent before `b`, by the full Slack timestamps in their refs, since `at`
 * keeps only the second and two messages can share one: the seconds, then the fractions padded to
 * the same width.
 */
function before(a: Change, b: Change): boolean {
  const [, , aSeconds = "0", aFraction = ""] = MESSAGE.exec(a.ref) ?? [];
  const [, , bSeconds = "0", bFraction = ""] = MESSAGE.exec(b.ref) ?? [];
  if (aSeconds !== bSeconds) return BigInt(aSeconds) < BigInt(bSeconds);
  const width = Math.max(aFraction.length, bFraction.length);
  return aFraction.padEnd(width, "0") < bFraction.padEnd(width, "0");
}

/** The item's detail as `key: value` pairs, each ref in it cited. */
function reading(item: Change, sources: readonly Source[]): string {
  const show = (key: string, value: unknown) =>
    REFS.has(key) && typeof value === "string"
      ? cite(value, urlOf(value, item.source, sources, { pull: key === "prs", nested: true }))
      : String(value ?? "none");
  return Object.entries(item.detail)
    .filter(([key]) => key !== "link")
    .map(([key, value]) => {
      const shown = Array.isArray(value)
        ? value.map((entry) => show(key, entry)).join(" ") || "none"
        : show(key, value);
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
  context: { now: Date; sources: readonly Source[]; ledger: Ledger },
): string {
  const { now, sources } = context;
  const age = (at: string) => `${minutesAgo(new Date(at), now)} min ago`;
  const line = (item: Change, read: string) =>
    [item.kind, link(item, sources), age(item.at), ...(read === "" ? [] : [read])].join(" · ");
  /** Each item's line, or a conversation's waiting messages where its first one stood. */
  const rows: (string | ChangeOf<"slack.waiting">[])[] = [];
  const waiting = new Map<string, ChangeOf<"slack.waiting">[]>();
  const people = new Map<string, Map<"moved" | "finished" | "new", number>>();
  /** Each channel's messages, by its source and id, and its name. */
  const channels = new Map<string, { source: string; name: string; count: number }>();
  for (const item of batch.items) {
    if (item.kind === "slack.waiting") {
      // A channel id is unique only within its workspace, so two sources never share a line.
      const key = `${item.source}\n${item.detail.channel}`;
      const conversation = waiting.get(key);
      if (conversation !== undefined) conversation.push(item);
      else {
        const first = [item];
        waiting.set(key, first);
        rows.push(first);
      }
    } else if (item.kind === "team.pulse") {
      const { detail } = item;
      const counts = people.get(detail.who) ?? new Map();
      tally(counts, "new" in detail ? "new" : detail.finished ? "finished" : "moved");
      people.set(detail.who, counts);
    } else if (item.kind === "slack.channel") {
      const key = `${item.source}\n${item.ref}`;
      const { source, detail } = item;
      const seen = channels.get(key);
      channels.set(key, { source, name: detail.name, count: (seen?.count ?? 0) + 1 });
    } else rows.push(line(item, reading(item, sources)));
  }
  const shown = rows.map((row) => {
    if (typeof row === "string") return row;
    const oldest = row.reduce((a, b) => (before(b, a) ? b : a));
    const via = [...new Set(row.map((item) => item.detail.via))].join(" and ");
    return line(oldest, `${plural(row.length, "message")} waiting, via ${via}`);
  });
  const pulse = [
    ...[...people].map(
      ([who, counts]) =>
        `${who} ${[...counts].map(([what, count]) => `${count} ${what}`).join(", ")}`,
    ),
    ...[...channels.values()].map(({ source, name, count }) => {
      const shared = [...channels.values()].filter((other) => other.name === name).length > 1;
      return `#${name}${shared ? ` (${source})` : ""} ${plural(count, "message")}`;
    }),
  ];
  if (pulse.length > 0) shown.push(["pulse", ...pulse].join(" · "));
  const done = deliveredNote(context.ledger, batch.id);
  const changes = plural(batch.items.length, "change");
  const header = `Batch ${batch.id} (${batch.kind}, ${changes}${done}): ${batch.reason}`;
  return [header, ...shown.map((row) => `- ${row}`)].join("\n");
}
