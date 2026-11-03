# figure-it-out: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/figure-it-out/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/figure-it-out/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `ae5650febf4320793844c12c4adaa937f417f8da`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Phases A to E become five numbered steps. The opening todolist that reads poteto-mode's Principles section becomes an /principles invocation, and the instruction to place designed steps between Phase C and Phase D todos is dropped; the numbered steps and the per-step trail rows carry the same order.
- Adds a user-facing recap through /ketchup, an agreed time limit, and scope and approved-interface gates on replanning.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                              |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8`. First fidelity check: restored the dropped rules (framing before a long run, riskiest-unknown-first units, harness and baseline before work, no second arena on a settled design, seam-only fan-out, judge-paired delegation, gate fixes in their own change, VERIFIED/NOT VERIFIED/INCONCLUSIVE verdicts, committed trail, encoding recurring corrections). Recorded the model-invoked mode, step restructuring, and local additions. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2026-11-03  | `ae5650febf4320793844c12c4adaa937f417f8da` | Audit fidelity repair, no upstream change since `190d287`: restored four upstream rules the local text had dropped without a record: "Don't hide a negative." in the verification step, the /principle-separate-before-serializing-shared-state and /principle-never-block-on-the-human pointers, and running /architect, which runs /arena, for one-way-door design decisions where the local text allowed /arena alone. Fidelity passes in both directions.              |
