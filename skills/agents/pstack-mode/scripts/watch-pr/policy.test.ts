import { describe, expect, it } from "bun:test";
import { WatcherQueryError } from "./github.ts";
import {
  applyQueueSnapshot,
  assessGitHubMerge,
  classifyPr,
  createQueueState,
  evaluateQueue,
  planQueue,
  queryBackoffSeconds,
  readSnapshot,
  runQueued,
  runSimple,
  selectTierMajorStackDecision,
} from "./policy.ts";
import { fakeReader, failedCheck, passingCheck, pendingCheck } from "./fakes.test-helper.ts";
import { renderStatusTable } from "./render.ts";
import type {
  GitHubReader,
  NonEmpty,
  PollingOptions,
  PrContext,
  ProgressVerdict,
  PullRequestFacts,
  RollupState,
} from "./types.ts";
import { parsePrNumber } from "./types.ts";

const context = (number: number): PrContext => ({
  owner: "owner",
  repo: "repo",
  number: parsePrNumber(number),
});
const options = {
  interval: 10,
  sweepInterval: 300,
  timeout: 0,
  maxQueryErrors: 5,
  allowDraft: false,
} satisfies PollingOptions;

describe("readiness truth table", () => {
  it("keeps approvals, forge requirements, and unknown mergeability as gates", async () => {
    const cases = [
      {
        facts: { reviewDecision: "REVIEW_REQUIRED", mergeStateStatus: "BLOCKED" },
        reason: "review-required",
      },
      { facts: { mergeStateStatus: "BLOCKED" }, reason: "forge-blocked" },
      { facts: { mergeStateStatus: "BEHIND" }, reason: "forge-blocked" },
      { facts: { mergeStateStatus: "UNKNOWN" }, reason: "mergeability-unknown" },
      { facts: { mergeable: "UNKNOWN" }, reason: "mergeability-unknown" },
      { facts: { isDraft: true, reviewDecision: "REVIEW_REQUIRED" }, reason: "review-required" },
    ] satisfies readonly { facts: Partial<PullRequestFacts>; reason: string }[];
    for (const { facts, reason } of cases) {
      const snapshot = await readSnapshot({
        reader: fakeReader({ facts }),
        context: context(1),
        pendingHistory: "include",
        allowDraft: true,
      });
      expect(classifyPr(snapshot, true)).toMatchObject({
        kind: "blocker",
        blocker: { kind: "merge-gate", reason },
      });
      expect(selectTierMajorStackDecision([snapshot], true)).toMatchObject({
        kind: "blocker",
        blocker: { reason },
      });
      expect(renderStatusTable([snapshot])).not.toMatch(/\| ✅ \|$/m);
    }
    const clear = await readSnapshot({
      reader: fakeReader(),
      context: context(1),
      pendingHistory: "include",
      allowDraft: false,
    });
    expect(classifyPr(clear).kind).toBe("ready");
  });
  it("covers every specified row and every UNKNOWN rollup value", () => {
    const cases: readonly [
      PullRequestFacts["mergeStateStatus"],
      RollupState,
      "allowed" | "refused",
    ][] = [
      ["BLOCKED", "FAILURE", "refused"],
      ["BLOCKED", "ERROR", "refused"],
      ["BLOCKED", "PENDING", "allowed"],
      ["UNSTABLE", "FAILURE", "allowed"],
      ["UNKNOWN", "ERROR", "allowed"],
      ["UNKNOWN", "EXPECTED", "allowed"],
      ["UNKNOWN", "FAILURE", "allowed"],
      ["UNKNOWN", "PENDING", "allowed"],
      ["UNKNOWN", "SUCCESS", "allowed"],
      ["UNKNOWN", null, "allowed"],
      ["CLEAN", "SUCCESS", "allowed"],
    ];
    for (const [mergeStateStatus, headRollupState, expected] of cases) {
      expect(assessGitHubMerge({ mergeStateStatus, headRollupState }).kind).toBe(expected);
    }
  });

  it("turns a clean visible list plus GitHub refusal into an explicit CI blocker", async () => {
    const reader = fakeReader({
      facts: { mergeStateStatus: "BLOCKED" },
      fastPath: { kind: "checks", checks: [passingCheck()] },
      commitRollups: [{ oid: "head", state: "FAILURE" }],
    });
    const snapshot = await readSnapshot({
      reader,
      context: context(1),
      pendingHistory: "include",
      allowDraft: false,
    });
    expect(snapshot.kind).toBe("open");
    if (snapshot.kind !== "open") throw new Error("expected open snapshot");
    expect(snapshot.ci.kind).toBe("ci-github-rejected");
    expect(classifyPr(snapshot)).toMatchObject({
      kind: "blocker",
      blocker: { kind: "failing-checks" },
    });
  });
});

