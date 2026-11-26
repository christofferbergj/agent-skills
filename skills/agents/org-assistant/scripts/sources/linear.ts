/**
 * Linear: the user's inbox as the event feed, their open tickets with relations and status history,
 * the tickets those depend on, and each listed team's changes since the last scan. Reads only;
 * never marks an inbox item read. Keeps ids, states, and staff names, never titles.
 */
import { Executor, read } from "../calls.ts";
import type { Change } from "../changes.ts";
import {
  type Infer,
  type Parser,
  array,
  boolean,
  isRecord,
  map,
  nullable,
  number,
  object,
  oneOf,
  record,
  refine,
  string,
  withDefault,
} from "../parse.ts";
import type { LinearSource } from "../profile.ts";
import { DAY, HOUR, calendarDate, midnight, time } from "../time.ts";
import type { Adapter, Context, Window } from "./index.ts";

const TOOLS = {
  inbox: "tools.linear.get_notifications",
  list: "tools.linear.list_issues",
  issue: "tools.linear.get_issue",
} as const;
const ISSUE = /\/issue\/([A-Z][A-Z0-9]*-\d+)/;
const CLOSED = new Set(["completed", "canceled", "duplicate"]);
/** Pages one read takes at most: 1,000 inbox items, or 5,000 tickets of a list. */
const PAGES = 20;
const INBOX_PAGE = 50;
const LIST_PAGE = 250;
const TEAM_MEMORY = 30 * DAY;
type InboxKind =
  | "ticket.assigned"
  | "ticket.unassigned"
  | "ticket.changed"
  | "ticket.mention"
  | "ticket.comment"
  | "linear.other";
/** Inbox type → change kind; any other type is `linear.other`, shown in the pulse. */
const INBOX: Record<string, InboxKind> = {
  issueAssignedToYou: "ticket.assigned",
  issueUnassignedFromYou: "ticket.unassigned",
  issueStatusChanged: "ticket.changed",
  issueCommentMention: "ticket.mention",
  issueMention: "ticket.mention",
  issueNewComment: "ticket.comment",
}; // Due dates and blockers come from the tickets themselves, so their inbox items aren't repeated.
const MINE_FIELDS = [
  "id",
  "status",
  "statusType",
  "priority",
  "dueDate",
  "assigneeId",
  "updatedAt",
  "project",
  "team",
];
const TEAM_FIELDS = [
  "id",
  "status",
  "statusType",
  "assignee",
  "assigneeId",
  "createdAt",
  "updatedAt",
  "completedAt",
  "project",
];

/** A time in the one form Linear writes, UTC to the millisecond, so any two compare as strings. */
type Stamp = string & { readonly __brand: "Stamp" };

function isStamp(text: string): text is Stamp {
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(text);
}

function stamp(instant: Date): Stamp {
  const text = instant.toISOString();
  if (!isStamp(text)) throw new Error(`toISOString gave ${text}`);
  return text;
}

/** A time a response gives, in Linear's form; one past year 9999 has no such form. */
const when: Parser<Stamp> = refine(
  map(time, (instant) => instant.toISOString()),
  isStamp,
  "expected a time before the year 10000",
);
/** A list that may also be absent or null. */
const list = <T>(item: Parser<T>) => map(nullable(array(item)), (value) => value ?? []);
const more = withDefault(boolean, false);

type Page<T> = { items: T[]; more: boolean; cursor: string | null };

const note = object({ id: string, type: nullable(string), url: nullable(string), createdAt: when });
type Note = Infer<typeof note>;
const notes: Parser<Page<Note>> = map(
  object({ notifications: array(note), hasNextPage: more, cursor: nullable(string) }),
  (read) => ({ items: read.notifications, more: read.hasNextPage, cursor: read.cursor }),
);

const priority = map(nullable(oneOf(number, object({ value: nullable(number) }))), (value) =>
  typeof value === "object" && value !== null ? value.value : value,
);
const mineIssue = object({
  id: string,
  status: nullable(string),
  statusType: nullable(string),
  priority,
  dueDate: nullable(calendarDate),
  assigneeId: nullable(string),
  updatedAt: nullable(when),
  project: nullable(string),
});
const issues = <T>(item: Parser<T>): Parser<Page<T>> =>
  map(object({ issues: array(item), hasNextPage: more, cursor: nullable(string) }), (read) => ({
    items: read.issues,
    more: read.hasNextPage,
    cursor: read.cursor,
  }));

