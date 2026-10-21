# pstack-create-formal-verification-skill: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/create-formal-verification-skill/SKILL.md`](https://github.com/cursor/plugins/blob/0b8e952052d482ee6de06deebf14d590d77b1b34/pstack/skills/create-formal-verification-skill/SKILL.md).
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `0b8e952052d482ee6de06deebf14d590d77b1b34`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Namespace: `create-formal-verification-skill` maps to `pstack-create-formal-verification-skill`.
- Upstream's sections become ordered steps that keep its model-to-code correspondence, failing control, real code mutation, restoration, evidence, and cleanup.
- Use /writing-for-agents for generated instructions and the invoking repository's skill conventions. No Cursor plugin registration or fixed verification tool is assumed.
- Tool choice: upstream `6b78e9f` makes TLA+ the default for event-ordering models in any language. Locally, TLA+ is considered alongside tools the repository already uses, so a project's existing verifier wins when it answers the question at lower cost.
- Preserve the checker-outcome, code-conformance, and draft-handoff branches owned by `SKILL.md`.
- Product repairs follow existing authorization; verification generation alone does not authorize them.
- `agents/openai.yaml` is locally owned.

## Maintenance

Invoke /maintain-skills for repository-wide upkeep. Preserve the import revision; advance reviewed-through only after the relevant source delta and required checks pass.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-18  | `0b8e952052d482ee6de06deebf14d590d77b1b34` | Imported the complete new skill within the established verification capability. Adapted its process to portable project-local skill discovery, an explicit writing owner, checkable steps, isolated negative proof and restoration, scope reporting, and preserved user invocation. Independent actual-code fixtures exhaust 102 states and 816 transitions; semantic negative controls, restoration, drift, and cleanup pass. Unavailable tools, incomplete exploration, masked existing failures, and drift-only models remain drafts. Repository gates and independent native review pass.                                                        |
| 2026-10-20  | `88d47514b82e7c44f00f2b2a72ff6dd12158038c` | Adapted per-check covered files/functions, exact confirmed sync commit and separate dirty-content fingerprints. New checks retain a pending sync until conclusive source correspondence, real-code semantic control, restoration and cleanup; drafts retain prior or pending positions. Generated-input fallback is testing evidence, not formal proof. Retained tool choice and readiness/outcome guards; user handoff points to formal upkeep. Cold actual-code fixtures cover code moves/new writers, distinct counterexamples, dirty state, blocked/inconclusive checks and pending drafts; repository gates and independent native review pass. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change in `pstack/skills/create-formal-verification-skill/` since `88d4751`, so the fidelity check at `88d4751` holds at this candidate. Tools and conventions pass: no fixed tool commands; /writing-for-agents and the formal-verification companions resolve; explicit user invocation matches `agents/openai.yaml`.                                                                                                                                                                                                                                                                                                                  |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
