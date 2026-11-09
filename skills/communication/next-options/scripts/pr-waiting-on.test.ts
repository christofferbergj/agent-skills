import assert from "node:assert/strict";
import { test } from "node:test";

import {
  type CheckRun,
  type Pr,
  type StatusContext,
  parsePr,
  requiredKnown,
  verdictOf,
  waitingOn,
} from "./pr-waiting-on.ts";

const READY_AT = "2026-11-09T13:57:30Z";
const BEFORE_READY = "2026-11-09T13:56:04Z";
const AFTER_READY = "2026-11-09T14:02:33Z";

function pr(checks: Pr["checks"], overrides: Partial<Pr> = {}): Pr {
  return {
    state: "OPEN",
    isDraft: false,
    reviewDecision: null,
    pendingReviewers: [],
    mergeStateStatus: "CLEAN",
    unseenChecks: 0,
    readyAt: null,
    requiredNames: [],
    checks,
    ...overrides,
  };
}

let nextRunId = 1;

/** Each call creates a newer run, as GitHub numbers them. */
function run(name: string, fields: Partial<CheckRun> = {}): CheckRun {
  return {
    __typename: "CheckRun",
    databaseId: nextRunId++,
    name,
    status: "COMPLETED",
    conclusion: "SUCCESS",
    startedAt: AFTER_READY,
    isRequired: true,
    ...fields,
  };
}

function status(state: string, description: string, isRequired = false): StatusContext {
  return {
    __typename: "StatusContext",
    context: "UI Tests: Dashboard",
    state,
    description,
    isRequired,
  };
}

function judge(input: Pr) {
  const items = waitingOn(input);
  return { items, verdict: verdictOf(items) };
}

const RUNNING = { status: "IN_PROGRESS", conclusion: null };

test("CI green on the ready run makes the PR ready, despite draft skips and a stalled outside status", () => {
  const { items, verdict } = judge(
    pr(
      [
        run("E2E", { conclusion: "SKIPPED", startedAt: BEFORE_READY }),
        run("E2E"),
        run("Unit", { conclusion: "SKIPPED", startedAt: BEFORE_READY, isRequired: false }),
        run("Unit", { isRequired: false }),
        status("PENDING", "Update your plan to resume testing"),
      ],
      { readyAt: READY_AT, mergeStateStatus: "UNSTABLE" },
    ),
  );
  assert.equal(verdict, "ready");
  assert.deepEqual(
    items.map((item) => [item.kind, item.name]),
    [["info", "UI Tests: Dashboard"]],
  );
});

test("a check the repository doesn't require still has to pass", () => {
  const unit = (fields: Partial<CheckRun>) => run("Unit", { isRequired: false, ...fields });
  assert.equal(judge(pr([run("E2E"), unit({ conclusion: "FAILURE" })])).verdict, "failed");
  assert.equal(judge(pr([run("E2E"), unit(RUNNING)])).verdict, "running");
  assert.equal(
    judge(pr([run("E2E"), unit({ status: "WAITING", conclusion: null })])).verdict,
    "person",
  );
});

test("a check still running on the ready run keeps the PR running", () => {
  const draft = run("E2E", { conclusion: "SKIPPED", startedAt: BEFORE_READY });
  assert.equal(judge(pr([draft, run("E2E", RUNNING)], { readyAt: READY_AT })).verdict, "running");
});

test("a draft run's skip or neutral result doesn't count as a pass before the ready run reports", () => {
  for (const conclusion of ["SKIPPED", "NEUTRAL"]) {
    const { items, verdict } = judge(
      pr([run("E2E", { conclusion, startedAt: BEFORE_READY })], { readyAt: READY_AT }),
    );
    assert.equal(verdict, "running", conclusion);
    assert.match(items[0]!.detail, /draft/);
  }
});

test("a check skipped on a PR that was never a draft passes", () => {
  const skipped = run("PDF", { conclusion: "SKIPPED", startedAt: BEFORE_READY });
  assert.equal(judge(pr([skipped])).verdict, "ready");
});

test("a rerun replaces the older run, even before it starts or within the same second", () => {
  const passed = run("Unit");
  const queued = run("Unit", { status: "QUEUED", conclusion: null, startedAt: null });
  assert.equal(judge(pr([passed, queued])).verdict, "running");
  assert.equal(judge(pr([run("Unit"), run("Unit", { conclusion: "FAILURE" })])).verdict, "failed");
  const rerun = pr([
    run("Unit", { conclusion: "CANCELLED", startedAt: BEFORE_READY }),
    run("Unit"),
  ]);
  assert.equal(judge(rerun).verdict, "ready");
  assert.equal(judge(pr([run("Unit", { conclusion: "CANCELLED" })])).verdict, "failed");
});

