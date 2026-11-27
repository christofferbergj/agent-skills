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
 * The workspace slug for a link of `kind`: the one the source `from` gives, or else, for a ref that
 * another kind of source found, the one of the profile's only source of that kind.
 */
function workspace(from: string, sources: readonly Source[], kind: "linear" | "slack") {
  const ofKind = sources.filter(
    (source): source is LinearSource | SlackSource => source.kind === kind,
  );
  const own = ofKind.find((source) => source.name === from);
  const chosen = own ?? (ofKind.length === 1 ? ofKind[0] : undefined);
  return chosen?.workspace ?? null;
}

/**
 * The URL of `ref`, found by the source `from`, or `ref` itself when the profile gives no way to
 * build one; `pull` reads `owner/repo#n` as a PR rather than an issue.
 */
function linkRef(ref: string, from: string, sources: readonly Source[], pull: boolean): string {
  if (TICKET.test(ref)) {
    const linear = workspace(from, sources, "linear");
    return linear === null ? ref : `https://linear.app/${linear}/issue/${ref}`;
  }
  const numbered = NUMBERED.exec(ref);
  if (numbered !== null) {
    const [, repo, number] = numbered;
    return `https://github.com/${repo}/${pull ? "pull" : "issues"}/${number}`;
  }
  const release = RELEASE.exec(ref);
  if (release !== null) {
    const [, repo, tag = ""] = release;
    return `https://github.com/${repo}/releases/tag/${encodeURIComponent(tag)}`;
  }
  const message = MESSAGE.exec(ref);
  if (message !== null) {
    const slack = workspace(from, sources, "slack");
    const [, channel, seconds, fraction] = message;
    return slack === null
      ? ref
      : `https://${slack}.slack.com/archives/${channel}/p${seconds}${fraction}`;
  }
  return ref;
}

/** The URL of what `item` names: a T3 thread's own link, or its ref's. */
function link(item: Change, sources: readonly Source[]): string {
  if ("link" in item.detail) return item.detail.link || item.ref;
  return linkRef(item.ref, item.source, sources, item.kind.startsWith("pr."));
}

/** The detail fields that hold refs: tickets, and the PRs a release names. */
const REFS: ReadonlySet<string> = new Set(["blocks", "blocker", "ticket", "prs"]);

/**
 * A message's place in time from the full Slack timestamp in its ref, since `at` keeps only the
 * second and two messages can share one.
 */
function sent(item: Change): bigint {
  const [, , seconds = "0", fraction = ""] = MESSAGE.exec(item.ref) ?? [];
  return BigInt(seconds + fraction.padEnd(6, "0"));
}

/** The item's detail as `key: value` pairs, each ref in it linked. */
function reading(item: Change, sources: readonly Source[]): string {
  const show = (key: string, value: unknown) =>
    REFS.has(key) && typeof value === "string"
      ? linkRef(value, item.source, sources, key === "prs")
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
    const oldest = row.reduce((a, b) => (sent(b) < sent(a) ? b : a));
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