const history = object({
  id: string,
  relations: nullable(object({ blockedBy: list(object({ id: string })) })),
  stateHistory: list(
    object({ state: nullable(object({ name: nullable(string) })), startedAt: nullable(when) }),
  ),
});
const blocker = object({
  status: nullable(string),
  statusType: nullable(string),
  assignee: nullable(string),
  updatedAt: nullable(string),
});

const teamIssue = object({
  id: string,
  status: nullable(string),
  statusType: nullable(string),
  assignee: nullable(string),
  assigneeId: nullable(string),
  createdAt: nullable(when),
  updatedAt: nullable(when),
  completedAt: nullable(when),
  project: nullable(string),
});

const stamped = refine(string, isStamp, "expected a time to the millisecond");
const section = object({
  at: stamped,
  /**
   * The inbox's watermark: the newest item read, with every item before it, and the ids at that
   * time, so an item that shares it joins once.
   */
  inbox_at: stamped,
  inbox_ids: array(string),
  /** The user's Linear id, from their own tickets. */
  me: nullable(string),
  mine: record(
    object({ priority: nullable(number), due: nullable(calendarDate), blockedBy: array(string) }),
  ),
  deps: record(object({ status: nullable(string) })),
  /** The due date each deadline change was raised for, so each due date wakes once. */
  deadlines: record(string),
  team: record(object({ status: nullable(string), seen: stamped })),
});
type Section = Infer<typeof section>;

/** A point in the inbox: a time, and the ids of the items read at that time. */
type Mark = { at: Stamp; ids: string[] };

/**
 * The items on up to PAGES pages of `tool`; `stop(item)` ends the walk early. `capped` says the walk
 * reached the cap with pages left; the next scan doesn't go on from there, so the health line says
 * what this one left unread.
 */
function walk<T>(
  executor: Executor,
  tool: string,
  input: Record<string, unknown>,
  page: Parser<Page<T>>,
  stop: (item: T) => boolean = () => false,
): { items: T[]; capped: boolean } {
  const items: T[] = [];
  let cursor: string | null = null;
  for (let count = 0; count < PAGES; count++) {
    const [value] = executor.call([
      { path: tool, input: cursor === null ? input : { ...input, cursor } },
    ]);
    const got = read(page, value, tool);
    items.push(...got.items);
    if (!got.more || got.cursor === null || got.items.some(stop)) return { items, capped: false };
    cursor = got.cursor;
  }
  return { items, capped: true };
}

/** What a read past the cap of `size`-item pages left out, for the health line. */
const capNote = (what: string, size: number, rest: string) =>
  `${what} capped at ${(PAGES * size).toLocaleString("en")}: ${rest}`;

/** The newest of `items` and `mark`, with the ids of the items at that time. */
function newest(items: Note[], mark: Mark): Mark {
  const at = items.reduce((top, item) => (item.createdAt > top ? item.createdAt : top), mark.at);
  const ids = items.filter((item) => item.createdAt === at).map((item) => item.id);
  return { at, ids: [...new Set([...ids, ...(at === mark.at ? mark.ids : [])])].sort() };
}

/**
 * The inbox items above the watermark, newest first, read down to the first item it covers: one
 * older than it, or one at its time already read. The watermark rises to the newest item read, so
 * items a read past the cap didn't reach stay unread.
 */
function readInbox(executor: Executor, prev: Section | null, since: Stamp) {
  const mark: Mark = { at: prev?.inbox_at ?? since, ids: prev?.inbox_ids ?? [] };
  const covered = (item: Note) =>
    item.createdAt < mark.at || (item.createdAt === mark.at && mark.ids.includes(item.id));
  const read = walk(executor, TOOLS.inbox, { limit: INBOX_PAGE }, notes, covered);
  const fresh = read.items.filter((item) => !covered(item));
  const top = newest(fresh, mark);
  return { fresh, capped: read.capped, mark: { inbox_at: top.at, inbox_ids: top.ids } };
}

