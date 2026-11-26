/**
 * Fake `probe.ts`, `gh`, and `t3` for the scan's tests: `node fakes.ts probe|gh|t3 …`. Each serves
 * `world.json` in the folder $FAKE names, shaped like the responses recorded from the live tools on
 * 26 Nov 2026, and logs every call, so a test can assert what a source and a thread received. Every
 * value in the fixtures is invented: no real ticket text, message text, or person.
 */
import { appendFileSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export type Note = { id: string; type: string; url: string; createdAt: string };
export type MineIssue = {
  id: string;
  status: string;
  statusType: string;
  priority: { value: number; name: string } | null;
  dueDate: string | null;
  assigneeId: string;
  updatedAt: string;
  project: string | null;
  team: string;
};
export type IssueDetail = {
  id: string;
  relations?: {
    blocks: unknown[];
    blockedBy: { id: string; title?: string }[];
    relatedTo: unknown[];
  };
  stateHistory?: {
    state: { name: string; type?: string };
    startedAt: string;
    endedAt: string | null;
  }[];
  status?: string;
  statusType?: string;
  assignee?: string;
  updatedAt?: string;
};
export type TeamIssue = {
  id: string;
  status: string;
  statusType: string;
  assignee: string;
  assigneeId: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  project: string | null;
};
export type SlackMessage = {
  channel: string;
  ts: string;
  from: string;
  thread?: string;
  mentions?: string[];
  name?: string;
  /** What the record's `Text:` line holds; the fixture leaves message text out by default. */
  text?: string;
  /** A record the tool sent without its `Message_ts:` line. */
  broken?: boolean;
};
export type Check = { status: string; conclusion: string; name?: string; __typename?: string };
export type Pr = {
  number: number;
  isDraft?: boolean;
  reviewDecision?: string;
  statusCheckRollup?: Check[];
  updatedAt?: string;
};
export type Repo = {
  mine?: Pr[];
  requested?: { number: number; updatedAt: string }[];
  issues?: {
    number: number;
    createdAt: string;
    updatedAt: string;
    assignees: { login: string }[];
  }[];
  open?: { number: number; createdAt: string }[];
  releases?: { tagName: string; publishedAt: string; isDraft: boolean }[];
};
export type T3Thread = {
  threadId: string;
  status: string;
  settled: boolean;
  snoozed: boolean;
  snoozedUntil: string | null;
  parentThreadId: string | null;
  itemCount: number;
  latestRunId: string | null;
  createdAt: string;
  updatedAt: string;
  link?: string;
  archived?: boolean;
};
export type World = {
  _about?: string;
  linear: {
    notifications: Note[];
    /** The user's tickets, in the order `list_issues` pages them. */
    mine: MineIssue[];
    issues: Record<string, IssueDetail>;
    team: Record<string, TeamIssue[]>;
    /** The most items a page holds, when it is fewer than a call's `limit`. */
    page_size?: number;
  };
  slack: { me: string; messages: SlackMessage[] };
  github: Record<string, Repo>;
  t3: {
    assistant: { threadId: string; status: string; last: string } | null;
    threads: T3Thread[];
    send_code?: number;
    /** Statuses the assistant thread shows at the next `thread show` calls, one each, in order. */
    shows?: string[];
    /** How long `thread show` takes, so a test can catch a scan while it runs. */
    show_ms?: number;
  };
  /** A source's app (`linear`, `slack`, `github`) → `auth`, or the text its error should carry. */
  fail?: Record<string, string>;
  /** Linear tickets `get_issue` fails to load, as for a ticket since deleted. */
  unreadable?: string[];
};

const FAKE = process.env.FAKE ?? "";

function world(): World {
  return JSON.parse(readFileSync(join(FAKE, "world.json"), "utf8"));
}

function log(name: string, entry: unknown): void {
  appendFileSync(join(FAKE, `${name}.jsonl`), `${JSON.stringify(entry)}\n`);
}

const text = (payload: unknown) => ({ content: [{ type: "text", text: JSON.stringify(payload) }] });

/**
 * A search page in the Slack tool's Markdown, as recorded: the header counts this page, and a next
 * cursor follows while more remain.
 */
function slackPage(messages: SlackMessage[], limit: number, offset: number) {
  const shown = messages.slice(offset, offset + limit);
  const lines = ["# Search Results for: ", "", `## Messages (${shown.length} results)`];
  shown.forEach((m, index) => {
    const label = m.channel.startsWith("D") ? "DM" : `#${m.name ?? "channel"}`;
    const thread = m.thread ? `?thread_ts=${m.thread}&cid=${m.channel}` : "";
    lines.push(
      `### Result ${index + 1} of ${shown.length}`,
      `Channel: ${label} (ID: ${m.channel})`,
      `From: Invented Person <invented@example.com> (ID: ${m.from}) `,
      "Time: 2026-11-26 10:00:00 CET",
      ...(m.broken ? [] : [`Message_ts: ${m.ts}`]),
      `Permalink: [link](https://example.slack.com/archives/${m.channel}/p${m.ts.replace(".", "")}${thread})`,
      `Text: ${m.text ?? "(left out of the fixture)"}`,
      "---",
    );
  });
  const more = messages.length > offset + limit;
  return {
    results: lines.join("\n"),
    pagination_info: more ? `Next page: \`${String(offset + limit).padStart(8, "0")}\`` : "",
  };
}

function slack(args: Record<string, unknown>, state: World["slack"]) {
  const after = Number(args.after ?? 0);
  const me = state.me;
  const messages = state.messages.filter((m) => Number(m.ts) >= after);
  const filters = String(args.filters ?? "");
  const keywords = JSON.stringify(args.keywords ?? []);
  let picked: SlackMessage[] = [];
  if (filters === "to:me")
    picked = messages.filter((m) => m.channel.startsWith("D") && m.from !== me);
  else if (keywords === JSON.stringify([`<@${me}>`]))
    picked = messages.filter((m) => m.mentions?.includes(me));
  else if (filters === `from:<@${me}>`) picked = messages.filter((m) => m.from === me);
  else if (filters.startsWith("in:<#")) {
    const channels = new Set(filters.split(" ").map((part) => part.slice(5, -1)));
    picked = messages.filter((m) => channels.has(m.channel));
  }
  const sign = args.sort_dir === "asc" ? 1 : -1;
  picked.sort((a, b) => sign * (Number(a.ts) - Number(b.ts)));
  return slackPage(picked, Number(args.limit ?? 20), Number(args.cursor ?? "0"));
}

/**
 * One page of `items`, after the item the cursor names, as Linear pages them: at most the `limit`
 * asked for, or the world's smaller `page_size`, with the last item's id as the next cursor.
 */
function page<T extends { id: string }>(
  items: T[],
  args: Record<string, unknown>,
  state: World["linear"],
): { items: T[]; hasNextPage: boolean; cursor: string | null } {
  const start =
    args.cursor === undefined ? 0 : items.findIndex((item) => item.id === args.cursor) + 1;
  const size = Math.min(Number(args.limit ?? 50), state.page_size ?? Infinity);
  const shown = items.slice(start, start + size);
  const more = start + size < items.length;
  return { items: shown, hasNextPage: more, cursor: more ? (shown.at(-1)?.id ?? null) : null };
}

function linear(path: string, args: Record<string, unknown>, state: World["linear"]) {
  if (path.endsWith("get_notifications")) {
    const sorted = [...state.notifications].sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
    const { items, ...rest } = page(sorted, args, state);
    return { notifications: items, ...rest };
  }
  if (path.endsWith("list_issues")) {
    const updated = (state.team[String(args.team)] ?? []).filter(
      (issue) => issue.updatedAt > String(args.updatedAt ?? ""),
    );
    const { items, ...rest } =
      args.assignee === "me" ? page(state.mine, args, state) : page(updated, args, state);
    return { issues: items, ...rest };
  }
  if (path.endsWith("get_issue")) {
    const id = String(args.id);
    return state.issues[id] ?? { id, relations: { blockedBy: [] }, stateHistory: [] };
  }
  throw new Error(`the fake has no ${path}`);
}

type Call = { path: string; input: { input: Record<string, unknown> } };

/** `probe … call <body>`: answers each call in the body as Executor would. */
function probe(args: string[]): void {
  const body: { calls: Call[] } = JSON.parse(args[1] ?? "{}");
  const state = world();
  const values = body.calls.map(({ path, input: { input } }) => {
    log("probe", { path, input });
    const app = path.split(".")[1] ?? "";
    const failure = state.fail?.[app];
    if (failure === "auth") {
      return {
        path,
        ok: false,
        error: { kind: "ToolFailure", message: "UNAUTHORIZED: sign in again" },
      };
    }
    if (failure) return { path, ok: false, error: { kind: "ToolFailure", message: failure } };
    if (path.endsWith("get_issue") && state.unreadable?.includes(String(input.id))) {
      return { path, ok: false, error: { kind: "ToolFailure", message: "Entity not found" } };
    }
    const payload = app === "slack" ? slack(input, state.slack) : linear(path, input, state.linear);
    return { path, ok: true, value: text(payload) };
  });
  console.log("executor_client: fake mapping");
  console.log(
    JSON.stringify({
      tool: "call",
      result: { structuredContent: { execution: { value: values } } },
    }),
  );
}

function gh(args: string[]): void {
  log("gh", args);
  const state = world();
  if (state.fail?.github) {
    process.stderr.write("HTTP 401: Bad credentials\n");
    process.exit(1);
  }
  const repo = state.github[args[args.indexOf("-R") + 1] ?? ""] ?? {};
  const [noun, verb] = args;
  const out =
    noun === "release" && verb === "list"
      ? repo.releases
      : noun === "issue" && verb === "list"
        ? repo.issues
        : args.includes("--author")
          ? repo.mine
          : args.includes("--search")
            ? repo.requested
            : repo.open;
  console.log(JSON.stringify(out ?? []));
}

function t3(args: string[]): void {
  const all = world();
  const state = all.t3;
  const [noun, verb] = args;
  if (noun !== "thread") return;
  if (verb === "list") {
    console.log(JSON.stringify(state.threads));
  } else if (verb === "show") {
    if (state.show_ms) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, state.show_ms);
    if (state.assistant === null) {
      process.stderr.write("the thread is gone\n");
      process.exit(1);
    }
    const status = state.shows?.shift() ?? state.assistant.status;
    if (state.shows !== undefined) writeFileSync(join(FAKE, "world.json"), JSON.stringify(all));
    const messages = [{ role: "assistant", text: state.assistant.last }];
    console.log(JSON.stringify({ thread: { ...state.assistant, status }, messages }));
  } else if (verb === "send") {
    log("sent", { to: args[2], message: readFileSync(0, "utf8") });
    process.exit(state.send_code ?? 0);
  }
}

const [tool, ...rest] = process.argv.slice(2);
if (tool === "probe") probe(rest);
else if (tool === "gh") gh(rest);
else if (tool === "t3") t3(rest);
