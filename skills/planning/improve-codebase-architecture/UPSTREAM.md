# improve-codebase-architecture: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/improve-codebase-architecture`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/improve-codebase-architecture).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Fidelity checked through: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Last upstream review: 2026-10-29.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Preserve domain-specific names and use the shared arena for interface alternatives.
- HTML report (`SKILL.md` step 2 and `HTML-REPORT.md`): Mermaid runs with `securityLevel: "strict"` instead of `"loose"`, and repository and issue text is escaped before it enters HTML, attributes, or diagram labels, because the report embeds untrusted repository text and loose mode renders HTML in labels.
- Grilling loop: upstream offers an ADR with a fixed question when the user rejects a candidate; locally /domain-modeling's ADR criteria decide, a settled qualifying decision is recorded within the current grant, and an unresolved one stays a question. Upstream's future-explorer and ephemeral-reason filter is kept.
- Implementation requires its own task scope, per the user's grant.

Local maintenance on 2026-10-20: Keep established product/domain names in HTML reports while using the shared architectural vocabulary for architectural reasoning. This local repair leaves the upstream reviewed-through position unchanged.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                                                                                                                  |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Fidelity check: restored "Be visual", editorial visuals, the Mermaid-mixing guidance, and the ADR future-explorer filter; capitalized an invocation; recorded the strict-Mermaid and escaping, offline fallback, ADR delegation, and completion divergences. The `mermaid@11` CDN pin still resolves (npm latest 12.2.0), so it stays. Formatter-only Markdown changes are not divergences. Catalog validation passes. Final review: added the /pstack-principles planning pass before candidates are graded, which the Matt planning-owner adaptation requires. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Owner decision: returned the report guidance in `SKILL.md` step 2 and `HTML-REPORT.md` to upstream's CDN-first wording and dropped the offline-fallback divergence; the strict Mermaid setting and escaping of repository text stay recorded. Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                |
| 2026-10-29  | `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa` | Upstream `7739eae` (#1341) and `a496f55` (#1342) start every subagent with a fresh context window rather than a fork. Carried the rule into /swarm's execution contract, the delegation owner, so both suites receive it, including Codex's `fork_turns` and Claude Code's `fork` type. Adopted upstream's "with a fresh context window" on the exploration sub-agent as written. Fidelity holds in both directions.                                                                                                                                                                |
