# Initial adaptation validation

Validated on macOS on 2026-10-15 against upstream Pstack 0.15.25, commit `e5136d82418d2db3165ea1050d17577cd618cc05`.

This is the historical initial-port record. The current /maintain-skills validation record and catalog commands supersede the Pstack-only `suite.py` engine removed during the combined-library review. The counts and commands below record what ran at that earlier revision.

The exercised tools were Codex CLI 0.162.1, Claude Code 2.1.292, Bun 1.4.3, Node 24.22.0, Python 3.9.6, Git 2.54.0, and GitHub CLI 2.102.0. Other operating systems were not exercised. The cross-vendor wrapper explicitly requires POSIX process groups and fails to the disclosed native-review path when required CLI controls are unavailable.

## Packaging and scripts

- The suite validator accounts for all 54 mapped skills, including the reused `bro`, with invocation metadata, local resources, licenses, provenance, and README listings.
- Skills CLI discovers 62 repository skills. An isolated installation of the complete 54-skill group exposes the instructions and supporting resources to both Codex and Claude Code. Global installations were not refreshed.
- All 72 Bun tests pass, including PR watcher and orchestration behavior, plan parsing and task-sized evidence requirements, and concurrent immutable-source bootstrap. TypeScript checks cover bootstrap, orchestration, watcher, and their TypeScript tests.
- All 41 Python tests pass: 15 scoped-history cases, 11 worktree-audit cases, four maintenance comparison/checkpoint cases, and 11 cross-vendor wrapper cases. They cover workspace switches, unusual paths, malformed or unavailable evidence, ignored files, hidden Git state, conflicting ownership, bounded process groups, and truthful failure results.
- Maintenance fixtures discover changed, added, and removed skills and shared license changes. A partial checkpoint preserves unfinished coverage and never advances source baselines. Comparing the pinned initial inventory finds no unmapped skill.
- Repository formatting, Skills CLI discovery, whitespace, and secret checks pass.

Run the script checks from the source repository:

```bash
pstack_runtime="$(bun skills/agents/pstack-mode/scripts/bootstrap.ts --print-runtime)"
(cd "$pstack_runtime" && bun test && bun run typecheck)
python3 -m unittest discover -s skills/agents/pstack-recall/scripts/tests -v
python3 -m unittest discover -s skills/agents/pstack-mode/scripts/tests -v
python3 -m unittest discover -s skills/agents/pstack-swarm/scripts/tests -v
python3 skills/agents/pstack-mode/scripts/suite.py validate --root .
```

The runtime is a frozen dependency cache outside skill source. The bootstrap test checks concurrent and repeated preparation without changing source files.

## Host and workflow exercises

| Exercise                                          | Observed result                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Cold Codex invocation of installed `pstack-mode`  | Chose Bug fix, invoked the relevant helpers, reproduced a CSV last-row defect with four failing regression cases, fixed it, and passed the same cases. A separate native source reviewer checked the result. The final diff and failing/passing logs were inspected.                                                     |
| Claude Code invocation of installed `pstack-mode` | Chose Investigation and dispatched a built-in general-purpose `Agent` with an explicit read-only brief. Returned source-backed behavior and labeled inferred outputs. Source files remained unchanged.                                                                                                                   |
| Cross-vendor wrapper from Codex                   | Authenticated Claude Code review completed with `claude-opus-5-5`; actual findings led to helper fixes and regression cases.                                                                                                                                                                                             |
| Cross-vendor wrapper from Claude Code             | Authenticated Codex review completed with `gpt-6.1-sol`; actual findings led to helper fixes and regression cases.                                                                                                                                                                                                       |
| Disclosed fallback                                | The read-only Claude investigation completed an independent native explanation and explicitly reported that the cross-vendor script could not run under its execution restrictions. Missing-CLI and unsupported-control branches also return explicit unavailable statuses in focused tests.                             |
| History scope                                     | Fixtures exercise both host formats, worktrees and subdirectories, archived Codex sessions, changes from foreign to selected workspaces, Codex input preceding its turn context, and bounded reads that exclude foreign messages. Actual local Codex record ordering was inspected without publishing conversation text. |
| Optional webhook contract                         | Missing receiver stopped that integration path. A temporary localhost receiver/proxy fixture passed 12 HTTP cases covering harmless delivery, idempotency, authentication, payload validation, acknowledgement validation, arbitrary HTTP 200 rejection, and timeout. Both listeners closed afterward.                   |

The host exercises are smoke tests of the selected branches, not evaluations of every workflow. Reviewers were read-only; their reports do not substitute for the coordinator's executed tests. Current model availability, authentication, and tools are checked again when a workflow runs.

## Integration limits

Real webhook-provider delivery, browser/UI behavior, Tailscale exposure, and durable retries were not exercised. No production receiver was added. PR watcher and orchestration policies use their preserved fixture suites; no test merged a real pull request or changed external tracker state.

History files can be unavailable, partially written, or use an unrecognized schema. Such failures remain named coverage gaps; they never establish inactivity. Worktree classification is read-only advice requiring fresh native ownership and final direct inspection before any authorized removal. The initial import does not establish that every future upstream change should be adopted.
