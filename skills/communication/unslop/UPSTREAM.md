# unslop: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/unslop/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/unslop/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `b4a4f6151b8e77f8d71045f09f553a733cf0ed37`.
- Fidelity checked through: `b4a4f6151b8e77f8d71045f09f553a733cf0ed37`.
- Last upstream review: 2026-11-17.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- The description scopes triggering to Pstack output and to prose submitted for editing.
- `<!-- prettier-ignore -->` precedes the rule list, so the repository formatter keeps upstream's gapped rule ids instead of renumbering them.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8`. First fidelity check: restored upstream rule ids 5 (vague attributions) and 22 (sycophantic tone), which a local renumbering had changed although the skill says rule numbers are stable ids. Recorded the model-invoked mode and description.                                                                                                                                                                                                                                                                                                                                    |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-11-17  | `b4a4f6151b8e77f8d71045f09f553a733cf0ed37` | Upstream `2f87c85` (shorter skill texts) is the only change since `190d287`. It replaces the category headings and long pattern entries with one terse numbered list, keeping every rule id (gaps at 1, 2, 4, 6, and 21), and trims the AI-vocabulary and abstract-metaphor word lists. Adopted as written. Adapted the formatter divergence: one `<!-- prettier-ignore -->` now precedes the single list instead of two category lists, so the formatter keeps the stable ids. The only cited id outside this skill, /pstack-mode's rule 14, still means the mid-sentence colon. Fidelity passes in both directions. |
