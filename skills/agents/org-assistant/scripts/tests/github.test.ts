/** The GitHub source, through the CLI: the user's PRs, review requests, issues, other PRs, and releases. */
import assert from "node:assert/strict";
import { test } from "node:test";

import { Org, utc } from "./helpers.ts";
import type { Pr } from "./fakes.ts";

const RED = [{ status: "COMPLETED", conclusion: "FAILURE" }];
const GREEN = [{ status: "COMPLETED", conclusion: "SUCCESS" }];

function myPr(org: Org): Pr {
  const [pr] = org.world.github["example/web"]?.mine ?? [];
  assert.ok(pr);
  return pr;
}

test("red CI, a review request, and a new release each wake once", (t) => {
  const org = new Org(t);
  org.startDay();
  Object.assign(myPr(org), { statusCheckRollup: RED, updatedAt: utc("09:35") });
  const web = org.world.github["example/web"];
  const api = org.world.github["example/api"];
  assert.ok(web && api);
  web.requested = [{ number: 12, updatedAt: utc("09:36") }];
  api.releases?.unshift({ tagName: "v1.1.0", isDraft: false, publishedAt: utc("09:10") });
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.batch(), [
    "pr.ci_failed example/web#11",
    "pr.review_requested example/web#12",
    "release.new example/api@v1.1.0",
  ]);
  org.deliver();
  org.scan("11:05");
  assert.equal(org.sent().length, 2);
});

test("a PR of the user's opened since the last scan counts its state as new", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.github["example/web"]?.mine?.push({
    number: 13,
    isDraft: false,
    reviewDecision: "CHANGES_REQUESTED",
    updatedAt: utc("09:40"),
    statusCheckRollup: RED,
  });
  org.save();
  assert.deepEqual(org.found("10:05"), { "pr.ci_failed": 1, "pr.changes_requested": 1 });
});

test("red CI wakes again after a green run with the same PR timestamp", (t) => {
  const org = new Org(t);
  org.startDay();
  for (const [clock, checks] of [
    ["10:05", RED],
    ["11:05", GREEN],
    ["12:05", RED],
  ] as const) {
    myPr(org).statusCheckRollup = [...checks];
    org.save();
    org.scan(clock);
    if (org.pending().sent) org.deliver();
  }
  assert.equal(org.sent().length, 3);
});

test("an approval is pulse, and pending checks are not red", (t) => {
  const org = new Org(t);
  org.startDay();
  Object.assign(myPr(org), {
    reviewDecision: "APPROVED",
    statusCheckRollup: [{ status: "IN_PROGRESS", conclusion: "" }],
  });
  org.save();
  assert.deepEqual(org.found("10:05"), { "pr.approved": 1 });
  assert.equal(org.sent().length, 1);
});

test("an issue assigned again within a week wakes again", (t) => {
  const org = new Org(t);
  org.startDay();
  const issue = {
    number: 5,
    createdAt: utc("08:00"),
    updatedAt: utc("09:30"),
    assignees: [{ login: "me-login" }],
  };
  const web = org.world.github["example/web"];
  assert.ok(web);
  web.issues = [issue];
  org.save();
  org.scan("10:05");
  org.deliver();
  Object.assign(issue, { assignees: [], updatedAt: utc("10:30") });
  org.save();
  org.scan("11:05");
  Object.assign(issue, { assignees: [{ login: "me-login" }], updatedAt: utc("11:30") });
  org.save();
  org.scan("12:05");
  assert.deepEqual(
    org
      .sent()
      .slice(1)
      .map((sent) => org.kinds(sent)),
    [["issue.assigned example/web#5"], ["issue.assigned example/web#5"]],
  );
});

test("other people's new and closed PRs are pulse", (t) => {
  const org = new Org(t);
  org.startDay();
  const api = org.world.github["example/api"];
  assert.ok(api);
  api.open = [{ number: 22, createdAt: utc("09:30") }];
  org.save();
  assert.deepEqual(org.found("10:05"), { "pr.opened": 1, "pr.closed": 1 });
  assert.deepEqual(
    org.pending().gathered.map((item) => item.ref),
    ["example/api#22", "example/api#21"],
  );
});

test("a release a PR waits on wakes as awaited and names the PR", (t) => {
  const org = new Org(t);
  org.startDay();
  org.ledger(["waits", "example/web#11", "example/api"]);
  org.world.github["example/api"]?.releases?.unshift({
    tagName: "v1.2.0",
    isDraft: false,
    publishedAt: utc("09:30"),
  });
  org.save();
  org.scan("10:05");
  assert.deepEqual(org.batch(), ["release.awaited example/api@v1.2.0"]);
  assert.deepEqual(org.pending().sent?.items[0]?.detail, { prs: ["example/web#11"] });
});

test("gh failing on its credentials fails the source as an expired sign-in", (t) => {
  const org = new Org(t);
  org.startDay();
  org.world.fail = { github: "on" };
  org.save();
  org.scan("10:05");
  assert.match(org.status("10:10"), /⚠️ github: example\/web PRs \(exit 1\): sign-in expired$/m);
});
