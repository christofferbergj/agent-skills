import assert from "node:assert/strict";
import { test } from "node:test";

import { type CommitStatus, verdictOf, waitingOn } from "./pr-waiting-on.ts";

const ready = { isDraft: false, reviewDecision: "", statusCheckRollup: [] };

function status(state: string, description: string): CommitStatus {
  return { context: "UI Tests: Dashboard", state, description, target_url: null };
}

test("Chromatic baselines waiting for acceptance wait on a person", () => {
  const items = waitingOn(ready, [status("pending", "4 changes must be accepted as baselines")]);
  assert.equal(verdictOf(items), "person");
});

test("Chromatic still running waits only on automation", () => {
  const items = waitingOn(ready, [status("pending", "Running 23 tests…")]);
  assert.equal(verdictOf(items), "running");
});

test("a person outranks a check that is still running", () => {
  const items = waitingOn(
    {
      ...ready,
      statusCheckRollup: [
        { __typename: "CheckRun", name: "E2E", status: "IN_PROGRESS", conclusion: "" },
      ],
    },
    [status("pending", "Waiting for review")],
  );
  assert.equal(verdictOf(items), "person");
});

test("a deployment waiting for approval waits on a person", () => {
  const items = waitingOn(
    {
      ...ready,
      statusCheckRollup: [
        { __typename: "CheckRun", name: "Deploy", status: "WAITING", conclusion: "" },
      ],
    },
    [],
  );
  assert.equal(verdictOf(items), "person");
});

test("a failed check is reported as failed", () => {
  const items = waitingOn(
    {
      ...ready,
      statusCheckRollup: [
        { __typename: "CheckRun", name: "Unit", status: "COMPLETED", conclusion: "FAILURE" },
      ],
    },
    [],
  );
  assert.equal(verdictOf(items), "failed");
});

test("passed, skipped and cancelled checks leave the PR clear", () => {
  const items = waitingOn(
    {
      ...ready,
      statusCheckRollup: [
        { __typename: "CheckRun", name: "Unit", status: "COMPLETED", conclusion: "SUCCESS" },
        { __typename: "CheckRun", name: "PDF", status: "COMPLETED", conclusion: "SKIPPED" },
        { __typename: "CheckRun", name: "Old run", status: "COMPLETED", conclusion: "CANCELLED" },
      ],
    },
    [status("success", "Tests passed")],
  );
  assert.equal(verdictOf(items), "clear");
});
