# domain-modeling: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/domain-modeling`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Own project artifact resolution and accepted-model reconciliation for both families. Preserve configured legacy context/domain roles, single-writer document ownership, qualifying ADR criteria, and authorized publication boundaries.
- Local-only file: `references/project-artifacts.md` holds the artifact contract both suites follow. `SKILL.md`, `ADR-FORMAT.md`, and `GLOSSARY-FORMAT.md` resolve configured or existing locations through it before using upstream's `GLOSSARY.md` and `docs/adr/` defaults.
- The description keeps upstream's triggers, adds legacy context files, and adds a branch for another skill needing the artifacts resolved, because this skill is the shared owner other skills invoke.
- "Offer ADRs sparingly": upstream only offers an ADR; locally a decision that already meets all three criteria is recorded without another save dialog, and an ADR is offered while the decision is still under discussion, so delegated and implementation workflows record settled decisions once.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                  |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Fidelity check: restored upstream's description triggers beside the shared-owner branch; recorded the local artifact contract, the record-or-offer ADR divergence, and the completion criterion. Formatter-only Markdown changes are not divergences. Catalog validation passes. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                              |
