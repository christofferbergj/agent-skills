# pstack-maintain-verification-skill: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/maintain-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/maintain-verification-skill/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Model-invoked, where upstream is user-invoked: a Pstack helper that /pstack-help routes to, with a description that scopes triggering to Pstack tasks.
- Looks for the target under `.agents/skills/verify-*/`, matching where /pstack-create-verification-skill generates it, instead of upstream's `.cursor/skills/`.
- Reads and reconciles project artifacts through /domain-modeling before the audit.
- Each step ends with a completion criterion, per the repository's skill rules.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                      |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change in `pstack/skills/maintain-verification-skill/` since `e5136d8`. First fidelity check: every upstream rule survives; the source wave's /pstack-swarm delegation and the draft PR follow library-wide adaptations. Recorded the model-invoked mode, target location, domain-modeling step, and completion criteria. Tools and conventions pass. |