function scan(source: LinearSource, window: Window<Section>, ctx: Context) {
  const executor = new Executor(source, Object.values(TOOLS));
  const now = stamp(ctx.now);
  const baseline = window.kind === "baseline";
  const prev = window.kind === "resume" ? window.prev : null;
  const since = prev?.at ?? (window.kind === "since" ? stamp(window.since) : now);
  const changes: Change[] = [];
  const notes: string[] = [];

  const inbox = readInbox(executor, prev, since);
  if (inbox.capped) notes.push(capNote("inbox", INBOX_PAGE, "older items unread"));
  const { fresh } = inbox;
  const ticketOf = (item: Note) => ISSUE.exec(item.url ?? "")?.[1] ?? null;
  const statusNoted = new Set(
    fresh
      .filter((item) => item.type === "issueStatusChanged")
      .flatMap((item) => ticketOf(item) ?? []),
  );

  // The user's open tickets.
  const listed = walk(
    executor,
    TOOLS.list,
    { assignee: "me", limit: LIST_PAGE, fields: MINE_FIELDS },
    issues(mineIssue),
  );
  const open = listed.items.filter((issue) => !CLOSED.has(issue.statusType ?? ""));
  const me =
    listed.items.find((issue) => issue.assigneeId !== null)?.assigneeId ?? prev?.me ?? null;
  const before = prev?.mine ?? {};
  const stale = open
    .filter((issue) => baseline || !(issue.id in before) || (issue.updatedAt ?? "") > since)
    .map((issue) => issue.id);
  const details = new Map(
    executor
      .call(
        stale.map((id) => ({
          path: TOOLS.issue,
          input: { id, fields: ["id", "relations", "stateHistory"] },
        })),
      )
      .map((value) => read(history, value, TOOLS.issue))
      .map((detail) => [detail.id, detail]),
  );
  const mine: Section["mine"] = {};
  const projects = new Set<string>();
  for (const issue of open) {
    const ref = issue.id;
    const old = before[ref];
    const detail = details.get(ref);
    mine[ref] = {
      priority: issue.priority,
      due: issue.dueDate,
      blockedBy: detail
        ? (detail.relations?.blockedBy ?? []).map((b) => b.id).sort()
        : (old?.blockedBy ?? []),
    };
    if (issue.project !== null) projects.add(issue.project);
    if (baseline) continue;
    for (const entry of detail?.stateHistory ?? []) {
      const started = entry.startedAt;
      if (started === null || started <= since) continue;
      changes.push(
        ctx.change(statusNoted.has(ref) ? "ticket.changed" : "ticket.moved", {
          ref,
          at: started,
          key: `status@${started}`,
          detail: { field: "status", to: entry.state?.name ?? null },
        }),
      );
    }
    if (old === undefined) continue;
    const current = mine[ref];
    for (const field of ["priority", "due"] as const) {
      if (old[field] === current[field]) continue;
      changes.push(
        ctx.change("ticket.changed", {
          ref,
          at: issue.updatedAt ?? now,
          key: `${field}@${issue.updatedAt}`,
          detail: { field, to: current[field], by: "unknown" },
        }),
      );
    }
  }
  // A list past the cap keeps each ticket it didn't reach as the last scan saw it.
  if (listed.capped) {
    notes.push(capNote("assigned tickets", LIST_PAGE, "the rest kept as last read"));
    const reached = new Set(listed.items.map((issue) => issue.id));
    for (const [ref, entry] of Object.entries(before)) if (!reached.has(ref)) mine[ref] = entry;
  }

  // The inbox items, read against the user's tickets: a status change or a comment counts only on
  // their own ticket, and a status change the history already shows isn't repeated.
  const moved = new Set(
    changes
      .filter((item) => "field" in item.detail && item.detail.field === "status")
      .map((item) => item.ref),
  );
  const owned = new Set([...Object.keys(mine), ...Object.keys(before)]); // a ticket closed or reassigned since was still theirs
  for (const item of baseline ? [] : fresh) {
    const ref = ticketOf(item) ?? "linear";
    let kind = INBOX[item.type ?? ""] ?? "linear.other";
    if ((kind === "ticket.changed" || kind === "ticket.comment") && !owned.has(ref))
      kind = "linear.other";
    if (kind === "ticket.changed" && moved.has(ref)) continue;
    changes.push(
      ctx.change(kind, { ref, at: item.createdAt, key: item.id, detail: { type: item.type } }),
    );
  }

  // Deadlines within 24 hours, each due date once.
  const deadlines: Record<string, string> = {};
  for (const [ref, issue] of Object.entries(mine)) {
    const raised = prev?.deadlines[ref];
    if (raised !== undefined) deadlines[ref] = raised;
    if (issue.due === null) continue;
    const left = midnight(issue.due, ctx.zone, 1).getTime() - ctx.now.getTime();
    if (left <= 0 || left > 24 * HOUR || raised === issue.due) continue;
    deadlines[ref] = issue.due;
    if (!baseline) {
      changes.push(
        ctx.change("deadline.soon", { ref, at: now, key: issue.due, detail: { due: issue.due } }),
      );
    }
  }

  // Tickets the user's work waits on: typed blocked-by relations, and the ones the user confirmed.
  const depends = new Map<string, Set<string>>();
  const blocks = (blockerRef: string, blocked: string) =>
    depends.set(blockerRef, (depends.get(blockerRef) ?? new Set()).add(blocked));
  for (const [ref, issue] of Object.entries(mine))
    for (const blockerRef of issue.blockedBy) blocks(blockerRef, ref);
  for (const pair of ctx.ledger.depends) if (pair.ticket in mine) blocks(pair.on, pair.ticket);
  // A blocker this scan can't read keeps its last state: one deleted ticket can't stop the source.
  const order = [...depends.keys()].sort();
  const fetched = executor.callEach(
    order.map((id) => ({
      path: TOOLS.issue,
      input: { id, fields: ["id", "status", "statusType", "assignee", "updatedAt"] },
    })),
  );
  const deps: Section["deps"] = {};
  const oldDeps = prev?.deps ?? {};
  order.forEach((ref, index) => {
    const value = fetched[index];
    const old = oldDeps[ref];
    if (!isRecord(value)) {
      if (old !== undefined) deps[ref] = old;
      return;
    }
    const issue = read(blocker, value, TOOLS.issue);
    deps[ref] = { status: issue.status };
    const moment = issue.updatedAt ?? issue.status;
    if (baseline || old === undefined || old.status === issue.status) return;
    for (const blocked of [...(depends.get(ref) ?? [])].sort()) {
      changes.push(
        CLOSED.has(issue.statusType ?? "")
          ? ctx.change("ticket.unblocked", {
              ref: blocked,
              at: now,
              key: `${ref}@${moment}`,
              detail: { blocker: ref, to: issue.status },
            })
          : ctx.change("dependency.changed", {
              ref,
              at: now,
              key: `${moment}@${blocked}`,
              detail: {
                blocks: blocked,
                before: old.status,
                to: issue.status,
                owner: issue.assignee,
              },
            }),
      );
    }
  });

  // Each team's movement since the last scan, as a pulse, and new tickets in the user's projects.
  const forget = stamp(new Date(ctx.now.getTime() - TEAM_MEMORY));
  const team = Object.fromEntries(
    Object.entries(prev?.team ?? {}).filter(([, entry]) => entry.seen >= forget),
  );
  for (const name of baseline ? [] : source.teams) {
    const input = { team: name, updatedAt: since, limit: LIST_PAGE, fields: TEAM_FIELDS };
    const read = walk(executor, TOOLS.list, input, issues(teamIssue));
    if (read.capped) notes.push(capNote(`team ${name}`, LIST_PAGE, "the rest unread"));
    for (const issue of read.items) {
      const ref = issue.id;
      const old = team[ref];
      team[ref] = { status: issue.status, seen: now };
      if ((me !== null && issue.assigneeId === me) || ref in mine) continue;
      const who = issue.assignee ?? "unassigned";
      // A move needs the status this scan saw before; a finish needs only its completion time.
      const movedOn = old !== undefined && old.status !== issue.status;
      const finished = issue.statusType === "completed" && (issue.completedAt ?? "") > since;
      if (movedOn || finished) {
        // A finish is keyed by its completion and a move by the window it was seen in, so a later
        // edit to the ticket, or a replay after a crash, can't count either twice.
        const key = finished
          ? `finished@${issue.completedAt}`
          : `${old?.status}>${issue.status}@${since}`;
        changes.push(
          ctx.change("team.pulse", {
            ref,
            at: issue.updatedAt ?? now,
            key,
            detail: { team: name, who, finished },
          }),
        );
      }
      const created = issue.createdAt;
      if (created === null || created <= since) continue;
      changes.push(
        issue.project !== null && projects.has(issue.project)
          ? ctx.change("ticket.new_in_project", {
              ref,
              at: created,
              detail: { project: issue.project },
            })
          : ctx.change("team.pulse", {
              ref,
              at: created,
              key: "new",
              detail: { team: name, who, new: true },
            }),
      );
    }
  }

  return {
    section: { at: now, ...inbox.mark, me, mine, deps, deadlines, team },
    changes,
    ...(notes.length > 0 ? { note: notes.join("; ") } : {}),
  };
}

export const linear: Adapter<LinearSource, Section> = { section, scan };
