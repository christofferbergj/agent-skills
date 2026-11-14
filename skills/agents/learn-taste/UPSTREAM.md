# learn-taste: source and adaptations

## Source and credit

- Original author: Emil Kowalski.
- Canonical source: [emilkowalski/skill](https://github.com/emilkowalski/skill).
- Original skill and resources: [`skills/learn-taste`](https://github.com/emilkowalski/skill/tree/0f2e23b32bb1265e84cff8d3e75785fec953fb1b/skills/learn-taste), with `SKILL.md`.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Reviewed through commit: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Fidelity checked through: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Last upstream review: 2026-11-14.
- License: [MIT, copyright 2026 Emil Kowalski](LICENSE), retained from the [pinned upstream license](https://github.com/emilkowalski/skill/blob/0f2e23b32bb1265e84cff8d3e75785fec953fb1b/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Phase 1 finds earlier sessions through /recall, which owns where Codex and Claude Code keep transcripts and scopes them to the repository. Upstream names Claude Code's default folder alone, which misses Codex sessions and a Claude Code profile with its own config directory.
- Phase 4 writes a project skill or an agent-instructions line through /writing-for-agents, the owner of agent-instruction writing.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. Record adopted, adapted, and excluded changes before advancing the baseline.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-14 | `0f2e23b32bb1265e84cff8d3e75785fec953fb1b` | Imported `SKILL.md`. Adapted Phase 1 to find earlier sessions through /recall and Phase 4 to write agent instructions through /writing-for-agents; both divergences are recorded above. First import; the skill was not installed before. Fidelity passes in both directions: the only differences from upstream are those two owner invocations and formatter output. Repository checks and catalog validation pass. |
