# Performance issue

Own the measured regression and the limiter behind it. Tie every fix to a measurement; don't read source instead of measuring.

1. Invoke /diagnosing-bugs for the shared performance diagnosis loop. Reproduce the slow path and capture a baseline trace on the matching surface. Invoke /pstack-benchmark-checklist to vet the baseline, and each later number, before trusting it. Complete when the actual work, completion state, and metric are known.
2. Instrument the relevant runtime and identify the limiting resource or causal path. Use /pstack-how to ground hypotheses, /pstack-why, and the appropriate forensics playbook where needed. Don't claim a perf ceiling without running it first. Try the performance mantras in order, cheapest first:
   1. Don't do it. Stop work whose result nothing uses rather than cheapening it.
   2. Do it, but don't do it again.
   3. Do it less.
   4. Do it later.
   5. Do it when they're not looking.
   6. Do it concurrently.
   7. Do it cheaper.

   When an earlier mantra meets the target, stop. Complete when a hypothesis predicts an observable improvement without changing the required work.

3. Plan the fix from the trace. If it crosses a function boundary, use /pstack-architect first. Delegate implementation through /pstack-swarm to a subagent on your configured perf-issue role, review the diff, and capture a post-fix trace. Apply /pstack-principle-sequence-verifiable-units, verifying each attempt before trying the next. Preserve semantic correctness, errors, and load. Complete when the change addresses the measured limiter.
4. Parse and compare the baseline and head artifacts with equivalent workloads (JSON to sqlite, diff), interleaved trials where useful, errors and work counts included. "Inconclusive" or wrong-surface is not a pass; flag it. Complete when the speed claim survives the checklist and the user-visible end state improves or the change is rejected.
5. Run correctness checks, review the change through /review-loop, cite the measurement in the PR, and follow Opening a PR when authorized. Complete when the final report explains both the number and its practical limits.

For sustained improvement against a metric rather than a one-off fix, use [Hillclimb](hillclimb.md).

Return reproduction, limiter, baseline number, post-fix number, delta, artifact path, methodology, correctness evidence, and uncertainty.
