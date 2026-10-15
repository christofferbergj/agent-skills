# Combined skills Thermos review

Reviewed on 2026-10-15. Two independent subagents ran the correctness/security and maintainability rubrics in parallel. Each reviewed the complete branch and the saved weekly maintenance prompt without editing source or delegating further. The parent verified their findings, added one Git-detector finding, and repaired all nine.

Both reviewers then rechecked the same 27-file repair snapshot in parallel and reported no supported remaining findings in that scope. The correctness reviewer independently reran all 76 Bun tests, the 16 catalog and guardrail tests, TypeScript checks, and catalog validation. It also verified that GitHub accepts the immutable-head query. The maintainability reviewer inspected the changed owners and the Wayfinder exercise artifacts.

The initial scope was merge-base `68a6d2f05d5ebd2a9120a9e9f7ceee667380add9` on the verified `origin/main` through `2655d5883416187e39d1b0569bb673a83d0dd59d`. It included the Pstack and Matt Pocock ports, their shared owners, executable helpers, packaging, provenance, and maintenance automation. The unrelated untracked `exa-results/` directory was excluded. This record also covers the subsequent repairs.

## Correctness repairs

All seven findings were medium priority. No high-severity security vulnerability was demonstrated.

| Finding                                                                                                      | Repair and evidence                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The watcher could report merge readiness while reviews were required or mergeability was blocked or unknown. | The policy and rendered status now preserve those forge gates. Single-PR and stack fixtures cover each gate, draft overrides, and a positive ready case. A rendering assertion failed before the repair and passes afterward.            |
| Upstream comparisons dropped shared files under the skills root.                                             | The combined catalog excludes only actual skill directories from shared changes. A Git fixture covers category documents, shared files, and rename endpoints.                                                                            |
| The orchestration frontier recorded local branch revisions as PR-head proof.                                 | GitHub rows now query, validate, and store immutable `headRefOid` values. Fixtures cover unpushed local changes and absent local branches. The optional Origin adapter reports unavailable until its immutable-head API can be verified. |
| Closed historical PRs prevented reuse of a branch with a current PR.                                         | Frontier discovery prefers a unique open PR and still rejects ambiguous active PRs. Both cases have regression coverage.                                                                                                                 |
| Missing `origin/HEAD` silently assumed the default branch was `main`.                                        | Frontier discovery uses the actual symbolic default or an explicit verified `--trunk` argument. Fixtures cover `master`, a missing symbolic default, and the explicit fallback.                                                          |
| Cyclic PR bases could hang stack discovery before the polling deadline started.                              | The ancestor walk detects revisited PRs and returns an invalid-stack failure. A bounded subprocess fixture covers a two-PR cycle.                                                                                                        |
| Shell comments and wrapper arguments could hide literal destructive Git commands from the guardrail.         | Comment handling preserves command boundaries and quoted hashes; wrapper parsing accounts for options that consume values. Fixtures cover comments, line continuations, `env`, `exec`, and read-only or quoted commands.                 |

## Maintainability repairs

Both independent maintainability findings were medium priority.

| Finding                                                                                                  | Repair and evidence                                                                                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Separate Pstack and combined maintenance engines produced different validation and checkpoint results.   | Removed the redundant Pstack engine and four duplicate tests. The combined catalog owns validation, comparison, and checkpoints; `suite.json` remains the Pstack source inventory. Live guidance uses that owner and earlier validation commands are labeled historical. |
| Wayfinder charting created a research coordinator that dispatched another investigator for every ticket. | Wayfinder submits ready questions to `/research`, which owns direct investigator dispatch. An isolated two-ticket exercise completed both notes and tickets with two direct investigators and no nested coordinators.                                                    |

The review did not require a speculative split of the upstream orchestration store. Its imported boundary and organized sections remain useful for upstream comparisons. The existing weekly automation already uses the combined maintenance owner and needed no further changes.

## Validation and limits

All 134 automated tests pass: 76 Bun tests, 37 Pstack Python tests, ten combined-catalog tests, six Git-detector tests, and five wizard dotenv tests. TypeScript checks pass. The catalog validates 86 mapped adaptations and 94 repository skills across two upstreams. Regression fixtures use temporary repositories and fake forge responses rather than live external writes.

Skills CLI discovery, repository formatting, whitespace checks, and Gitleaks pass. A final isolated Skills CLI copy installs all 94 skills for Codex and Claude Code. All 1,034 supporting-file hash comparisons match the source, and the removed maintenance engine is absent from both installations.

The Wayfinder exercise used installed instructions, a local tracker, and two local provider documents. The parent inspected its map, both tickets, both research notes, and source hashes. Earlier native Codex and Claude Code exercises remain documented in the [combined validation record](../../skills/agents/maintain-skills/VALIDATION.md). These exercises cover selected branches, not every expensive workflow or optional service integration.

The Git detector remains an accidental-operation guardrail rather than a shell sandbox. Live hook activation, Origin immutable-head compatibility, GitLab tier behavior, production services, external tracker publication, and other operating systems remain unverified. Upstream pins and license notices remain unchanged.

The combined library remains on draft PR #2 until merged into the default branch. This review does not merge it or refresh global installations. The weekly automation retains its deployment prerequisite and does not recreate the unmerged port.
