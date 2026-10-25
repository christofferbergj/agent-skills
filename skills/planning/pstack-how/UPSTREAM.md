# pstack-how: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/how/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/how/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `99b609a72323b70204eab407c622f436e858e112`.
- Last upstream review: 2026-10-25.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Without delegation, run the explorer and explainer passes sequentially and disclose it; upstream assumes Cursor's Task tool.
- Step 4 names /pstack-why as the owner of rationale, which upstream's description carried.
- `references/explainer-prompt.md` tells the explainer to read and search with the host's read-only tools where upstream names `Read, Grep, and Glob`: Codex has no tools by those names, and Claude Code leaves Glob and Grep out of its default tool set on macOS, Linux, and WSL.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                    |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8` in `pstack/skills/how/`. First fidelity check: restored upstream's opening scope, stating an interpretation of an ambiguous scope, the simple and complex paths with "when in doubt, take the simple path", 2 to 4 angles spawned in one message, synthesis after all explorers return, and presenting without substantial rewriting; the reference prompts differ only in blank lines. Recorded the model-invoked mode, the /domain-modeling preamble, the sequential fallback, and the completion criteria. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 2026-10-25  | `99b609a72323b70204eab407c622f436e858e112` | No upstream change since `190d287` in `pstack/skills/how/`. Current-tools review: replaced the explainer prompt's `Read, Grep, and Glob` with the host's read-only tools, because Claude Code's tools reference marks Glob and Grep absent by default on macOS, Linux, and WSL and Codex has no such tools. Fidelity check passes in both directions.                                                                                                                                                                                            |
