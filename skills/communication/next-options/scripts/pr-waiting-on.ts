/**
 * Says what a PR's merge waits on, so an agent watching a PR merges it once CI is green, and hands
 * it back when only a person can move it, instead of waiting for a status that never finishes.
 *
 * usage: node pr-waiting-on.ts <PR number or URL> [--repo owner/name]
 *
 * Every check run on the PR's head must pass, whether or not the repository requires it. A run only
 * passes on the ready PR: a check skipped while the PR was a draft is still running, and so is a
 * required check with no run yet. A merged PR reads `ready`.
 *
 * Prints one line per unfinished item, then a last `verdict:` line:
 *   person   something waits on a person; hand the PR back (exit 2)
 *   failed   a check failed; fix it or report it (exit 1)
 *   running  a check is still running; keep the watch (exit 0)
 *   ready    CI is green on this head and nothing waits on a person; the PR can merge (exit 0)
 * `info` lines are pending commit statuses from outside services the repository doesn't require,
 * such as a visual-test service stopped by its billing plan. They never change the verdict.
 * `required: unknown` means neither the base branch's rules nor the checks show a required check,
 * so every status counts as required too.
 * While the verdict is `running`, an `auto-merge:` line says whether GitHub's auto-merge, which
 * waits only for required checks, would wait for everything still running:
 *   safe         only required checks remain; arming auto-merge is safe
 *   wait         a check the repository doesn't require is still running
 *   not allowed  the repository has auto-merge turned off
 */
import { execFileSync } from "node:child_process";

export type Verdict = "person" | "failed" | "running" | "ready";
export type Item = {
  kind: Exclude<Verdict, "ready"> | "info";
  name: string;
  detail: string;
  url?: string;
  /** Whether GitHub's merge rules wait for this item. */
  required: boolean;
};
export type AutoMerge = "safe" | "wait" | "not allowed";

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
  /** The Actions workflow that created the run, when one did. */
  workflow?: string | null;
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
  /** People or teams asked to review who haven't yet; bots are left out. */
  pendingReviewers: string[];
  mergeStateStatus: string;
  autoMergeAllowed: boolean;
  /** Checks on the head beyond the ones fetched, which the script can't judge. */
  unseenChecks: number;
  /** When the PR last left draft; checks that started earlier ran on the draft. */
  readyAt: string | null;
  /** Check names the base branch's protection or rulesets require, when the token can read them. */
  requiredNames: string[];
  checks: (CheckRun | StatusContext)[];
};

// Statuses whose text says a person must act, such as Chromatic's "4 changes must be accepted as
// baselines" or a service waiting for a review or an approval.
const PERSON_STATUS =
  /must be (accepted|reviewed|approved)|waiting for (a )?(review|approval)|requires? (a )?(review|approval)/i;
const FAILED_CONCLUSIONS = new Set(["FAILURE", "TIMED_OUT", "STARTUP_FAILURE", "CANCELLED"]);
const MERGE_STATE_ITEMS: Record<string, Omit<Item, "name" | "required">> = {
  DIRTY: { kind: "person", detail: "conflicts with the base branch; rebase needed" },
  BEHIND: { kind: "person", detail: "behind the base branch, which this repository requires" },
  BLOCKED: { kind: "person", detail: "blocked by a repository rule" },
  UNKNOWN: { kind: "running", detail: "GitHub is still computing whether it can merge" },
};

type Judgement = Omit<Item, "name" | "required">;

/** Only a check's newest run counts; reruns and the ready run replace the draft run. */
function newestRuns(runs: CheckRun[]): CheckRun[] {
  const byName = new Map<string, CheckRun>();
  for (const run of runs) {
    const seen = byName.get(run.name);
    if (!seen || run.databaseId > seen.databaseId) byName.set(run.name, run);
  }
  return [...byName.values()];
}

/**
 * A matrix job skipped on the draft keeps its unexpanded name, such as `E2E (${{ matrix.label }})`,
 * so no later run shares it. Its expanded jobs from the same workflow, such as `E2E (chromium)`,
 * replace it once one has started since the PR left draft.
 */
function expandedSince(run: CheckRun, sinceReady: CheckRun[]): boolean {
  const parts = run.name.split(/\$\{\{.*?\}\}/);
  if (parts.length < 2 || !run.workflow || parts.join("").trim() === "") return false;
  const escape = (text: string) => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const expanded = new RegExp(`^${parts.map(escape).join(".+")}$`);
  return sinceReady.some(
    (later) =>
      later.workflow === run.workflow && later.name !== run.name && expanded.test(later.name),
  );
}

/**
 * What the run waits on, or `null` when it passed. `draftSkipPending` says a skip on the draft
 * still stands in for a run the ready PR hasn't started.
 */
