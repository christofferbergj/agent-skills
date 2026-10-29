# grilling: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/productivity/grilling`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/productivity/grilling).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Fidelity checked through: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Last upstream review: 2026-10-29.
- Upstream stage: `productivity`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Invoke /principles during design interviews so recommendations use the shared design and coding owners while preserving the design frontier and user confirmation.
- A frontier question that running something could settle, such as state-model behavior or speed, is answered by a throwaway sketch, through /design-prototype or a measuring script, and reported as a settled decision the user can overturn; a look-and-feel question is asked with /design-prototype's variants in hand. Sketches stay out of the user's uncommitted work. Upstream puts every decision to the user. Reason: [ADR 0005](../../../docs/adr/0005-plan-through-code-by-default.md) adopts Pstack's rule that an observable answer is not the human's to give, and the final confirmation of shared understanding stays.

Local maintenance on 2026-10-27: frontier questions that running something could settle go to a sketch before the user, per ADR 0005. This local change leaves the upstream reviewed-through position unchanged.

Local maintenance on 2026-10-20: Route environment-fact investigations through /swarm, investigating directly when it or delegation is unavailable. This local repair leaves the upstream reviewed-through position unchanged.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                  |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Fidelity check: restored upstream's "frontier is empty" completion wording after the /pstack-principles recheck; removed an adaptation entry that restated upstream behavior. /pstack-swarm routing falls under the library-wide host adaptation. Formatter-only Markdown changes are not divergences. Catalog validation passes.                                |
| 2026-10-29  | `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa` | Upstream `7739eae` (#1341) and `a496f55` (#1342) start every subagent with a fresh context window rather than a fork. Carried the rule into /swarm's execution contract, the delegation owner, so both suites receive it, including Codex's `fork_turns` and Claude Code's `fork` type. No local change: fact-finding dispatches through /swarm. Fidelity holds in both directions. |
