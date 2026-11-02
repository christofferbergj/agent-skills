---
name: usage-review
description: Measure how the owner works across their T3 Code threads, follow up on earlier changes, and open one draft PR of evidence-backed improvements.
disable-model-invocation: true
---

# Usage review

Measure the owner's real T3 Code usage, check whether changes from earlier runs worked, and turn patterns that clear the evidence bar into at most one draft PR in this repository. Merging stays with the owner. A weekly scheduled task runs this from the default branch's `skills/` tree.

The state folder, `~/.local/state/usage-review/`, holds `baseline.json` (the last run's metrics), `shipped.json` (every change a run proposed, as metric contracts), `private-names.txt` (names the owner adds for the public check), and `runs/<date>/`. Scripts are in this skill's `scripts/` folder; each prints its usage when run without arguments.

**This repository is public and the threads hold client work.** Everything published, meaning changed files, commit messages, and the PR title and body, carries counts and paraphrased patterns only: no quoted thread text, client, project, or people names, other repositories' URLs, or ticket ids.

## 1. Begin

Read the repository's `AGENTS.md`. Create `~/.local/state/usage-review/lock` with this run's date; when it already exists, stop and report its date. Read `baseline.json` and `shipped.json` when they exist.

**Complete when:** this run holds the lock, and the baseline and shipped changes are loaded or known to be absent.

## 2. Measure

Run `extract.ts --days 7 --out runs/<date>/messages.jsonl`, then `metrics.ts --in runs/<date>/messages.jsonl --out runs/<date>/metrics.json --shipped shipped.json --baseline baseline.json`, leaving out the flags whose files don't exist. Owner messages are typed `request`, `steer` (sent while a run was active), `answer`, or `unpaired` (the run before it has no final reply); menu metrics and assistant length use `answer` rows only. With fewer than 30 owner messages, report "too little data", release the lock, and stop.

**Complete when:** `messages.jsonl` and `metrics.json` exist in the run folder, or the run stopped on too little data.

## 3. Follow up

For each entry in `shipped.json`, read its PR with `gh pr view <pr> --json state,mergedAt`. A merged change counts from the first window that starts after installed copies include it, which `scripts/check-installs.py` confirms; earlier windows read as `insufficient-exposure`. Take its result from `metrics.json`'s `followUps`: `moved`, `unchanged`, `wrong-way`, or `insufficient-exposure`. Two `unchanged` results in a row, or one `wrong-way`, make the change a revert candidate for step 4.

**Complete when:** every shipped change has a result for this window and every revert candidate is named.

## 4. Find patterns

Candidates come from `metrics.json`: recurring phrases (`candidates`, each with its message ids), options the owner always extends the same way, options never picked (`picksByMenuSize`), and revert candidates. Validate each by reading its threads with `t3_thread_read`, since a recurring phrase alone shows neither a preference nor a correction. A pattern clears the bar with at least 10 validated messages across at least 5 threads, in this window or the last two combined. Save each validated pattern's message ids to `runs/<date>/patterns.json`.

**Complete when:** every candidate is validated or dropped with a reason, and every kept pattern has its message ids saved.

## 5. Decide

Pick at most three changes, each tied to one validated pattern. Skip a rule changed in the last 14 days unless its follow-up reads `wrong-way`. Give each change a metric contract for `shipped.json`: a stable `rule` id, the `opportunity` and `success` predicates, the preferred `direction`, and a `minExposure` of at least 20, as `metrics.ts`'s `Contract` type defines. A change to skill text in this repository goes into the PR; a finding outside it, such as the global instructions in `~/.config/agents`, T3 settings, or scheduled tasks, goes in the report as a lettered option, because edits under `~/.config` publish live.

**Complete when:** each picked change has a pattern, a target file, and a metric contract, and each finding outside the repository is written as an option.

## 6. Deliver

When a change was picked, branch `usage-review/<date>` from `origin/main` in its own worktree and make the edits through /writing-for-agents, following this repository's change rules: an `UPSTREAM.md` departure for a sourced skill, and an ADR revision where an ADR owns the area. Run `pnpm check`. Write the PR body through /pr. Before every push, and before creating or editing the PR, run `public-check.ts --pr-title <title> --pr-body <file>` from the worktree; a hit blocks publication and goes in the report by class and position. Then push and open one draft PR. Append the changes to `shipped.json` with the PR number, and write this run's `metrics.json` to `baseline.json`.

**Complete when:** a draft PR exists that passed `public-check.ts`, with `shipped.json` and `baseline.json` updated, or the report says why no PR was opened.

## 7. Report

Reply in the run's thread with this week's metrics against the baseline, each follow-up result, the PR link, and the outside-repository options. Delete the lock.

**Complete when:** the reply is posted and the lock is gone.
