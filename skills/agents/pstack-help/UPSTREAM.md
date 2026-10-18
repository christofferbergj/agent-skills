# pstack-help: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/poteto-help/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/poteto-help/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `0b8e952052d482ee6de06deebf14d590d77b1b34`.
- Last upstream review: 2026-10-18.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- Route whole-library upkeep through /maintain-skills and read cadence and model from the saved maintenance automation rather than duplicating its settings in help text.

- Namespace: `poteto-help` maps to `pstack-help`. Preserve the installed name and invocation metadata.
- Support Codex and Claude Code through native tool schemas and explicit dependency invocation. Shared execution is owned by `/pstack-swarm`.
- Preserve workflow outcomes and evidence; scale effort to scope and budget. Prefer cross-vendor review with a disclosed independent-native fallback.
- Honor repository conventions and existing authorization. Default to draft pull requests; prepare learning-driven source edits for review.
- `agents/openai.yaml` and local runtime, maintenance, and validation resources are owned here.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                       |
| 2026-10-18  | `0b8e952052d482ee6de06deebf14d590d77b1b34` | Adapted the new formal-verification route as an explicitly user-invoked entrypoint. Reviewed the expanded ketchup route; retained the concise local catch-up pointer because the behavior belongs to its owner. Preserved local Skills CLI installation and host-capability guidance. The formal entrypoint retains matching explicit-user metadata and its writing companion. Repository gates and independent native review pass. |
