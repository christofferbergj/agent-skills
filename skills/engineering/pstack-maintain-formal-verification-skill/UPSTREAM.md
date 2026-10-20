# pstack-maintain-formal-verification-skill: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/maintain-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/skills/maintain-formal-verification-skill/SKILL.md).
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `88d47514b82e7c44f00f2b2a72ff6dd12158038c`.
- Reviewed through commit: `88d47514b82e7c44f00f2b2a72ff6dd12158038c`.
- Last upstream review: 2026-10-20.
- Fidelity checked through: `88d47514b82e7c44f00f2b2a72ff6dd12158038c`.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE), retained from [pstack/LICENSE](https://github.com/cursor/plugins/blob/88d47514b82e7c44f00f2b2a72ff6dd12158038c/pstack/LICENSE).

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Namespace: `maintain-formal-verification-skill` maps to `pstack-maintain-formal-verification-skill`. Preserve explicit user invocation and matching Codex metadata.
- Discover generated drafts and generated-input fallbacks alongside formal checks; testing evidence remains distinct from proof.
- Resolve every covered-code delta, moved function and new state writer against the current implementation. Property changes need evidence of an intended promise change.
- Retain upstream's four outcomes, verification-only edit scope, unweakened failing properties, step-by-step counterexamples with harm, uncommitted reproductions, stale-pass reporting, and a separate verification change. Add ready/draft readiness alongside the outcome.
- Keep checker outcome, source correspondence and skill readiness separate. Require a real-code semantic control, distinguishable counterexamples, restoration of the updated unmutated result, preserved evidence and owned scratch cleanup.
- Record exact committed sync points separately from modified or untracked content fingerprints. Blocked or inconclusive checks retain prior sync points; a conclusive code finding never claims the property passed.
- Use /writing-for-agents for instruction changes and the invoking project's conventions. Product repairs require an existing grant.
- `agents/openai.yaml` and this record are locally owned packaging; retain the upstream license notice when redistributing.

## Maintenance

Invoke /maintain-skills for whole-library upkeep and the source/shared-input comparison. Keep this import fixed; advance reviewed-through only after the full relevant delta and required checks pass.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-20  | `88d47514b82e7c44f00f2b2a72ff6dd12158038c` | Imported the complete eligible formal-upkeep companion within the established verification scope. Adapted portable project-local discovery, explicit invocation, exact freshness accounting, draft/fallback routing, source-driven property updates, real-code controls and checkable completion. Cold native fixtures expose a new recovery writer after a code move, preserve the resulting code finding, distinguish a second semantic counterexample, and retain blocked/inconclusive/dirty/pending boundaries. Repository gates and independent native review pass. |
