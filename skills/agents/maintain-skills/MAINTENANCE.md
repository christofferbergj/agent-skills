# Maintenance guide

Reference for the commands, runtime state, catalog, checks, and branches that /maintain-skills uses in this repository. `$STATE` is `~/.local/state/agent-skills/maintenance`, `$REPO` is the main checkout of this repository, `$RUN` is the run folder `begin` opens, and `$HELPER` is `skills/agents/maintain-skills/scripts/catalog.py`.

## Runtime state

Keep run evidence in `$STATE`, outside installed skills:

- `lock/` marks the run that owns the state. `begin` takes it, `release` frees it, and `begin` takes over a lock older than three hours.
- `sources/` holds one blobless clone per upstream repository, reused across runs.
- `worktrees/library/` and `worktrees/process/` hold the two maintenance worktrees, reused across runs.
- `runs/<UTC timestamp>-<mode>/`, such as `runs/2026-10-21T080000Z-upstream/`, holds the run's `begin.json`, `inventory.json`, `fetch.json`, compare reports, worker assignments and evidence, and `checkpoint.json`.
- `questions.json` lists questions waiting on the owner, each with its item, question, recommendation, date asked, and PR link. Remove a question once its answer is recorded in the repository.
- `next-actions.json` lists carried items, each with its `item`, `reason`, and `firstCarried` date. Remove an item once it is finished or asked.

A missing `questions.json` or `next-actions.json` means the list is empty.

## Helper commands

### Begin and release

Run `begin` first, from the default branch's copy of the helper, since the worktrees are unsynced until it holds the lock:

```bash
git -C "$REPO" fetch --quiet origin
git -C "$REPO" show "origin/main:$HELPER" | python3 - begin --state "$STATE"
```

It exits 3 when another run holds the lock. Otherwise it prints, and saves as `$RUN/begin.json`:

- `run` and `mode`, with `modeReason`. Without `--mode`, it picks audit unless an audit's checkpoint finished with `coverageComplete` fewer than seven calendar days ago.
- `resume`: the newest valid checkpoint, skipping unreadable ones, which it lists in `skippedCheckpoints`.
- `commentsSince`: when that checkpoint's run started. Owner comments posted since then are new.
- `questions` and `nextActions` from runtime state. A carried item is `overdue` once an audit has finished since it was first carried. `legacyNextActions` names an older run's `next-actions.md` to convert when `next-actions.json` is missing.
- `leftovers`: what an interrupted run left in each worktree, saved before syncing discards it. Uncommitted `changes` are in its `patch` file, and `unpushed` commits, newest first, stay reachable under its `ref`. After syncing, reapply them with `git -C "$WORKTREE" apply --3way <patch>` and by cherry-picking the commits oldest first.

Free the lock after the last write to `$STATE`, the same way:

```bash
git -C "$REPO" show "origin/main:$HELPER" | python3 - release --state "$STATE" --run "$RUN"
```

### Inventory, fetch, and compare

Run the other commands from the root of the synced library worktree, so its fingerprints include the open library PR's edits. Changes on the process branch take effect after they merge.

`inventory` lists every local skill, its provenance records, and source groups. Each group key combines a repository and its tracking choice, such as `github.com/cursor/plugins@branch:main`. `fidelityBacklog` lists sourced skills whose record has no `Fidelity checked through` line. With `--resume`, `changedSince` lists the skills whose files changed since that checkpoint, `contextChanged` the governing inputs that changed, and `staleReviews` the skills whose last local review is more than four weeks old, oldest first.

```bash
python3 "$HELPER" --root . inventory --resume <checkpoint> --output "$RUN/inventory.json"
```

`fetch` clones or updates every source in `$STATE/sources/` and writes `candidates`, `checkouts`, and `errors`, each keyed by group. It exits non-zero when any source fails; compare a failed source with `--source` from its clone at the checkpoint's candidate, and report the failure.

```bash
python3 "$HELPER" --root . fetch --state "$STATE" --output "$RUN/fetch.json"
```

`compare` reports each group's changes since each skill's reviewed position. With `--fetch`, it compares every fetched group and writes one report per group, named from its key, such as `github.com-cursor-plugins-branch-main-compare.json`, plus a summary to stdout:

```bash
python3 "$HELPER" --root . compare --fetch "$RUN/fetch.json" --resume <checkpoint> --output-dir "$RUN"
```

To compare one group again, pass `--source <group-key> --upstream <checkout> --candidate <sha> --output <file>`, taking the checkout and candidate from `fetch.json`.

Each skill gets `unchanged`, `changed`, `removed`, or `blocked`, with the changed files and `since`, the revision it was compared from. With `--resume`, a skill whose files are unchanged since a checkpoint that reviewed it is compared from that checkpoint's candidate and marked `carriedForward`, so decided and held changes do not return. For each catalog source, `suites` lists added, removed, possibly moved, and excluded upstream skills, and `sharedInputs` lists changed shared files since `sharedReviewedThrough` or the resumed checkpoint. A source without a catalog entry, such as OpenClaw, compares only the paths its record lists; it has no added-skill detection, because its record tracks those files alone. A `blocked` skill keeps its position; missing history never resets one.

