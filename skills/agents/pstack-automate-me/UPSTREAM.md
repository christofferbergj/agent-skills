# pstack-automate-me: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/automate-me/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/automate-me/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Mining discovers and reads sessions through /pstack-recall instead of the Cursor `agent-transcripts/` path the system prompt names. Neither host names a transcript directory, and /pstack-recall's history script is the one owner that scopes Codex and Claude Code sessions to this repository, which keeps upstream's "don't cross workspace boundaries" rule enforceable.
- Step 0 treats installed copies as discovery inputs and edits the mode in its source repository. Skills CLI installs are copies that the next refresh overwrites, so an edit there is lost and silently changes other chats.
- Step 3 links upstream's `poteto-mode` SKILL.md at the candidate for section granularity. The local /pstack-mode is a playbook router and no longer shows a personal mode's sections.
- Step 3 sends recurring mistakes to /pstack-correct. Repeated corrections are mining's strongest signal, and Pstack's encode-lessons-in-structure principle prefers an enforcer to another rule; /pstack-correct owns that work.
- Step 4 keeps raw transcript quotes, organization details, and credentials out of the skill. Mining reads transcripts that can hold secrets and private context, and the mode is committed and opened as a PR.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8`. Re-imported from upstream text at the candidate, replacing the condensed rewrite: restored the update-or-fresh confirmation, parallel slice mining with the 2+-slice cross-check, structured multiple-choice questions (no 20-question dump), the section clustering list, the placement and frontmatter rules, the Guardrails, Evaluation, and When not to use. Translated `create-skill` to /writing-for-agents, `AskQuestion` to the host's structured question tool, Cursor skill paths to Codex and Claude Code paths, and the PR to a draft. Kept /pstack-recall mining, the installed-copy rule, /pstack-correct, and the privacy rule with recorded reasons; dropped the local isolated-example validation, which upstream's Evaluation rejects. Final review: a numbered-list fallback covers hosts whose question tool takes one choice or is absent. |
