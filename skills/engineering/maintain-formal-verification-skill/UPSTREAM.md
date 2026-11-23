# maintain-formal-verification-skill: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/skills/maintain-formal-verification-skill/SKILL.md).
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `88d47514b82e7c44f00f2b2a72ff6dd12158038c`.
- Reviewed through commit: `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9`.
- Last upstream review: 2026-11-23.
- Fidelity checked through: `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9`.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE), retained from [pstack/LICENSE](https://github.com/cursor/plugins/blob/88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/LICENSE).

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- The description is a short human-facing summary, because the skill keeps upstream's user invocation and this repository gives user-invoked skills one.
- Updating the verify skill invokes /writing-for-agents, the shared owner of instruction writing.

## Maintenance

Invoke /maintain-skills for whole-library upkeep and the source/shared-input comparison. Keep this import fixed; advance reviewed-through only after the full relevant delta and required checks pass.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-20  | `88d47514b82e7c44f00f2b2a72ff6dd12158038c` | Imported the complete eligible formal-upkeep companion within the established verification scope. Adapted portable project-local discovery, explicit invocation, exact freshness accounting, draft/fallback routing, source-driven property updates, real-code controls and checkable completion. Cold native fixtures expose a new recovery writer after a code move, preserve the resulting code finding, distinguish a second semantic counterexample, and retain blocked/inconclusive/dirty/pending boundaries. Repository gates and independent native review pass.                              |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change in `pstack/skills/maintain-formal-verification-skill/` since `88d4751`, so the fidelity check at `88d4751` holds at this candidate. Tools and conventions pass: no fixed tool commands; /writing-for-agents and the formal-verification companions resolve; explicit user invocation matches `agents/openai.yaml`.                                                                                                                                                                                                                                                                 |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-11-23  | `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9` | No upstream change in `pstack/skills/maintain-formal-verification-skill/` since `88d4751`. Closeness re-check by the owner's rule: restored upstream's `SKILL.md` body. The restructured steps and completion criteria, ready/draft readiness, generated-input fallback discovery, isolated scratch worktrees, working-change fingerprints, inconclusive results, distinguishable-counterexample controls, cleanup evidence, and the reworded product-code grant were added rules that no host needs. Kept the short description and the /writing-for-agents call. Fidelity holds in both directions. |
