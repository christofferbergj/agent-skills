# pstack-create-verification-skill: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/create-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/create-verification-skill/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Model-invoked, where upstream is user-invoked: /pstack-setup offers it and loads it when the user accepts, and /pstack-help routes to it, so its description scopes triggering to Pstack tasks.
- Generated skills live at `.agents/skills/verify-<app>/`, or the repository's existing skill-source convention, and are exposed to Claude Code through a `.claude/skills/` link or documented installation, instead of upstream's `.cursor/skills/`.
- Reads and reconciles project artifacts through /domain-modeling before generating the skill.
- Each step ends with a completion criterion, per the repository's skill rules.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                      |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change in `pstack/skills/create-verification-skill/` since `e5136d8`. First fidelity check: restored the feature-map example README to upstream, bringing back its maintained-source opening (read the index before driving, use the feature file as the recipe) and dropping a local collapsible restyle that generated maps would copy. Recorded the model-invoked mode, skill location, domain-modeling step, and completion criteria. Tools and conventions pass. |
