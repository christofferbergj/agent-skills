/**
 * GitHub, through the `gh` CLI: the user's open PRs with reviews and checks, review requests,
 * issues, other people's open PRs, and releases, per repository as the profile sets them. Reads
 * only. Keeps numbers, states, and tags, never titles or bodies.
 */
import { runJson } from "../calls.ts";
import type { Change } from "../changes.ts";
import {
  type Infer,
  type Parser,
  array,
  boolean,
  literal,
  nullable,
  number,
  object,
  optional,
  record,
  string,
  withDefault,
} from "../parse.ts";
import type { GithubSource } from "../profile.ts";
import { iso } from "../time.ts";
import type { Adapter, Context, Window } from "./index.ts";

const RED = new Set(["FAILURE", "ERROR", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"]);
const WAITING = new Set(["PENDING", "EXPECTED", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"]);

const check = object({
  conclusion: nullable(string),
  state: nullable(string),
  status: nullable(string),
});
const minePr = object({
  number,
  reviewDecision: nullable(string),
  statusCheckRollup: nullable(array(check)),
  updatedAt: nullable(string),
});
const requestedPr = object({ number, updatedAt: nullable(string) });
const issue = object({
  number,
  assignees: nullable(array(object({ login: nullable(string) }))),
  createdAt: nullable(string),
  updatedAt: nullable(string),
});
const openPr = object({ number, createdAt: nullable(string) });
const release = object({
  tagName: string,
  publishedAt: nullable(string),
  isDraft: withDefault(boolean, false),
});

const ci = literal("failing", "pending", "passing");
const repoState = object({
  mine: optional(record(object({ ci, review: string }))),
  requested: optional(array(string)),
  /** Issue number → whether it is assigned to the user. */
  issues: optional(record(boolean)),
  open: optional(array(string)),
  releases: optional(array(string)),
});
type RepoState = Infer<typeof repoState>;
const section = object({ at: string, repos: record(repoState) });
type Section = Infer<typeof section>;

function ciOf(rollup: Infer<typeof check>[] | null): Infer<typeof ci> {
  const states = (rollup ?? []).map((entry) => ({
    conclusion: entry.conclusion ?? entry.state ?? "",
    status: entry.status ?? "",
  }));
  if (states.some(({ conclusion }) => RED.has(conclusion))) return "failing";
  const running = ({ conclusion, status }: { conclusion: string; status: string }) =>
    WAITING.has(status) ||
    WAITING.has(conclusion) ||
    (status !== "" && status !== "COMPLETED" && conclusion === "");
  return states.some(running) ? "pending" : "passing";
}

/**
 * A `gh` list of one repository, named in errors by its place in the profile, `repos[1] PRs`, since
 * stderr reaches the journal and never names a repository.
 */
function gh<T>(
  repo: { name: string; index: number },
  args: string[],
  what: string,
  item: Parser<T>,
): T[] {
  return runJson(
    ["gh", ...args.slice(0, 2), "-R", repo.name, ...args.slice(2)],
    `repos[${repo.index}] ${what}`,
    array(item),
  );
}

function scan(source: GithubSource, window: Window<Section>, ctx: Context) {
  const baseline = window.kind === "baseline";
  const prev = window.kind === "resume" ? window.prev : null;
  const now = iso(ctx.now);
  const since = window.kind === "since" ? iso(window.since) : null;
  // The start of what this scan covers. A transition this scan sees for the first time is keyed by
  // it: a replay after a crash keeps the key, and the next transition gets a new one.
  const key = prev?.at ?? since ?? now;
  /** New since the last scan; with no list yet, created after the `--since` start. */
  const isNew = (before: string[] | undefined, id: string, created: string | null) =>
    before !== undefined ? !before.includes(id) : since !== null && (created ?? "") >= since;
  const waits = new Map<string, string[]>();
  for (const wait of ctx.ledger.waits) waits.set(wait.on, [...(waits.get(wait.on) ?? []), wait.pr]);
  const repos: Section["repos"] = {};
  const changes: Change[] = [];
  for (const [index, entry] of source.repos.entries()) {
    const repo = entry.repo;
    const at = { name: repo, index };
    const old: RepoState = prev?.repos[repo] ?? {};
    const state: RepoState = {};
    if (entry.mine) {
      const fields = "number,isDraft,reviewDecision,statusCheckRollup,updatedAt";
      const prs = gh(
        at,
        ["pr", "list", "--author", "@me", "--state", "open", "--limit", "100", "--json", fields],
        "PRs",
        minePr,
      );
      state.mine = {};
      for (const pr of prs) {
        const ref = `${repo}#${pr.number}`;
        const seen = { ci: ciOf(pr.statusCheckRollup), review: pr.reviewDecision ?? "" };
        state.mine[String(pr.number)] = seen;
        const was = old.mine?.[String(pr.number)];
        const at = pr.updatedAt ?? now;
        // A PR first seen after the baseline counts its state as new: one opened red still wakes.
        if (
          baseline ||
          (was === undefined && old.mine === undefined && !(since !== null && at >= since))
        )
          continue;
        if (seen.ci === "failing" && was?.ci !== "failing") {
          changes.push(ctx.change("pr.ci_failed", { ref, at, key, detail: {} }));
        }
        if (seen.review !== (was?.review ?? "") && seen.review === "CHANGES_REQUESTED") {
          changes.push(ctx.change("pr.changes_requested", { ref, at, key, detail: {} }));
        } else if (seen.review !== (was?.review ?? "") && seen.review === "APPROVED") {
          changes.push(ctx.change("pr.approved", { ref, at, key, detail: {} }));
        }
      }
    }
    if (entry.review_requests) {
      const args = [
        "pr",
        "list",
        "--search",
        "review-requested:@me",
        "--state",
        "open",
        "--limit",
        "100",
        "--json",
        "number,updatedAt",
      ];
      const asked = gh(at, args, "review requests", requestedPr);
      state.requested = asked.map((pr) => String(pr.number)).sort();
      for (const pr of asked) {
        if (baseline || (old.requested ?? []).includes(String(pr.number))) continue;
        changes.push(
          ctx.change("pr.review_requested", {
            ref: `${repo}#${pr.number}`,
            at: pr.updatedAt ?? now,
            key,
            detail: {},
          }),
        );
      }
    }
    if (entry.issues) {
      const args = [
        "issue",
        "list",
        "--state",
        "open",
        "--limit",
        "200",
        "--json",
        "number,assignees,createdAt,updatedAt",
      ];
      const issues = gh(at, args, "issues", issue);
      const before = old.issues;
      state.issues = {};
      for (const found of issues) {
        const number = String(found.number);
        const ref = `${repo}#${found.number}`;
        const mine = (found.assignees ?? []).some((assignee) => assignee.login === source.me);
        state.issues[number] = mine;
        const fresh = isNew(
          before === undefined ? undefined : Object.keys(before),
          number,
          found.createdAt,
        );
        if (baseline) continue;
        if (mine && (fresh || before?.[number] === false)) {
          const at = found.updatedAt ?? now;
          changes.push(
            ctx.change("issue.assigned", { ref, at, key: found.updatedAt ?? key, detail: {} }),
          );
        } else if (fresh) {
          changes.push(
            ctx.change("issue.new", { ref, at: found.createdAt ?? now, key: "new", detail: {} }),
          );
        }
      }
    }
    if (entry.open_prs) {
      const prs = gh(
        at,
        ["pr", "list", "--state", "open", "--limit", "200", "--json", "number,createdAt"],
        "open PRs",
        openPr,
      );
      const before = old.open;
      const open = prs.map((pr) => String(pr.number)).sort();
      state.open = open;
      if (!baseline) {
        for (const pr of prs) {
          if (!isNew(before, String(pr.number), pr.createdAt)) continue;
          changes.push(
            ctx.change("pr.opened", {
              ref: `${repo}#${pr.number}`,
              at: pr.createdAt ?? now,
              key,
              detail: {},
            }),
          );
        }
        for (const number of (before ?? []).filter((n) => !open.includes(n)).sort()) {
          changes.push(
            ctx.change("pr.closed", { ref: `${repo}#${number}`, at: now, key, detail: {} }),
          );
        }
      }
    }
    if (entry.releases) {
      const found = gh(
        at,
        ["release", "list", "--limit", "10", "--json", "tagName,publishedAt,isDraft"],
        "releases",
        release,
      );
      const before = old.releases;
      state.releases = found.filter((r) => !r.isDraft).map((r) => r.tagName);
      for (const published of found) {
        if (
          baseline ||
          published.isDraft ||
          !isNew(before, published.tagName, published.publishedAt)
        )
          continue;
        const prs = waits.get(repo);
        changes.push(
          ctx.change(prs === undefined ? "release.new" : "release.awaited", {
            ref: `${repo}@${published.tagName}`,
            at: published.publishedAt ?? now,
            key: published.tagName,
            detail: { prs: prs ?? [] },
          }),
        );
      }
    }
    repos[repo] = state;
  }
  return { section: { at: now, repos }, changes };
}

export const github: Adapter<GithubSource, Section> = { section, scan };
