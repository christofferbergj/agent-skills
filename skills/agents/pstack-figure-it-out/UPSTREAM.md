# pstack-figure-it-out: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/figure-it-out/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/figure-it-out/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Model-invoked, where upstream `figure-it-out` is user-invoked: /pstack-mode and /pstack-help route large or bespoke runs to it by prose invocation, which a user-invoked skill cannot receive.
- Phases A to E become five numbered steps with completion criteria. The opening todolist that reads poteto-mode's Principles section becomes an /pstack-principles invocation, and the instruction to place designed steps between Phase C and Phase D todos is dropped; the numbered steps and the per-step trail rows carry the same order.
- Adds a user-facing recap through /pstack-ketchup, an agreed time limit, and scope and approved-interface gates on replanning.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                      |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8`. First fidelity check: restored the dropped rules (framing before a long run, riskiest-unknown-first units, harness and baseline before work, no second arena on a settled design, seam-only fan-out, judge-paired delegation, gate fixes in their own change, VERIFIED/NOT VERIFIED/INCONCLUSIVE verdicts, committed trail, encoding recurring corrections). Recorded the model-invoked mode, step restructuring, and local additions. |
