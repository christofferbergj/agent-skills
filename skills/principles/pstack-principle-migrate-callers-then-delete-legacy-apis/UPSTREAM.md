# pstack-principle-migrate-callers-then-delete-legacy-apis: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Own the choice between coordinated internal migration and justified expand-contract, including caller inventory, real compatibility obligations, bounded migration tickets, phase checks, dependent-work gates, and final acceptance. The description and body are rewritten as ordered steps for that choice. Reason: the [library architecture](../../../docs/architecture.md) makes this skill the migration-strategy owner that both suites' workflow owners defer to, so it must also cover the external-compatibility case upstream leaves out of scope.
- Keep explicit caller inventory, deletion, temporary-adapter and test-migration rules in this callable dependency, with its external-compatibility applicability limits. Upstream cut the caller-inventory, deletion, and time-boxed-adapter rules as marginal in `99743e9`; they stay because callers invoke this skill for exactly those rules.
- Remain model-invoked; upstream is user-invoked. /pstack-principles discovers installed principle descriptions and applies the matching principles in each phase of both suites, so the principle must stay visible to the model.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                           |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | Removed duplicate introduction and rationale. Retained explicit caller inventory, deletion, timeboxed adapters, test migration and applicability rules for this callable dependency; inspected the refactoring consumer. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md). |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Audit: no upstream change to the skill since `f713f14`. Compared every upstream rule and recorded divergence in both directions. Recorded the invocation-mode change and added reasons, with the upstream `99743e9` comparison, to both existing divergences. No SKILL.md change. Invocations resolve, metadata matches model invocation, and catalog validation passes. |
