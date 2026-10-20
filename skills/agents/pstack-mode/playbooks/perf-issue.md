# Performance issue

Own the measured regression and the limiter behind it.

1. Invoke /diagnosing-bugs for the shared performance diagnosis loop. Reproduce the slow path and record a meaningful baseline. Invoke /pstack-benchmark-checklist before trusting the number. Complete when the actual work, completion state, and metric are known.
2. Instrument the relevant runtime and identify the limiting resource or causal path. Use /pstack-how, /pstack-why, and the appropriate forensics playbook where needed. Complete when a hypothesis predicts an observable improvement without changing the required work.
3. Make one scoped change, preserving semantic correctness, errors, and load. Complete when the change addresses the measured limiter.
4. Compare baseline and head with equivalent workloads, interleaved trials where useful, errors and work counts included. Complete when the speed claim survives the checklist and the user-visible end state improves or the change is rejected.
5. Run correctness checks, review the change through /review-loop, and follow Opening a PR when authorized. Complete when the final report explains both the number and its practical limits.

Return reproduction, limiter, change, baseline/head measurements, methodology, correctness evidence, and uncertainty.
