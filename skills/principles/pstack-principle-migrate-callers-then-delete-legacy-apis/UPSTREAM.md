# pstack-principle-migrate-callers-then-delete-legacy-apis: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `f713f14203cd6420cec13cd7c55c32d598dbab68`.
- Last upstream review: 2026-10-16.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- Allow shared selection by /pstack-principles in ordinary Matt and Pstack workflows; applicability does not require Pstack mode. Keep this skill as the single owner of its principle rules. Own the choice between coordinated internal migration and justified expand-contract, including caller inventory, real compatibility obligations, bounded migration tickets, phase checks, dependent-work gates, and final acceptance.

- Keep explicit caller inventory, deletion, temporary-adapter and test-migration rules in this callable dependency, with its external-compatibility applicability limits.

- Namespace: `principle-migrate-callers-then-delete-legacy-apis` maps to `pstack-principle-migrate-callers-then-delete-legacy-apis`. Preserve the installed name and invocation metadata.
- Support Codex and Claude Code through native tool schemas and explicit dependency invocation. Shared execution is owned by `/pstack-swarm`.
- Preserve workflow outcomes and evidence; scale effort to scope and budget. Prefer cross-vendor review with a disclosed independent-native fallback.
- Honor repository conventions and existing authorization. Default to draft pull requests; prepare learning-driven source edits for review.
- `agents/openai.yaml` and local runtime, maintenance, and validation resources are owned here.

## Maintenance

Invoke `/pstack-mode` for its suite-maintenance reference, or read its `MAINTENANCE.md` from the source checkout during `/maintain-skills`. That owner tracks the complete suite inventory, supporting wrappers, scripts, guides, and licenses. Installing from this repository refreshes adaptations; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                           |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | Removed duplicate introduction and rationale. Retained explicit caller inventory, deletion, timeboxed adapters, test migration and applicability rules for this callable dependency; inspected the refactoring consumer. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md). |
