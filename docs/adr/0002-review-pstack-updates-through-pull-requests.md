# Review Pstack updates through pull requests

Partly superseded: the [maintenance guide](../../skills/agents/maintain-skills/MAINTENANCE.md) now owns branches and pull requests, and the [scheduled prompt](../../skills/agents/maintain-skills/references/scheduled-prompt.md) owns budgets and the action grant. Saved scheduled tasks replaced the automations named below. Where this record differs, those files are current.

Use scheduled, scoped runs of `/maintain-skills` to prepare validated update pull requests. Compare the whole upstream suite as well as known imports so additions, removals, and renames are discovered.

Maintenance may commit scoped changes, push an update branch, and create or update a draft pull request. Merging to `main` and refreshing installed copies require separate authorization. This preserves human review of changes to workflows that will govern future agent behavior.

The original 2026-10-15 schedule was a local Codex automation every Monday at 09:00 Europe/Copenhagen. Its replacement is the standalone **Combined skill maintenance** automation; the saved automation settings own its current schedule and model. Notify only when there is a proposed update, a failure, or a decision requiring the user.

Give scheduled reviews a 60-minute working budget and reserve the final ten minutes for validation and reporting. Prepare a draft pull request for the validated subset, checkpoint unfinished work, and leave unfinished review baselines unchanged. Ad hoc autonomous tasks follow their own agreed limits.

Propose straightforward upstream additions when they fit the agreed scope. Treat a new backend or broader authority as a scope change. Preserve local skills removed upstream and propose retirement explicitly for review.

The combined library initially extended that review to Matt Pocock and Pstack together. The 2026-10-16 maintenance expansion covers every local skill and provenance-discovered upstream, including first-party and future skills, through active subagents and one coordinator. Use the [repository maintenance guide](../../skills/agents/maintain-skills/MAINTENANCE.md) and its versioned prompt; the catalog retains suite mappings and upstream-addition policy without limiting local coverage. Keep one update branch/PR and independent completed source positions. The original Pstack-only guide is a compatibility entrypoint.
