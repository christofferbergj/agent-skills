# pr: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/pr`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/pr).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Inherited attribution

Attribution-only source: https://github.com/humanlayer/skills

Attribution-only source: https://github.com/humanlayer/humanlayer

The frontmatter and `CREDITS.md` retain Dex Horthy and Humanlayer's credit for the earlier `show-me` template using these two repository identities. This repository imported Matt's adapted `pr` skill and tracks that version through Matt's source record above. The inherited credits are not independently tracked imports; Matt's reviewed revision never establishes a Humanlayer review baseline.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Keep the upstream description template and inherited source credit. Repository contribution formats take precedence, and publication follows the invoking grant.
- Evidence, in the template and its section, states when screenshots are due (a visible change on a view that is cheap to capture), lays them out as a `Before | After` table per view when the base branch shows the same state and as a table of the new states otherwise, and says how to host them when the forge CLI cannot attach images. Reason: owner request (#33, #35). Upstream never says when screenshots are due or where they go, and `gh` cannot attach images, so agents fell back to text evidence for visible UI changes; side-by-side tables spare reviewers scrolling between the two. States joined the rule on owner request, because a forced before for a state the base branch never reaches shows nothing.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                       |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Fidelity check in both directions; the skill, `CREDITS.md`, and Codex metadata have no upstream delta since import. Recorded the /domain-modeling delegation. Restored upstream's `PR` display name in `agents/openai.yaml`, which read `Pr`. Catalog validation passes. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                   |
