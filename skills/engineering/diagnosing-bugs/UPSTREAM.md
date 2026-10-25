# diagnosing-bugs: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/diagnosing-bugs`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/diagnosing-bugs).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-25.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- `scripts/hitl-loop.template.sh` tells the agent that the user runs the copied script and pastes its output back, where upstream has the agent run it: neither host's agent shell is a terminal the user can type into, and in Claude Code's the first `read` hits end of input and `set -e` exits.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                                                                                  |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Compared SKILL.md, `scripts/hitl-loop.template.sh`, and Codex metadata in both directions: the only divergences are the recorded configured-artifacts reading through /domain-modeling and /pstack-swarm delegation; Pstack's bug-fix and perf-issue playbooks still compose this loop. The template passes `bash -n`; dependencies resolve. No changes.                                                                                                                                                                         |
| 2026-10-25  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. The HITL template exited 1 at its first `read` in the Claude Code Bash tool (no TTY, stdin at EOF), so its header now has the user run the copy and paste the output back; it passes `bash -n` and prints the Captured block when run with input. Dropped the bullet restating the library-wide project-artifact and host adaptations, and its claim that Pstack's bug and perf playbooks compose this loop: #19 removed /diagnosing-bugs from the Bug fix playbook and no skill invokes it. Fidelity passes in both directions. |
