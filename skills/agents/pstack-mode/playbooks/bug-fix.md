# Bug fix

Own the discriminating reproduction and the root-cause fix.

1. Invoke /diagnosing-bugs for the shared reproduction and diagnosis loop, using the remaining steps as Pstack evidence and delivery coverage rather than a second diagnosis. Reproduce the reported symptom on the affected surface before editing. Distinguish similar failures with the actual inputs, state, timing, or trace. Use /pstack-how and /pstack-why as needed. Complete when the original failure is observed or the missing prerequisite is explicit.
2. Trace the first violated contract and invoke /pstack-principle-fix-root-causes. Use /pstack-tdd when a cheap regression path exists. Complete when a concrete causal path, rather than a guess, explains the reproduction.
3. Fix within scope and remove the causal defect rather than masking an invalid state. Delegate bounded work through /pstack-swarm when useful. Complete when the original reproduction passes and neighboring contracts hold.
4. Re-run the same user path and relevant tests, preserve failing/passing evidence, and inspect indirect effects through /pstack-blast-radius when appropriate. Complete when the fix is proved on the actual artifact or the limitation is recorded.
5. Review the diff and follow Opening a PR when authorized. Complete when the report distinguishes reproduced facts, causal inference, and unverified cases.

Return the symptom, root cause, change, before/after proof, regression coverage, and outstanding gaps.
