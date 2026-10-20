# review-loop: source and local adaptations

## Source and credit

- Original author: Oliver Cederborg.
- Source repository: [olivercederborg/skills](https://github.com/olivercederborg/skills).
- Original skill: [`review-loop/SKILL.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/review-loop/SKILL.md).
- Tracking policy: upstream `main`, reviewed as a principle source under the adaptation contract's [principle-derived skills](../../agents/maintain-skills/references/ADAPTATION.md#principle-derived-skills).
- Imported from commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Reviewed through commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Fidelity checked through: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Last upstream review: 2026-10-20.
- Attribution-only source: https://gist.github.com/olivercederborg/92236670065aaa661db221f22203ded5 is Oliver's handover gist. Its `review-loop-SKILL.md` matches the tracked file at the imported commit, so the repository is tracked instead. The gist's `t3-delegation.md` is tracked by /pstack-swarm's record.
- License: [MIT, copyright 2026 Oliver Cederborg](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

The wording is first-party. These are the principles taken from the source and the deliberate departures.

Adopted principles:

- The other vendor's model reviews what the current one wrote: Codex from Claude, Claude Opus from Codex.
- Round 1 runs both models in parallel, and the coordinator verifies every finding against the code before acting, adds none of its own, and merges findings by root cause with who raised each.
- Blocker, Cleanup, and Optional severities, with a fix, follow-up, or skip call per finding.
- One go runs the whole loop. Later rounds review only the delta, with only the counterpart, and are skipped when every fix was local and its checks pass.
- Three rounds at most; a repeated class of finding stops the loop for a premise check; an autonomous run puts open findings at the top of the PR description.
- Plans and specs are reviewable targets.
- In T3 Code the counterpart is a tracked child task with an explicit model and effort, launched read-only in plan mode.

Departures:

- The same-model pass is /code-review's Standards and Spec axes, not a second generic reviewer with a byte-identical prompt, so the library's review rubric, smell baseline, and selected principles keep one owner.
- Effort scales with scope: full reviews run at `max` for Codex and `xhigh` for Claude, delta reviews at `xhigh` and `high`. The source uses `high` for every round.
- The loop is the final review of /implement, /implement-spec, and Pstack's implementation playbooks, through a library-wide adaptation, instead of a separate step after a verify-work skill.
- A script builds the packet with pinned revisions, a working-tree snapshot commit, and excluded lockfiles, binaries, and generated or vendored files. Packets live in a temporary directory: plan-mode T3 children of both vendors read it there, and a route that cannot, such as the restricted Claude CLI, gets the packet pasted into its brief.
- Outside T3 Code, /pstack-swarm's other routes keep the loop working: the bounded CLI wrapper, then a labeled same-model critic.
- Oliver's shared chat format, lens skills (`coding-standards`, `grounding`, `taste`), and `verify-work`, `autopilot`, `architect`, and `open-pr` handoffs map to /code-review, /pstack-principles, /pr, and /pstack-principle-attack-the-premise. The merge gate and verdict recording, Franklin and Linear specifics, and reply layout are excluded.

`agents/openai.yaml`, `references/reviewer-brief.md`, the `scripts/` directory, and this record are locally maintained.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep. Decide each upstream change to the tracked files by the principle-derived rules; /pstack-swarm's record tracks Oliver's delegation guide. Advance the reviewed-through position only after the delta is decided and checks pass.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-20  | `e8db4fa3e2468a0b9e0297955367ff6efde28dee` | Adapted the review loop as principles and mapped Oliver's supporting concepts to this library's owners, as ADR 0004's concept map records. The change itself ran through the loop: round 1 paired a Codex `gpt-6.1-sol` `max` review with /code-review's two Claude axes, and rounds 2 and 3 were Codex `xhigh` delta reviews. Round 3 was Clean. All 16 verified findings were fixed, and three smaller suggestions were skipped with reasons. Rounds 1 and 2 both found snapshot gaps, so a premise check replaced the index-seeding fix with a tested matrix of index states. Packet, hook, and wrapper tests pass. |