function judgeRun(run: CheckRun, draftSkipPending: boolean): Judgement | null {
  const url = run.detailsUrl ?? undefined;
  if (run.status === "WAITING" || run.conclusion === "ACTION_REQUIRED") {
    return { kind: "person", detail: "waits for an approval", url };
  }
  if (run.status !== "COMPLETED") return { kind: "running", detail: run.status.toLowerCase(), url };
  if (FAILED_CONCLUSIONS.has(run.conclusion ?? "")) {
    return { kind: "failed", detail: (run.conclusion ?? "").toLowerCase(), url };
  }
  const skipped = run.conclusion === "SKIPPED" || run.conclusion === "NEUTRAL";
  if (skipped && draftSkipPending) {
    return { kind: "running", detail: "skipped on the draft; waiting for the ready run", url };
  }
  return null;
}

/** A status nobody requires that is only pending becomes `info`, since it may never finish. */
function judgeStatus(status: StatusContext, counts: boolean): Judgement | null {
  const detail = status.description ?? status.state.toLowerCase();
  const url = status.targetUrl ?? undefined;
  if (status.state === "PENDING" || status.state === "EXPECTED") {
    if (PERSON_STATUS.test(detail)) return { kind: "person", detail, url };
    return { kind: counts ? "running" : "info", detail, url };
  }
  if (status.state === "FAILURE" || status.state === "ERROR") {
    return { kind: "failed", detail, url };
  }
  return null;
}

/** Whether the base branch or any check shows a required check. */
export function requiredKnown(pr: Pr): boolean {
  return pr.requiredNames.length > 0 || pr.checks.some((check) => check.isRequired);
}

function checkName(check: CheckRun | StatusContext): string {
  return check.__typename === "CheckRun" ? check.name : check.context;
}

/** The PR's unfinished items, each labelled with who it waits on. */
export function waitingOn(pr: Pr): Item[] {
  if (pr.state === "MERGED") return [];
  if (pr.state === "CLOSED") {
    return [{ kind: "person", name: "state", detail: "the PR is closed", required: true }];
  }

  const items: Item[] = [];
  if (pr.isDraft) {
    items.push({ kind: "person", name: "draft", detail: "the PR is a draft", required: true });
  }
  if (pr.reviewDecision === "REVIEW_REQUIRED" || pr.reviewDecision === "CHANGES_REQUESTED") {
    const detail = pr.reviewDecision.toLowerCase();
    items.push({ kind: "person", name: "review", detail, required: true });
  }
  for (const reviewer of pr.pendingReviewers) {
    items.push({
      kind: "person",
      name: "review",
      detail: `requested from ${reviewer}`,
      required: true,
    });
  }
  if (pr.unseenChecks > 0) {
    const detail = `${pr.unseenChecks} more checks than the script reads; check them by hand`;
    items.push({ kind: "person", name: "checks", detail, required: true });
  }

  const known = requiredKnown(pr);
  const required = (check: CheckRun | StatusContext) =>
    check.isRequired || pr.requiredNames.includes(checkName(check));
  const runs = pr.checks.filter((check) => check.__typename === "CheckRun");
  const readyAt = pr.readyAt;
  const sinceReady = runs.filter(
    (run) => readyAt !== null && (run.startedAt === null || run.startedAt >= readyAt),
  );

  for (const run of newestRuns(runs)) {
    const ranOnDraft = readyAt !== null && (run.startedAt ?? "") < readyAt;
    const draftSkipPending = ranOnDraft && !expandedSince(run, sinceReady);
    const item = judgeRun(run, draftSkipPending);
    // GitHub counts a skipped required check as passed, so it won't wait for the ready run.
    const waitedFor = required(run) && !(draftSkipPending && run.status === "COMPLETED");
    if (item) items.push({ ...item, name: run.name, required: waitedFor });
  }
  for (const status of pr.checks.filter((check) => check.__typename === "StatusContext")) {
    const item = judgeStatus(status, required(status) || !known);
    if (item) items.push({ ...item, name: status.context, required: required(status) });
  }

  const reported = new Set(pr.checks.map(checkName));
  for (const name of pr.requiredNames) {
    if (!reported.has(name)) {
      items.push({ kind: "running", name, detail: "required; no run yet", required: true });
    }
  }

  // GitHub also reports BLOCKED for a draft, a missing review or an unfinished required check;
  // only when none of those explain it is a rule the agent can't see blocking the merge.
  const explained = items.some((item) => item.kind !== "info" && item.required);
  const mergeState = MERGE_STATE_ITEMS[pr.mergeStateStatus];
  if (mergeState && !(pr.mergeStateStatus === "BLOCKED" && explained)) {
    items.push({ ...mergeState, name: "merge state", required: true });
  }

  return items;
}

