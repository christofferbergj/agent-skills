# pstack-mode: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/poteto-mode/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/poteto-mode/SKILL.md), including its skill-local resources.
- Additional supporting sources: `pstack/agents/poteto-agent.md`, `pstack/.cursor-plugin/plugin.json`, `pstack/README.md`, and `pstack/docs/` at the same imported revision. The wrapper and guides inform routing and installation; no Cursor agent registration is required.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `f713f14203cd6420cec13cd7c55c32d598dbab68`.
- Last upstream review: 2026-10-16.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- Share phase-specific principle selection with Matt entrypoints through the locally authored /pstack-principles owner. Preserve explicit mode activation and keep suite.json as a source mapping rather than a second selection policy. The refactoring playbook uses the migration owner for compatibility and verification gates.

- Namespace: `poteto-mode` maps to `pstack-mode`. Preserve the installed name and invocation metadata.
- Support Codex and Claude Code through native tool schemas and explicit dependency invocation. Shared execution is owned by `/pstack-swarm`.
- Preserve workflow outcomes and evidence; scale effort to scope and budget. Prefer cross-vendor review with a disclosed independent-native fallback.
- Honor repository conventions and existing authorization. Default to draft pull requests; prepare learning-driven source edits for review.
- `agents/openai.yaml` and local runtime, maintenance, and validation resources are owned here.
- Keep one maintenance engine in `/maintain-skills`; `suite.json` remains this family's data source. Include category/shared files inside upstream skill roots.
- Preserve explicit review and unknown/blocked merge gates, cycle-safe stack traversal, forge-supplied immutable PR heads, active-over-historical PR selection, and verified trunk resolution. Hold an unverified Origin head API instead of substituting local refs.
- Keep polling sleeps, retries, and queued partial sweeps within the configured deadline. In-flight queries finish; this option does not cancel subprocesses.

- Combined-library integration delegates project artifacts to `/domain-modeling`, design vocabulary to `/codebase-design`, behavior testing to `/tdd`, Standards/Spec review to `/code-review`, and PR descriptions to `/pr` as applicable. Preserve these calls and the single-coordinator contract when updating.

## Maintenance

Invoke `/pstack-mode` for its suite-maintenance reference, or read its `MAINTENANCE.md` from the source checkout during `/maintain-skills`. That owner tracks the complete suite inventory, supporting wrappers, scripts, guides, and licenses. Installing from this repository refreshes adaptations; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                                                                           |
| 2026-10-16  | `f713f14203cd6420cec13cd7c55c32d598dbab68` | Reviewed complete source roots, resources, and shared inputs. Retained local guidance after the upstream README removed a redundant type-rule summary. Repaired local watcher deadlines with failing-before/passing-after public-runner evidence for interval/backoff overshoot, known-blocker priority, and early timer wakes. Preserved tier-major blockers, terminal query-error budgets, and incomplete-coverage limits. All 85 Bun tests and typecheck pass. Invocation and merge policies are unchanged. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md). |
