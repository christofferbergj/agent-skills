# git-guardrails: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/misc/git-guardrails-claude-code`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/misc/git-guardrails-claude-code).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `misc`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Preserve literal shell comment boundaries, quoted hashes, line continuations, and supported wrapper-option values when detecting accidental destructive Git commands.
- Generalize the Claude-specific name and provide Codex/Claude hook adapters sharing a Python detector. Handle common Git options, shell separators, forced deletion, and quoted mentions; disclose indirect-command limits and native hook trust requirements.
- The detector runs as `python3 <path>` instead of an executable Bash/`jq` script, so no `chmod +x` step applies. On a block it exits 2 with the BLOCKED message on stderr, as upstream does, and also prints the `permissionDecision: deny` JSON both hosts document. Its configured operations are parsed Git verbs and flags rather than upstream's grep patterns, so customization edits the detector's operation checks.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Restored dropped upstream rules: trigger description (translated to both hosts), the blocked-operations list and authority message, the customization question, the `$CLAUDE_PROJECT_DIR` project command and hook locations, and the exit-2/stderr verification expectation; added Codex's documented git-root project path. Recorded the Python runner and dual JSON/exit-2 denial. Checked hook keys, events, matchers, exit-2 and deny JSON against current Claude Code and Codex hooks docs (Claude Code 2.1.304, codex-cli 0.163.0). Synced the Codex short description to upstream; category README row proposed. Detector unit tests pass. |
