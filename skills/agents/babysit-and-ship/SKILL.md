---
name: babysit-and-ship
description: Takes a PR or stack through to merged, with Pstack's independent verifier before each merge. Use when the user asks to merge a PR once it's good to go and CI is green, to see a PR through to merge, or picks the babysit-and-ship option.
---

# Babysit and ship

The user's request is their go to mark the PR ready and merge it. The work runs through two playbooks of the installed /pstack-mode skill: read its `playbooks/babysit.md` and `playbooks/shipping.md` from the path the host's skill index gives, and follow them except where a step below says otherwise. In a coordinator thread, the coordinator's merge step owns this go instead.

1. **Mark the frontier ready.** Mark the lowest unmerged PR ready for review, through the run's built-in PR tool or `gh pr ready <pr>`, so its full CI runs, and mark each later PR ready when it becomes the frontier. This replaces both playbooks' rule that a draft stays a draft until its own merge, so pass Babysit's watcher no `--allow-draft`. Complete when `gh pr view <pr> --json isDraft` reads `false` for the frontier.
2. **Babysit.** Run Babysit in `drive` mode, whatever the PR's size. Complete when Babysit's `drive` stop condition holds for the frontier.
3. **Ship.** Run Shipping. Complete when its ceiling is the top of the stack and every PR reads merged into trunk.
4. **Loop back on a failed verdict.** Fix a `FAIL` on the PR's own branch and return to step 2 for that PR. When two fixes for the same verifier finding have failed, apply /principle-attack-the-premise before the next one.
5. **Stop where only the user can act.** Stop the watch or loop and bring the user each item with its link: a required human approval; a check that waits on a person, such as a Chromatic baseline; a bot finding Babysit's triage classes as `ask`; a rebase Babysit reports instead of making; a push to a branch someone else owns, or one that would dismiss an approval; and a check that still fails after the root-cause fix. When the user answers, resume at step 2.

**Complete when** every PR reads merged into trunk, every watch or loop you started is stopped, and the reply is Shipping's.
