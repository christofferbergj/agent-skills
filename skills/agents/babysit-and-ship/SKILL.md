---
name: babysit-and-ship
description: Takes a PR or stack from where it stands to merged by marking it ready, babysitting it to green, having an independent agent verify it, and landing it. Use when the user asks to merge a PR once it's good to go and CI is green, to babysit a PR until it merges, or picks the babysit-and-ship option that /next-options offers beside a PR watch.
---

# Babysit and ship

The user's request is their go to mark the PR ready and merge it, so no step below waits for another go except step 5. The work runs through two /pstack-mode playbooks, Babysit and then Shipping, and follows each one's rules. This skill adds only the order, the draft step, and the loop back after a failed verdict.

1. **Mark it ready.** Mark each draft PR ready for review, through the run's built-in PR tool or `gh pr ready <pr>`, so the full CI runs. Complete when `gh pr view <pr> --json isDraft` reads `false` for every PR.
2. **Babysit to merge-ready.** Run Babysit in `drive` mode. It handles conflicts, then review threads from people and bots such as Bugbot or Sentry Seer, then CI. In T3 Code, watch each PR with `watch_pull_request`, read status once per wake with Babysit's watcher and `--status-only`, and add no second loop. Complete when the watcher reports `READY`, or `WAITING` with reason `merge-queue` for a queued stack.
3. **Verify and land.** Run Shipping. A verifier agent that didn't write the code runs the change, and only the verified run lands, bottom-up. Complete when each PR reads merged into trunk in `gh pr view <pr> --json state,baseRefName`.
4. **Loop back on a failed verdict.** Fix a `FAIL` on the PR's own branch and return to step 2 for that PR. The push changes the patch, so Shipping's patch-id rule makes the PR's old verdict stale. After a second `FAIL` on the same PR, stop, and bring the user both fixes and why each failed, as /principle-attack-the-premise asks.
5. **Stop where only the user can act.** Stop the watch with `unwatch_pull_request` and bring the user each item with its link. That covers a required human approval, a check that /next-options' manual-checks rule reports as waiting on a person, such as a Chromatic baseline, a bot finding that Babysit's triage classes as `ask`, and a rebase that Babysit reports instead of making. When the user answers, resume at step 2.

**Complete when** every PR reads merged into trunk and every watch you started is stopped. The reply names what landed, each PR's verdict and the agent that produced it, and the merge read-back.
