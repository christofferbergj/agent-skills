# sharpen: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/sharpen/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/sharpen/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Execute the sharpened task, keeping one outside correctness check. The body keeps the imported revision's wording, which already carries upstream's expert approach, raw material, methods, outside check, deeper-not-bigger, and user-owned choices. Since `88d4751` upstream returns only a rewritten prompt; that is excluded because the skill is model-invoked before a Pstack task runs, and prompt-only output would halt the task it was invoked for.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                           |
| 2026-10-20  | `88d47514b82e7c44f00f2b2a72ff6dd12158038c` | Reviewed both intermediate removal of the rewritten-prompt ban and the final upstream prompt-rewrite-only reversal. Deliberately retained the documented local model-invoked execute-task outcome and matching metadata: changing implicit invocation into prompt-only output would break that local contract. No automatic consumer or installation policy changes are needed. Complete source/shared comparison, repository gates and independent native review pass. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `88d4751` in `pstack/skills/sharpen/`. First fidelity check: every current upstream rule survives in the imported wording except the prompt-only output, which the recorded divergence covers; that divergence still holds because /pstack-mode invokes this skill mid-task. Named the retained wording in the record.                                                                                                                         |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                  |
