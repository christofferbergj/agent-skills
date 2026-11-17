---
name: swarm
description: "Use for Pstack delegation or independent review; organize coverage slices, races, or parallel exploration."
---

# Swarm

For every Pstack delegate or cross-vendor review, read [the execution contract](references/execution.md). It owns native host APIs, model settings, isolation, review restrictions, and disclosed fallback. A caller can use that contract for one delegate without starting a coverage swarm.

To hand a check that needs Computer Use to Codex, follow [the Computer Use route](references/computer-use.md).

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Pick the worker model from the `swarm-workers` role, which [the execution contract](references/execution.md#model-roles) resolves: by default Opus at `high` in Claude Code and the session's model in Codex. For `auto` or `inherit-parent`, omit `model` so the workers run on the parent model. If the host rejects a model, follow the contract's rejected-model rule and say so. For a model race, name each arm's model up front. Pick each subagent's reasoning level for the job through the contract.
4. Give each worker its own writable output when it writes. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

## Phase B: Fan out

Spawn all N workers at once, in the background, as general-purpose agents with the step 3 model, left unset for `auto` or `inherit-parent`, each isolated in its own worktree as the execution contract describes. Run a worker in the session's checkout only when it needs access to something on the user's computer. In T3 Code, a job that needs another machine's tools, or would load this one for long, runs there through [the T3 route's On another machine](references/t3.md#on-another-machine).

When a worker must start from a non-default pushed branch, tell it to check out that branch first.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

## Phase D: Report

Return one consolidated in-chat report with a result table, issue one-liners, gaps or dropouts, and the race rule when used.
