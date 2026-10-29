# Whole-library maintenance

Historical audit and rebase record. Counts and pending prerequisites describe those snapshots. Later full-inventory and attribution repairs are recorded in the [combined validation history](2026-10-15-combined-validation.md#rebase-on-the-current-library); current ownership is explained in the [library architecture](../architecture.md).

Reviewed all 94 local skills and 517 supporting files from default-branch commit `aa659e21f4484b3be362541cb0435526e235b6e4`. The inventory includes 90 sourced adaptations and four first-party skills. No new or relevant untracked skill was omitted. Three direct native Codex workers used disjoint write boundaries; none started another coordinator.

## Rebase onto the reorganized library

Rebased onto `6e13dca230ce7d7a2476ae53b609b4ec7a651930` on 2026-10-16. The category moves and explicit retirement of `migrate-to-shoehorn`, `writing-beats`, `writing-fragments`, and `writing-shape` leave 90 installed skills and 501 supporting files, including 86 sourced adaptations and four first-party skills. All 19 original maintenance files retain their exact contents at the new paths before this note was added. The watcher implementation and regression tests are unchanged.

At this rebase, the suite catalog had 82 mappings. Completed coverage carried forward for 88 retained skills; `maintain-skills` and `pr` awaited the separate full-inventory and Humanlayer attribution prerequisite. The expanded validator then reported the same two ancestry-record problems. The sections below preserve the original 94-skill audit and its evidence; the rebase inventory, integration checks, and fingerprints were recorded in the checkpoint outside installed skills. No source position advanced as part of the rebase.

## Original audit slices

| Review slice                     | Coverage                                                          | Terminal result                                                           |
| -------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Additional skills and provenance | Eight skills, 51 files, Thermos and OpenClaw comparisons          | ISSUES: repaired pnpm guidance; retained known maintenance prerequisite   |
| Matt adaptations                 | 32 skills, 157 files, complete source inventory and shared inputs | ISSUES: repaired two guides; retained known PR ancestry prerequisite      |
| Pstack adaptations               | 54 skills, 309 files, complete source inventory and shared inputs | PASS: repaired watcher and TypeScript guidance; preserved local contracts |

## Repairs and observed evidence

- The PR watcher used an entire polling interval or retry delay even when it exceeded the deadline, then queried again. Three public-runner regression tests fail against the exact base. The repair stops before another poll, including during queued partial sweeps. A Claude critique exposed a priority regression in the first repair: a partial sweep or retry deadline could hide a known blocker. Two further regressions fail that frozen intermediate artifact and pass after restoring tier-major blocker priority. A second critique identified early timer wakes: a Bun 1.4.3 probe observed waits finishing before their requested fractional duration. Two additional regressions fail the preceding repair and pass when a wait capped by the remaining budget terminates polling directly. Terminal query-error budgets remain first, and incomplete snapshots cannot establish readiness. Retry events no longer promise a retry after the deadline. The option is explicitly a polling deadline; in-flight queries finish.
- `pnpm update --no-save` preserves manifest ranges but still creates `node_modules` in an isolated pnpm 11.28.5 fixture. Adding supported `--lockfile-only` preserves the manifest and leaves `node_modules` absent. The guide distinguishes both effects and checks installed-version support.
- Dependency-cruiser 18.6.0 with TypeScript 6.0.2 and Node 24.22.0 misses an app deep import when scanning only packages. Scanning all source roots detects it. The revised recipe proves both test and external-app violations with restored passes, including separate package/app roots. All five configured rules detect their intended violations.
- Triage's nested Markdown fences now contain the complete example and expose the following operating instructions. A fence-state check verifies both roles.
- TypeScript 7.0.2 declarations and execution verify safe const assertions, validated brands, and contextual inference for `satisfies`. The examples define their target type and distinguish literal-union inference from broad strings and numbers. Numeric range constraints retain boundary validation.
- Technical-writing snippets follow the invoking repository's formatter.

## Sources and decisions

Each canonical repository was fetched once with full baseline history, then compared at an immutable candidate:

| Source         | Candidate                                  | Inventory decision                                                                                                                                            |
| -------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Matt Pocock    | `49dd158d1076134a641b33efb035946536778336` | 38 skills; 32 retained adaptations and six recorded import exclusions; no delta                                                                               |
| Cursor plugins | `f713f14203cd6420cec13cd7c55c32d598dbab68` | 111 skills: 54 Pstack adaptations, three excluded Benny skills, three Thermos adaptations, and 51 unrelated skills in other plugins; no additions or removals |
| OpenClaw       | `faca2b7a732ddd837c72aa34f970064d2c8baa34` | 126 skills versus 125 at baseline; reviewed two additions and one removal                                                                                     |

Thermos's complete tree is unchanged, including wrappers, documentation, manifest, assets, and license. All Pstack skill roots match their recorded baselines; relevant shared changes were reviewed, retaining local native-host execution, concrete type guidance, canonical owners, and action boundaries. All 90 retained licenses match their reviewed sources and candidates.

OpenClaw's audit body, campaign, audit reference, and license are unchanged. Both testing-support deltas and relevant linked resources were reviewed. Generic proportional proof is already local. OpenClaw services, CI commands, live-channel policies, expected-failure authority, fixed timing budgets, and fixture recipes remain excluded. New `pr-simplify` overlaps existing review/test-value owners; `plugin-sdk-impact` adds OpenClaw SDK/service scope. Removed `deslop` has no OpenClaw-sourced local consumer. Preserve the unknown historical imports of `test-audit` and the earlier `bro` copy separately from their established reconciliation baselines.

## Validation and retained gaps

The regenerated runtime passes 85 Bun tests and type checking. All 58 existing Python tests pass, for 143 repository tests in total. An independent native critic ran 15 additional watcher cases, covering disabled timeouts, terminal/error precedence, queue completion, partial sweeps, known-blocker priority, and early timer wakes. Its separate 20-sample real-timer probe observed four extra polls before the timing repair and none afterward; this is fixture evidence, not a population-frequency claim. It also reconciled all 94 skills and 517 supporting files with the worker evidence. Formatting, skill discovery, metadata, local links, retained licenses, whitespace, and secret checks pass for the delivered subset; the expanded provenance validator's known failures are retained below. Isolated local installations expose all 94 skills to both host layouts; global installations remain unchanged.

At the original review, the default branch's helper and guide accounted for only 86 mapped adaptations and two source aliases. The expanded implementation and PR's inherited Humanlayer attribution-only clarification already existed at local commit `c483887`; this pass did not duplicate that unmerged work. The original external full-inventory ledger recorded 92 completed skills and kept `maintain-skills` and `pr` pending that prerequisite. A mapped-only checkpoint is not whole-library completion. Runtime candidates, assignments, terminal evidence, fingerprints, source decisions, checks, and next actions are kept under the maintenance state directory, outside installed skills.

Live hook activation/trust, GitLab server/tier behavior, the optional Origin head schema, external tracker writes, optional services, and every UI/framework permutation remain unverified. Unchanged selected current/legacy artifact and host workflows reuse their recorded evidence; this pass does not claim to rerun every skill. No global installation was refreshed.
