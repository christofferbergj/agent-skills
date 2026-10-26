# Maintain an owned Pstack adaptation

The initial adaptation covers the 54 registered skills in upstream Pstack and their supporting playbooks, prompts, and scripts as an owned adaptation for Codex and Claude Code. The three dormant Benny automation workflows are outside this scope.

Preserve each workflow's purpose and evidence requirements. Adapt worker counts, model choices, and continuous loops to the task, available capabilities, and budget.

Namespace new skills as `pstack-*`, reuse the existing identical `bro` skill, and maintain an upstream-to-local mapping. This prevents collisions with other installed skills and makes upstream comparisons traceable. The revision below drops the prefix.

Proceed autonomously within agreed scope. Pause when scope or an approved interface changes, or repeated failures require a decision. Deliver draft pull requests by default and honor existing authorization for further actions.

## Revisions

- **2026-10-26, upstream names.** Pstack skills now keep their upstream names, as Matt Pocock's, Thermos, and the other sources do. The prefix had come to suggest a skill works only in Pstack mode, while each one works alone and several serve the whole library: `/swarm` runs `/review-loop`'s counterpart, and Matt's flow invokes `/principles` and the principles. It also made every upstream sync rewrite each cross-reference. `suite.json` already traces each skill to its upstream, and of the 58 upstream names only `tdd` collides with an installed skill, Matt Pocock's, so Pstack's stays `pstack-tdd`. The entrypoints stay `pstack-mode`, `pstack-help`, and `pstack-setup`, because upstream names two of them after the author's handle and the three share the suite's name. The first-party selector `pstack-principles` became `principles`. The adaptation contract's names rule now covers every source, and the catalog check rejects a rename without a recorded reason.
