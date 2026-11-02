---
name: usage-review
description: Measure how the owner works across their T3 Code threads, follow up on earlier changes, and open one draft PR of evidence-backed improvements.
disable-model-invocation: true
---

# Usage review

Measure the owner's real T3 Code usage, check whether changes from earlier runs worked, and turn patterns that clear the evidence bar into at most one draft PR in this repository. Merging stays with the owner. A weekly scheduled task runs this from the default branch's `skills/` tree.

The state folder `~/.local/state/usage-review/`, written `$STATE` below, holds `baseline.json` (the last run's metrics, for week-over-week comparison), `shipped.json` (every change a run proposed, as metric contracts with frozen baselines), `private-names.txt` (names the owner adds for the public check), and `runs/<date>/`, written `$RUN`. Scripts are in this skill's `scripts/` folder, run with `node`, and document their flags in their header comments.

**This repository is public and the threads hold client work.** Everything published, meaning changed files, commit messages, and the PR title and body, carries counts and paraphrased patterns only: no quoted thread text, client, project, or people names, other repositories' URLs, or ticket ids.

## 1. Begin

Read the repository's `AGENTS.md`. Take the lock with `mkdir $STATE/lock`, which fails when another run holds it. When it fails and the folder is less than two days old, stop and report its age; when it is older, a run died holding it, so remove it, take it again, and say so in the report. Read `baseline.json` and `shipped.json` when they exist.

**Complete when:** this run holds the lock, and the baseline and shipped changes are loaded or known to be absent.

## 2. Measure

Run `extract.ts --days 7 --out $RUN/messages.jsonl`, then `metrics.ts --in $RUN/messages.jsonl --out $RUN/metrics.json --shipped $STATE/shipped.json`, leaving out `--shipped` before the first change ships. Owner messages are typed `request`, `steer` (sent while a run was active), `answer`, or `unpaired` (the run before it left no final reply); menu metrics and assistant length use `answer` rows only. With fewer than 30 owner messages, report "too little data", remove the lock, and stop.

**Complete when:** `messages.jsonl` and `metrics.json` exist in `$RUN`, or the run stopped on too little data.

## 3. Follow up

For each entry in `shipped.json` without a `measureFrom`, read its PR with `gh pr view <pr> --json state`. Once it reads merged and the repository's `scripts/check-installs.py` reports no stale installs, set the entry's `measureFrom` to now, since only messages written after installed copies hold the change can show its effect; rerun `metrics.ts` when you set one. Take each result from `metrics.json`'s `followUps`: `moved`, `unchanged`, `wrong-way`, or `insufficient-exposure`, each against the baseline frozen when the change shipped. One `wrong-way`, or `unchanged` here and in the previous run's `metrics.json`, makes the change a revert candidate for step 4.

**Complete when:** every shipped change has a result for this window and every revert candidate is named.

## 4. Find patterns

Candidates are the recurring phrases in `metrics.json`'s `candidates`, each with its message ids; the `extensions` the owner adds when picking a letter, such as a merge, a review first, or both options, each with its message ids; `confusion` replies, which ask for the work to be explained again; letters the owner rarely picks, from `picksByMenuSize`; and revert candidates. Validate each by reading its threads with `t3_thread_read`, since a recurring phrase alone shows neither a preference nor a correction. A pattern clears the bar `phraseCandidates` applies, counted in validated messages; when one falls short in 7 days, rerun `extract.ts --days 14 --out $RUN/14d/messages.jsonl`, then `metrics.ts` on that file into `$RUN/14d/metrics.json`, and require the bar there. Record each kept pattern's message ids, and each dropped candidate with its reason, in `$RUN/patterns.json`.

**Complete when:** every candidate is in `patterns.json`, kept with its message ids or dropped with a reason.

## 5. Decide

Pick at most three changes, each tied to one kept pattern. Skip a rule changed in the last 14 days unless its follow-up reads `wrong-way`. Write each as a metric contract, the `Contract` type in `metrics.ts`: a stable `rule` id, `opportunity` and `success` predicates, the preferred `direction`, and a `minExposure`, which the script raises to 20. A change to skill text in this repository goes into the PR; a finding outside it, such as the global instructions in `~/.config/agents`, T3 settings, or scheduled tasks, goes in the report as a lettered option, because edits under `~/.config` publish live. Freeze each contract's baseline with `metrics.ts --in $RUN/messages.jsonl --freeze <contracts.json>`; it refuses a baseline below the minimum exposure, so rerun it on `extract.ts --days 28` output, and drop the change with its reason when the baseline is still too small. Save the picks, their frozen contracts, and the outside findings to `$RUN/decisions.json`.

**Complete when:** `decisions.json` holds each pick with its pattern, target file, and frozen contract, each dropped pick with its reason, and each finding outside the repository as an option.

## 6. Deliver

When a change was picked, branch `usage-review/<date>` from `origin/main` in its own worktree and make the edits through /writing-for-agents, following this repository's change rules: an `UPSTREAM.md` departure for a sourced skill, and an ADR revision where an ADR owns the area. Run `pnpm check`. Write the PR body through /pr. Before every push, and before creating or editing the PR, run `public-check.ts --pr-title <title> --pr-body <file>` from the worktree; a hit blocks publication and goes in the report by class and position. Then push and open one draft PR. Add its number to each frozen contract in `decisions.json` and append them to `shipped.json`.

**Complete when:** a draft PR exists that passed `public-check.ts` and its contracts are in `shipped.json` with baselines, or no change was picked, or the report names the check that blocked publication.

## 7. Report

Copy `$RUN/metrics.json` to `$STATE/baseline.json`. Reply in the run's thread with this week's metrics against the previous baseline, each follow-up result, the PR link, and the outside-repository options. Remove the lock.

**Complete when:** `baseline.json` is this run's metrics, the reply is posted, and the lock is gone.