### Checkpoint and prune

`checkpoint` records coverage without touching source records:

```bash
python3 "$HELPER" --root . checkpoint \
  --candidates "$RUN/fetch.json" --compare "$RUN"/*-compare.json \
  --source-reviews "$RUN/source-reviews.json" --completed <names> \
  --elapsed-minutes <minutes> --resume <checkpoint> --output "$RUN/checkpoint.json"
```

- `--candidates` takes `fetch.json` as written. A failed group keeps the checkpoint's candidate and stays pending, whatever the compare reports say.
- `--compare` counts every unchanged skill, and every empty inventory and shared-input report, as reviewed. A quiet run needs only `--candidates`, `--compare`, `--resume`, `--elapsed-minutes`, and `--output`.
- `--source-reviews` adds the groups' decided changes, including held ones:

  ```json
  {
    "github.com/cursor/plugins@branch:main": {
      "candidate": "<40-character-sha>",
      "inventoryReviewed": true,
      "sharedInputsReviewed": true,
      "skills": ["pstack-help"]
    }
  }
  ```

- `--completed` names the skills whose local review finished this run, each as its own argument (in zsh, expand a list with `${=names}`); `--resume` carries earlier reviews of unchanged skills forward.
- A change to a governing input lapses every earlier local review. After reviewing that change, add `--context-reviewed`, with `--context-affected <names>` for the skills it affects; every other review stands.
- `--elapsed-minutes` is the decimal minutes since `begin`.
- Add `--integration-validated` only after the affected checks pass. When no skill or governing input changed since a validated checkpoint, the resumed validation carries over on its own.

Set every acknowledgement from collected evidence; the helper checks coverage and fingerprints but cannot confirm that a review happened. `validate` checks names, metadata, links, listings, and provenance across the library.

After saving the checkpoint, keep the 14 newest runs:

```bash
python3 "$HELPER" prune --state "$STATE" --keep 14
```

## Catalog

`catalog.json` holds a policy for each tracked suite: Matt Pocock, Pstack (its mapping is in `skills/agents/pstack-mode/suite.json`), and Thermos. Each policy maps upstream skills to local ones. A mapping whose local name differs from upstream's gives the reason in `renamed`, by [the adaptation contract's names rule](references/ADAPTATION.md#library-wide-adaptations). Each policy also sets:

- `excludedNames` and `excludedPaths`: upstream skills and paths left out, each with a reason; `excludedPathComponents`: directory names, such as personal folders, left out wherever they appear. Exclusions apply to new imports and shared inputs, never to an existing local skill.
- `sharedRoot`, or else `sharedPaths`: suite-wide inputs such as READMEs, guides, and agent wrappers. When both are set, only `sharedRoot` is compared.
- `sharedReviewedThrough`: the revision through which those shared inputs are decided. Advance it with the same rule as a skill's reviewed-through position.

`owners` names the shared-owner roles. `contextPaths` and `contextOwners` name the governing inputs whose change lapses earlier local reviews.

## Checks

Run `pnpm check` from the worktree root; it runs every repository gate and test suite. Use [Thermos's guide](../../reviews/thermos/MAINTENANCE.md) for Thermos behavior changes.

## Branches and pull requests

Library changes go on the `skill-maintenance` branch. Changes to this skill's own process files, everything in `skills/agents/maintain-skills/` except `catalog.json`, go on `skill-maintenance-process`. A shared-owner change edits `catalog.json`'s `owners`, `docs/architecture.md`, and the adaptation contract's shared owners together on `skill-maintenance`, because a test keeps them equal. Each branch has at most one open draft PR.

Sync each worktree after `begin`, creating it with `git worktree add` when missing; create the process worktree at the first process edit. After fetching, record `git -C "$WORKTREE" rev-parse --verify --quiet "origin/$BRANCH"` as the branch's lease, empty when it has no remote branch:

- **Open PR:** start from its pushed head, which includes any owner commits, rebased onto the default branch. When the rebase stops on a conflict, abort it and ask the owner; that branch's work waits.

  ```bash
  git -C "$WORKTREE" fetch --quiet origin
  git -C "$WORKTREE" checkout --quiet --force -B "$BRANCH" "origin/$BRANCH"
  git -C "$WORKTREE" clean -fdq
  git -C "$WORKTREE" rebase --quiet origin/main
  ```

- **Merged or no PR:** detach at the default branch, and create the branch from it at the first edit.

  ```bash
  git -C "$WORKTREE" fetch --quiet origin
  git -C "$WORKTREE" checkout --quiet --force --detach origin/main
  git -C "$WORKTREE" clean -fdq
  ```

- **Closed without merging:** read its comments and record each stated decision. Add its other proposals to `questions.json`.

Push only against the recorded lease, so an owner commit pushed during the run stops the push instead of being overwritten: `git -C "$WORKTREE" push --force-with-lease="$BRANCH:$LEASE" origin "HEAD:$BRANCH"`. When the push is refused, sync again and redo the delivery.

Follow /pr for descriptions, list the open questions in each PR description, and link each PR to the run's thread when the host supports it. PR descriptions carry a run's evidence; add a dated `docs/reviews/` record only for an audit run or a change to how the library is maintained.
