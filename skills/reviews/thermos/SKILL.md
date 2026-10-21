---
name: thermos
description: Run parallel correctness and maintainability reviews, then combine the findings.
disable-model-invocation: true
---

# Thermos

Run two independent reviews of the same changes and synthesize their findings. This workflow explicitly delegates to two subagents when the host supports them.

## Prepare

1. Resolve the review scope from the user's branch, PR, commit range, or working changes. Read repository guidance and record the repository path, base and head revisions, and included working changes. For a branch review, use the merge-base with the requested or verified base branch; do not assume `main`. Include untracked files only when they belong to the requested scope. Preparation is complete when both reviewers can identify the same changes.
2. Resolve the installed `/thermo-nuclear-review` and `/thermo-nuclear-code-quality-review` skills. They are required dependencies. Supply each reviewer its rubric's absolute `SKILL.md` path and have it read that file, or include the full rubric text when child contexts cannot access the skill. Child agents may not inherit skill discovery or parent context. If a dependency is missing, identify it and stop before presenting a Thermos verdict.
3. Gather the diff, changed-file list, relevant full-file contents, and known constraints. Give both reviewers the same scope and evidence, with repository access for tracing callers and related code. For a large diff, provide accessible artifact paths instead of truncated excerpts. List the repository guidance files already read and the rules from them that bear on the scope, so reviewers read further guidance only for paths that list does not cover. Finish preparation when the evidence and guidance list are accessible to both reviewers.

## Delegate

Choose the branch matching the tools exposed in this session. Use the actual tool schema; tool names and parameters can vary between host versions. Use built-in agents without requiring custom agent registration, a plugin, a particular model, or an agent team.

### Codex

Use the native `spawn_agent` tool, possibly exposed under a collaboration namespace, to launch two reviewers. Put the rubric and scope in each task message. Use separate task names when supported. Launch both before waiting for either. Collect both results with the host's native wait or completion mechanism, then close the completed agents if that host exposes a close tool.

### Claude Code

Use the native `Agent` tool, called `Task` in older versions, with the built-in `subagent_type: "general-purpose"`. Submit both calls together with `run_in_background: true` when supported. Otherwise use the tool's supported concurrent dispatch. Omit model overrides to inherit the session's choice. Collect both results through completion notifications or the tool's returned output/task handles before synthesizing.

### Unavailable delegation

If subagent tools are unavailable, blocked, or lack two available slots, report the limitation. Complete both rubrics as separate sequential passes when permitted, and label the result as sequential without independent subagents. If one dispatched reviewer fails, retry that reviewer once when the failure is recoverable; otherwise report the missing pass or complete it locally with that limitation stated. Never claim two independent reviews when only one completed.

## Reviewer tasks

Assign these two tasks, supplying the prepared scope and evidence with each:

- **Correctness and security:** Invoke `/thermo-nuclear-review` using the supplied rubric. Trace bugs, breaking behavior, security risks, developer-experience regressions, and feature-gate leaks introduced by the diff. Finish the independent audit before checking existing PR discussion when the rubric calls for it.
- **Maintainability:** Invoke `/thermo-nuclear-code-quality-review` using the supplied rubric. Evaluate structural simplification, branching complexity, abstractions, type and ownership boundaries, canonical helpers, and file growth introduced by the diff.

Each reviewer works directly without further delegation, edits, commits, or posting comments. Read surrounding code to verify impact, but report only issues introduced by the scoped changes. Return prioritized findings with file and line references, evidence, impact, and an actionable remedy. Distinguish verified findings from limitations that prevented verification. If no supported findings remain, say so. Keep the reviews independent until both finish.

## Synthesize

Wait for both passes to finish or explicitly account for a failed pass. Check overlapping findings against the code, merge duplicates, and resolve disagreements using evidence. Agreement alone does not raise severity. Keep correctness defects distinct from maintainability recommendations and preserve the rubric's rationale for structural blockers.

Return findings first, ordered by impact, followed by a brief verdict and material limitations. State which passes completed and whether they ran as independent parallel subagents. If the review scope changed while the reviewers were running, reconcile the affected findings before giving a verdict. If individual reviewer summaries are already visible to the user, do not restate them wholesale; surface the unified verdict, the highest-signal findings, and any remaining uncertainty.
