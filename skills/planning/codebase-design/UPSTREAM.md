# codebase-design: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/codebase-design`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/codebase-design).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Reuse Pstack arena execution for alternative interfaces and preserve established project domain names. Apply test replacement only after equivalent public-seam coverage exists.
- `SKILL.md` Glossary: upstream's "use these terms exactly; don't substitute component, service, API, or boundary" is softened to architectural reasoning, so a project's documented domain names (a domain Service, API, or bounded context) keep their meaning; project terminology goes through /domain-modeling, which owns it.
- `DESIGN-IT-TWICE.md`: the pattern applies to any consequential interface with materially different viable shapes, since /pstack-architect and /tdd invoke this owner for interface decisions, not only to a chosen deepening candidate. Candidates run through one /pstack-arena invocation (blind judging, base selection, grafting) instead of a bare parallel spawn, with candidate count scaled to the decision rather than "3+". An existing `/pstack-architect` or `/pstack-arena` run receives the constraints instead of a second competition. Upstream's framing, radically different constraints, candidate outputs, sequential presentation, and opinionated recommendation are kept. Ousterhout's attribution sentence and the vocabulary list are dropped as exposition the step text already carries.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                         |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Fidelity check: restored upstream's design-it-twice framing hand-off, radically different constraints, candidate outputs, sequential presentation, and opinionated recommendation inside the /pstack-arena steps; recorded the glossary softening, arena execution and trigger, and completion criteria. Formatter-only Markdown changes are not divergences. Catalog validation passes. Final review: restored the rough illustrative code sketch in the framing step. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                     |
