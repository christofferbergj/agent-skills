# Weekly audit, 2026-10-21

Historical audit record. Counts and pending work describe this snapshot; current behavior lives in each `SKILL.md` and its `UPSTREAM.md`.

The first fidelity audit since the check was added. It started from default-branch commit `83f960a` with 96 skills. No upstream source changed since any recorded baseline, so every edit repairs local drift from the 2026-10-15 import or records an existing divergence. The fidelity backlog went from 79 records to 10.

## Sources

| Source           | Candidate                                  | Delta since baselines  |
| ---------------- | ------------------------------------------ | ---------------------- |
| Cursor plugins   | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | none in tracked skills |
| Matt Pocock      | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | none in tracked skills |
| Oliver Cederborg | `f3e4c1001f8483c2e07d98d452cb5d8466f3358c` | none in tracked files  |
| OpenClaw         | `9edb131db8deb28ca53a8e51f8886bdf6645f6c4` | none in tracked paths  |

## Slices

Ten Claude Opus workers each took one slice in its own worktree, and the coordinator cherry-picked their commits. Two Codex `gpt-6.1-sol` reviewers at `xhigh` reviewed the integrated diff.

| Slice                         | Skills                                                                                           | Advanced                          | Pending                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------- | ---------------------------------------------------------------------------------------- |
| Principles A and B            | 24 Pstack principles                                                                             | 24                                | none                                                                                     |
| Pstack agents                 | mode, figure-it-out, automate-me, help, recall, reflect, show-me-your-work                       | figure-it-out                     | mode (5 of 22 playbooks repaired), automate-me, help, recall, reflect, show-me-your-work |
| Pstack communication          | bro, in-your-own-words, ketchup, teach, technical-writing, unslop                                | 6                                 | none                                                                                     |
| Pstack engineering            | 8 helpers                                                                                        | 8                                 | none                                                                                     |
| Pstack planning and reviews   | architect, arena, how, sharpen, why, benchmark-checklist, blast-radius, interrogate, no-comments | 5                                 | architect, arena, why, no-comments                                                       |
| Thermos, review owners, local | 2 Thermos rubrics, test-audit, code-review, pr, 4 first-party skills                             | 5 sourced                         | none                                                                                     |
| Matt planning A and B         | 14 skills                                                                                        | 14                                | none                                                                                     |
| Matt agents and engineering   | 10 skills                                                                                        | 9; chief-of-staff already checked | none                                                                                     |

## Patterns

- **Invocation mode:** upstream marks most Pstack skills user-invoked; locally 50 of 56 are model-invoked so other skills can load them. No library-wide rule states this, so each record now repeats it.
- **Rewrites:** several Pstack skills (pstack-mode's playbooks, architect, arena, why, no-comments, automate-me, recall, show-me-your-work) were condensed into local steps at import and dropped upstream rules without a record. The skills repaired this run restore upstream's wording with only the library-wide adaptations applied.
- **Completion criteria and the /domain-modeling preamble** were added across many sourced skills to follow AGENTS.md and are recorded per skill.

## Evidence

- `pnpm check` passes on the integrated branch.
- Tool checks cited by workers include Claude Code 2.1.304 and codex-cli 0.163.0 hook documentation for git-guardrails, Husky 9.1.7 and lint-staged 17.6.0 for setup-pre-commit, Bun 1.2's text `bun.lock`, Tailscale 1.102.2 flags, gh 2.102.1, pnpm 11.28.6, and dependency-cruiser 18.7.0, which scans no modules under TypeScript 7.0.2 while still exiting 0.
