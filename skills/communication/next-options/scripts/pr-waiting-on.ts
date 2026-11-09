/**
 * Says what a PR's merge waits on, judging only the checks the repository requires, so an agent
 * watching a PR merges it once it is ready, and hands it back when only a person can move it,
 * instead of waiting for a check that never finishes on its own.
 *
 * usage: node pr-waiting-on.ts <PR number or URL> [--repo owner/name]
 *
 * A merged PR reads `ready` with no items. Prints one line per unfinished item, `required: unknown` when the repository shows no required
 * check (every check then counts as required), and a last `verdict:` line:
 *   person   something waits on a person; hand the PR back (exit 2)
 *   failed   a required check failed; fix it or report it (exit 1)
 *   running  a required check is still running; keep the watch (exit 0)
 *   ready    every required check passed on this head; the PR can merge (exit 0)
 * `info` lines are checks the repository doesn't require. They never change the verdict.
 */
import { execFileSync } from "node:child_process";

export type Verdict = "person" | "failed" | "running" | "ready";
export type Item = {
  kind: Exclude<Verdict, "ready"> | "info";
  name: string;
  detail: string;
  url?: string;
};

export type CheckRun = {
  __typename: "CheckRun";
  /** Grows with each run GitHub creates, so it orders reruns even before they start. */
  databaseId: number;
  name: string;
  status: string;
  conclusion: string | null;
  startedAt: string | null;
  detailsUrl?: string | null;
  isRequired: boolean;
};
export type StatusContext = {
  __typename: "StatusContext";
  context: string;
  state: string;
  description: string | null;
  targetUrl?: string | null;
  isRequired: boolean;
};
export type Pr = {
  /** OPEN, MERGED or CLOSED. */
  state: string;
  isDraft: boolean;
  reviewDecision: string | null;
  mergeStateStatus: string;
  /** When the PR last left draft; checks that started earlier ran on the draft. */
  readyAt: string | null;
  checks: (CheckRun | StatusContext)[];
};

// Statuses whose text says a person must act, such as Chromatic's "4 changes must be accepted as
// baselines" or a service waiting for a review or an approval.
const PERSON_STATUS =
  /must be (accepted|reviewed|approved)|waiting for (a )?(review|approval)|requires? (a )?(review|approval)/i;
const FAILED_CONCLUSIONS = new Set(["FAILURE", "TIMED_OUT", "STARTUP_FAILURE", "CANCELLED"]);
const MERGE_STATE_ITEMS: Record<string, Omit<Item, "name">> = {
  DIRTY: { kind: "person", detail: "conflicts with the base branch; rebase needed" },
  BEHIND: { kind: "person", detail: "behind the base branch, which this repository requires" },
  BLOCKED: { kind: "person", detail: "blocked by a repository rule" },
  UNKNOWN: { kind: "running", detail: "GitHub is still computing whether it can merge" },
};

/** Only a check's newest run counts; reruns and the ready run replace the draft run. */
function newestRuns(runs: CheckRun[]): CheckRun[] {
  const byName = new Map<string, CheckRun>();
  for (const run of runs) {
    const seen = byName.get(run.name);
    if (!seen || run.databaseId > seen.databaseId) byName.set(run.name, run);
  }
  return [...byName.values()];
}

/** What the run waits on, or `null` when it passed. */
function judgeRun(run: CheckRun, readyAt: string | null): Omit<Item, "name"> | null {
  const url = run.detailsUrl ?? undefined;
  if (run.status === "WAITING" || run.conclusion === "ACTION_REQUIRED") {
    return { kind: "person", detail: "waits for an approval", url };
  }
  if (run.status !== "COMPLETED") return { kind: "running", detail: run.status.toLowerCase(), url };
  if (FAILED_CONCLUSIONS.has(run.conclusion ?? "")) {
    return { kind: "failed", detail: (run.conclusion ?? "").toLowerCase(), url };
  }
  const skipped = run.conclusion === "SKIPPED" || run.conclusion === "NEUTRAL";
  if (skipped && readyAt && (run.startedAt ?? "") < readyAt) {
    return { kind: "running", detail: "skipped on the draft; waiting for the ready run", url };
  }
  return null;
}

function judgeStatus(status: StatusContext): Omit<Item, "name"> | null {
  const detail = status.description ?? status.state.toLowerCase();
  const url = status.targetUrl ?? undefined;
  if (status.state === "PENDING" || status.state === "EXPECTED") {
    return { kind: PERSON_STATUS.test(detail) ? "person" : "running", detail, url };
  }
  if (status.state === "FAILURE" || status.state === "ERROR")
    return { kind: "failed", detail, url };
  return null;
}

/** Whether the repository marks any check required; when not, every check counts as required. */
export function requiredKnown(pr: Pr): boolean {
  return pr.checks.some((check) => check.isRequired);
}

