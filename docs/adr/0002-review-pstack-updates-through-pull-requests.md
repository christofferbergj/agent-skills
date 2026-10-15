# Review Pstack updates through pull requests

Use scheduled, scoped runs of `/maintain-skills` to prepare validated update pull requests. Compare the whole upstream suite as well as known imports so additions, removals, and renames are discovered.

Maintenance may commit scoped changes, push an update branch, and create or update a draft pull request. Merging to `main` and refreshing installed copies require separate authorization. This preserves human review of changes to workflows that will govern future agent behavior.

Run the review through a local Codex automation every Monday at 09:00 Europe/Copenhagen. Notify only when there is a proposed update, a failure, or a decision requiring the user.

Give scheduled reviews a 60-minute working budget and reserve the final ten minutes for validation and reporting. Prepare a draft pull request for the validated subset, checkpoint unfinished work, and leave unfinished review baselines unchanged. Ad hoc autonomous tasks follow their own agreed limits.

Propose straightforward upstream additions when they fit the agreed scope. Treat a new backend or broader authority as a scope change. Preserve local skills removed upstream and propose retirement explicitly for review.

The combined library extends this same weekly review to Matt Pocock and Pstack together. Use the maintain-skills catalog and shared integration contract; keep one update branch/PR and independent completed source positions. The original Pstack-only guide is a compatibility entrypoint.
