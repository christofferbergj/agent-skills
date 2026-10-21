# setup-matt-pocock-skills: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/setup-matt-pocock-skills`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/setup-matt-pocock-skills).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Configure one shared project contract for both hosts. Reuse existing domain/tracker/label choices and legacy artifact locations; personal Pstack model-role setup remains optional. Use the GitLab API relation `is_blocked_by` when identifying native blockers; `/blocked_by` remains the quick action.
- Instruction files: upstream never creates `AGENTS.md` beside `CLAUDE.md` (or the reverse). Locally the existing source stays authoritative, and the smallest host-native pointer or documented symlink lets the other host reach it, because Codex reads `AGENTS.md` and Claude Code reads `CLAUDE.md`.
- `domain.md` is restructured as a role-based contract: it names authoritative artifacts by role, respects legacy `CONTEXT.md`/`context.md`/`domain.md` files, delegates updates to /domain-modeling and architectural vocabulary to /codebase-design, and keeps canonical edits with the coordinator. Upstream's single- and multi-context file trees are delegated to /domain-modeling, which holds the same layouts. Upstream's read list, silent-absence rule, glossary-vocabulary rule, and ADR-conflict example are kept in its wording.
- GitHub and GitLab notes preflight the CLI and pass multiline text through UTF-8 body files or JSON API input instead of heredocs and inline `--body`, so issue text never passes through shell quoting. GitHub closing comments are posted with `--body-file` before `gh issue close`, and GitLab's interactive `--description -` editor option is dropped because agents cannot drive an editor. Publishing waits for the task's grant.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                      |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream change since `49dd158`. First fidelity check: restored the explore-present-confirm-write sentence and `domain.md`'s silent-absence, glossary-vocabulary, and ADR-conflict rules, and recorded the instruction-file pointer, the role-based `domain.md`, and the body-file tracker commands. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                  |

Local maintenance on 2026-10-17: Corrected the GitLab blocker API relation to `is_blocked_by`, verified against the official issue-links API documentation; `/blocked_by` remains the quick action. The source candidate `49dd158d1076134a641b33efb035946536778336` is unchanged. Repository checks pass; live GitLab integration remains unexercised.