describe("snapshot query planning", () => {
  it("does not query commit rollups while queued checks are pending", async () => {
    const reader = fakeReader({
      fastPath: { kind: "checks", checks: [pendingCheck()] },
    });
    const snapshot = await readSnapshot({
      reader,
      context: context(2),
      pendingHistory: "omit",
      allowDraft: false,
    });
    expect(snapshot.kind).toBe("open");
    if (snapshot.kind !== "open") throw new Error("expected open snapshot");
    expect(snapshot.ci.kind).toBe("ci-pending");
    expect(reader.calls).toEqual(["pullRequest", "reviewThreadPage:null", "checksFastPath"]);
  });

  it("queries rollups for settled and failed lists", async () => {
    const settled = fakeReader();
    await readSnapshot({
      reader: settled,
      context: context(3),
      pendingHistory: "omit",
      allowDraft: false,
    });
    expect(settled.calls).toContain("commitRollups");

    const failed = fakeReader({
      fastPath: { kind: "checks", checks: [failedCheck()] },
    });
    await readSnapshot({
      reader: failed,
      context: context(4),
      pendingHistory: "omit",
      allowDraft: false,
    });
    expect(failed.calls).toContain("commitRollups");
  });

  it("short-circuits merged rows before threads and checks", async () => {
    const reader = fakeReader({
      facts: { state: "MERGED", mergedAt: "2026-07-26T00:00:00Z" },
    });
    expect(
      (
        await readSnapshot({
          reader,
          context: context(5),
          pendingHistory: "include",
          allowDraft: false,
        })
      ).kind,
    ).toBe("merged");
    expect(reader.calls).toEqual(["pullRequest"]);
  });
});

it("scans stacks tier-major so an upstack conflict outranks frontier CI", async () => {
  const frontier = await readSnapshot({
    reader: fakeReader({
      fastPath: { kind: "checks", checks: [failedCheck()] },
      commitRollups: [{ oid: "head", state: "FAILURE" }],
    }),
    context: context(10),
    pendingHistory: "omit",
    allowDraft: false,
  });
  const upstack = await readSnapshot({
    reader: fakeReader({ facts: { mergeable: "CONFLICTING" } }),
    context: context(11),
    pendingHistory: "omit",
    allowDraft: false,
  });
  const decision = selectTierMajorStackDecision([frontier, upstack]);
  expect(decision).toMatchObject({
    kind: "blocker",
    blocker: { kind: "merge-conflicts", pr: { number: 11 } },
  });
});

it("attributes a stack wait to the PR whose checks are pending, not the bottom", async () => {
  const readyBottom = await readSnapshot({
    reader: fakeReader(),
    context: context(20),
    pendingHistory: "omit",
    allowDraft: false,
  });
  const pendingUpstack = await readSnapshot({
    reader: fakeReader({
      fastPath: { kind: "checks", checks: [pendingCheck("upstack-build")] },
    }),
    context: context(21),
    pendingHistory: "omit",
    allowDraft: false,
  });
  const decision = selectTierMajorStackDecision([readyBottom, pendingUpstack]);
  expect(decision).toMatchObject({
    kind: "waiting",
    frontier: { number: 21 },
    pending: [{ name: "upstack-build" }],
  });
});

it("waits on a draft while checks are pending, then reports the draft gate", async () => {
  const pending = await readSnapshot({
    reader: fakeReader({
      facts: { isDraft: true },
      fastPath: { kind: "checks", checks: [pendingCheck()] },
    }),
    context: context(12),
    pendingHistory: "omit",
    allowDraft: false,
  });
  expect(classifyPr(pending).kind).toBe("waiting");

  const settled = await readSnapshot({
    reader: fakeReader({ facts: { isDraft: true } }),
    context: context(12),
    pendingHistory: "omit",
    allowDraft: false,
  });
  expect(classifyPr(settled)).toMatchObject({
    kind: "blocker",
    blocker: { kind: "merge-gate", reason: "draft-pr" },
  });
});

