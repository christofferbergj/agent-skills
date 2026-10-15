# Shipping

Own an independently verified landing, not merely green checks.

1. Confirm existing explicit authority to merge, land, ship, or merge when ready. Otherwise stop at merge-ready. Resolve the exact ordered PR chain and exclusions the user owns. Complete when the authorized merge scope is unambiguous.
2. Obtain an independent per-PR verdict on the exact head and relevant base through /pstack-swarm, using actual runtime and test evidence. Scale verification to the changed surfaces. Green CI alone is insufficient. Complete when each PR is `PASS`, `PASS+NOTES` with no unresolved defect, or held with an explicit failure or gap.
3. Land only the contiguous verified run from the lowest unmerged dependency. A verified PR above an unverified prerequisite waits. Rebase only when required for current base compatibility, inspect the resulting diff, and reverify changed behavior at the new head. A pure rebase can retain prior behavior evidence only when equivalent patch identity and all environmental assumptions are proved; merge conflict resolution requires fresh evidence. Complete when the next PR's verdict applies to the actual artifact being merged.
4. Honor forge approvals, branch protection, draft promotion authority, and deployment gates. Never bypass them to make the run green. Merge through the repository's established tool, then verify the resulting state before advancing. Complete when each landed result and remaining frontier are observed.

Return merged PRs, revisions, independent verdicts, retained evidence rationale, and anything held. New commits invalidate stale verdicts unless their continued validity is proved explicitly.
