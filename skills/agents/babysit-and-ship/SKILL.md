---
name: babysit-and-ship
description: Takes a PR or stack through to merged, with Pstack's independent verifier before each merge. Use when the user asks to babysit a PR and merge it, to merge it once it's good to go and CI is green, or picks the babysit-and-ship option.
---

# Babysit and ship

The user's request is their go to mark the PR ready and merge it. The work runs through two playbooks of the installed /pstack-mode skill: read `~/.agents/skills/pstack-mode/playbooks/babysit.md` and `shipping.md` beside it (or in the `playbooks/` folder of /pstack-mode, if installed elsewhere), and follow them except where a step below says otherwise. In a coordinator thread, the coordinator's merge step owns this go instead.

Work one frontier, the lowest unmerged PR, at a time through steps 1 to 3, then repeat them for the next frontier until every PR has merged.

1. **Mark the frontier ready.** Mark it ready for review, through the run's built-in PR tool or `gh pr ready <pr>`, so its full CI runs. This replaces both playbooks' rule that a draft stays a draft until its own merge, so pass Babysit's watcher no `--allow-draft`. Complete when `gh pr view <pr> --json isDraft` reads `false` for the frontier.
2. **Babysit.** Run Babysit in `drive` mode, whatever the PR's size, and start Shipping's independent verifier beside it. In T3 Code, watch the frontier with `watch_pull_request`, which owns the wakes, and at each wake read status once with Babysit's `scripts/watch-pr/watch-pr --pr <pr> --status-only` instead of polling; it also reads the unresolved review threads. At every wake, and before ending any turn while the frontier is open, run /next-options' `pr-waiting-on.ts <pr>`, which reads `ready` only when CI is green on the head and nothing waits on a person. `ready` meets the stop condition. On `running`, keep the watch and name in the reply the checks still running, since the merge waits on the host's next wake. Complete when the frontier is merge-ready, where Babysit's `drive` loop stops.
3. **Ship.** Run Shipping for the frontier, merging with `--match-head-commit <verified sha>` so only the verified head lands. Complete when it reads merged into trunk.
4. **Loop back on a failed verdict.** Fix a `FAIL` on the PR's own branch and return to step 2 for that PR. When two fixes for the same verifier finding have failed, apply /principle-attack-the-premise before the next one.
5. **Stop where only the user can act.** Stop the watch or loop and bring the user each item with its link: a required human approval; a check that waits on a person, such as a Chromatic baseline; a bot finding Babysit's triage classes as `ask`; a rebase Babysit reports instead of making; a push to a branch someone else owns, or one that would dismiss an approval; and a check that still fails after the root-cause fix. When the user answers, resume at step 2.

**Complete when** every PR reads merged into trunk, every watch or loop you started is stopped, and the reply is Shipping's.
