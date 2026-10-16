---
name: pstack-mode
description: "Run the Pstack playbooks for the current conversation."
disable-model-invocation: true
---

# Pstack mode

Activate this mode for the current conversation when the user explicitly invokes it. Match each new task to the playbooks below. Direct helper invocation does not activate the whole mode. Follow the invoking repository's conventions and the host's actual tools.

## Run a task

1. Invoke /domain-modeling to resolve and read the project's shared artifacts. Reuse the existing spec, ticket graph, glossary, domain model, and ADRs as their source of truth. State the goal, scope, and observable done predicate. Identify the data shape and current implementation before changing code. Invoke /pstack-how for unfamiliar architecture and /pstack-why when existing rationale constrains the change. Complete when the brief names the behavior to prove and the relevant boundaries.
2. Read the matching playbook from `playbooks/` in this skill directory. Copy its steps into the task list, retaining a skipped step with its reason. Use /pstack-figure-it-out for a large bespoke run; a standing multi-day program uses Orchestrate. Complete when one execution path and its checks are explicit.
3. Invoke the workflow and principle skills needed by that path. Use /pstack-swarm for host execution, native delegation, independent review, isolation, and fallback behavior. Helpers own their references; resolve their installed paths through the host's skill index. Complete when every delegate has its scope, evidence contract, and permitted side effects.
4. Execute within the agreed scope. Proceed on reversible implementation work; pause when scope or an approved interface changes, or repeated failures require the user's decision. Explicit merge, deployment, or messaging authorization remains specific to that action. Complete when each unit is proved or its blocker is recorded.
5. Reconcile accepted domain changes through /domain-modeling; canonical docs are edited by the coordinator. Verify against the real artifact, inspect delegated changes, and report the evidence, gaps, and decisions that need attention. Draft pull requests are the default. A missing check never becomes a pass. Complete when the done predicate is demonstrated or the exact unfinished work is reported.

## Routing

- Read-only behavior or rationale question: [Investigation](playbooks/investigation.md).
- Reproduce and fix a defect: [Bug fix](playbooks/bug-fix.md).
- One measured performance regression: [Perf issue](playbooks/perf-issue.md).
- Sustained metric improvement: [Hillclimb](playbooks/hillclimb.md).
- Diagnose live runtime signals: [Runtime forensics](playbooks/runtime-forensics.md).
- Diagnose a captured profile or trace: [Trace forensics](playbooks/trace-forensics.md).
- Build changed behavior: [Feature](playbooks/feature.md).
- Preserve behavior while changing structure: [Refactoring](playbooks/refactoring.md).
- Settle an empirical fork cheaply: [Prototype](playbooks/prototype.md).
- Match visual output: [Visual parity](playbooks/visual-parity.md).
- Create or edit skill instructions: [Authoring a skill](playbooks/authoring-a-skill.md).
- Evaluate instruction or workflow behavior: [Eval](playbooks/eval.md).
- Bring a PR or stack to merge-ready: [Babysit](playbooks/babysit.md).
- Independently verify and land authorized PRs: [Shipping](playbooks/shipping.md).
- Drive one task to a predicate: [Autonomous run](playbooks/autonomous-run.md).
- Coordinate a standing project: [Orchestrate](playbooks/orchestrate.md).
- Run a queue through explicitly authorized merges: [Autopilot full](playbooks/autopilot-full.md).
- Build a verified stack for the user to land: [Autopilot stack](playbooks/autopilot-stack.md).
- Resume prior work: [Session pickup](playbooks/session-pickup.md).
- Preserve in-flight work on a pause: [Pause safely](playbooks/pause-safely.md).
- Produce a multi-PR execution plan: [Multi-phase plan](playbooks/multi-phase-plan.md).
- Audit and reclaim owned worktrees: [Worktree cleanup](playbooks/worktree-cleanup.md).
- Prepare a reviewable PR: [Opening a PR](playbooks/opening-a-pr.md).

## Principles and helpers

Read each principle skill in full before applying it, and cite it only when it changed a concrete choice. Architecture uses the domain, boundary, type-system, reader-load, and migration principles; verification uses proof, behavior tests, root causes, and measured-number principles; delegation uses context and separate-state principles. The complete principle names are in `suite.json` alongside the upstream-to-local mapping. Invoke the matching `/pstack-principle-*` owner rather than copying its rules.

Use /codebase-design for architecture vocabulary, /tdd for behavior tests, /code-review for Standards/Spec review, and /pr for PR descriptions. Keep user entrypoints such as /grill-with-docs, /to-spec, /to-tickets, and /implement-spec explicit; reuse their artifacts rather than starting another planning process. Use /pstack-architect for consequential interfaces, /pstack-arena for competing artifacts, /pstack-interrogate for an adversarial review of a concrete diff, /pstack-blast-radius for indirect effects, and /pstack-benchmark-checklist before acting on a measured number. Scale comparisons and verification coverage to the task; justify skipped surfaces and checks.

Use /pstack-unslop for prose, /pstack-technical-writing for structured documents, /pstack-no-comments before review, and the repository's available cleanup process before committing. Use /pstack-show-me-your-work for long or unattended work and /pstack-ketchup for a useful progress recap.

## Suite maintenance

For upstream upkeep, read [MAINTENANCE.md](MAINTENANCE.md) and invoke /maintain-skills for the whole repository, including this suite, other upstreams, and first-party skills. `suite.json` owns the Pstack mapping; local discovery determines maintenance coverage. Skill-local `UPSTREAM.md` records own import history and review decisions. User configuration and generated runtime state live outside installed instruction files.
