# chief-of-staff: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/in-progress/chief-of-staff`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/in-progress/chief-of-staff).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Last upstream review: 2026-10-29.
- Fidelity checked through: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Upstream stage: `in-progress`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Bind coordination to an agreed goal and budget with bounded native delegates. Propose environment improvements within scope; goals do not authorize unrelated services, schedules, or external actions.
- Wiki memory follows upstream's location agreement, index, history-only claims, and unedited sources. Locally, an existing goal notes location is reused, sources keep their access boundary, and the lint schedule needs a scheduling grant.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                                                                                         |
| 2026-10-20  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Adopted the wiki-memory delta: location agreed with the user before the first write, index, query/ingest/lint, history-only dated and commit-cited claims, superseded rather than rewritten claims, and unedited sources. Adapted reuse of existing goal notes, source access boundaries, a granted lint schedule, and a checkpoint criterion. All 38 source skills and shared changes are accounted for; source exclusions and experimental status are preserved. Focused packaging, command checks, repository gates and independent native review pass. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Tools and conventions check only; fidelity already holds through this candidate. Frontmatter, user-invoked mode and `agents/openai.yaml` policy agree; the /pstack-swarm dependency resolves; the skill names no host tools or commands. No changes.                                                                                                                                                                                                                                                                                                       |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2026-10-29  | `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa` | Upstream `7739eae` (#1341) and `a496f55` (#1342) start every subagent with a fresh context window rather than a fork. Carried the rule into /swarm's execution contract, the delegation owner, so both suites receive it, including Codex's `fork_turns` and Claude Code's `fork` type. Adopted upstream's sentence as written after the background-agents line. Fidelity holds in both directions.                                                                                                                                                        |
