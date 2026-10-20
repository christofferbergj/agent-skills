# pstack-swarm: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/swarm/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/swarm/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `f713f14203cd6420cec13cd7c55c32d598dbab68`.
- Last upstream review: 2026-10-16.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Match review briefs to the restricted reviewer's readable scope. Supply recorded checks and inline snapshots for inaccessible evidence; use a native critic when independent execution or broader evidence access is required.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                       |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                  |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | Reviewed the upstream cuts; retained the already-adapted host, budget, isolation and terminal-evidence contract. Native delegates and restricted Claude synthesis exercised the current owner without restoring Cursor cloud or model defaults. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md). |

Local maintenance on 2026-10-17 clarified the restricted reviewer's evidence scope. The Claude wrapper exposes `Read,Glob,Grep` without a shell, and its restricted session denied external runtime paths. Supply relevant snapshots inline and recorded checks; use a native critic for independent execution. The reviewed source candidate is `101b274dd991f694e1f7024be2157e5f3adf07de`; portable host behavior and source exclusions are retained.
