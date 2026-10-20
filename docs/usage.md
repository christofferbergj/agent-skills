# Using the library

[Install and browse skills](../README.md) · [How the library fits together](architecture.md)

## Choose a workflow

For a feature, use `grill-with-docs` → `to-spec` → `to-tickets` → `implement-spec`. Skip stages that are already settled; `implement` handles a smaller agreed piece of work. Relevant Pstack principles apply automatically throughout the Matt flow, including implementation and review. Implementation ends with `review-loop`: the other vendor's model reviews the change alongside the main model's own reviewers, and the agent fixes what holds and re-reviews until clean. Invoke `review-loop` directly for a second opinion on any branch, PR, or plan.

Use `pstack-mode` when you want the agent to choose and drive a playbook for an investigation, bug fix, feature, refactor, or performance task. Give it a goal, observable completion criteria, required proof, and constraints. You can hand it an accepted spec and ticket graph from the Matt flow; it reuses them. Invoke it explicitly for the current conversation. Installation and individual helper invocations do not activate the mode.

Both paths use the same [principles, shared owners, and project artifacts](architecture.md#how-the-workflows-compose). You do not need to remember every helper. Use `pstack-help` for routing or invoke a specialist directly when you know which one you need.

## Configuration and prerequisites

Existing project conventions take precedence. Use `/setup-matt-pocock-skills` to establish or reconcile shared domain-document and issue-tracker guidance. `/pstack-setup` is optional personal configuration for model roles, effort, review providers, and source locations; omitted options use the adaptation's defaults. These setup skills change configuration only when invoked for that purpose.

Capability-dependent workflows declare their prerequisites. Bun-backed Pstack tools prepare a runtime cache outside installed source; the `review-loop` and `next-options` scripts run on Node 24 or newer. Cross-vendor review runs the other vendor's model, Codex from Claude and Claude Opus from Codex, with an explicit model and effort: as a T3 child task in T3 Code, and through the other authenticated CLI elsewhere. It labels fallback coverage. `/pstack-setup` can override the counterpart's model and effort. The webhook UI needs an existing receiver and defaults to localhost; it does not provide an agent execution service.

`/next-options` ends replies with up to three lettered next steps for the current conversation. To load it in every Claude Code and Codex session, ask it to install its SessionStart hook; that changes host settings only on request. `/reply-shape` lays out the rest of each reply, status line first with folded details, and loads through the same hook.

## Install and update

Use the [complete-library install](../README.md#install). Skills CLI does not install dependencies transitively; partial installs need the listed companions. To try unpublished changes, run that command from the repository root with `.` as the source.

Installations are snapshots. After changes merge, rerun the complete install to refresh your selected agents and discover new skills. Install from this repository rather than overwriting its adaptations with same-named upstream skills. A repository update does not refresh global installations automatically. To check them against `main`, run `git fetch origin main`, then `python3 scripts/check-installs.py` from this repository. It reports stale, missing, unknown, and retired installs, same-named skills from other sources, and entries in `~/.claude/skills` that load something other than the shared install.

For source upkeep, use `/maintain-skills` and the [repository maintenance guide](../skills/agents/maintain-skills/MAINTENANCE.md). Daily runs adopt upstream changes while keeping the library's local adaptations; weekly audits also review every skill against current tools and conventions. This is separate from refreshing installed copies.

## Agent compatibility

Use `$skill-name` in Codex and `/skill-name` in Claude Code. Native delegation and hook adapters target these two hosts. Skills CLI offers other agents too; workflows that depend on host-specific tools need a compatible integration. Agent selection during installation does not add that integration. The [validation history](reviews/README.md) records exercised branches and remaining limits.
