# Publish documentation improvements

Read only in Publish mode after local validation. A request to publish authorizes the following ready-PR workflow.

## 1. Resolve the destination

Resolve the hosting remote and default branch from current repository state. Apply repository branch, commit, and review guidance while preserving unrelated user work.

Explicit user instructions may select another base branch, a draft PR, an earlier stopping point, or another publication path. Push directly to the default branch only when explicitly requested and permitted by repository guidance. If an override conflicts with repository guidance or available authority, stop at the last safe boundary and report the exact blocker.

**Complete when:** the remote, target base, publication path, and applicable constraints are established.

## 2. Publish the validated changes

Put the intended changes on a non-default branch, commit them, push that branch, and open a ready PR targeting the default branch. Apply any authorized override established above. Publication does not authorize merging or enabling auto-merge.

**Complete when:** the ready PR or requested override is complete, or the last successful boundary and exact blocker are recorded.

## 3. Report publication status

Record the branch, target base, PR URL or state, and whether hosted checks are settled, pending, or unknown. Keep local validation separate from hosted-check results.

**Complete when:** the user can identify the published result and remaining work.
