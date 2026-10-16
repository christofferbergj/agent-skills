# setup-ts-deep-modules: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/in-progress/setup-ts-deep-modules`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/in-progress/setup-ts-deep-modules).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `49dd158d1076134a641b33efb035946536778336`.
- Last upstream review: 2026-10-15.
- Upstream stage: `in-progress`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- Respect existing workspace layout/configuration, do not commit an unsolicited example, and verify Node/TypeScript compatibility and nonzero source scanning. Scan every external importer root as well as the packages. Prove test and app deep-import failures, with a restored pass after each.
- Preserve the familiar command, except the documented `prototype` to `design-prototype` and `git-guardrails-claude-code` to `git-guardrails` mappings.
- Share domain artifacts through `/domain-modeling`, architecture vocabulary through `/codebase-design`, behavior tests through `/tdd`, Standards/Spec review through `/code-review`, and PR descriptions through `/pr`.
- Use `/pstack-swarm` for actual Codex/Claude Code delegation and bounded cross-vendor execution. Preserve explicit user entrypoints and callable dependency metadata.
- Honor existing project artifacts, approved decisions, and action authorization. Keep draft-PR defaults, isolated writers, and learning changes prepared for review.
- This skill's `agents/openai.yaml`, provenance, and integration changes are locally owned.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                           |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures. |

Local maintenance on 2026-10-16 corrected the package-only scan command and added external-importer proof. Dependency-cruiser 18.6.0 with TypeScript 6.0.2 and Node 24.22.0 misses an app violation when scanning only packages, detects it when scanning all source roots, and passes after restoration. Both default and separate workspace roots were exercised; all five configured rules detect their intended violations. The upstream candidate and reviewed position are unchanged. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md).
