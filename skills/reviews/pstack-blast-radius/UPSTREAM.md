# pstack-blast-radius: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/blast-radius/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/blast-radius/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `99b609a72323b70204eab407c622f436e858e112`.
- Last upstream review: 2026-10-25.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                       |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8` in `pstack/skills/blast-radius/`. First fidelity check: restored four dropped or softened upstream rules (pull the PR and commits through /pstack-why, spend the time on the one safety fact, the same evidence rules as /pstack-why, and ask more than one model and merge for a big or wide change), and recorded the model-invoked mode, the /domain-modeling preamble, the anchor-step pointer, and the completion criteria. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                              |
| 2026-10-25  | `99b609a72323b70204eab407c622f436e858e112` | No upstream change since `190d287` in `pstack/skills/blast-radius/`. Converged step 1 on upstream's `why` step 2 pointer as /pstack-why step 2 and dropped the anchor-step divergence: the local /pstack-why has kept upstream's numbering, with Step 2 as the code anchor, since its re-import in #19. Fidelity check in both directions; the remaining differences are library-wide adaptations.                                                                  |
