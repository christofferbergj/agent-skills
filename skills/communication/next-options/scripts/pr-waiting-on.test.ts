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
    mergeStateStatus: "CLEAN",
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

test("required checks that passed on the ready run make the PR ready despite their skipped draft runs", () => {
  const { items, verdict } = judge(
    pr(
      [
        run("E2E", { conclusion: "SKIPPED", startedAt: BEFORE_READY }),
        run("E2E"),
        run("Code quality", { conclusion: "SKIPPED", startedAt: BEFORE_READY }),
        run("Code quality"),
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

test("a required check still running on the ready run keeps the PR running", () => {
  const { verdict } = judge(
    pr(
      [
        run("E2E", { conclusion: "SKIPPED", startedAt: BEFORE_READY }),
        run("E2E", { status: "IN_PROGRESS", conclusion: null }),
      ],
      { readyAt: READY_AT },
    ),
  );
  assert.equal(verdict, "running");
});

test("a draft run's skip doesn't count as a pass before the ready run reports", () => {
  const { items, verdict } = judge(
    pr([run("E2E", { conclusion: "SKIPPED", startedAt: BEFORE_READY })], { readyAt: READY_AT }),
  );
  assert.equal(verdict, "running");
  assert.match(items[0]!.detail, /draft/);
});

test("a neutral draft run of a required check doesn't count as a pass either", () => {
  const draftRun = run("E2E", { conclusion: "NEUTRAL", startedAt: BEFORE_READY });
  assert.equal(judge(pr([draftRun], { readyAt: READY_AT })).verdict, "running");
});

test("a required status that hasn't reported keeps the PR running, and an errored one fails it", () => {
  assert.equal(judge(pr([status("EXPECTED", "", true)])).verdict, "running");
  assert.equal(judge(pr([status("ERROR", "Build errored", true)])).verdict, "failed");
});

test("the PR's last ready-for-review time and its head's checks come from the GraphQL response", () => {
  const check = run("E2E", { conclusion: "SKIPPED", startedAt: BEFORE_READY });
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
          mergeStateStatus: "UNSTABLE",
          reviewDecision: null,
          timelineItems: { nodes: [{ createdAt: READY_AT }] },
          commits: { nodes: [{ commit: { statusCheckRollup: { contexts: { nodes: [check] } } } }] },
        },
      },
    },
  });
  assert.deepEqual(parsed.requiredNames, ["E2E", "Lint"]);
  assert.deepEqual(
    judge(parsed).items.map((item) => [item.name, item.detail]),
    [
      ["E2E", "skipped on the draft; waiting for the ready run"],
      ["Lint", "required; no run yet"],
    ],
  );
});

test("a required check with no run yet keeps the PR running, and explains a blocked merge state", () => {
  const { items, verdict } = judge(
    pr([run("Code quality", { isRequired: false })], {
      requiredNames: ["Code quality", "E2E"],
      mergeStateStatus: "BLOCKED",
    }),
  );
  assert.equal(verdict, "running");
  assert.deepEqual(
    items.map((item) => item.name),
    ["E2E"],
  );
});

test("an unrelated job in the same workflow doesn't replace a required check's draft skip", () => {
  const e2e = run("E2E", { conclusion: "SKIPPED", startedAt: BEFORE_READY, workflow: "CI" });
  const lint = run("Lint", { workflow: "CI", isRequired: false });
  assert.equal(judge(pr([e2e, lint], { readyAt: READY_AT })).verdict, "running");
});

test("a matrix name that starts with an expression is replaced only by jobs that fill it in", () => {
  const template = run("${{ matrix.project }} E2E", {
    conclusion: "SKIPPED",
    startedAt: BEFORE_READY,
    workflow: "CI",
  });
  const lint = run("Lint", { workflow: "CI", isRequired: false });
  assert.equal(judge(pr([template, lint], { readyAt: READY_AT })).verdict, "running");
  const dashboard = run("Dashboard E2E", { workflow: "CI" });
  assert.equal(judge(pr([template, dashboard], { readyAt: READY_AT })).verdict, "ready");
});

test("a matrix job's draft skip counts as replaced once its expanded jobs start after the PR left draft", () => {
  const template = run("E2E (${{ matrix.label }})", {
    conclusion: "SKIPPED",
    startedAt: BEFORE_READY,
    workflow: "CI",
  });
  const chromium = run("E2E (chromium)", {
    status: "IN_PROGRESS",
    conclusion: null,
    workflow: "CI",
  });
  assert.deepEqual(
    judge(pr([template, chromium], { readyAt: READY_AT })).items.map((item) => item.name),
    ["E2E (chromium)"],
  );
  const finished = run("E2E (chromium)", { workflow: "CI" });
  assert.equal(judge(pr([template, finished], { readyAt: READY_AT })).verdict, "ready");
  assert.equal(judge(pr([template], { readyAt: READY_AT })).verdict, "running");
});

test("a required check skipped on a PR that was never a draft passes", () => {
  assert.equal(
    judge(pr([run("PDF", { conclusion: "SKIPPED", startedAt: BEFORE_READY })])).verdict,
    "ready",
  );
});

