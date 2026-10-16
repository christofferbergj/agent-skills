# Using the library

[Install and browse skills](../README.md) · [Documentation index](README.md)

## Shared workflow

The [combined validation record](../skills/agents/maintain-skills/VALIDATION.md) documents packaging, host exercises, tests, and remaining integration limits. The [Thermos review record](reviews/2026-10-15-combined-skills-thermos.md) records the independent audit and its repairs.

Use `/grill-with-docs` to resolve a design, `/to-spec` to capture an accepted spec, `/to-tickets` to build its dependency graph, and `/implement` or `/implement-spec` to execute it. Invoke `$pstack-mode` in Codex or `/pstack-mode` in Claude Code when you want its coordinated playbooks. Both paths use the same project documents and reusable disciplines; neither starts another coordinator automatically.

The Matt flow invokes `/pstack-principles` automatically at each phase and before completion. That shared selector reads the applicable principle owners, carries accepted constraints into the existing spec and tickets, and supplies implementation and review workers with the rules. It does not activate Pstack mode. New installed principles enter selection through their descriptions, without a separate list to update.

Principles stay within the current phase and accepted scope. An interview still waits for confirmation; a spec records unresolved conflicts instead of inventing decisions. The migration principle chooses coordinated internal migration or staged coexistence when compatibility requires it, and owns the verification gates for both flows. Runtime completion includes direct evidence from the real user or caller path, with unavailable checks reported as gaps.

| Responsibility                                                           | Shared owner         |
| ------------------------------------------------------------------------ | -------------------- |
| Configured glossary, domain model, legacy context files, and ADR updates | `/domain-modeling`   |
| Architecture vocabulary and interface depth                              | `/codebase-design`   |
| Behavior tests and red/green slices                                      | `/tdd`               |
| Standards and spec review                                                | `/code-review`       |
| PR description                                                           | `/pr`                |
| Native delegation, isolated writers, cross-vendor review and fallback    | `/pstack-swarm`      |
| Principle selection and composition within the current phase             | `/pstack-principles` |
| Every local skill, its upstreams, and integration changes                | `/maintain-skills`   |

Pstack architecture and domain-model work updates the same configured artifacts as Matt's skills. Current defaults are `GLOSSARY.md`, optional `GLOSSARY-MAP.md`, `docs/adr/`, and setup's `docs/agents/domain.md`. Existing `context.md`, `CONTEXT.md`, or domain-model files keep their roles and names. Accepted spec/ticket artifacts remain authoritative; plans and evidence logs link to them. The coordinator owns canonical document edits while delegates return proposals.

Matt's familiar command names are retained except `prototype` becomes `/design-prototype`, preserving Emil Kowalski's installed `/prototype`, and the host-specific guardrail name becomes `/git-guardrails`. The latter changes host settings only when invoked for that purpose. `/setup-matt-pocock-skills` now configures the shared project contract; `/pstack-setup` remains optional personal model-role setup.

Install from this repository to replace eligible Matt command snapshots with the owned adaptations. Do not install the same commands from Matt's repository or the original Pstack plugin over them. The excluded skills and unrelated global skills are outside this migration. This source change does not silently replace global installations.

## Pstack

The Pstack adaptation covers all 54 registered skills from [Lauren Tan's MIT-licensed Pstack](https://github.com/cursor/plugins/tree/main/pstack): 53 namespaced skills plus the existing `bro`. It includes 24 principles, 23 playbooks, native Codex and Claude Code execution, and a disclosed fallback when cross-vendor review is unavailable. The dormant Benny automation pack is outside this suite.

Use the [complete-library install](../README.md#install). Pstack's coordinated workflows depend on shared Matt-derived owners as well as their own helpers. Skills CLI does not install dependencies transitively. To install unpublished changes, run the command from the repository root with `.` as the source. Reinstall after source changes because installed copies are snapshots.

Invoke `$pstack-mode` in Codex or `/pstack-mode` in Claude Code for the current conversation. Give it a goal, observable done predicate, proof, and constraints. Use `pstack-help` for routing and `pstack-setup` for personal model roles. Installation does not activate a mode or modify host startup instructions.

The suite preserves evidence requirements while scaling parallelism to the task. Draft PRs are the default. Cross-vendor critics use the other authenticated CLI when available; independent native or sequential fallback is labeled. Bun-dependent PR/orchestration commands declare their prerequisites and use a runtime cache outside installed source. The webhook UI requires an existing receiver and defaults to localhost.

Read the [repository maintenance guide](../skills/agents/maintain-skills/MAINTENANCE.md) for source comparisons, local adaptations, checks, checkpointing, and scheduled review. The [validation record](../skills/agents/pstack-mode/VALIDATION.md) covers tested hosts and integration limits. Each sourced skill retains its own `LICENSE` and `UPSTREAM.md`; the [suite catalog](../skills/agents/maintain-skills/catalog.json) references the Pstack index and includes `bro`. Filesystem inventory and skill-local source records determine full review coverage beyond the suite catalog. `/maintain-skills` requires `/writing-for-agents` and `/pstack-swarm`; see the [installation guidance](../README.md#install).

## Upstream stages

The maintained catalog preserves experimental and frozen upstream status. The remaining experimental Matt workflows are `chief-of-staff`, `loop-me`, and `setup-ts-deep-modules`. `git-guardrails` and `setup-pre-commit` come from the frozen upstream misc collection. These are reusable workflows; Matt's personal-directory skills are excluded.

The [catalog's exclusions](../skills/agents/maintain-skills/catalog.json) also record user-retired skills. These include the Shoehorn migration and the three experimental article-writing workflows. Maintenance keeps those exclusions even if upstream moves a skill to another category.

## Updating an installation

Published and local-path installs are snapshots. After source changes are merged, rerun the complete install from the main README to refresh both hosts and discover newly added skills. Install from this repository rather than overwriting the adaptations with same-named upstream skills.