/** The PR's unfinished items, each labelled with who it waits on. */
export function waitingOn(pr: Pr): Item[] {
  const items: Item[] = [];
  const known = requiredKnown(pr);

  if (pr.state === "MERGED") return items;
  if (pr.state === "CLOSED") return [{ kind: "person", name: "state", detail: "the PR is closed" }];
  if (pr.isDraft) items.push({ kind: "person", name: "draft", detail: "the PR is a draft" });
  if (pr.reviewDecision === "REVIEW_REQUIRED" || pr.reviewDecision === "CHANGES_REQUESTED") {
    items.push({ kind: "person", name: "review", detail: pr.reviewDecision.toLowerCase() });
  }
  const runs = newestRuns(pr.checks.filter((check) => check.__typename === "CheckRun"));
  const statuses = pr.checks.filter((check) => check.__typename === "StatusContext");
  const judged = [
    // A draft run's skip only matters for a check the merge needs.
    ...runs.map((run) => ({
      check: run,
      name: run.name,
      item: judgeRun(run, run.isRequired || !known ? pr.readyAt : null),
    })),
    ...statuses.map((status) => ({
      check: status,
      name: status.context,
      item: judgeStatus(status),
    })),
  ];

  for (const { check, name, item } of judged) {
    if (!item) continue;
    items.push({ ...item, name, kind: check.isRequired || !known ? item.kind : "info" });
  }

  // GitHub also reports BLOCKED for a draft, a missing review or an unfinished required check;
  // only when none of those explain it is a rule the agent can't see blocking the merge.
  const explained = items.some((item) => item.kind !== "info");
  const mergeState = MERGE_STATE_ITEMS[pr.mergeStateStatus];
  if (mergeState && !(pr.mergeStateStatus === "BLOCKED" && explained)) {
    items.push({ name: "merge state", ...mergeState });
  }

  return items;
}

/** Person first, since a failure or a running check can wait while the user acts. */
export function verdictOf(items: Item[]): Verdict {
  const order = ["person", "failed", "running"] as const;
  return order.find((kind) => items.some((item) => item.kind === kind)) ?? "ready";
}

const QUERY = `query($owner:String!,$name:String!,$n:Int!){repository(owner:$owner,name:$name){pullRequest(number:$n){
  state isDraft mergeStateStatus reviewDecision
  timelineItems(itemTypes:[READY_FOR_REVIEW_EVENT],last:1){nodes{... on ReadyForReviewEvent{createdAt}}}
  commits(last:1){nodes{commit{statusCheckRollup{contexts(first:100){nodes{__typename
    ... on CheckRun{databaseId name status conclusion startedAt detailsUrl isRequired(pullRequestNumber:$n)}
    ... on StatusContext{context state description targetUrl isRequired(pullRequestNumber:$n)}}}}}}}}}}`;

type Response = {
  data: {
    repository: {
      pullRequest: {
        state: string;
        isDraft: boolean;
        mergeStateStatus: string;
        reviewDecision: string | null;
        timelineItems: { nodes: { createdAt: string }[] };
        commits: {
          nodes: { commit: { statusCheckRollup: { contexts: { nodes: Pr["checks"] } } | null } }[];
        };
      };
    };
  };
};

export function parsePr(response: Response): Pr {
  const pr = response.data.repository.pullRequest;
  return {
    state: pr.state,
    isDraft: pr.isDraft,
    reviewDecision: pr.reviewDecision,
    mergeStateStatus: pr.mergeStateStatus,
    readyAt: pr.timelineItems.nodes.at(-1)?.createdAt ?? null,
    checks: pr.commits.nodes[0]?.commit.statusCheckRollup?.contexts.nodes ?? [],
  };
}

function gh(args: string[]): string {
  return execFileSync("gh", args, { encoding: "utf8", stdio: ["ignore", "pipe", "inherit"] });
}

/** The repository and PR number from a PR URL, `--repo`, or the current checkout. */
function resolveTarget(target: string, repo: string | undefined): [string, string, number] {
  const url = target.match(/github\.com\/([^/]+)\/([^/]+)\/pull\/(\d+)/);
  if (url) return [url[1]!, url[2]!, Number(url[3])];
  const nameWithOwner =
    repo ?? gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).trim();
  const [owner, name] = nameWithOwner.split("/");
  return [owner!, name!, Number(target)];
}

function main(): void {
  const [target, ...rest] = process.argv.slice(2);
  if (!target) {
    console.error("usage: node pr-waiting-on.ts <PR number or URL> [--repo owner/name]");
    process.exit(64);
  }
  const repo = rest[0] === "--repo" ? rest[1] : undefined;
  const [owner, name, number] = resolveTarget(target, repo);

  const response: Response = JSON.parse(
    gh([
      "api",
      "graphql",
      "-f",
      `query=${QUERY}`,
      "-f",
      `owner=${owner}`,
      "-f",
      `name=${name}`,
      "-F",
      `n=${number}`,
    ]),
  );
  const pr = parsePr(response);

  const items = waitingOn(pr);
  for (const item of items) {
    console.log([item.kind, item.name, item.detail, item.url].filter(Boolean).join("\t"));
  }
  if (!requiredKnown(pr)) console.log("required: unknown");
  const verdict = verdictOf(items);
  console.log(`verdict: ${verdict}`);
  process.exitCode = verdict === "person" ? 2 : verdict === "failed" ? 1 : 0;
}

if (import.meta.main) main();
