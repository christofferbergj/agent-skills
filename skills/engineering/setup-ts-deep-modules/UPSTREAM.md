# setup-ts-deep-modules: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/in-progress/setup-ts-deep-modules`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/in-progress/setup-ts-deep-modules).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `in-progress`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Respect existing workspace layout/configuration, do not commit an unsolicited example, and verify Node/TypeScript compatibility and nonzero source scanning. Scan every external importer root as well as the packages. Prove test and app deep-import failures, with a restored pass after each.
- Upstream's "Four rules" is corrected to the five checks its own config defines (the entry-point boundary is split into app and cross-package rules). Bun's text `bun.lock` is detected beside `bun.lockb`.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                                                                                                                              |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Compared SKILL.md, the config template, and Codex metadata in both directions; restored upstream's "all `error`" severity statement and recorded the five-check correction, Bun lockfile, and /domain-modeling step. Config diff is formatting only. A fixture with dependency-cruiser 18.7.0 (Node engines 22, 24, or 26 and later) scanned 0 modules with exit 0 under TypeScript 7.0.2 (`missing-typescript-transpiler`, supported <7) and failed `entrypoint-boundary-from-app` under TypeScript 6.0.3, so the compatibility and nonzero-scan divergences remain needed. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

Local maintenance on 2026-10-16 corrected the package-only scan command and added external-importer proof. Dependency-cruiser 18.6.0 with TypeScript 6.0.2 and Node 24.22.0 misses an app violation when scanning only packages, detects it when scanning all source roots, and passes after restoration. Both default and separate workspace roots were exercised; all five configured rules detect their intended violations. The upstream candidate and reviewed position are unchanged. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md).
