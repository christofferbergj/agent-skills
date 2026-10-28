---
name: maintain-skills
description: Adopt upstream changes into this skill library while keeping its local adaptations, and audit its skills.
disable-model-invocation: true
---

# Maintain skills

Keep this library's sourced skills current with their upstreams while keeping the light local adaptations that fit them to this setup. [The adaptation contract](references/ADAPTATION.md) defines that setup and how to decide each upstream change. [The maintenance guide](MAINTENANCE.md) gives the helper commands, runtime state, checks, and branch rules the steps use.

Run in one of two modes:

- **Upstream**: adopt upstream changes since each skill's reviewed position, import new upstream skills, and review skills whose files changed since the last run.
- **Audit**: do the upstream work, then work through carried items, the fidelity backlog, pending skills, and stale reviews, checking each skill against current tools, documentation, and repository conventions.

The user or the scheduled task can name the mode; otherwise `begin` picks it. Only an explicitly named subset of skills narrows either mode.

Use /swarm throughout. Give each worker one slice, such as a source group, a batch of skills, or a repair, with the exact local revision, the immutable candidate, the adaptation contract, its evidence requirements, and the files it may write. Workers do their slice directly without starting another coordinator. The coordinator fetches sources, owns the checkpoint, canonical documents, and integration, and collects every worker's result; a failed or missing result stays pending. Without delegation, work sequentially and note the lost independence in the run's report.

## 1. Begin

Read the repository's `AGENTS.md`, the adaptation contract, and the maintenance guide. Run `begin`. When it reports the lock held, stop and name the run that holds it. Otherwise this run owns the lock until it runs `release`.

Sync both worktrees by the guide's branch rules, then reapply each of `begin`'s `leftovers`, the saved edits of a run that ended before delivery, to its synced worktree as the guide describes; report and carry one that no longer applies. When `begin` reports `legacyNextActions`, convert that file into `next-actions.json`. Read the owner comments posted since `commentsSince` on the open maintenance PRs and on the PRs the questions link to. Check installed copies with `scripts/check-installs.py`, and refresh them as `AGENTS.md` says when they are stale. Run `inventory --resume` with `begin`'s checkpoint from the library worktree.

**Complete when:** this run holds the lock, both worktrees match their sync rule, every leftover is reapplied or carried, and you hold `begin`'s mode, checkpoint, questions, carried items, and leftovers, every owner comment since `commentsSince`, a current install check, and the inventory with its `changedSince`, `contextChanged`, and `staleReviews` lists.

## 2. Find what changed

Run `fetch`, then `compare --fetch` with `--resume`. Save the inventory, fetch result, and compare reports in the run folder. Build the worklist in this order, which is also the order of work:

1. Reapplied leftovers, which still need validation and delivery.
2. Owner answers and comments not yet applied.
3. Changed upstream skills and shared inputs, and every source whose fetch failed.
4. New, removed, or moved upstream skills in the catalog's suites.
5. Skills in `changedSince`, including new skills, and the inputs in `contextChanged`.
6. In audit mode only: carried items, overdue ones first; the inventory's `fidelityBacklog`; skills the checkpoint lists as pending; then the oldest `staleReviews`, up to a quarter of the library.

When items 1 to 5 are empty in upstream mode, save a checkpoint from the compare reports, prune old runs, run `release`, and stop. A quiet run needs no branch, checks, review, PR, or report.

**Complete when:** every reapplied leftover, unapplied owner answer, compare report entry, failed source, `changedSince` skill, and `contextChanged` input, and in audit mode every carried item, `fidelityBacklog` record, pending skill, and the oldest `staleReviews` up to a quarter of the library, is on the worklist or recorded as unchanged, or the run has stopped as a quiet run.

## 3. Decide and repair

Edit on the maintenance branches by the guide's branch rules. Decide each upstream change by the adaptation contract, and record each decision as it describes. Dispatch repairs to isolated writers using /writing-for-agents, and inspect each returned diff. Import new upstream skills and propose retirements as the contract describes. When a change touches a shared owner, check its consumers in both suites.

For each skill in `changedSince`, check that its edits keep its recorded adaptations and repository conventions. For each input in `contextChanged`, read its diff since the checkpoint's `libraryRevision` and name every skill whose review it affects. In audit mode, check tool names, commands, links, and practices against the environments each skill supports, starting from exposed tool schemas, installed versions, and local help output. Review first-party skills and local adaptation text with /writing-for-agents, and treat sourced text by the contract's minimal-divergence rule.

Run the contract's fidelity check on every sourced skill you edit or find in `changedSince`, and in audit mode on backlog records.

Settle each item that waits on the owner as a question, as the contract's decision records describe. Carry an item only when the budget ran out or it waits on a later upstream revision: record it in `next-actions.json` with the date it was first carried. An overdue carried item has already survived an audit; finish it in this audit or ask it as a question.

**Complete when:** every worklist item is adopted, adapted, excluded, asked as a question, or carried in `next-actions.json` with its reason; every overdue carried item is finished or asked; every `contextChanged` input has its affected skills named; and every edited or locally changed sourced skill passes both fidelity directions.

## 4. Validate

Read changed instructions end to end and run the maintenance guide's checks. Exercise changed scripts or workflows on a small isolated example, and confirm each new regression test fails with its repair reverted. Dispatch an independent final review of the exact diff, its decisions, fidelity, and coverage, and resolve its findings. Re-enumerate skills so additions made during the run enter coverage.

Advance a skill's reviewed-through position only when its whole upstream delta is decided and checks pass. Save the checkpoint with this run's finished local reviews; after step 3 reviewed a context change, add `--context-reviewed` with the affected skills. A checkpoint never advances a position.

**Complete when:** checks pass; every new regression test fails with its repair reverted; every final-review finding is fixed, asked, or carried; every moved reviewed-through position has its whole delta decided; and the checkpoint is saved.

## 5. Deliver

Commit library changes and changes to this skill's own process on their separate maintenance branches, push each by the guide's push rule, and create or update one draft PR for each, within the action grant: the scheduled prompt's grant for a scheduled run, and the user's request for an invoked one. Prune old runs, then run `release`.

Report what changed, the questions waiting on the owner, failures such as failed sources and discarded leftovers, and coverage still pending.

At the budget's wrap-up point, start no new worklist items: validate, checkpoint, and deliver what is finished, carrying the rest.

**Complete when:** each PR is a draft whose head on the forge equals the pushed commit and whose description lists its open questions; the report is written; every action stayed within the grant; and the lock is released.
