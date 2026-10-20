# pstack-typescript-best-practices: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/typescript-best-practices/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `0b8e952052d482ee6de06deebf14d590d77b1b34`.
- Last upstream review: 2026-10-18.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- A duration stored as a plain number still needs boundary validation; preserve the corrected example rather than promising that the field shape excludes negative values.
- Distinguish unchecked assertions from `as const` and validated brands. Preserve the explicit `Config` type and contextual-inference caveat in the `satisfies` example.
- Demonstrate the guaranteed first position of a non-empty tuple; dynamic numeric indexes still require narrowing under `noUncheckedIndexedAccess`.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | No upstream file delta. Corrected the duration example: a plain number admits negative, infinite and NaN values, which require boundary validation. Compiled and executed all three counterexamples; retained other concrete type guidance. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md).                                                                                                                                                                                                                                                                                                              |
| 2026-10-17  | `101b274dd991f694e1f7024be2157e5f3adf07de` | No skill-resource delta. Retained the local type rules after reviewing shared source changes. Replaced random indexing in the non-empty tuple example with its guaranteed first position and explained unchecked dynamic indexing. The exact good snippet fails before with TS2322 and compiles after under TypeScript 7.0.2 with strict and noUncheckedIndexedAccess. Repository checks pass.                                                                                                                                                                                                                                                                                          |
| 2026-10-18  | `0b8e952052d482ee6de06deebf14d590d77b1b34` | Reviewed the upstream verifying-type-guard branding example and guard-only policy. Retained the validated constructor assertion because it follows a real boundary check and is an equally valid TypeScript pattern; the compiler trusts user-defined guards too, so requiring a guard adds no correctness guarantee. Preserved the stricter indexing correction and the local numeric-range, satisfies, schema, and boundary adaptations. Clarified parser-specific ProtoJSON compatibility options and removed a false argument-swap comment. Both brand variants compile under TypeScript 7.0.2 with strict unchecked indexing. Repository gates and independent native review pass. |

Further local maintenance on 2026-10-16 corrected the assertion and `satisfies` guidance. TypeScript 7.0.2 declarations and Node execution confirm const assertions, validated brands, and the distinct literal-union versus broad-string inference. Repository checks pass; the already reviewed candidate is unchanged. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md).
