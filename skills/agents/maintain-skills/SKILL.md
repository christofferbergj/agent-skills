---
name: maintain-skills
description: Adopt upstream changes into this skill library while keeping its local adaptations, and audit its skills.
disable-model-invocation: true
---

# Maintain skills

Keep this library's sourced skills current with their upstreams while keeping the light local adaptations that fit them to this setup. [The adaptation contract](references/ADAPTATION.md) defines that setup and how to decide each upstream change; read it before deciding anything. [The maintenance guide](MAINTENANCE.md) gives the helper commands, runtime state, checks, and branch rules the steps use.

Run one of two modes:

- **Upstream**, the default: adopt upstream changes since each skill's reviewed position, import new upstream skills, and review skills whose files changed since the last run.
- **Audit**, when the user or the scheduled prompt asks: do the upstream work, then work through the fidelity backlog and review every other skill against current tools, documentation, and repository conventions.

Only an explicitly named subset of skills narrows either mode.

Use /pstack-swarm throughout. Give each worker one slice, such as a source group, a batch of skills, or a repair, with the exact local revision, the immutable candidate, the adaptation contract, its evidence requirements, and the files it may write. Workers do their slice directly without starting another coordinator. The coordinator fetches sources, owns the coverage ledger, canonical documents, and integration, and collects every worker's result; a failed or missing result stays pending. Without delegation, work sequentially and note the lost independence in the run's report.

## 1. Resume

Read repository guidance. Open the library worktree the maintenance guide describes and run the helper there. Load the newest checkpoint and the waiting questions from runtime state. Read new owner comments on the open maintenance PRs and on the PRs the waiting questions link to. Run `inventory --resume` with the checkpoint, and reconcile it with the actual `SKILL.md` files, including untracked ones.

**Complete when:** you hold the checkpoint, the waiting questions, every new owner comment, and the inventory with its `changedSince` list.

## 2. Find what changed

Run `fetch`, then `compare --fetch` with `--resume`. Save the inventory, fetch result, and compare reports in the run folder. Build the worklist in this order, which is also the order of work:

1. Owner answers and comments not yet applied.
2. Changed upstream skills and changed shared inputs.
3. New, removed, or moved upstream skills in the catalog's suites.
4. Skills in `changedSince`, including new skills.
5. In audit mode only: the inventory's `fidelityBacklog`, then every skill not yet reviewed against current tools and conventions.

Unfinished items from earlier runs keep their place in this order. In upstream mode, skills the checkpoint lists as pending for other reasons wait for the audit.

When items 1 to 4 are empty in upstream mode, save a checkpoint from the compare reports, prune old runs, and stop. A quiet run needs no branch, checks, review, PR, or report.

**Complete when:** every compare report entry and every `changedSince` skill is on the worklist or recorded as unchanged, or the run has stopped as a quiet run.

## 3. Decide and repair

Prepare the maintenance branches by the guide's branch rules before the first edit. Decide each upstream change by the adaptation contract, and record each decision as it describes. Dispatch repairs to isolated writers using /writing-for-agents, and inspect each returned diff. Import new upstream skills and propose retirements as the contract describes. When a change touches a shared owner, check its consumers in both suites.

For each skill in `changedSince`, check that its edits keep its recorded adaptations and repository conventions. In audit mode, check tool names, commands, links, and practices against the environments each skill supports, starting from exposed tool schemas, installed versions, and local help output; use Context7 for library documentation and Exa for releases and gaps. Review first-party skills and local adaptation text with /writing-for-agents, and treat sourced text by the contract's minimal-divergence rule.

Run the contract's fidelity check on every sourced skill you edit or find in `changedSince`, and in audit mode on backlog records.

**Complete when:** every worklist item is adopted, adapted, excluded, held with a question, or carried to the next actions with a reason, and every edited or locally changed sourced skill passes both fidelity directions.

## 4. Validate

Read changed instructions end to end and run the maintenance guide's checks. Exercise changed scripts or workflows on a small isolated example, and confirm each new regression test fails with its repair reverted. Dispatch an independent final review of the exact diff, its decisions, fidelity, and coverage, and resolve its findings. Re-enumerate skills so additions made during the run enter coverage.

Advance a skill's reviewed-through position only when its whole upstream delta is decided and checks pass. Save a checkpoint of coverage, worker evidence, waiting questions, and next actions; a checkpoint never advances a position or claims a finished review.

**Complete when:** checks pass, every final-review finding is fixed or recorded as a next action, and the checkpoint is saved.

## 5. Deliver

Commit library changes and changes to this skill's own process on their separate maintenance branches, push, and create or update one draft PR for each, within the action grant. Report what changed, decisions the owner must make, failures, and coverage still pending.

At the time limit's wrap-up point, start no new worklist items: validate, checkpoint, and deliver what is finished, carrying the rest forward.

**Complete when:** each PR is verified on the forge, pending work is in the checkpoint, and every action stayed within the grant.
