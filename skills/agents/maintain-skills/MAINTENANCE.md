# Maintenance guide

Reference for the commands, runtime state, catalog, checks, and branches that /maintain-skills uses in this repository. `$STATE` is `~/.local/state/agent-skills/maintenance`, and `$RUN` is this run's folder under it.

## Runtime state

Keep run evidence in `$STATE`, outside installed skills:

- `sources/` holds one blobless clone per upstream repository, reused across runs.
- `runs/<UTC timestamp>-<mode>/`, such as `runs/2026-10-21T080000Z-upstream/`, holds the run's fetch result, compare reports, worker assignments and evidence, `checkpoint.json`, and next actions.
- `questions.json` lists questions waiting on the owner, each with its item, question, date asked, and PR link. Remove a question once its answer is recorded in the repository.

Resume from the newest `checkpoint.json` under `runs/`; until `runs/` has one, use the newest under the older timestamped folders directly in `$STATE`. After saving the checkpoint, keep the 14 newest runs:

```bash
python3 skills/agents/maintain-skills/scripts/catalog.py --root . prune --state "$STATE" --keep 14
```

## Helper commands

Run the helper from the root of the library worktree, so its fingerprints include the open library PR's edits.

`inventory` lists every local skill, its provenance records, and source groups. Each group key combines a repository and its tracking choice, such as `github.com/cursor/plugins@branch:main`. `fidelityBacklog` lists sourced skills whose record has no `Fidelity checked through` line. With `--resume`, `changedSince` lists the skills whose files changed since that checkpoint.

```bash
python3 skills/agents/maintain-skills/scripts/catalog.py --root . inventory --resume <prior-checkpoint.json>
```

`fetch` clones or updates every source in `$STATE/sources/` and writes `candidates`, `checkouts`, and `errors`, each keyed by group. It exits non-zero when any source fails. Compare a failed source from its clone at the prior checkpoint's candidate, keep its review pending, and report the failure.

```bash
python3 skills/agents/maintain-skills/scripts/catalog.py --root . fetch --state "$STATE" --output "$RUN/fetch.json"
```

`compare` reports one group's changes since each skill's reviewed position:

```bash
python3 skills/agents/maintain-skills/scripts/catalog.py --root . compare \
  --source <group-key> --upstream <checkout> --candidate <sha> \
  --resume <prior-checkpoint.json> --output "$RUN/<group>-compare.json"
```

Each skill gets `unchanged`, `changed`, `removed`, or `blocked`, with the changed files and `since`, the revision it was compared from. With `--resume`, a skill whose files are unchanged since a checkpoint that reviewed it is compared from that checkpoint's candidate and marked `carriedForward`, so decided and held changes do not return. For each catalog source, `suites` lists added, removed, possibly moved, and excluded upstream skills, and `sharedInputs` lists changed shared files since `sharedReviewedThrough` or the resumed checkpoint. A source without a catalog entry, such as OpenClaw, compares only the paths its record lists. A `blocked` skill keeps its position; missing history never resets one.

`checkpoint` records coverage without touching source records:

```bash
python3 skills/agents/maintain-skills/scripts/catalog.py --root . checkpoint \
  --candidates "$RUN/fetch.json" --compare "$RUN"/*-compare.json \
  --source-reviews "$RUN/source-reviews.json" --completed <names> \
  --elapsed-minutes <minutes> --resume <prior-checkpoint.json> --output "$RUN/checkpoint.json"
```

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

- `--completed` names the skills whose local review finished this run; `--resume` carries earlier reviews of unchanged skills forward.
- Add `--integration-validated` only after the affected checks pass.

Set every acknowledgement from collected evidence; the helper checks coverage and fingerprints but cannot confirm that a review happened. `validate` checks names, metadata, links, listings, and provenance across the library.

## Catalog

`catalog.json` holds a policy for each tracked suite: Matt Pocock, Pstack (its mapping is in `skills/agents/pstack-mode/suite.json`), and Thermos. Each policy maps upstream skills to local ones and sets:

- `excludedNames`, `excludedPathComponents`, and `excludedPaths`: upstream skills and paths left out, each with a reason. Exclusions apply to new imports and shared inputs, never to an existing local skill.
- `sharedRoot` or `sharedPaths`: suite-wide inputs such as READMEs, guides, and agent wrappers.
- `sharedReviewedThrough`: the revision through which those shared inputs are decided. Advance it with the same rule as a skill's reviewed-through position.

`owners` names the shared-owner roles; [the adaptation contract](references/ADAPTATION.md) lists the same owners, and a test keeps them equal. `contextPaths` and `contextOwners` name the inputs whose change invalidates earlier local reviews.

## Checks

```bash
pnpm fmt:check
npx skills@latest add . --list
git diff --check
gitleaks dir . --redact --no-banner
python3 skills/agents/maintain-skills/scripts/catalog.py --root . validate
python3 -m unittest discover -s skills/agents/maintain-skills/scripts/tests
```

Run the tests of each changed script owner under its `scripts/tests/`. For Pstack's Bun tools, run `bun skills/agents/pstack-mode/scripts/bootstrap.ts --print-runtime`, then `bun test` and `bun run typecheck` in the returned directory. Use [Thermos's guide](../../reviews/thermos/MAINTENANCE.md) for Thermos behavior changes. [The validation record](VALIDATION.md) holds earlier host exercises and known limits.

## Branches and pull requests

Library changes go on the `skill-maintenance` branch. Changes to this skill's own process files, everything in `skills/agents/maintain-skills/` except `catalog.json`, go on `skill-maintenance-process`. Each branch has at most one open draft PR, and each gets its own worktree outside the main checkout.

The library worktree checks out `skill-maintenance` while its PR is open, and the default branch otherwise.

- **Open PR:** keep working on its branch. Before pushing, rebase onto the default branch and push with `--force-with-lease`.
- **Merged or no PR:** create the branch from the default branch at the first edit.
- **Closed without merging:** read its comments and record each stated decision. Add its other proposals to `questions.json`.

Follow /pr for descriptions, list the open questions in each PR description, and link each PR to the run's thread when the host supports it. PR descriptions carry a run's evidence; add a dated `docs/reviews/` record only for an audit run or a change to how the library is maintained.
