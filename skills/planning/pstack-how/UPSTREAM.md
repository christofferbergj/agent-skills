# pstack-how: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/how/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Model-invoked, where upstream is user-invoked: /pstack-architect, /pstack-blast-radius, /pstack-why, /pstack-teach, and other skills invoke it for walkthroughs, so the model must be able to load it.
- Open with the /domain-modeling invocation that reads the project's configured artifacts and reports documentation drift without edits; that skill is the shared owner of project vocabulary.
- Without delegation, run the explorer and explainer passes sequentially and disclose it; upstream assumes Cursor's Task tool.
- End each step with a completion criterion, following the repository's rule that steps end on checkable criteria; step 4 names /pstack-why as the owner of rationale, which upstream's description carried.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                      |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8` in `pstack/skills/how/`. First fidelity check: restored upstream's opening scope, stating an interpretation of an ambiguous scope, the simple and complex paths with "when in doubt, take the simple path", 2 to 4 angles spawned in one message, synthesis after all explorers return, and presenting without substantial rewriting; the reference prompts differ only in blank lines. Recorded the model-invoked mode, the /domain-modeling preamble, the sequential fallback, and the completion criteria. |
