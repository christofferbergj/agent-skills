# Weekly audit, 2026-10-25

Historical audit record. Counts and pending work describe this snapshot; current behavior lives in each `SKILL.md` and its `UPSTREAM.md`.

The audit started from default-branch commit `05b4dc1` with 98 skills and an empty fidelity backlog. The AGENTS.md change in #24 reset every earlier local review, so all 98 skills were reviewed again against current tools and conventions. Only Oliver Cederborg's tracked files changed upstream.

## Sources

| Source           | Candidate                                  | Delta since baselines                        |
| ---------------- | ------------------------------------------ | -------------------------------------------- |
| Cursor plugins   | `99b609a72323b70204eab407c622f436e858e112` | none in tracked skills                       |
| Matt Pocock      | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | none                                         |
| Oliver Cederborg | `da75c37f81a8e8184fdea5b72885fa59c2fdd2ab` | reply-shape, next-options, review-loop files |
| OpenClaw         | `3303e8489906adec524b119f8e808b3fc1aa374b` | none in tracked paths                        |

## Slices

Nine Claude Opus workers each took one slice in its own worktree, and the coordinator cherry-picked their commits. A Codex `gpt-6.1-sol` reviewer at `xhigh` reviewed the integrated diff.

| Slice                     | Skills                                                      | Result                                                           |
| ------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------- |
| Agents                    | 9 first-party and Matt agent skills, with pstack-principles | one stale divergence reason corrected                            |
| Local changes             | pstack-mode, pstack-setup, pstack-swarm (#25)               | fidelity holds; records advanced                                 |
| Oliver delta              | reply-shape, next-options, review-loop, thermos (#26)       | delta decided; one change held                                   |
| Pstack agents and replies | 13 skills                                                   | recall and reflect fixed for current transcripts                 |
| Matt engineering          | 8 skills and pr                                             | HITL script, three display names, one invocation line            |
| Pstack engineering        | 9 skills                                                    | one stale divergence reason corrected                            |
| Planning                  | 19 skills                                                   | two Cursor-only tool names replaced                              |
| Principles                | 24 principles                                               | model-the-domain delegates to /domain-modeling                   |
| Reviews                   | 8 skills                                                    | one stale divergence dropped, one unrecorded divergence recorded |

## Patterns

- **Host tools:** Pstack text still names Cursor or Claude-only tools in places, such as `Read, Grep, Glob` and `mcp_auth`. Claude Code leaves Glob and Grep out by default on macOS, and Codex has neither.
- **Stale reasons:** several divergence records gave reasons that host releases have since overtaken, such as Claude Code reading `AGENTS.md` and its scheduled tasks taking an API trigger.
- **Transcripts:** Claude Code workflow journals and Codex's injected `AGENTS.md` first message broke assumptions in /pstack-recall and /pstack-reflect.

## Evidence

- `pnpm check` passes on the integrated branch, and `catalog.py validate` reports 98 skills with no problems.
- The new /pstack-recall regression test fails with its fix reverted and passes with it.
- next-options' six SessionStart tests pass, with the loaded rules at about 5,800 of 8,000 characters.
- Tool checks cited by workers include codex-cli 0.164.0, Claude Code 2.1.308, gh 2.103.0, git 2.56.0, pnpm 11.28.7, Husky 9.1.7, lint-staged 17.6.0, dependency-cruiser 18.7.0, TypeScript 7.0.2, mise 2026.10.17, and Tailscale 1.102.2.

## Follow-up: owner decisions

The owner accepted every recommendation the same day:

- **Kept:** no T3 thread settling before a Done reply, the `xhigh` cap on GPT models, and no receiver creation in /pstack-make-bot-ui.
- **Principles:** principle descriptions keep upstream's triggers, since /pstack-principles selects them by description in both suites; helper descriptions stay scoped to Pstack tasks. The contract change is on the process branch, and /pstack-help's loading lines match it.
- **Skills:** /pstack-principle-prove-it-works hands Computer Use checks in Claude sessions to /pstack-swarm's route, /setup-matt-pocock-skills recommends `AGENTS.md` when a repository has neither file, and /test-audit delegates through /pstack-swarm and applies the test-behavior principle.
- **Recall:** a session in a removed Claude Code agent worktree counts as the repository's activity once Git confirms the nearest existing parent belongs to it.
- **Machine:** `ffmpeg` is installed through the Homebrew list in `~/.config`.

Three Codex `gpt-6.1-sol` `high` delta reviews checked the follow-up. Rounds 1 and 2 each found a Blocker in the recall fallback, which attributed a removed path to this repository without checking Git ownership; both were fixed with regression tests, and round 3 passed.
