# Adaptation contract

This library tracks Pstack, Matt Pocock's skills, Thermos, and OpenClaw's test audit, and adapts them lightly so they work together in Codex and Claude Code. Upstream authors keep improving these skills; the library stays close enough to their text to keep receiving those improvements, and diverges only where this setup needs it. Oliver Cederborg's skills are tracked differently, as the source of [principle-derived skills](#principle-derived-skills).

## Library-wide adaptations

These apply to every sourced skill of the named source. A skill's `UPSTREAM.md` lists only that skill's own divergences.

Every source:

- **Hosts:** Codex and Claude Code. Translate host-specific execution, such as Cursor plugin registration, named Cursor agents, and fixed host model mappings, into each host's native tools. /pstack-swarm owns delegation, isolated writers, and cross-vendor review.
- **Packaging:** install with the Skills CLI from this repository. Each skill's locally owned `agents/openai.yaml` mirrors its invocation mode: user-invoked skills set `disable-model-invocation: true` and `policy.allow_implicit_invocation: false`. Dependencies are `/skill-name` invocations, and the README lists required companions.
- **Coordination:** one coordinator writes canonical artifacts while delegates return proposals, and each effort keeps one accepted spec and ticket graph. Scale effort and parallelism to the task's scope and budget, and keep each workflow's outcomes and evidence.
- **Review:** a workflow's final review of its own implementation runs through /review-loop, which keeps /code-review's axes and adds /thermo-nuclear-review's correctness audit, the counterpart model's review, and the fix rounds.
- **Authority:** honor the invoking repository's conventions and the user's existing authorization. Pull requests default to drafts, and learning-driven edits to source skills are prepared for review.
- **Licenses:** keep each upstream notice with the material it covers.
- **Steps:** a sourced step may end with a completion criterion, per this repository's skill rules.
- **Project artifacts:** a sourced skill that reads or changes project vocabulary, domain docs, or ADRs resolves them through /domain-modeling first.
- **Formatting:** differences the repository formatter makes, such as table padding and list or emphasis markers, are not divergences.

Pstack and Thermos:

- Pstack skills install with a `pstack-` prefix, except `bro`, so every Pstack skill and principle is reachable under one name space. `suite.json` records each mapping, such as `setup-pstack` to `pstack-setup`. /pstack-help routes to the user-facing entrypoints, and /pstack-principles discovers and applies the principles.
- Each Pstack skill works on its own; only an explicit /pstack-mode invocation activates the mode.
- Pstack helpers and principles are model-invoked, where upstream marks most of them user-invoked, so playbooks, routers, and other skills can load them; their descriptions scope triggering to Pstack tasks. Entrypoints and skills with outward effects keep upstream's user-invoked mode: /pstack-mode, /pstack-help, /pstack-automate-me, /bro, both formal-verification skills, /pstack-maintain-verification-skill, and /pstack-make-bot-ui.
- Thermos keeps its names, and its own `MAINTENANCE.md` owns its review contracts.

Matt Pocock:

- Matt's names stay, except `prototype` becomes `design-prototype` and `git-guardrails-claude-code` becomes `git-guardrails`. Upstream stages such as `in-progress` stay recorded in the catalog.
- Matt's interview, planning, implementation, testing, and review owners invoke /pstack-principles in the current phase and before completion, so Pstack's principles improve Matt's workflow without Pstack mode.

## Shared owners

One skill owns each shared discipline. Other skills invoke the owner rather than restating its rules, and a change to an owner is checked against its consumers in both suites.

