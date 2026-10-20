# pstack-sharpen: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/sharpen/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/sharpen/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `88d47514b82e7c44f00f2b2a72ff6dd12158038c`.
- Last upstream review: 2026-10-20.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- Namespace: `sharpen` maps to `pstack-sharpen`. Preserve the installed name and invocation metadata.
- Remain model-invoked and execute the sharpened task, keeping one outside correctness check. Upstream is user-invoked (`disable-model-invocation: true`) and, since `88d4751`, returns only a rewritten prompt; both are excluded because the local skill triggers automatically before a Pstack task runs, and prompt-only output would halt the task it was invoked for.
- Support Codex and Claude Code through native tool schemas and explicit dependency invocation. Shared execution is owned by `/pstack-swarm`.
- Preserve workflow outcomes and evidence; scale effort to scope and budget. Prefer cross-vendor review with a disclosed independent-native fallback.
- Honor repository conventions and existing authorization. Default to draft pull requests; prepare learning-driven source edits for review.
- `agents/openai.yaml` and local runtime, maintenance, and validation resources are owned here.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                           |
| 2026-10-20  | `88d47514b82e7c44f00f2b2a72ff6dd12158038c` | Reviewed both intermediate removal of the rewritten-prompt ban and the final upstream prompt-rewrite-only reversal. Deliberately retained the documented local model-invoked execute-task outcome and matching metadata: changing implicit invocation into prompt-only output would break that local contract. No automatic consumer or installation policy changes are needed. Complete source/shared comparison, repository gates and independent native review pass. |
