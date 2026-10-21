# pstack-interrogate: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/interrogate/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/interrogate/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Keep migration strategy and compatibility exceptions with /pstack-principle-migrate-callers-then-delete-legacy-apis; the review rubric invokes that owner instead of restating a conflicting rule.
- For a code diff, invoke /code-review for Standards/Spec coverage and keep its reports as separate axes in the verdict; /code-review is the shared owner of Standards and Spec review, and this skill adds the adversarial lens.
- Verify each finding against the code before bucketing it, and treat agreement as signal rather than proof.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                    |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | Adopted the lead-judgment cuts, including removal of the five-finding quota. The caller retains evidence-based dismissal and separate Standards/Spec axes. Current and legacy synthesis fixtures retain seven supported findings and disclose sequential coverage. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md).                                                                                                                                                |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `f713f14` in `pstack/skills/interrogate/`. First fidelity check: restored upstream's model-diversity framing and no-auto-apply rule, the scope bullets, the intent paragraph with its ask-if-unsure rule, the synthesis rules, the four bucket definitions, and the output template; the reference files differ only in the recorded rubric delegation and blank lines. Recorded the model-invoked mode, the /domain-modeling preamble, the /code-review delegation, finding verification, and the completion criteria. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
