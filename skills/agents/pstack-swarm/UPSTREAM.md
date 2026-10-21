# pstack-swarm: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/swarm/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/swarm/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Model-invoked, where upstream `swarm` is user-invoked: it is the shared delegation owner, so other skills' prose must be able to load it.
- Local-only files: `references/execution.md`, the host execution contract that replaces Cursor's Task-tool and model-rule mechanics, and `scripts/review.py` with its tests, the bounded cross-vendor CLI wrapper.
- Match review briefs to the restricted reviewer's readable scope. Supply recorded checks and inline snapshots for inaccessible evidence; use a native critic when independent execution or broader evidence access is required.
- Route counterpart critics through T3 Code child tasks when the session exposes `delegate_task`, before the CLI wrapper, and pass an explicit counterpart model and scope-scaled effort on every route ([T3 route](references/t3.md)). The T3 route is principle-derived from the second source below.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                   |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | Reviewed the upstream cuts; retained the already-adapted host, budget, isolation and terminal-evidence contract. Native delegates and restricted Claude synthesis exercised the current owner without restoring Cursor cloud or model defaults. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md).                                                  |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `f713f14` in `pstack/` or since `e8db4fa` in the tracked Oliver files. First fidelity check: restored four dropped upstream rules (a task list per phase, naming each model-race arm, listing every provable issue, and no raw worker output in the report), and recorded the model-invoked mode and the local-only execution contract and review wrapper. The Oliver T3 route passes both directions. |

Local maintenance on 2026-10-17 clarified the restricted reviewer's evidence scope. The Claude wrapper exposes `Read,Glob,Grep` without a shell, and its restricted session denied external runtime paths. Supply relevant snapshots inline and recorded checks; use a native critic for independent execution. The reviewed source candidate is `101b274dd991f694e1f7024be2157e5f3adf07de`; portable host behavior and source exclusions are retained.

## Second source: T3 delegation

- Original author: Oliver Cederborg.
- Source repository: [olivercederborg/skills](https://github.com/olivercederborg/skills).
- Original skill: [`orchestrate/SKILL.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/orchestrate/SKILL.md), for its T3 Code section.
- Supporting sources: [`shared/t3-delegation.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/shared/t3-delegation.md), the delegation guide that section follows.
- Tracking policy: upstream `main`, reviewed as a principle source under the adaptation contract's [principle-derived skills](../../agents/maintain-skills/references/ADAPTATION.md#principle-derived-skills).
- Imported from commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Reviewed through commit: `f3e4c1001f8483c2e07d98d452cb5d8466f3358c`.
- Fidelity checked through: `f3e4c1001f8483c2e07d98d452cb5d8466f3358c`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Oliver Cederborg](LICENSE), the second notice in that file. Retain it with `references/t3.md`.

### Local adaptations to preserve

Adopted principles: cross-provider critics run as tracked T3 child tasks; every call names the model and effort; the brief is the child's whole context and passes files by absolute path; a stable `clientRequestId` per task; read-only critics in plan mode; a critic returns findings as its final message, and a writer returns a short report naming a file; a failed optional critic is reported, and the work continues without it.

Departures: the counterpart's model and effort come from the execution contract's table or the personal configuration, not a role table of writers and sketchers; a new key for each retry attempt; collection through a repeated `wait` call; T3 is the first of three routes, ahead of the CLI wrapper and a native critic; Oliver's owner threads, report-file paths, thread-paging rules, and eval players are left out.

Decide upstream changes to these files by the principle-derived rules. The 2026-10-20 import adapted the T3 section and guide; plan-mode children of both vendors and a repeated `wait` call collecting an async child were exercised in T3 Code, and the CLI wrapper's model and effort flags pass unit tests and a preflight on both real CLIs.
