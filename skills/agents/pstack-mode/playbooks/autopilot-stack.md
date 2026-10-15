# Autopilot stack

Own a verified linear stack that the user can land.

1. Confirm queue, dependency order, desired base, approved interfaces, and budget. This path ends at merge-ready unless a separate explicit landing grant changes it. Complete when each PR's parent and owned boundary are fixed.
2. Assign scoped owners through /pstack-swarm in separate worktrees. Independent work can proceed together; dependent work bases on its actual parent branch. Use the repository's stack tool when configured. Complete when ownership and branch relationships are recorded.
3. Build, self-verify, and open draft PRs with each child targeting its parent. Run an independent verification wave at code-ready and revalidate relevant changes at later heads. Complete when evidence is attached to exact heads and required prerequisites.
4. Reconcile conflicts and reviews without hiding scope or interface changes. Keep the stack coherent and run Babysit within its budget where requested. Complete when each PR is verified and ready for its appropriate human gate, or held explicitly.
5. Preserve the ordered stack, receipts, and decision trail. Complete when the user can review and land bottom-up without reconstructing agent state.

Return ordered PR links, base relationships, exact revisions, verdicts, review gates, trail, and unfinished work. Use /pstack-ketchup for the concise user-facing explanation.
