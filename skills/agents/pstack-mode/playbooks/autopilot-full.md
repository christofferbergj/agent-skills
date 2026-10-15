# Autopilot full

Own an explicitly authorized queue through independently verified merges.

1. Confirm queue items, dependencies, operator-owned gates, merge authority, and budget. Without merge authority use Autopilot stack. Complete when each item has its allowed lifecycle and the run has a durable brief.
2. Assign one owner per PR through /pstack-swarm, with isolated writers and one coordinator for shared state. Each owner handles build, self-proof, triage, and authorized landing. Open draft PRs early and record head revisions after meaningful pushes. Complete each dispatch when its lifecycle, evidence, and stop conditions are explicit.
3. At code-ready, run an independent verification wave sized to behavior and risk. Another full wave is needed for new behavior or redesign; a small correction still needs a fresh check at the new head. Read receipts rather than PR claims. Complete when each verdict matches the actual head and has no unresolved defect.
4. Follow Shipping for base compatibility, forge approvals, authorized draft promotion, and contiguous verified landing. An owner cannot countersign its own request to loosen a gate. Complete when every merged artifact is verified and every held item is explicit.
5. Audit progress within the agreed cadence and budget, using available native status APIs and artifact checks. Replace failed workers with consolidated briefs, preserve a decision trail, and stand down writes promptly on the user's stop. Complete when all jobs are accounted for or a durable checkpoint identifies the remainder.

Return queue status, PRs and revisions, verdicts, merged results, held gates, trail, and checkpoint. Report user-facing progress through /pstack-ketchup.
