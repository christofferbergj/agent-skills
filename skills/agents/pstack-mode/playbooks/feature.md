# Feature

Own the user-visible behavior and the contract that proves it. You own the design: plan, review, verify. Delegate implementation and stay in the lead.

1. Read the configured project artifacts through /domain-modeling and reuse any accepted spec and ticket graph. Inspect the existing system and name the data shape, user path, invariants, and done predicate. Invoke /pstack-how over the affected subsystem. Complete when implementation has a grounded boundary and measurable result.
2. For consequential interfaces use /pstack-architect for parallel design exploration; use /pstack-arena when competing shapes would materially change the outcome. Build a cheap prototype to settle empirical forks rather than asking the user to guess. Complete when the selected shape fits the scope and any requested approval exists.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target (/pstack-principle-separate-before-serializing-shared-state). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.

   Complete when every unit has an owner, output, and check.

4. Delegate code-writing through /pstack-swarm to a subagent on your configured feature role, with a specific scope: file paths, the named data shape and its organizing structure per /pstack-principle-model-the-domain chosen before the delegate writes logic, and success criteria. When the implementation admits multiple valid shapes (error handling, abstraction layer, test structure), delegate via /pstack-arena instead. Mandatory: no skip-with-reason escape, and the Laziness Protocol does not override it (the gain is review separation, not lines saved). A subagent forbidden to spawn satisfies this by owning the diff directly with the same review separation. The delegate implements the smallest sufficient behavior through /tdd at accepted public seams when a practical test path exists. Reconcile accepted domain changes through /domain-modeling. Use relevant principle owners, inspect the delegated diff, and avoid preserving obsolete internal APIs. No "standing by" reply that waits on a nested agent. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit liberally. Pause before changing approved scope or interfaces. Complete when the implementation matches the agreed behavior.
5. Run applicable unit and integration checks and drive the real user path using the repository's verification skill or available control tools. "Inconclusive" or wrong-surface is not a pass; flag it. Preserve before/after evidence, including durable side effects. Use /pstack-benchmark-checklist for performance claims. Complete when required surfaces have evidence or an explicit unresolved gap.
6. Rebase into small, ordered commits and stack follow-ups. Use /pstack-principle-sequence-verifiable-units, building, verifying, and committing each small unit before the next. Complete when each commit is a verified, landable unit.
7. Invoke /review-loop for the final review; if the design is contested, add /pstack-interrogate before shipping, reusing equivalent current evidence. Apply /pstack-no-comments, and prepare the result through Opening a PR when authorized. Complete when the final committed artifact and reported evidence agree.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries. Spawn a fresh owner rather than chaining interrupts.

Return the user-facing result, what you chose and why, the throughput checkpoint, verification, open decisions, PR or artifact paths, and exact remaining gaps. Use tables for design alternatives.
