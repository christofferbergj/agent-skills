# design-prototype: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/prototype`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/prototype).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Rename prototype to design-prototype to preserve Emil Kowalski's command. Keep both logic/UI branches; accepted model changes use the shared owner, and implementation/publication require their own task scope.
- `SKILL.md` rule 6 and the capture steps in `LOGIC.md` and `UI.md`: upstream always folds the decision into real code, commits the prototype to a throwaway branch, and comments on the implementation issue. Locally the prototype may stay in the project's chosen scratch location instead of a branch, folding into production code waits for implementation scope, and branch or issue publication follows the existing grant, because committing, pushing, and commenting need the user's authorization. The answer is captured as the question, observed answer, and remaining uncertainty, linked from the implementation artifact.
- A completion criterion ends `SKILL.md`, per the repository's skill rules.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                             |
| 2026-10-16  | `49dd158d1076134a641b33efb035946536778336` | No upstream delta. Aligned both branch capture stages with the shared implementation/publication boundary and preserved scratch retention. Native current-layout capture and authorized legacy UI/logic adoption passed; primary sources and canonical docs remained unchanged. Repository and catalog checks pass; see the [combined review](../../../docs/reviews/2026-10-16-combined-skill-maintenance.md). |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Fidelity check: restored the portable-module rationale in `LOGIC.md`, the variant-retention reason in `UI.md`, and "the main branch keeps only the validated decision"; recorded the scratch-location, grant-bound capture divergence and the completion criterion. Formatter-only Markdown changes are not divergences. Catalog validation passes. |
