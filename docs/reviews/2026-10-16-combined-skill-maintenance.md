# Combined skill maintenance, 2026-10-16

Prototype-only tasks now retain their answer and runnable sources without adopting code into production. Both UI and logic references reach the existing shared capture rule. Authorized implementation remains supported. The Pstack review reference no longer suggests filtering a valid findings list down to five items. A TypeScript example now states that `durationMs: number` still needs boundary validation for negative, infinite and `NaN` values.

The review also adopts selected upstream prose cuts and aligns the Loop Me, TDD and commit-check descriptions with their existing bodies. Installed names, invocation policies, shared owners, license notices and original imports remain intact.

## Source coverage and decisions

The review starts from default-branch commit `51cb87dd8d4f45dd2a3bbff8fe05e7d11d70a311` on an owned maintenance branch. Each upstream was fetched once with full branch history; one immutable candidate was reused for each family.

| Family      | Reviewed baseline                          | Candidate                                  | Coverage                                                                                             |
| ----------- | ------------------------------------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Pstack      | `e5136d82418d2db3165ea1050d17577cd618cc05` | `f713f14203cd6420cec13cd7c55c32d598dbab68` | All 54 mappings; complete `pstack/` tree and shared inputs                                           |
| Matt Pocock | `49dd158d1076134a641b33efb035946536778336` | `49dd158d1076134a641b33efb035946536778336` | All 32 mappings, including experimental and frozen misc skills; complete inventory and shared inputs |

Recursive discovery finds 57 Pstack skill files: 54 suite entries and the three unchanged, excluded Benny automation skills. Matt's inventory has 38 skill files: 32 mappings and six recorded exclusions, including the README-omitted experimental `chief-of-staff`. No eligible additions, removals, moves, renames, license changes or missing baseline history remain. Benny retains its service and messaging exclusion. Matt's named, personal and course-scaffolding exclusions remain catalog-owned.

The complete Pstack delta is [upstream commit 99743e9](https://github.com/cursor/plugins/commit/99743e9c151c8537cbbf1f98bb38f34ef3368453), touching four skills and its README. Matt has no source delta.

| Unit                      | Decision                                                                                                                                                          |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Interrogate               | Adopt the lead-judgment cuts. The caller still requires evidence, dismissal reasons and separate Standards/Spec results.                                          |
| Swarm                     | Retain the portable local contract. Its useful worker counts, host settings, isolation and truthful completion evidence already replace the removed Cursor prose. |
| Migration principle       | Remove repeated introduction and rationale; retain explicit caller inventory, deletion, temporary-adapter and test rules with compatibility limits.               |
| Type-system principle     | Adopt four bullet cuts and the summary trim; retain the total-function/partiality rule and the concrete TypeScript owner.                                         |
| Local integration repairs | Correct prototype capture branches, the duration guarantee and three stale descriptions.                                                                          |

Shared-owner consumer inspection covered both families, including prototype, implementation, refactoring, domain artifacts, TDD, review, delegation and PR delivery. One coordinator still owns canonical document edits. The accepted spec/ticket graph, approved seams, current glossary/ADR roles and configured legacy context/domain roles remain authoritative.

Five touched Pstack records advance through the candidate after their complete relevant deltas and checks pass. The other 49 source-unchanged records retain their existing positions to avoid repetitive audit edits. Matt's source positions remain unchanged. All immutable import revisions remain fixed. Runtime coverage records account for all 86 mappings separately from those source positions.

## Fresh validation

- Repository formatting, Skills CLI discovery, whitespace, secret and combined-catalog checks pass. Discovery finds 94 repository skills; the catalog validates 86 mappings across two sources. All 86 retained MIT notices match their upstream notices byte for byte. A full YAML parse with Ruby Psych 3.1.0 checks all 94 frontmatter records and Codex invocation policies.
- The ten combined-catalog and eleven bounded-review-wrapper tests pass. Matt Python AST, shell syntax and dependency-cruiser template syntax checks pass. No executable source was changed.
- A native Codex prototype-only capture consumes `GLOSSARY.md` and the configured ADR, records both supplied synthetic answers and preserves every existing input. It writes only a scratch capture, without production adoption or publication.
- A native Codex authorized implementation consumes legacy `context.md` and `domain.md`, preserves both prototypes and all canonical inputs, and implements the two approved production seams. Three of four unchanged contract tests fail before implementation; all four pass afterward. Python and browser JavaScript each pass the 15-case transition matrix. Actual browser controls observe Hold, Release, Hold, Capture and terminal disabled controls.
- Restricted Claude synthesis runs consume the exact updated instruction snapshots with both current and legacy artifacts. Each retains seven distinct, independently reproduced fixture defects, keeps Standards and Spec results separate, writes no canonical artifacts and discloses sequential rather than independent review. These are synthesis-stage exercises with supplied synthetic findings, not new full independent swarms.
- TypeScript 7.0.2 compiles and Node 24.22.0 executes the negative, infinite and `NaN` duration counterexamples. The old field shape accepts all three, supporting the corrected guidance.

Fresh host evidence uses Codex CLI 0.163.0 and Claude Code 2.1.292, with `claude-opus-5-5` reported by the restricted reviewer. Native tools supply their actual schemas and inherited settings. The [initial combined validation](../../skills/agents/maintain-skills/VALIDATION.md) is reused explicitly for unchanged executable internals and expensive workflows; its earlier Codex 0.162.1 checks are not presented as fresh runs.

## Limits and delivery

The restricted Claude runner initially could not read instructions outside its fixture. Those attempts are retained as incomplete evidence. Reruns use byte-verified copies inside each fixture and complete the intended synthesis checks. The browser blocks direct `file:` navigation, so the standalone HTML exercise uses the exact bytes as a data URL. Screenshot export outside allowed tool roots was denied; no screenshot or direct-file pass is claimed. No service was created.

The selected exercises cover changed capture/adoption and review-synthesis behavior. They do not revalidate every UI, actual host hook activation, GitLab server behavior, optional Origin schema, external tracker writes or optional service integrations. Those unchanged limits remain explicit in the initial validation record. No new service, authority expansion or incompatible scope change is proposed.

Candidate SHAs, full inventories, hashes, source diffs, separate family coverage, successful and incomplete fixture results, held exclusions, integration status and next actions are saved outside installed skills under `~/.local/state/agent-skills/maintenance/2026-10-16T082954Z/`. The runtime checkpoint is bookkeeping, leaves baselines untouched and never claims a completed review. Delivery is one draft PR; merging and global installation refresh remain outside this run.