test("jobs with the same name in different workflows or events are different checks", () => {
  const failing = run("test", { conclusion: "FAILURE", workflow: "Package tests" });
  assert.equal(judge(pr([failing, run("test", { workflow: "Docs" })])).verdict, "failed");
  const onPush = run("test", { conclusion: "FAILURE", workflow: "CI", event: "push" });
  const onPr = run("test", { workflow: "CI", event: "pull_request" });
  assert.equal(judge(pr([onPush, onPr])).verdict, "failed");
});

test("an unfinished workflow keeps the PR running, since jobs waiting on others have no run yet", () => {
  const suite = (status: string) => ({ id: 7, status });
  const passed = run("Playwright", {
    workflow: "CI",
    isRequired: false,
    suite: suite("IN_PROGRESS"),
  });
  const { items, verdict } = judge(pr([passed]));
  assert.equal(verdict, "running");
  assert.deepEqual(
    items.map((item) => item.name),
    ["CI"],
  );

  const finished = run("Playwright", {
    workflow: "CI",
    isRequired: false,
    suite: suite("COMPLETED"),
  });
  assert.equal(judge(pr([finished])).verdict, "ready");
});

test("an outside status waiting on a person, or failing, blocks the PR whether required or not", () => {
  const baselines = status("PENDING", "4 changes must be accepted as baselines");
  assert.equal(judge(pr([run("Unit"), baselines])).verdict, "person");
  assert.equal(judge(pr([run("Unit"), status("FAILURE", "Deploy failed")])).verdict, "failed");
  assert.equal(judge(pr([run("Unit"), status("ERROR", "Build errored")])).verdict, "failed");
});

test("a required outside status that hasn't reported keeps the PR running", () => {
  assert.equal(judge(pr([run("Unit"), status("EXPECTED", "", true)])).verdict, "running");
  assert.equal(judge(pr([run("Unit"), status("PENDING", "Running", true)])).verdict, "running");
});

test("a person outranks a check that is still running", () => {
  const review = status("PENDING", "Waiting for review");
  assert.equal(judge(pr([run("E2E", RUNNING), review])).verdict, "person");
});

test("a draft, a requested review, conflicts, or an unexplained blocking rule wait on a person", () => {
  const passing = [run("Unit")];
  assert.equal(judge(pr(passing, { isDraft: true })).verdict, "person");
  assert.equal(judge(pr(passing, { reviewDecision: "REVIEW_REQUIRED" })).verdict, "person");
  assert.equal(judge(pr(passing, { reviewDecision: "CHANGES_REQUESTED" })).verdict, "person");
  for (const mergeStateStatus of ["DIRTY", "BEHIND", "BLOCKED"]) {
    assert.equal(judge(pr(passing, { mergeStateStatus })).verdict, "person", mergeStateStatus);
  }
});

test("a person asked to review, or checks the script can't read, wait on a person", () => {
  assert.equal(judge(pr([run("Unit")], { pendingReviewers: ["alice"] })).verdict, "person");
  assert.equal(judge(pr([run("Unit")], { unseenChecks: 3 })).verdict, "person");
});

test("a blocked merge state that an unfinished required check explains adds no item of its own", () => {
  const failing = judge(
    pr([run("Unit", { conclusion: "FAILURE" })], { mergeStateStatus: "BLOCKED" }),
  );
  assert.deepEqual(
    failing.items.map((item) => item.name),
    ["Unit"],
  );
  const missing = judge(
    pr([run("Code quality")], {
      requiredNames: ["Code quality", "E2E"],
      mergeStateStatus: "BLOCKED",
    }),
  );
  assert.equal(missing.verdict, "running");
  assert.deepEqual(
    missing.items.map((item) => [item.name, item.detail]),
    [["E2E", "required; no run yet"]],
  );
});

test("a merge state GitHub is still computing keeps the PR running", () => {
  assert.equal(judge(pr([run("Unit")], { mergeStateStatus: "UNKNOWN" })).verdict, "running");
});

