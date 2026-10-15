# pstack-mode: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/poteto-mode/SKILL.md), including its skill-local resources.
- Additional supporting sources: `pstack/agents/poteto-agent.md`, `pstack/.cursor-plugin/plugin.json`, `pstack/README.md`, and `pstack/docs/` at the same imported revision. The wrapper and guides inform routing and installation; no Cursor agent registration is required.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Last upstream review: 2026-10-15.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- Namespace: `poteto-mode` maps to `pstack-mode`. Preserve the installed name and invocation metadata.
- Support Codex and Claude Code through native tool schemas and explicit dependency invocation. Shared execution is owned by `/pstack-swarm`.
- Preserve workflow outcomes and evidence; scale effort to scope and budget. Prefer cross-vendor review with a disclosed independent-native fallback.
- Honor repository conventions and existing authorization. Default to draft pull requests; prepare learning-driven source edits for review.
- `agents/openai.yaml` and local runtime, maintenance, and validation resources are owned here.

- Combined-library integration delegates project artifacts to `/domain-modeling`, design vocabulary to `/codebase-design`, behavior testing to `/tdd`, Standards/Spec review to `/code-review`, and PR descriptions to `/pr` as applicable. Preserve these calls and the single-coordinator contract when updating.

## Maintenance

Invoke `/pstack-mode` for its suite-maintenance reference, or read its `MAINTENANCE.md` from the source checkout during `/maintain-skills`. That owner tracks the complete suite inventory, supporting wrappers, scripts, guides, and licenses. Installing from this repository refreshes adaptations; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                      |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary. |
