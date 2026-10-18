---
name: pstack-help
description: "Explain Pstack installation, entrypoints, playbooks, prerequisites, and how to recover a run."
disable-model-invocation: true
---

# Pstack help

Answer the user's help question without starting its underlying task. If they explicitly ask for execution, explain the relevant entrypoint and follow that request's existing authorization.

- Installation: use this repository's complete Pstack Skills CLI command for `codex` and `claude-code`. Dependencies are not installed transitively. A missing skill needs its documented installation group.
- Start: invoke `$pstack-mode` in Codex or `/pstack-mode` in Claude Code with a goal, done predicate, proof, and real constraints. Activation applies to the conversation, not every chat.
- Configure: invoke /pstack-setup for personal role settings and capabilities. Missing optional CLIs or webhook receivers remain explicit prerequisites.
- Understand: /pstack-how explains behavior, /pstack-why investigates rationale, and /pstack-teach combines them.
- Design: /pstack-architect sketches interfaces, /pstack-arena compares artifacts, and /pstack-interrogate critiques a concrete diff.
- Prove: /pstack-create-verification-skill creates an app-driving skill; /pstack-maintain-verification-skill keeps its feature map honest; /pstack-blast-radius and /pstack-benchmark-checklist handle indirect effects and measured claims.
- Formal verification: explicitly invoke `/pstack-create-formal-verification-skill` to prove one property beyond ordinary test coverage and generate a project-local check.
- Coordinate: /pstack-swarm owns execution and coverage; /pstack-figure-it-out designs a bespoke run; /pstack-show-me-your-work records decisions; /pstack-ketchup catches the user up.
- Learn: /pstack-recall reconstructs same-repository history, /pstack-reflect proposes source improvements, and the explicitly invoked /pstack-automate-me creates a personal mode.
- Writing: /pstack-unslop and /pstack-technical-writing refine prose; `/bro` restates the previous reply plainly.
- Maintenance: invoke /maintain-skills from the source repository for the whole library. Read the saved maintenance automation for its current cadence and model. Scheduled runs prepare reviewed update PRs; merge and installation refresh follow existing authorization.

For help composing a task, read [prompting guidance](references/prompting.md). For the complete playbook list and principle inventory, point to the explicitly invoked `pstack-mode` entrypoint and its suite index. Complete when the question has a practical next action and known limitations, without claiming an integration was exercised.
