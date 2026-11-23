# principle-outcome-oriented-execution: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/principle-outcome-oriented-execution/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/principle-outcome-oriented-execution/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9`.
- Fidelity checked through: `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9`.
- Last upstream review: 2026-11-23.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- None beyond the library-wide adaptations.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                   |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Audit: no upstream change to the skill since `e5136d8`. Compared every upstream rule and recorded divergence in both directions. Recorded the invocation-mode change; the existing migration-owner delegation is still present and needed. No SKILL.md change. Invocations resolve, metadata matches model invocation, and catalog validation passes.           |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                          |
| 2026-11-23  | `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9` | Audit: closeness re-check against the owner's rule on #113. No upstream change since the last review. Restored upstream's guardrails by dropping the added migration-owner bullet: it was an added rule no host needs, and it routed planned rewrites toward staged coexistence beside the Refactoring playbook's no-shims rule. Both fidelity directions pass. |