describe("queued-stack cadence", () => {
  async function openSnapshot(pr: PrContext) {
    return readSnapshot({
      reader: fakeReader(),
      context: pr,
      pendingHistory: "omit",
      allowDraft: false,
    });
  }

  it("drops a sweep head only after its snapshot succeeds", async () => {
    const queue = [context(20), context(21), context(22)] satisfies NonEmpty<PrContext>;
    let state = createQueueState(queue, 0);
    const first = await openSnapshot(queue[0]);
    state = applyQueueSnapshot(state, first, 0, options).state;
    expect(state.work).toMatchObject({
      kind: "whole-stack-sweep",
      remaining: [{ number: 21 }, { number: 22 }],
    });
    const second = await openSnapshot(queue[1]);
    state = applyQueueSnapshot(state, second, 60, options).state;
    expect(state.work).toMatchObject({
      kind: "whole-stack-sweep",
      remaining: [{ number: 22 }],
    });
  });

  it("resumes the sweep at the PR whose read failed", async () => {
    const middle = context(21);
    const base = fakeReader();
    let failNext = true;
    const timeline: string[] = [];
    const reader = {
      ...base,
      async pullRequest(pr: PrContext) {
        if (pr.number === middle.number && failNext) {
          failNext = false;
          timeline.push(`fail:${pr.number}`);
          throw new WatcherQueryError({
            kind: "command-exit",
            retryable: true,
            detail: "rate limited",
            code: 1,
          });
        }
        timeline.push(`read:${pr.number}`);
        return base.pullRequest(pr);
      },
    } satisfies GitHubReader;
    let now = 0;
    let sleeps = 0;
    const running = runQueued({
      dependencies: {
        reader,
        clock: {
          now: () => now,
          observedAt: () => "2026-07-26T00:00:00.000Z",
          async sleep(seconds) {
            timeline.push("sleep");
            now += seconds;
            sleeps += 1;
            if (sleeps === 2) throw new Error("stop after resume proof");
          },
        },
        emit(verdict) {
          timeline.push(`emit:${verdict.kind}`);
        },
      },
      contexts: [context(20), middle, context(22)],
      options,
    });
    await expect(running).rejects.toThrow("stop after resume proof");
    expect(timeline).toEqual([
      "emit:QUEUE",
      "read:20",
      "fail:21",
      "emit:RETRY",
      "sleep",
      "read:21",
      "read:22",
      "emit:STATUS",
      "emit:WAITING",
      "sleep",
    ]);
  });

  it("emits a completed sweep only after its final successful snapshot", async () => {
    const queue = [context(30), context(31)] satisfies NonEmpty<PrContext>;
    let state = createQueueState(queue, 0);
    const first = applyQueueSnapshot(state, await openSnapshot(queue[0]), 0, options);
    expect(first.completedSweepRows).toBeNull();
    state = first.state;
    const second = applyQueueSnapshot(state, await openSnapshot(queue[1]), 5, options);
    expect(second.completedSweepRows?.map((row) => Number(row.context.number))).toEqual([30, 31]);
    expect(second.state.nextSweepAt).toBe(305);
  });

  it("ADVANCE continues directly to the new frontier without sleeping", async () => {
    const one = context(40);
    const two = context(41);
    const base = fakeReader();
    const reads = new Map<number, number>();
    const timeline: string[] = [];
    const reader = {
      ...base,
      async pullRequest(pr: PrContext) {
        timeline.push(`read:${pr.number}`);
        const facts = await base.pullRequest(pr);
        const count = (reads.get(pr.number) ?? 0) + 1;
        reads.set(pr.number, count);
        return pr.number === one.number && count > 1
          ? {
              ...facts,
              state: "MERGED" as const,
              mergedAt: "2026-07-26T00:00:00Z",
            }
          : facts;
      },
    } satisfies GitHubReader;
    let now = 0;
    let sleeps = 0;
    const emitted: ProgressVerdict[] = [];
    const running = runQueued({
      dependencies: {
        reader,
        clock: {
          now: () => now,
          observedAt: () => "2026-07-26T00:00:00.000Z",
          async sleep(seconds) {
            timeline.push("sleep");
            now += seconds;
            sleeps += 1;
            if (sleeps === 2) throw new Error("stop after advance proof");
          },
        },
        emit(verdict) {
          emitted.push(verdict);
          timeline.push(`emit:${verdict.kind}`);
        },
      },
      contexts: [one, two],
      options,
    });
    await expect(running).rejects.toThrow("stop after advance proof");
    expect(emitted.some((event) => event.kind === "ADVANCE")).toBe(true);
    const firstSleep = timeline.indexOf("sleep");
    expect(timeline.slice(firstSleep, firstSleep + 5)).toEqual([
      "sleep",
      "read:40",
      "emit:ADVANCE",
      "read:41",
      "emit:WAITING",
    ]);
  });

  it("deduplicates identical waits and schedules the next due sweep", async () => {
    const queue = [context(50)] satisfies NonEmpty<PrContext>;
    let state = createQueueState(queue, 0);
    state = applyQueueSnapshot(state, await openSnapshot(queue[0]), 0, options).state;
    const first = evaluateQueue(state, 0, options);
    expect(first.kind).toBe("waiting");
    if (first.kind !== "waiting") throw new Error("expected waiting");
    expect(first.emit).toBe(true);
    const second = evaluateQueue(first.state, 10, options);
    expect(second.kind).toBe("waiting");
    if (second.kind !== "waiting") throw new Error("expected waiting");
    expect(second.emit).toBe(false);
    expect(planQueue(second.state, 300).work?.kind).toBe("whole-stack-sweep");
  });
});

