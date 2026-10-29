# implement-spec: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/implement-spec`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement-spec).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Fidelity checked through: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Last upstream review: 2026-10-29.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Invoke /principles before implementation and final verification; explicitly pass selected owner instructions and decisions to workers. Honor migration-owner phase and integration-unit gates without treating transitional progress as full acceptance.
- Use one integration coordinator and existing ticket graph, owned isolated writers, serial accepted merges, and proposed domain edits from workers. Preserve unknown work and real tracker completion boundaries.
- Without a configured tracker, local artifacts carry the graph while the user runs /setup-matt-pocock-skills, so setup does not block implementation; nothing is published externally until authorized.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream change since `49dd158`. First fidelity check: restored the /setup-matt-pocock-skills pointer, context pointers, shared exploration notes, the early draft PR that closes the spec and tickets, and merging the integration tip before done; recorded the local-artifact fallback. Prior review evidence now passes to /review-loop instead of replacing its passes.                                                                                                                                                                                                                                                        |
| 2026-10-29  | `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa` | Upstream `7739eae` (#1341) and `a496f55` (#1342) start every subagent with a fresh context window rather than a fork. Carried the rule into /swarm's execution contract, the delegation owner, so both suites receive it, including Codex's `fork_turns` and Claude Code's `fork` type. Adapted #1342's fresh implementer per ticket into step 2's /swarm dispatch. Upstream step 7's fixer subagent, now a fresh one, stays replaced by step 4's /review-loop, whose coordinator applies verified fixes itself by the library-wide review adaptation, so "fresh" has no local subagent to qualify. Fidelity holds in both directions. |
