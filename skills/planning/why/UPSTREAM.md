# why: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/why/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/why/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `99b609a72323b70204eab407c622f436e858e112`.
- Last upstream review: 2026-10-25.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- `references/synthesizer-prompt.md` puts upstream's placeholder citation `[PR #123](url)` in a code span, because the repository's link check rejects `url` as a broken link.
- `references/sources/slack.md` says the Slack MCP may require MCP authentication where upstream names Cursor's `mcp_auth` tool, which neither Codex nor Claude Code provides.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8` in `pstack/skills/why/`. Re-imported `SKILL.md` and all twelve reference files from upstream at the owner's direction, restoring the operating posture, the seven-category roster with its "Best at" guidance, "Always spawn" source control, the two quoted skip reasons, "do not rewrite the confidence language", the Output Format section list, and Common Failure Modes. Applied only the library-wide adaptations; the references differ from upstream only by formatter output and the placeholder-link divergence. `catalog.py validate` passes. |
| 2026-10-25  | `99b609a72323b70204eab407c622f436e858e112` | No upstream change since `190d287` in `pstack/skills/why/`. Current-tools review: replaced the Slack playbook's Cursor-only `mcp_auth` with MCP authentication; the `gh pr view --json` fields and git commands match `gh` 2.103.0 and git 2.56.0. Fidelity check passes in both directions.                                                                                                                                                                                                                                                                                                 |