it("uses the specified retry floor and cap", () => {
  expect(queryBackoffSeconds(1, 1)).toBe(60);
  expect(queryBackoffSeconds(1, 2)).toBe(120);
  expect(queryBackoffSeconds(60, 4)).toBe(300);
});

it("ends a pending poll at its deadline before reading the PR again", async () => {
  let now = 0;
  let reads = 0;
  const base = fakeReader({ fastPath: { kind: "checks", checks: [pendingCheck()] } });
  const verdict = await runSimple({
    dependencies: {
      reader: {
        ...base,
        async pullRequest(pr) {
          reads += 1;
          return base.pullRequest(pr);
        },
      },
      clock: {
        now: () => now,
        observedAt: () => "2026-10-16T00:00:00Z",
        async sleep(seconds) {
          now += seconds;
        },
      },
      emit() {},
    },
    contexts: [context(1)],
    mode: "single",
    statusOnly: false,
    options: { ...options, interval: 60, timeout: 1 },
  });
  expect({ now, reads, kind: verdict.kind }).toEqual({ now: 1, reads: 1, kind: "TIMEOUT" });
});

it("ends retry backoff at its deadline without another query", async () => {
  let now = 0;
  let reads = 0;
  const retries: ProgressVerdict[] = [];
  const base = fakeReader();
  const verdict = await runSimple({
    dependencies: {
      reader: {
        ...base,
        async pullRequest() {
          reads += 1;
          throw new WatcherQueryError({
            kind: "command-exit",
            retryable: true,
            detail: "fixture unavailable",
            code: 1,
          });
        },
      },
      clock: {
        now: () => now,
        observedAt: () => "2026-10-16T00:00:00Z",
        async sleep(seconds) {
          now += seconds;
        },
      },
      emit(verdict) {
        retries.push(verdict);
      },
    },
    contexts: [context(1)],
    mode: "single",
    statusOnly: false,
    options: { ...options, interval: 60, timeout: 1 },
  });
  expect({ now, reads, retries, verdict }).toMatchObject({
    now: 1,
    reads: 1,
    retries: [],
    verdict: { kind: "TIMEOUT", reason: { kind: "status-unavailable" } },
  });
});

it("stops queued polling and partial sweeps before another read after the deadline", async () => {
  for (const expireDuringRead of [false, true]) {
    let now = 0;
    let reads = 0;
    const base = fakeReader();
    const verdict = await runQueued({
      dependencies: {
        reader: {
          ...base,
          async pullRequest(pr) {
            reads += 1;
            if (expireDuringRead) now = 2;
            return base.pullRequest(pr);
          },
        },
        clock: {
          now: () => now,
          observedAt: () => "2026-10-16T00:00:00Z",
          async sleep(seconds) {
            now += seconds;
          },
        },
        emit() {},
      },
      contexts: expireDuringRead ? [context(1), context(2)] : [context(1)],
      options: { ...options, interval: 60, timeout: 1 },
    });
    expect({ now, reads, verdict }).toMatchObject({
      now: expireDuringRead ? 2 : 1,
      reads: 1,
      verdict: {
        kind: "TIMEOUT",
        reason: {
          kind: "queued-stack",
          frontier: { number: 1 },
          unmergedCount: expireDuringRead ? 2 : 1,
        },
      },
    });
  }
});

