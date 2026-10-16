# pstack-typescript-best-practices: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/typescript-best-practices/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/typescript-best-practices/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `f713f14203cd6420cec13cd7c55c32d598dbab68`.
- Last upstream review: 2026-10-16.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- A duration stored as a plain number still needs boundary validation; preserve the corrected example rather than promising that the field shape excludes negative values.
- Distinguish unchecked assertions from `as const` and validated brands. Preserve the explicit `Config` type and contextual-inference caveat in the `satisfies` example.

- Namespace: `typescript-best-practices` maps to `pstack-typescript-best-practices`. Preserve the installed name and invocation metadata.
- Support Codex and Claude Code through native tool schemas and explicit dependency invocation. Shared execution is owned by `/pstack-swarm`.
- Preserve workflow outcomes and evidence; scale effort to scope and budget. Prefer cross-vendor review with a disclosed independent-native fallback.
- Honor repository conventions and existing authorization. Default to draft pull requests; prepare learning-driven source edits for review.
- `agents/openai.yaml` and local runtime, maintenance, and validation resources are owned here.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                   |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                              |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | No upstream file delta. Corrected the duration example: a plain number admits negative, infinite and NaN values, which require boundary validation. Compiled and executed all three counterexamples; retained other concrete type guidance. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md). |

Further local maintenance on 2026-10-16 corrected the assertion and `satisfies` guidance. TypeScript 7.0.2 declarations and Node execution confirm const assertions, validated brands, and the distinct literal-union versus broad-string inference. Repository checks pass; the already reviewed candidate is unchanged. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md).