/** Person first, since a failure or a running check can wait while the user acts. */
export function verdictOf(items: Item[]): Verdict {
  const order = ["person", "failed", "running"] as const;
  return order.find((kind) => items.some((item) => item.kind === kind)) ?? "ready";
}

/** Whether arming auto-merge now would wait for everything still running; `null` unless running. */
export function autoMergeOf(pr: Pr, items: Item[]): AutoMerge | null {
  if (verdictOf(items) !== "running") return null;
  if (!pr.autoMergeAllowed) return "not allowed";
  const running = items.filter((item) => item.kind === "running");
  return running.every((item) => item.required) ? "safe" : "wait";
}

const QUERY = `query($owner:String!,$name:String!,$n:Int!){repository(owner:$owner,name:$name){
  autoMergeAllowed
  pullRequest(number:$n){
  state isDraft mergeStateStatus reviewDecision
  reviewRequests(first:50){nodes{requestedReviewer{__typename ... on User{login} ... on Team{slug}}}}
  baseRef{branchProtectionRule{requiredStatusCheckContexts}
    rules(first:50){nodes{parameters{... on RequiredStatusChecksParameters{requiredStatusChecks{context}}}}}}
  timelineItems(itemTypes:[READY_FOR_REVIEW_EVENT],last:1){nodes{... on ReadyForReviewEvent{createdAt}}}
  commits(last:1){nodes{commit{statusCheckRollup{contexts(first:100){totalCount nodes{__typename
    ... on CheckRun{databaseId name status conclusion startedAt detailsUrl isRequired(pullRequestNumber:$n)
      checkSuite{workflowRun{workflow{name}}}}
    ... on StatusContext{context state description targetUrl isRequired(pullRequestNumber:$n)}}}}}}}}}}`;

type ResponseCheck =
  | (Omit<CheckRun, "workflow"> & {
      checkSuite?: { workflowRun: { workflow: { name: string } } | null } | null;
    })
  | StatusContext;

type Response = {
  data: {
    repository: {
      autoMergeAllowed: boolean;
      pullRequest: {
        baseRef: {
          branchProtectionRule: { requiredStatusCheckContexts: string[] } | null;
          rules: {
            nodes: { parameters: { requiredStatusChecks?: { context: string }[] } | null }[];
          };
        } | null;
        state: string;
        isDraft: boolean;
        mergeStateStatus: string;
        reviewDecision: string | null;
        reviewRequests: {
          nodes: {
            requestedReviewer: { __typename: string; login?: string; slug?: string } | null;
          }[];
        };
        timelineItems: { nodes: { createdAt: string }[] };
        commits: {
          nodes: {
            commit: {
              statusCheckRollup: {
                contexts: { totalCount: number; nodes: ResponseCheck[] };
              } | null;
            };
          }[];
        };
      };
    };
  };
};

export function parsePr(response: Response): Pr {
  const repository = response.data.repository;
  const pr = repository.pullRequest;
  const fromRules = (pr.baseRef?.rules.nodes ?? []).flatMap(
    (rule) => rule.parameters?.requiredStatusChecks?.map((check) => check.context) ?? [],
  );
  const fromProtection = pr.baseRef?.branchProtectionRule?.requiredStatusCheckContexts ?? [];
  const contexts = pr.commits.nodes[0]?.commit.statusCheckRollup?.contexts;
  const nodes = contexts?.nodes ?? [];
  const pendingReviewers = pr.reviewRequests.nodes.flatMap(({ requestedReviewer: who }) =>
    who?.__typename === "User" || who?.__typename === "Team" ? [who.login ?? who.slug ?? ""] : [],
  );
  return {
    state: pr.state,
    isDraft: pr.isDraft,
    reviewDecision: pr.reviewDecision,
    pendingReviewers,
    mergeStateStatus: pr.mergeStateStatus,
    autoMergeAllowed: repository.autoMergeAllowed,
    unseenChecks: (contexts?.totalCount ?? 0) - nodes.length,
    readyAt: pr.timelineItems.nodes.at(-1)?.createdAt ?? null,
    requiredNames: [...new Set([...fromProtection, ...fromRules])],
    checks: nodes.map((node) => {
      if (node.__typename !== "CheckRun") return node;
      const { checkSuite, ...run } = node;
      return { ...run, workflow: checkSuite?.workflowRun?.workflow.name ?? null };
    }),
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
  const autoMerge = autoMergeOf(pr, items);
  if (autoMerge) console.log(`auto-merge: ${autoMerge}`);
  const verdict = verdictOf(items);
  console.log(`verdict: ${verdict}`);
  process.exitCode = verdict === "person" ? 2 : verdict === "failed" ? 1 : 0;
}

if (import.meta.main) main();
