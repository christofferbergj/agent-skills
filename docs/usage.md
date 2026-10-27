# Using the library

[Install and browse skills](../README.md) · [How the library fits together](architecture.md)

## Choose a workflow

For a feature, bug fix, refactor, investigation, or performance task, start with `pstack-mode`. Give it a goal, observable completion criteria, required proof, and constraints, and it chooses and drives a playbook. It plans through code: a design question it could settle by running something gets a prototype or an `architect` sketch rather than a written plan or a question to you. Invoke it explicitly for the current conversation. Installation and individual helper invocations do not activate the mode.

When an effort should be written down first, such as work other people will pick up from a tracker, use the Matt flow: `grill-with-docs` → `to-spec` → `to-tickets` → `implement-spec`. Skip stages that are already settled; `implement` handles a smaller agreed piece of work. You can hand the accepted spec and ticket graph to `pstack-mode`; it reuses them. Relevant Pstack principles apply automatically throughout the Matt flow, including implementation and review.

Both paths end implementation with `review-loop`: the other vendor's model reviews the change alongside the main model's own reviewers, and the agent fixes what holds and re-reviews until clean. Invoke `review-loop` directly for a second opinion on any branch or PR, or on a plan when you want one.

Both paths use the same [principles, shared owners, and project artifacts](architecture.md#how-the-workflows-compose). You do not need to remember every helper. Use `pstack-help` for routing or invoke a specialist directly when you know which one you need.

## Configuration and prerequisites

Existing project conventions take precedence. Use `/setup-matt-pocock-skills` to establish or reconcile shared domain-document and issue-tracker guidance. `/pstack-setup` is optional personal configuration for model roles, effort, review providers, and source locations; omitted options use the adaptation's defaults. These setup skills change configuration only when invoked for that purpose.

Capability-dependent workflows declare their prerequisites. Bun-backed Pstack tools prepare a runtime cache outside installed source; the `review-loop` and `next-options` scripts run on Node 24 or newer; `ketchup-video` needs a video encoder such as `ffmpeg` to render and check its frames. Cross-vendor review runs the other vendor's model, Codex from Claude and Claude Opus from Codex, with an explicit model, effort, and speed: as a T3 child task in T3 Code, and through the other authenticated CLI elsewhere. Codex delegates run in fast mode while at least 40% of Codex usage is left and at standard speed below that. Below 5%, reviews go to a same-vendor critic, and the report labels that fallback coverage. Claude delegates run at standard speed. Claude hands checks that need Computer Use to Codex, which needs Codex's Computer Use plugin and macOS Screen Recording and Accessibility permissions. Pstack's helper agents for exploration, investigation, tooling review, check runs, and trivial edits use Sonnet in Claude Code, while code, judgment, and synthesis keep the main model. `/pstack-setup` can override any of these roles, the counterpart's model, effort, and speed, and the usage thresholds. The webhook UI needs an existing receiver and defaults to localhost; it does not provide an agent execution service.

`/next-options` ends replies with what comes next for the current conversation: one plain line when the agent carries on by itself, or up to three lettered options when the user decides. To load it in every Claude Code and Codex session, ask it to install its SessionStart hook; that changes host settings only on request. `/reply-shape` lays out the rest of each reply, status line first with folded details, and loads through the same hook.

## Install and update

Use the [complete-library install](../README.md#install). Skills CLI does not install dependencies transitively; partial installs need the listed companions. To try unpublished changes, run that command from the repository root with `.` as the source.

Installations are snapshots. After changes merge, rerun the complete install to refresh your selected agents and discover new skills. Install from this repository rather than overwriting its adaptations with same-named upstream skills. A repository update does not refresh global installations automatically. To check them against `main`, run `git fetch origin main`, then `python3 scripts/check-installs.py` from this repository. It reports stale, missing, unknown, and retired installs, same-named skills from other sources, and entries in `~/.claude/skills` that load something other than the shared install.

For source upkeep, use `/maintain-skills` and the [repository maintenance guide](../skills/agents/maintain-skills/MAINTENANCE.md). Daily runs adopt upstream changes while keeping the library's local adaptations; weekly audits also review every skill against current tools and conventions. This is separate from refreshing installed copies.

## Agent compatibility

Use `$skill-name` in Codex and `/skill-name` in Claude Code. Native delegation and hook adapters target these two hosts. Skills CLI offers other agents too; workflows that depend on host-specific tools need a compatible integration. Agent selection during installation does not add that integration. The [validation history](reviews/README.md) records exercised branches and remaining limits.
