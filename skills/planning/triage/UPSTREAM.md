# triage: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/triage`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/triage).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `49dd158d1076134a641b33efb035946536778336`.
- Last upstream review: 2026-10-15.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Use configured artifacts and the native execution contract while retaining the upstream verification, label, and agent-brief workflow.
- Keep the complete rejected-feature example inside its four-backtick fence; the following operating instructions remain Markdown prose. Keep agent-brief examples consistent with the owning out-of-scope format.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                           |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures. |

Local maintenance on 2026-10-16 repaired the nested example fences in `OUT-OF-SCOPE.md`. A fence-state check confirms that prior requests stay in the example and naming, checking, writing, and updating guidance renders as instructions. Formatting and repository checks pass. The upstream candidate and reviewed position are unchanged. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md).

Local maintenance on 2026-10-17: Aligned the agent-brief example with its owning out-of-scope record format. The source candidate `49dd158d1076134a641b33efb035946536778336` is unchanged. Local references and repository checks pass.