test("a merged PR has nothing left to wait on, and a closed one waits on a person", () => {
  const merged = pr([run("Unit")], { state: "MERGED", mergeStateStatus: "UNKNOWN" });
  assert.equal(judge(merged).verdict, "ready");
  assert.equal(judge(pr([run("Unit")], { state: "CLOSED" })).verdict, "person");
});

test("without any required check, a pending outside status counts as running", () => {
  const pending = pr([run("Unit", { isRequired: false }), status("PENDING", "Running 23 tests…")]);
  assert.equal(requiredKnown(pending), false);
  assert.equal(judge(pending).verdict, "running");
  const passing = pr([run("Unit", { isRequired: false }), status("SUCCESS", "Tests passed")]);
  assert.equal(judge(passing).verdict, "ready");
});

test("a matrix job's draft skip is replaced only by its own expanded jobs", () => {
  const template = (name: string) =>
    run(name, { conclusion: "SKIPPED", startedAt: BEFORE_READY, workflow: "CI" });
  const later = (name: string, fields: Partial<CheckRun> = {}) =>
    run(name, { workflow: "CI", ...fields });
  const ready = { readyAt: READY_AT };

  const suffix = template("E2E (${{ matrix.label }})");
  assert.equal(judge(pr([suffix, later("E2E (chromium)")], ready)).verdict, "ready");
  assert.deepEqual(
    judge(pr([suffix, later("E2E (chromium)", RUNNING)], ready)).items.map((item) => item.name),
    ["E2E (chromium)"],
  );
  assert.equal(judge(pr([suffix, later("Lint")], ready)).verdict, "running");

  const leading = template("${{ matrix.project }} E2E");
  assert.equal(judge(pr([leading, later("Lint")], ready)).verdict, "running");
  assert.equal(judge(pr([leading, later("Dashboard E2E")], ready)).verdict, "ready");

  assert.equal(judge(pr([template("E2E"), later("Lint")], ready)).verdict, "running");

  const onPr = run("E2E (${{ matrix.label }})", {
    conclusion: "SKIPPED",
    startedAt: BEFORE_READY,
    workflow: "CI",
    event: "pull_request",
  });
  const onPush = later("E2E (chromium)", { event: "push" });
  assert.equal(judge(pr([onPr, onPush], ready)).verdict, "running");
});

test("the GraphQL response gives the required names, the ready time, reviewers and each run's workflow", () => {
  const check = {
    __typename: "CheckRun" as const,
    databaseId: 1,
    name: "E2E",
    status: "COMPLETED",
    conclusion: "SKIPPED",
    startedAt: BEFORE_READY,
    isRequired: false,
    checkSuite: {
      databaseId: 7,
      status: "COMPLETED",
      workflowRun: { event: "pull_request", workflow: { name: "CI" } },
    },
  };
  const parsed = parsePr({
    data: {
      repository: {
        pullRequest: {
          baseRef: {
            branchProtectionRule: { requiredStatusCheckContexts: ["E2E"] },
            rules: { nodes: [{ parameters: { requiredStatusChecks: [{ context: "Lint" }] } }] },
          },
          state: "OPEN",
          isDraft: false,
          mergeStateStatus: "BLOCKED",
          reviewDecision: null,
          reviewRequests: {
            nodes: [
              { requestedReviewer: { __typename: "User", login: "alice" } },
              { requestedReviewer: { __typename: "Bot", login: "copilot" } },
              { requestedReviewer: { __typename: "Team", slug: "web" } },
            ],
          },
          timelineItems: { nodes: [{ createdAt: READY_AT }] },
          commits: {
            nodes: [
              { commit: { statusCheckRollup: { contexts: { totalCount: 101, nodes: [check] } } } },
            ],
          },
        },
      },
    },
  });
  assert.deepEqual(parsed.pendingReviewers, ["alice", "web"]);
  assert.equal(parsed.unseenChecks, 100);
  assert.deepEqual(parsed.requiredNames, ["E2E", "Lint"]);
  assert.deepEqual(
    [(parsed.checks[0] as CheckRun).workflow, (parsed.checks[0] as CheckRun).event],
    ["CI", "pull_request"],
  );
  assert.deepEqual((parsed.checks[0] as CheckRun).suite, { id: 7, status: "COMPLETED" });
  const { items } = judge({ ...parsed, pendingReviewers: [], unseenChecks: 0 });
  assert.deepEqual(
    items.map((item) => [item.name, item.detail]),
    [
      ["E2E", "skipped on the draft; waiting for the ready run"],
      ["Lint", "required; no run yet"],
    ],
  );
});
