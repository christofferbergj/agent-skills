# Close

Read when the user picks close at a [phase](phases.md) end, or asks to close the project in any later message.

For `Delivery: one-pr`, prove the delivery by its final PR's state, as [phase end and close](one-pr.md#phase-end-and-close) says.

For multi-PR delivery, run the **integrated check**, which proves the PRs work together, not only one by one. A phase end runs it too: when the last one ran it at the PRs' current heads and the trunk's current SHA, copy its result from Decisions or that phase's archive instead of running it again. Otherwise start a fresh `delegate_task` verifier with `isolation: "worktree"`, `role: "test"`, a new `clientRequestId` for each run, and the `swarm-workers` target from /swarm's model roles. Its brief carries the goal and its proof, every PR's head SHA and base, the Decisions, and each worker's verdict. It takes a slot, since it builds. In its own worktree it merges every unmerged project PR branch onto the current trunk they target, merging nothing on GitHub, runs the repository's checks there, and reports missing outcomes and anything that breaks across PRs. Send each finding as a fix to the worker that owns that code, and rerun the check after any fix that touches what it covered. Record its result under `## Result` in `project.md`.

Then give every worker a final state: `done`, `replaced by <worker>`, `absorbed into <worker>`, or `dropped`. Delete the heartbeat and any startup timer with `delete_scheduled_task`, `unwatch_pull_request` every watch, write the final summary under `## Result`, and unpin this thread with `t3_thread_organize` `unpin`.

**Complete when:** Result records the multi-PR integrated check passing at the PRs' current heads or the one-PR proof [phase end and close](one-pr.md#phase-end-and-close) requires, or the user accepted a stated limitation through a decision card, recorded under Decisions; every Listening line reads none, every Workers row has a final state, and the thread is unpinned.
