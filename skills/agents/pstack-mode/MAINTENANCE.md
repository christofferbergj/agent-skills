# Maintain the Pstack adaptation

Invoke /maintain-skills from this source repository, scoped to every local name in `suite.json`, including `bro`. Install its `/writing-for-agents` dependency. This guide owns suite-specific review; individual `UPSTREAM.md` records own immutable import and reviewed-through positions. `suite.json` owns membership and name mapping.

The [initial validation record](VALIDATION.md) documents exercised hosts, fixtures, and integration limits. Re-run only checks relevant to a maintenance change.

## 1. Establish the review

Read repository guidance, this guide, the mapped source records, and initial Git status. Protect unrelated work. Use a dedicated update branch or host-managed worktree; reuse an existing maintenance branch/PR when it belongs to this suite and its state is understood. Runtime checkpoints belong outside installed skills.

For scheduled work, record a 60-minute working budget and start wrapping up by minute 50. Read the clock at phase boundaries. Reserve validation and reporting time rather than starting another large unit near the deadline. Ad hoc runs use their own agreed limits.

Complete when scope, ownership, current work, candidate source location, and deadline are recorded.

## 2. Fetch once and inventory

Fetch `https://github.com/cursor/plugins.git` outside the working tree with enough history for recorded baselines. Resolve upstream `main` to one immutable candidate SHA and keep that snapshot for this review. Do not install the original plugin over the adaptations.

Run `python3 scripts/suite.py compare --root <source-repo> --upstream <upstream-checkout> --candidate <candidate-sha> --output <runtime-report.json>` from this skill directory. Inspect the whole `pstack/` tree as well as per-skill changes, including agents, playbooks, scripts, guides, manifests, and licenses. The report is a coverage input, not a completed review. The local suite index intentionally excludes the dormant Benny automation pack.

Complete when mapped changes, additions, removals, renames, shared inputs, and unavailable history are accounted for. A missing baseline remains blocked rather than becoming today's import.

## 3. Review and adapt selectively

Compare the previous reviewed source, candidate source, and local files. Preserve the portable execution contract, explicit router activation, scoped history, draft-PR default, existing receiver boundary, and task-sized rigor. Preserve local invocation changes needed for callable dependencies. Retain MIT credit and review license changes before importing new material.

Translate useful changes into the adaptation rather than copying upstream over it. Record adopted, adapted, and excluded changes and their reasons. Original Cursor model slugs, cloud-only APIs, ten-lane policy, raw forced cleanup, automatic tracker writes, and ready-PR defaults are deliberate differences, not drift to undo.

Propose straightforward new skills within the existing capability boundary in the update PR, with names, metadata, source records, resources, listings, and suite mapping. A new backend or broader authority is a scope change. Preserve removed local skills and propose retirement explicitly for review. A rename needs continuity evidence before changing an existing installed name.

Complete each skill only after its full relevant delta and shared inputs are resolved. Hold behavior whose required verification is unavailable and continue independent validated work.

## 4. Validate and checkpoint

Run repository formatting, Skills CLI discovery, diff, and secret checks. Run `python3 scripts/suite.py validate --root <source-repo>`. Exercise changed scripts and consequential host branches with focused fixtures or smoke tasks; do not run every expensive skill to test prose. Disclose an unavailable optional cross-vendor pass separately from missing required workflow evidence.

Run focused Python tests with `python3 -m unittest discover -s scripts/tests -v` from each changed owner: this skill, `/pstack-recall`, or `/pstack-swarm`.

For Bun tools, run `bun scripts/bootstrap.ts --print-runtime` to prepare an immutable-source runtime cache, then run `bun test` and `bun run typecheck` in the returned directory. The source scripts and installed instruction directories remain unchanged by bootstrap. The runtime cache includes the exact source and frozen dependency lockfile.

Advance a skill's reviewed-through revision only after its relevant delta is resolved and required checks pass. Keep the imported revision fixed. Use `python3 scripts/suite.py checkpoint --candidate <sha> --completed <validated-local-names> --elapsed-minutes <elapsed> --output <runtime-checkpoint.json>` to save coverage. This command never advances source records. Store unfinished diffs, evidence, and next actions with that checkpoint; omit raw private history from published changes.

Complete when the validated subset and exact unfinished coverage are durable, with incomplete baselines unchanged.

## 5. Prepare the update PR

The scheduled grant permits scoped commits, pushing an update branch, and creating or updating a draft PR. Keep validated changes separate from held changes. Lead the PR description with resulting behavior, meaningful upstream changes, preserved adaptations, validation, and outstanding gaps. An empty relevant delta needs no PR or duplicate decision row.

Merging to `main`, refreshing installed copies, and expanding services or action authority require separate authorization. Keep unchanged or non-actionable reviews quiet. Notify for a proposed update, failure, or decision the user must make. If the working budget expires, report the validated subset and resume checkpoint without declaring the full review complete.

Complete when the draft PR or no-change outcome is verified, unfinished work is explicit, and all actions stay within the grant.