it("reports an observed conflict before a partial-sweep deadline without reading the next PR", async () => {
  let now = 0;
  const reads: number[] = [];
  const base = fakeReader({ facts: { mergeable: "CONFLICTING" } });
  const verdict = await runQueued({
    dependencies: {
      reader: {
        ...base,
        async pullRequest(pr) {
          reads.push(pr.number);
          now = 2;
          return base.pullRequest(pr);
        },
      },
      clock: {
        now: () => now,
        observedAt: () => "2026-10-16T00:00:00Z",
        async sleep(seconds) {
          now += seconds;
        },
      },
      emit() {},
    },
    contexts: [context(1), context(2)],
    options: { ...options, timeout: 1 },
  });
  expect({ reads, verdict }).toMatchObject({
    reads: [1],
    verdict: {
      kind: "BLOCKER",
      exitCode: 2,
      blocker: { kind: "merge-conflicts", pr: { number: 1 } },
    },
  });
});

it("preserves an observed blocker when a later query exhausts the retry deadline", async () => {
  let now = 0;
  const reads: number[] = [];
  const base = fakeReader({ facts: { mergeable: "CONFLICTING" } });
  const verdict = await runQueued({
    dependencies: {
      reader: {
        ...base,
        async pullRequest(pr) {
          reads.push(pr.number);
          if (pr.number === 2)
            throw new WatcherQueryError({
              kind: "command-exit",
              retryable: true,
              detail: "fixture unavailable",
              code: 1,
            });
          return base.pullRequest(pr);
        },
      },
      clock: {
        now: () => now,
        observedAt: () => "2026-10-16T00:00:00Z",
        async sleep(seconds) {
          now += seconds;
        },
      },
      emit() {},
    },
    contexts: [context(1), context(2)],
    options: { ...options, interval: 60, timeout: 1 },
  });
  expect({ now, reads, verdict }).toMatchObject({
    now: 1,
    reads: [1, 2],
    verdict: {
      kind: "BLOCKER",
      exitCode: 2,
      blocker: { kind: "merge-conflicts", pr: { number: 1 } },
    },
  });
});

it("ranks all observed blocker tiers and completes the sweep when the deadline is disabled", async () => {
  for (const timeout of [0, 1]) {
    let now = 0;
    const reads: number[] = [];
    const base = fakeReader();
    const verdict = await runQueued({
      dependencies: {
        reader: {
          ...base,
          async pullRequest(pr) {
            reads.push(pr.number);
            const facts = await base.pullRequest(pr);
            if (pr.number === 1) return { ...facts, reviewDecision: "CHANGES_REQUESTED" as const };
            if (pr.number === 2) {
              now = 2;
              return { ...facts, mergeable: "CONFLICTING" as const };
            }
            return facts;
          },
        },
        clock: {
          now: () => now,
          observedAt: () => "2026-10-16T00:00:00Z",
          async sleep(seconds) {
            now += seconds;
          },
        },
        emit() {},
      },
      contexts: [context(1), context(2), context(3)],
      options: { ...options, timeout },
    });
    expect({ reads, verdict }).toMatchObject({
      reads: timeout === 0 ? [1, 2, 3] : [1, 2],
      verdict: {
        kind: "BLOCKER",
        exitCode: 2,
        blocker: { kind: "merge-conflicts", pr: { number: 2 } },
      },
    });
  }
});

