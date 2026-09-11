# Publication

An explicit request to publish authorizes this workflow after local validation:

1. Resolve the hosting remote and default branch from current state. Inspect open PRs for the same work and continue the matching branch when one owns the change. Use repository branch, commit, and review conventions. Complete when the destination, existing review context, and requirements are known.
2. Put only the intended changes on that non-default branch, creating one if needed. Preserve unrelated work and commit the validated change. Complete when the commit and diff match the audited repairs.
3. Push the branch and update the matching PR, preserving its base and draft/ready status unless a change is requested. If none exists, open a ready PR targeting the default branch. Rewrite the title and description around the final change using the repository template. Complete when the remote branch and review request are verified, or the failing operation is recorded.
4. Report the branch, base, review URL, and observed hosted checks. Complete when local validation and hosted results are clearly distinguished, including pending or unavailable checks.

Use an explicit user override for another base, draft status, or publication path, subject to governing instructions and permissions. Direct default-branch pushes require an explicit request. Publication ends at the review request; merging or enabling auto-merge requires separate explicit authorization.

Where the host uses another review mechanism, use its equivalent. If publication is unavailable, preserve the validated local result and report the exact missing capability.
