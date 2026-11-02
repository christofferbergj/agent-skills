# writing-for-agents: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/productivity/writing-for-agents`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `59db609eb1e18aaf59b63284d0e52255aff0c63c`.
- Last upstream review: 2026-10-27.
- Upstream stage: `productivity`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Retain the writing mechanics and branch-specific reference as the shared instruction-writing dependency, installed from this repository. Shared reference belongs to a model-invoked owner; its consumers invoke that owner rather than linking outside the owning skill.
- `SKILL-MECHANICS.md` names Codex's `policy.allow_implicit_invocation` key in `agents/openai.yaml` beside Claude Code's `disable-model-invocation` for both invocation modes, because Codex reads only the former and does not read the frontmatter field.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                                                               |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Compared SKILL.md, `SKILL-MECHANICS.md`, and Codex metadata in both directions: the body matches upstream except the recorded shared-reference reversal in `SKILL-MECHANICS.md` and the closing completion criterion, now recorded. No owner text changed, so consumers need no recheck.                                                                                                                                                                                                                      |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 2026-10-27  | `59db609eb1e18aaf59b63284d0e52255aff0c63c` | No upstream delta. Checked skill mechanics against Claude Code 2.1.308 and codex-cli 0.164.0: Claude Code's skills docs keep `disable-model-invocation: true` out of context; Codex's skills docs set invocation with `policy.allow_implicit_invocation` in `agents/openai.yaml`, and its skill catalog hides such skills from the prompt without reading the frontmatter field. Added the Codex key to both invocation mechanics and restored upstream's `Writing for Agents` display name. Fidelity passes in both directions. |

Local maintenance on 2026-10-17: Aligned shared-reference placement with this library's callable-owner contract. The source candidate `49dd158d1076134a641b33efb035946536778336` is unchanged. The affected guidance and consumers were reread; repository checks pass.
