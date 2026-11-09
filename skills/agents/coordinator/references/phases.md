# Phases

Read at coordinator step 7, once the phase's proof holds. A project runs in **phases**, each with its own goal and proof in `project.md`'s Goal. A phase ends here, and the project closes only on the user's word.

1. **Integrated check**, skipped when no project work is unmerged. For multi-PR, run [close](close.md)'s integrated check on every unmerged project PR, and record its result, the heads it merged, and the trunk SHA it ran at under Decisions. For one-PR, run the check in [phase end and close](one-pr.md#phase-end-and-close).
2. **Promote**: `phase` moves Decisions and Learnings into the phase's archive, which a wake doesn't read, so first carry forward what the next phase needs:
   - Append each decision and learning that binds later work to `standing-rules.md`.
   - Add to Goal's Follow-ups each follow-up whose detail sits only in Decisions or Learnings, and each later phase the plan or the user named, with its proof.
   - Set each worker whose delivery is still open to `waiting` on it, with Waits on as [project](project.md#workers) gives it, so its row and thread carry into the next phase. Its PR's watch follows step 4's PR watch.
   - For one-PR delivery, carry the integrator and tickets as [phase end and close](one-pr.md#phase-end-and-close) says.
3. **One card**: bring the user one decision card, as step 5 lays it out, asking how the project goes on, with three options: start the next phase, park, or close. Pick the next phase when `project.md` or the user already named one, and give its goal and proof.

Then follow the user's pick, with `<slug>` naming the phase that ended:

- **Next phase**: run `scripts/project.py <folder> phase <slug> --result <one line> --goal <goal> --proof <proof>`, remove the new goal's entry from Goal's Follow-ups by hand, then plan it from step 2.
- **Park**: run `scripts/project.py <folder> phase <slug> --result <one line> --park <reason>`. Delete any startup timer with `delete_scheduled_task` and set its Listening line to none; step 4's heartbeat rule decides whether the heartbeat stays. Keep the thread pinned, and reply with step 5's one-line status, naming that the project is parked and wakes on the user's message.
- **Close**: follow [close](close.md).

`phase` archives and resets the phase as [project](project.md#phase-end) describes.

**Complete when:** the integrated check passed or no project work was unmerged; every binding decision and learning is in `standing-rules.md`; every follow-up and named later phase is in Goal's Follow-ups; every worker with an open delivery is `waiting` on it; and the project is in step 2 of its next phase with that phase gone from Follow-ups, parked with no startup timer, or in close.

## Wake a parked project

When the user's message on a parked project names new work, run `scripts/project.py <folder> start --goal <goal> --proof <proof>`, remove the new goal's entry from Goal's Follow-ups by hand if it was one, then plan it from step 2. Any other message, such as a merge go on an open PR, goes through step 4, and the project stays parked.