it("keeps the terminal query-error budget ahead of a known blocker at the deadline", async () => {
  let now = 0;
  const base = fakeReader({ facts: { mergeable: "CONFLICTING" } });
  const verdict = await runQueued({
    dependencies: {
      reader: {
        ...base,
        async pullRequest(pr) {
          if (pr.number === 2) {
            now = 2;
            throw new WatcherQueryError({
              kind: "command-exit",
              retryable: true,
              detail: "fixture unavailable",
              code: 1,
            });
          }
          return base.pullRequest(pr);
        },
      },
      clock: {
        now: () => now,
        observedAt: () => "2026-10-16T00:00:00Z",
        async sleep(seconds) {
          now += seconds;
        },
      },
      emit() {},
    },
    contexts: [context(1), context(2)],
    options: { ...options, timeout: 1, maxQueryErrors: 1 },
  });
  expect(verdict).toMatchObject({
    kind: "BLOCKER",
    exitCode: 7,
    blocker: { kind: "status-query", failures: 1 },
  });
});

for (const firstRead of ["pending", "retry"] as const) {
  it(`finishes a capped ${firstRead} wait when the timer wakes fractionally early`, async () => {
    let now = 0;
    let reads = 0;
    const base = fakeReader();
    const verdict = await runSimple({
      dependencies: {
        reader: {
          ...base,
          async pullRequest(pr) {
            reads += 1;
            if (reads === 1 && firstRead === "retry")
              throw new WatcherQueryError({
                kind: "command-exit",
                retryable: true,
                detail: "fixture unavailable",
                code: 1,
              });
            return base.pullRequest(pr);
          },
          async checksFastPath() {
            return {
              kind: "checks" as const,
              checks: [reads === 1 ? pendingCheck() : passingCheck()],
            };
          },
        },
        clock: {
          now: () => now,
          observedAt: () => "2026-10-16T00:00:00Z",
          async sleep(seconds) {
            now += seconds - 0.001;
          },
        },
        emit() {},
      },
      contexts: [context(1)],
      mode: "single",
      statusOnly: false,
      options: { ...options, interval: 60, timeout: 1 },
    });
    expect({ reads, now, verdict }).toMatchObject({
      reads: 1,
      now: 0.999,
      verdict: { kind: "TIMEOUT", exitCode: 5 },
    });
  });
}

describe("polling deadline sleeps", () => {
  for (const mode of ["single", "queued-stack", "query-retry"] as const) {
    it(`caps ${mode} sleeps at the configured deadline`, async () => {
      let now = 0;
      const sleeps: number[] = [];
      const pending = fakeReader({ fastPath: { kind: "checks", checks: [pendingCheck()] } });
      const reader =
        mode === "query-retry"
          ? {
              ...pending,
              async pullRequest(): Promise<PullRequestFacts> {
                throw new WatcherQueryError({
                  kind: "command-exit",
                  retryable: true,
                  code: 1,
                  detail: "temporary failure",
                });
              },
            }
          : pending;
      const dependencies = {
        reader,
        clock: {
          now: () => now,
          observedAt: () => "2026-07-26T00:00:00.000Z",
          async sleep(seconds: number) {
            sleeps.push(seconds);
            now += seconds;
          },
        },
        emit() {},
      };
      const polling = { ...options, interval: 60, timeout: 5 };
      const result =
        mode === "queued-stack"
          ? await runQueued({ dependencies, contexts: [context(1)], options: polling })
          : await runSimple({
              dependencies,
              contexts: [context(1)],
              mode: "single",
              statusOnly: false,
              options: polling,
            });
      expect(result.kind).toBe("TIMEOUT");
      expect(sleeps).toEqual([5]);
      expect(now).toBe(5);
    });
  }
  it("preserves the polling interval when the deadline is disabled", async () => {
    let now = 0;
    let reads = 0;
    const sleeps: number[] = [];
    const pending = fakeReader({ fastPath: { kind: "checks", checks: [pendingCheck()] } });
    const passed = fakeReader({ fastPath: { kind: "checks", checks: [passingCheck()] } });
    const result = await runSimple({
      dependencies: {
        reader: {
          ...pending,
          async checksFastPath(pr) {
            reads += 1;
            return reads === 1 ? pending.checksFastPath(pr) : passed.checksFastPath(pr);
          },
        },
        clock: {
          now: () => now,
          observedAt: () => "2026-07-26T00:00:00.000Z",
          async sleep(seconds) {
            sleeps.push(seconds);
            now += seconds;
          },
        },
        emit() {},
      },
      contexts: [context(1)],
      mode: "single",
      statusOnly: false,
      options: { ...options, interval: 60, timeout: 0 },
    });
    expect(result.kind).toBe("READY");
    expect(sleeps).toEqual([60]);
  });
});
