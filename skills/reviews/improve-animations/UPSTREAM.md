# improve-animations: source and adaptations

## Source and credit

- Original author: Emil Kowalski.
- Canonical source: [emilkowalski/skill](https://github.com/emilkowalski/skill).
- Original skill and resources: [`skills/improve-animations`](https://github.com/emilkowalski/skill/tree/0f2e23b32bb1265e84cff8d3e75785fec953fb1b/skills/improve-animations), with `SKILL.md`, `AUDIT.md`, and `PLAN-TEMPLATE.md`.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Reviewed through commit: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Fidelity checked through: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Last upstream review: 2026-11-14.
- License: [MIT, copyright 2026 Emil Kowalski](LICENSE), retained from the [pinned upstream license](https://github.com/emilkowalski/skill/blob/0f2e23b32bb1265e84cff8d3e75785fec953fb1b/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Phase 2's fan-out and `execute` dispatch their subagents through /swarm, the owner of delegation and isolated writers.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging. The repository's `.prettierignore` keeps `PLAN-TEMPLATE.md` byte-identical to upstream, because the formatter rewrites the code fences its zero-width spaces escape.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. Record adopted, adapted, and excluded changes before advancing the baseline.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-14 | `0f2e23b32bb1265e84cff8d3e75785fec953fb1b` | Imported `SKILL.md`, `AUDIT.md`, and `PLAN-TEMPLATE.md` as written, without the fixed greeting, and routed its two subagent dispatches through /swarm. The Skills CLI had installed this skill from upstream; the installed copy was byte-identical to this revision, and the adopted copy replaces it. Fidelity passes in both directions: the only differences from upstream are the dropped greeting, the /swarm route, and formatter output. Repository checks and catalog validation pass. |
