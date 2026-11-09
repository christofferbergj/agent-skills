import assert from "node:assert/strict";
import { test } from "node:test";

import {
  type CheckRun,
  type Pr,
  type StatusContext,
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
    checks,
    ...overrides,
  };
}

function run(name: string, fields: Partial<CheckRun> = {}): CheckRun {
  return {
    __typename: "CheckRun",
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

test("Chromatic baselines waiting for acceptance wait on a person even when every required check passed", () => {
  const { verdict } = judge(
    pr([run("Unit"), status("PENDING", "4 changes must be accepted as baselines")]),
  );
  assert.equal(verdict, "person");
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
      status("PENDING", "Waiting for review"),
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
