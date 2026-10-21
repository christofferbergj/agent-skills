# pstack-principle-never-block-on-the-human: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/principle-never-block-on-the-human/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/principle-never-block-on-the-human/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Remain model-invoked; upstream is user-invoked. /pstack-principles discovers installed principle descriptions and applies the matching principles in each phase of both suites, so the principle must stay visible to the model.
- Beyond the library-wide authority adaptation, which honors authorization already given for irreversible actions, reversible actions proceed only within the user's grant, and the human also owns interview confirmation and explicitly requested approval checkpoints; a later incompatible change to an approved contract returns to that decision gate. Reason: principles operate within the calling phase and accepted scope, and Matt's interview keeps its confirmation boundary.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                      |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                 |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Audit: no upstream change to the skill since `e5136d8`. Compared every upstream rule and recorded divergence in both directions. Recorded the invocation-mode change; merged the existing authorization divergence into one entry that names the rewording of the last three rules and its reason. No SKILL.md change. Invocations resolve, metadata matches model invocation, and catalog validation passes. |
