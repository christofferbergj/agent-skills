/**
 * Says who a PR's unfinished checks wait on, so an agent watching a PR hands it back when only a
 * person can move it, such as accepting Chromatic baselines, instead of waiting for checks that
 * never finish on their own.
 *
 * usage: node pr-waiting-on.ts <PR number or URL> [--repo owner/name]
 *
 * Prints one line per unfinished item and a last `verdict:` line:
 *   person   something waits on a person; hand the PR back (exit 2)
 *   failed   a check failed; fix it or report it (exit 1)
 *   running  only automation is still running; keep the watch (exit 0)
 *   clear    nothing is unfinished (exit 0)
 */
import { execFileSync } from "node:child_process";

export type Verdict = "person" | "failed" | "running" | "clear";
export type Item = { kind: Exclude<Verdict, "clear">; name: string; detail: string; url?: string };

type CheckRun = {
  __typename: "CheckRun";
  name: string;
  status: string;
  conclusion: string;
  detailsUrl?: string;
};
type StatusContext = { __typename: "StatusContext"; context: string };
type Pr = {
  headRefOid: string;
  isDraft: boolean;
  reviewDecision: string;
  url: string;
  statusCheckRollup: (CheckRun | StatusContext)[];
};
export type CommitStatus = {
  context: string;
  state: string;
  description: string | null;
  target_url: string | null;
};

// Statuses whose text says a person must act, such as Chromatic's "4 changes must be accepted as
// baselines" or a service waiting for a review or an approval.
const PERSON_STATUS =
  /must be (accepted|reviewed|approved)|waiting for (a )?(review|approval)|requires? (a )?(review|approval)/i;
const FAILED_CONCLUSIONS = new Set(["FAILURE", "TIMED_OUT", "STARTUP_FAILURE"]);

function gh(args: string[]): string {
  return execFileSync("gh", args, { encoding: "utf8", stdio: ["ignore", "pipe", "inherit"] });
}

/** The PR's unfinished items, each labelled with who it waits on. */
export function waitingOn(pr: Omit<Pr, "headRefOid" | "url">, statuses: CommitStatus[]): Item[] {
  const items: Item[] = [];

  if (pr.isDraft) items.push({ kind: "person", name: "draft", detail: "the PR is a draft" });
  if (pr.reviewDecision === "REVIEW_REQUIRED" || pr.reviewDecision === "CHANGES_REQUESTED") {
    items.push({ kind: "person", name: "review", detail: pr.reviewDecision.toLowerCase() });
  }

  for (const check of pr.statusCheckRollup) {
    if (check.__typename !== "CheckRun") continue;
    const url = check.detailsUrl;
    if (check.status === "WAITING" || check.conclusion === "ACTION_REQUIRED") {
      items.push({ kind: "person", name: check.name, detail: "waits for an approval", url });
    } else if (check.status !== "COMPLETED") {
      items.push({ kind: "running", name: check.name, detail: check.status.toLowerCase(), url });
    } else if (FAILED_CONCLUSIONS.has(check.conclusion)) {
      items.push({ kind: "failed", name: check.name, detail: check.conclusion.toLowerCase(), url });
    }
  }

  for (const status of statuses) {
    const detail = status.description ?? status.state;
    const url = status.target_url ?? undefined;
    if (status.state === "pending") {
      const kind = PERSON_STATUS.test(detail) ? "person" : "running";
      items.push({ kind, name: status.context, detail, url });
    } else if (status.state === "failure" || status.state === "error") {
      items.push({ kind: "failed", name: status.context, detail, url });
    }
  }

  return items;
}

/** Person first, since a failure or a running check can wait while the user acts. */
export function verdictOf(items: Item[]): Verdict {
  const order: Verdict[] = ["person", "failed", "running"];
  return order.find((kind) => items.some((item) => item.kind === kind)) ?? "clear";
}

function main(): void {
  const [target, ...rest] = process.argv.slice(2);
  if (!target) {
    console.error("usage: node pr-waiting-on.ts <PR number or URL> [--repo owner/name]");
    process.exit(64);
  }
  const repoArgs = rest[0] === "--repo" && rest[1] ? ["--repo", rest[1]] : [];

  const pr: Pr = JSON.parse(
    gh([
      "pr",
      "view",
      target,
      ...repoArgs,
      "--json",
      "headRefOid,isDraft,reviewDecision,url,statusCheckRollup",
    ]),
  );
  const repo = new URL(pr.url).pathname.split("/").slice(1, 3).join("/");
  // The rollup leaves out a status's description, which is where Chromatic says it waits on a person.
  const statuses: CommitStatus[] = JSON.parse(
    gh(["api", `repos/${repo}/commits/${pr.headRefOid}/status`, "--jq", ".statuses"]),
  );

  const items = waitingOn(pr, statuses);
  for (const item of items) {
    console.log([item.kind, item.name, item.detail, item.url].filter(Boolean).join("\t"));
  }
  const verdict = verdictOf(items);
  console.log(`verdict: ${verdict}`);
  process.exitCode = verdict === "person" ? 2 : verdict === "failed" ? 1 : 0;
}

if (import.meta.main) main();
