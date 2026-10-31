---
name: swarm
description: "Use for Pstack delegation or independent review; organize coverage slices, races, or parallel exploration."
---

# Swarm and host execution

For every Pstack delegate or cross-vendor review, read [the execution contract](references/execution.md). It owns native host APIs, model settings, isolation, review restrictions, and disclosed fallback. A caller can use that contract for one delegate without starting a coverage swarm.

To hand a check that needs Computer Use to Codex, follow [the Computer Use route](references/computer-use.md).

## 1. Frame

Open a task list with one entry per phase before dispatching anything. Name the done predicate, report or artifact, and required coverage. Choose slices, an identical-brief race, or a mix. Declare a race rule before dispatch: first passing result, rank all, or best-of. Workers take the `swarm workers` role from [the execution contract](references/execution.md#model-roles); for a model race, name each arm's model before dispatch instead. Choose the smallest useful worker count within the user's budget and host capacity; total jobs can exceed concurrent slots.

Give each writer its own worktree or output directory. A verification or measurement brief names the exact revisions, sample definition, method, and acceptance predicate. Complete when every required slice or arm has an independent brief and output location.

## 2. Dispatch

Use the host's native delegation tools, or the route the execution contract names for a borrowed worker, and their actual schema. Start independent jobs before waiting, respecting the available concurrency window. Each brief supplies the goal, boundary, repository guidance, resolved rubric or reference paths, evidence to return, and allowed writes. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first. Prefer cross-vendor critics through the execution contract when available.

Complete when each job has a handle or an explicit dispatch failure. A dropped worker is a gap, never an implicit success.

## 3. Aggregate

Collect terminal results. Accept `PASS`, `ISSUES`, or `BLOCKED` only with the brief's required revisions, method, and evidence. Retry a missing or malformed result once when recoverable; after another miss, record the gap. Inspect each finding rather than treating agreement as proof. Coverage requires every mandatory slice; a race uses the declared selection rule.

Complete when every dispatched job is accounted for and every required slice has evidence or a named gap.

## 4. Report

Return one compact table of jobs, verdicts, revisions, and evidence, followed by actionable issues, dropouts, and the race result, without pasting raw worker output. Disclose sequential execution, same-vendor review, or unavailable delegation. Complete when the report distinguishes actual independent passes from local fallback work.
