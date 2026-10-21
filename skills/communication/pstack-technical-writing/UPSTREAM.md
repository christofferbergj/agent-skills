# pstack-technical-writing: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/technical-writing/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/technical-writing/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Match the invoking repository's snippet formatting instead of prescribing tabs.
- Model-invoked, where upstream is user-invoked: /pstack-mode and its PR playbook apply it to documents and PR prose. The description keeps upstream's writing-or-reviewing branches and omits the command and layer names.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                            |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | No skill or resource delta; relevant suite inputs reviewed. Adapted snippet indentation to the invoking repository's formatting. Repository checks pass. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md).                                                        |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `f713f14`. First fidelity check: restored upstream's "as an addition to" wording for proposed unslop offenders, restored the reviewing and RFC branches to the description, and recorded the model-invoked mode. The snippet-formatting divergence is still present and needed. |
