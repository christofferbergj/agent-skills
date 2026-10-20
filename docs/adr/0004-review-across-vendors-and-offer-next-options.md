# Review across vendors and offer lettered next options

Adopt two workflows from Oliver Cederborg's skills as principles, not text: a review loop in which the other vendor's model reviews what the current one wrote, and replies that end with lettered next steps. His setup is tied to his own skills, router, and repositories, so `review-loop` and `next-options` are first-party skills. Maintenance tracks his repository for ideas worth adopting, under the adaptation contract's principle-derived rules, instead of preserving his wording.

## Review loop

Each model misses things the other catches, so the **counterpart** reviews: Codex when Claude is the main agent, Claude Opus when Codex is. Round 1 runs the counterpart beside `/code-review`, whose Standards and Spec axes remain the library's single review rubric; the revisions below add a correctness critic. The coordinator verifies each finding against the code before acting, because reviewers make false claims. Later rounds review only the fixes, with only the counterpart. A three-round cap and a premise check on repeated findings keep the loop from chasing edge cases. `/implement`, `/implement-spec`, and Pstack's implementation playbooks end with the loop through a library-wide adaptation, so review needs no separate request.

In T3 Code the counterpart runs as a `delegate_task` child rather than a shell-launched CLI, because T3 shows, tracks, and cancels child tasks. Every route, the CLI wrapper included, sets the model and effort explicitly, because a T3 provider switch otherwise takes the first listed model, and Codex's default effort can be `low`. Full reviews run at `max` for Codex and `xhigh` for Claude, while delta reviews drop one level; the revisions below cap Codex at `xhigh`. `/pstack-swarm` owns this route next to its CLI wrapper and native fallback, so every cross-vendor critic in the library gains it, not only the loop.

## Next options

Lettered options at the end of a reply let the user steer with one letter, and the rule to keep working on reversible steps stays with `/pstack-principle-never-block-on-the-human`. A SessionStart hook loads the rules in both hosts. Global instructions would also reach native subagents, which report to a coordinator rather than to the user. The hook reads the installed skill, so a Skills CLI refresh updates the rules without a settings change. Installing it changes host settings, so it stays opt-in.

Oliver's hook skips T3 delegated tasks by reading T3's internal state database. This library instead tells delegated tasks, through the rules and `/pstack-swarm`'s briefs, to report without options. The hook then depends on no unversioned schema, at the cost of loading about 4,000 characters into each delegated session.

## Concept map

Each of Oliver's supporting concepts was checked against an existing owner before anything new was built:

| Oliver's concept                                          | This library                                                                                        | Decision                                                                  |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `review-loop`                                             | `review-loop`, with `code-review` and `thermo-nuclear-review` as its same-model pass                | New skill, principles adopted                                             |
| `orchestrate`'s T3 section and `shared/t3-delegation.md`  | `pstack-swarm`'s T3 route                                                                           | Added to the existing delegation owner                                    |
| `replies.md` and the reply-shape endings                  | `next-options`                                                                                      | New skill                                                                 |
| `reply-shape` layout: Status, Needs you, Details, cards   | none                                                                                                | Left out until wanted; only the endings are taken                         |
| `reply-shape-context.py`                                  | `next-options/scripts/session-start.ts`                                                             | Ported to TypeScript without the T3 database lookup                       |
| `grounding`                                               | the global research rules, `review-loop`'s verify step, and `pstack-principle-prove-it-works`       | Reused                                                                    |
| `shared/taste.md` and `coding-standards`                  | `pstack-principles`, `pstack-typescript-best-practices`, and `code-review`'s standards and smells   | Reused                                                                    |
| `shared/format.md` severities and evidence lines          | `review-loop`'s brief and report                                                                    | Adopted inside the loop                                                   |
| `verify-work`, its merge gate, and verdict stamps         | `code-review` and `pstack-principle-prove-it-works`                                                 | Reused; the merge gate is left out                                        |
| `router.md` routes, stops, and autonomy                   | `pstack-mode`'s routing, `next-options`' stop list, and `pstack-principle-never-block-on-the-human` | Reused                                                                    |
| `autopilot`, `architect`, `open-pr`, `babysit`            | Pstack's playbooks, `pstack-architect`, and `pr`                                                    | Reused                                                                    |
| `t3-children-only.py`, which denies shell-launched agents | `pstack-swarm` names T3 as the first route                                                          | An instruction instead of a hook, since the wrapper is still the fallback |

## Revisions

- **2026-10-20, effort cap.** GPT models never run above `xhigh`, by the user's rule, so Codex runs at `xhigh` for full and delta reviews. Round 2 of this ADR's own review showed `xhigh` delta reviews still finding real defects. Claude keeps `xhigh` for full reviews and `high` for deltas.
- **2026-10-20, correctness critic.** Round 1's same-model pass adds a critic on `/thermo-nuclear-review`'s correctness and security rubric, so bugs get both models' review; before, Claude's side checked conformance only. The rubric's owner keeps its text. Thermos's maintainability rubric stays a manual `/thermos` audit, because its presumptive structural blockers would become unrequested refactors in a loop that fixes without asking. A full swap to Thermos was rejected because it drops `/code-review`'s Spec axis, which `/implement-spec` relies on.