- /writing-for-agents owns agent-instruction writing and skill mechanics.
- /domain-modeling owns project vocabulary, domain relationships, and qualifying ADRs, including existing legacy context and domain files.
- /codebase-design owns architectural vocabulary and seam reasoning.
- /tdd owns behavior-test discipline: red-green mechanics and test seams. /pstack-principle-test-behavior-not-implementation owns the test-quality criteria, and Pstack's bug-fix adapter adds before-and-after evidence.
- /code-review owns Standards and Spec review; Pstack's adversarial lenses add coverage of the same artifact.
- /pr owns PR description shape; Pstack owns its delivery playbook and evidence mechanics.
- /reply-shape owns the layout of replies to the user; a skill's own report format is laid out within it.
- /next-options owns how replies end.
- /pstack-swarm owns native host execution, isolation, bounded cross-vendor review, its T3 Code route, and disclosed fallback.
- /review-loop owns cross-model review rounds, finding verification, and the fix-and-re-review loop.
- /thermo-nuclear-review owns the correctness and security audit that /thermos and /review-loop run.
- /pstack-principles selects the principles for each phase in both suites, keeping each principle's rules in that principle.
- /maintain-skills owns library upkeep and coverage accounting.

## Deciding an upstream change

Adopt by default. Taking upstream's improvements is the reason these skills are sourced.

- **Adopt** a change as written when it already fits the library-wide adaptations.
- **Adapt** a change by applying the library-wide adaptations, such as installed names, host translation, and owner delegation, or by keeping a recorded divergence whose reason still holds. Keep the change's intent. When it improves a discipline a shared owner holds, carry the improvement into the owner so both suites receive it, and keep the consumer delegating.
- **Exclude** a change only when it is specific to the author's own environment or product, or has evidence that it makes the skill worse. Record the reason; the reviewed-through position then covers it.
- **Hold** a change that needs a new service, wider authority, or a scope change, and ask the owner.
- **Upstream reverses a local divergence:** keep the divergence only when its reason outweighs upstream's stated reason, and record the comparison either way.
- **Converge:** when upstream now handles what a divergence was for, or a library-wide adaptation covers it, drop the divergence and take upstream's text.

Import each new upstream skill unless the catalog excludes it or it needs owner approval. Package it like its siblings: provenance record, license, Codex metadata, suite or catalog mapping, README listings, companion rows, and /pstack-help routing for a user-facing Pstack entrypoint. When upstream removes a skill without a successor, propose its retirement and a catalog exclusion with the removal commit as evidence, unless a local skill depends on it; then hold it and name the dependency.

## Principle-derived skills

Some first-party skills take another author's ideas rather than text. Their `UPSTREAM.md` names the source in its tracking policy and lists the adopted principles and the deliberate departures under its local adaptations. For these skills:

- Decide each upstream change to the tracked files by whether it improves the behavior the skill takes from the source. Adopt an improvement in this library's own words and through its shared owners, or exclude it with a reason.
- The minimal-divergence rule does not apply; the wording is first-party and reviewed with /writing-for-agents.
- The fidelity check compares ideas in both directions: every adopted principle still exists upstream or is kept on purpose with a reason, and every recorded departure still holds.

## Minimal divergence

Every local edit to upstream text is a divergence to record and carry forward. Edit sourced text only to apply a library-wide adaptation, or where it fails on these hosts or is factually wrong. Keep upstream's wording otherwise, and put style improvements into first-party skills. Record each divergence in the skill's `UPSTREAM.md` with its reason, and drop it once upstream fixes the cause.

## Fidelity check

After editing a sourced skill, compare it with the candidate upstream text in both directions:

- Every upstream rule survives, or the record lists its divergence, whether dropped, softened, reversed, or a changed invocation mode, with the reason.
- Every recorded divergence is still present and still needed. Remove the ones that are not.

When both directions pass, set the record's `Fidelity checked through` line to the candidate revision.

## Recording decisions

Record each decision where the next run reads it. Skill decisions go in the skill's `UPSTREAM.md` decision log. An excluded upstream skill or path goes in the catalog's `excludedNames` or `excludedPaths` with its reason. Owner answers from PR comments or chat are recorded the same way.

A held change counts as reviewed: its question goes in runtime state and in each open maintenance PR's description, and the change waits there until the owner answers.
