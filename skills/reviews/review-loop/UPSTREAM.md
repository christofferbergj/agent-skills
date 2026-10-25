# review-loop: source and local adaptations

## Source and credit

- Original author: Oliver Cederborg.
- Source repository: [olivercederborg/skills](https://github.com/olivercederborg/skills).
- Original skill: [`review-loop/SKILL.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/review-loop/SKILL.md).
- Tracking policy: upstream `main`, reviewed as a principle source under the adaptation contract's [principle-derived skills](../../agents/maintain-skills/references/ADAPTATION.md#principle-derived-skills).
- Imported from commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Reviewed through commit: `f3e4c1001f8483c2e07d98d452cb5d8466f3358c`.
- Fidelity checked through: `f3e4c1001f8483c2e07d98d452cb5d8466f3358c`.
- Last upstream review: 2026-10-21.
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

- The same-model pass is /code-review's Standards and Spec axes plus a correctness and security critic on /thermo-nuclear-review's rubric, not a second generic reviewer with a byte-identical prompt. Each rubric keeps its one owner, and bugs get both models' review. Thermos's maintainability rubric stays a manual /thermos audit, because its presumptive structural blockers would become unrequested refactors in an automatic fix loop (user decision, 2026-10-20). The first round 1 in this shape, on the change that introduced it, ran Codex at `xhigh` beside the two /code-review axes and the correctness critic: Codex found nothing, the Claude reviewers raised nine verified Cleanup or Optional findings, all fixed without a delta round, and three suggestions were skipped with reasons.
- When Codex is the counterpart and the diff changes code that runs, round 1 adds a second Codex task, the counterpart correctness pass, on /thermo-nuclear-review's rubric. Codex raised most of the verified Blockers in a count of the user's loops, and the user favors Codex usage and review quality over saving usage (ADR 0004, 2026-10-25). The same-model correctness critic stays until that revision's trial decides between them.
- Effort is explicit and scales with scope: both vendors run full reviews at `xhigh` and delta reviews at `high`, and GPT models never run above `xhigh`. The source uses `high` for every round.
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
| 2026-10-21  | `f3e4c1001f8483c2e07d98d452cb5d8466f3358c` | No upstream change to the tracked files. The report example now leads with the bold verdict that the text and /reply-shape require. Packet tests pass.                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

A Codex-led trial on 2026-10-20 ran the loop in a throwaway repository with Codex `gpt-6.1-sol` as the main agent. It dispatched Claude Opus 5.5 at `xhigh` as a T3 plan-mode child beside three native Codex critics, and T3's thread records confirm all four. Every reviewer reported Clean on a correct change. Its notes on delta-round refreshes and the PR handoff clarified steps 5 and 4. A second Codex-led trial gave the loop a committed implementation with two planted defects: a trailing window that dropped the current page, and a zero width returned silently instead of rejected. Round 1 had Claude Opus at `xhigh` plus three native Codex critics; every reviewer raised the width defect, and Claude, Spec, and Correctness raised the trailing window. Codex verified and fixed three findings in separate commits, and round 2, a Claude Opus `high` delta review in a new T3 task, came back Clean. An independent check of the fixed function confirmed both defects gone. That trial's notes clarified same-model effort inheritance, the Claude plan-mode plan file, and axis-separate reports.