test("a newer run that is still going replaces an older pass", () => {
  const { verdict } = judge(
    pr([
      run("E2E", { startedAt: BEFORE_READY }),
      run("E2E", { status: "QUEUED", conclusion: null }),
    ]),
  );
  assert.equal(verdict, "running");
});

test("a failed required check fails the PR", () => {
  assert.equal(judge(pr([run("Unit", { conclusion: "FAILURE" })])).verdict, "failed");
});

test("a cancelled required check fails the PR, but a cancelled run a rerun replaced doesn't", () => {
  assert.equal(judge(pr([run("Unit", { conclusion: "CANCELLED" })])).verdict, "failed");
  const rerun = pr([
    run("Unit", { conclusion: "CANCELLED", startedAt: BEFORE_READY }),
    run("Unit"),
  ]);
  assert.equal(judge(rerun).verdict, "ready");
});

test("a failed check the repository doesn't require is only information", () => {
  const { items, verdict } = judge(
    pr([run("Unit"), run("Lighthouse", { conclusion: "FAILURE", isRequired: false })]),
  );
  assert.equal(verdict, "ready");
  assert.deepEqual(
    items.map((item) => item.kind),
    ["info"],
  );
});

test("required Chromatic baselines waiting for acceptance wait on a person", () => {
  const { verdict } = judge(
    pr([run("Unit"), status("PENDING", "4 changes must be accepted as baselines", true)]),
  );
  assert.equal(verdict, "person");
});

test("a person's step on a check the merge doesn't need is only information", () => {
  const { items, verdict } = judge(
    pr([
      run("Unit"),
      status("PENDING", "4 changes must be accepted as baselines"),
      run("Deploy preview", { status: "WAITING", conclusion: null, isRequired: false }),
    ]),
  );
  assert.equal(verdict, "ready");
  assert.deepEqual(
    items.map((item) => item.kind),
    ["info", "info"],
  );
});

test("a rerun that hasn't started, or started in the same second, replaces the older run", () => {
  const queued = pr([
    run("Unit"),
    run("Unit", { status: "QUEUED", conclusion: null, startedAt: null }),
  ]);
  assert.equal(judge(queued).verdict, "running");
  const sameSecond = pr([run("Unit"), run("Unit", { conclusion: "FAILURE" })]);
  assert.equal(judge(sameSecond).verdict, "failed");
});

test("a deployment waiting for approval waits on a person", () => {
  assert.equal(
    judge(pr([run("Deploy", { status: "WAITING", conclusion: null })])).verdict,
    "person",
  );
});

test("a person outranks a required check that is still running", () => {
  const { verdict } = judge(
    pr([
      run("E2E", { status: "IN_PROGRESS", conclusion: null }),
      status("PENDING", "Waiting for review", true),
    ]),
  );
  assert.equal(verdict, "person");
});

test("a draft, a requested review, conflicts, or a blocking rule wait on a person", () => {
  const passing = [run("Unit")];
  assert.equal(judge(pr(passing, { isDraft: true })).verdict, "person");
  assert.equal(judge(pr(passing, { reviewDecision: "REVIEW_REQUIRED" })).verdict, "person");
  assert.equal(judge(pr(passing, { reviewDecision: "CHANGES_REQUESTED" })).verdict, "person");
  for (const mergeStateStatus of ["DIRTY", "BEHIND", "BLOCKED"]) {
    assert.equal(judge(pr(passing, { mergeStateStatus })).verdict, "person", mergeStateStatus);
  }
});

test("a blocked merge state that a failed required check explains adds no item of its own", () => {
  const { items } = judge(
    pr([run("Unit", { conclusion: "FAILURE" })], { mergeStateStatus: "BLOCKED" }),
  );
  assert.deepEqual(
    items.map((item) => item.name),
    ["Unit"],
  );
});

test("a merged PR has nothing left to wait on, and a closed one waits on a person", () => {
  assert.equal(
    judge(pr([run("Unit")], { state: "MERGED", mergeStateStatus: "UNKNOWN" })).verdict,
    "ready",
  );
  assert.equal(judge(pr([run("Unit")], { state: "CLOSED" })).verdict, "person");
});

test("a skipped draft run of a check the repository doesn't require is no item at all", () => {
  const optional = run("Matrix", {
    conclusion: "SKIPPED",
    startedAt: BEFORE_READY,
    isRequired: false,
  });
  assert.deepEqual(waitingOn(pr([run("Unit"), optional], { readyAt: READY_AT })), []);
});

test("a merge state GitHub is still computing keeps the PR running", () => {
  assert.equal(judge(pr([run("Unit")], { mergeStateStatus: "UNKNOWN" })).verdict, "running");
});

test("without any required check, every check counts as required", () => {
  const pending = pr([run("Unit", { isRequired: false }), status("PENDING", "Running 23 tests…")]);
  assert.equal(requiredKnown(pending), false);
  assert.equal(judge(pending).verdict, "running");

  const passing = pr([run("Unit", { isRequired: false }), status("SUCCESS", "Tests passed")]);
  assert.equal(judge(passing).verdict, "ready");
});
