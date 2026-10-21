# wayfinder: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/wayfinder`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/wayfinder).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Ready research tickets go to /research as one batch, and the session collects every terminal result before stopping, where upstream fires subagents and stops: a host subagent reports to its coordinator session. Canonical map and ticket edits stay with Wayfinder; pushing the research branch follows the existing grant.
- Read the decision type from the configured tracker: the remote `wayfinder:<type>` label, or the `Type:` field for local Markdown, so upstream's "the body never states the type" is dropped (local repair, 2026-10-20).
- Added: a closing completion criterion, because the library requires checkable completion criteria.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                       |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                             |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream change since `49dd158`. First fidelity check: restored upstream's throwaway `research/<name>` branch that gets no PR (upstream #576), which the batch rewrite had replaced, and fixed the capitalization of step 1's invocation. Moved the 2026-10-20 type-field repair into the adaptations list. |
