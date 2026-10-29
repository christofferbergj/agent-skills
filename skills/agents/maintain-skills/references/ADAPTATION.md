# Adaptation contract

This library tracks Pstack, Matt Pocock's skills, Thermos, OpenClaw's test audit, and two of Emil Kowalski's UI reviews, and adapts them lightly so they work together in Codex and Claude Code. Upstream authors keep improving these skills; the library stays close enough to their text to keep receiving those improvements, and diverges only where this setup needs it. Oliver Cederborg's skills are tracked differently, as the source of [principle-derived skills](#principle-derived-skills).

## Library-wide adaptations

These apply to every sourced skill of the named source. A skill's `UPSTREAM.md` lists only that skill's own divergences.

Every source:

- **Hosts:** Codex and Claude Code. Translate host-specific execution, such as Cursor plugin registration, named Cursor agents, and fixed host model mappings, into each host's native tools. /swarm owns delegation, isolated writers, and cross-vendor review.
- **Names:** a sourced skill keeps its upstream name, with no source prefix. Rename it only when the name collides with another skill the user installs, from this library or elsewhere, or with a skill in a tracked source's repository; when it names its author or one host rather than what the skill does; or so a suite's entrypoints share the suite's name, as `pstack-mode`, `pstack-help`, and `pstack-setup` do. Record the reason in the mapping's `renamed` field in the catalog or `suite.json`, or in `UPSTREAM.md` for an unmapped skill; the catalog check rejects a mapped rename without one. Upstream references to a renamed skill use its local name, such as `/tdd` in Pstack's text becoming `/pstack-tdd`.
- **Packaging:** install with the Skills CLI from this repository, and package each sourced skill by the repository's `AGENTS.md`; its `agents/openai.yaml` is locally owned.
- **Coordination:** one coordinator writes canonical artifacts while delegates return proposals, and each effort keeps one accepted spec and ticket graph. Scale effort and parallelism to the task's scope and budget, and keep each workflow's outcomes and evidence.
- **Review:** a workflow's final review of its own implementation runs through /review-loop, which keeps /code-review's axes and adds /thermo-nuclear-review's correctness audit, the counterpart model's review, and the fix rounds. A review the user names runs as well, and /review-loop still gives the final verdict.
- **Authority:** honor the invoking repository's conventions and the user's existing authorization. Pull requests default to drafts, and learning-driven edits to source skills are prepared for review.
- **Licenses:** keep each upstream notice with the material it covers.
- **Steps:** a sourced step may end with a completion criterion, per this repository's skill rules.
- **Project artifacts:** a sourced skill that reads or changes project vocabulary, domain docs, or ADRs resolves them through /domain-modeling first.
- **Formatting:** differences the repository formatter makes, such as table padding and list or emphasis markers, are not divergences.

Pstack and Thermos:

- Pstack's /pstack-help routes to the user-facing entrypoints, and /principles discovers and applies the principles.
- Each Pstack skill works on its own; only an explicit /pstack-mode invocation activates the mode.
- Pstack helpers and principles are model-invoked, where upstream marks most of them user-invoked, so playbooks, routers, and other skills can load them. Helper descriptions scope triggering to Pstack tasks; principle descriptions keep upstream's triggers, because /principles selects principles by description in both suites. Entrypoints and skills with outward effects keep upstream's user-invoked mode: /pstack-mode, /pstack-help, /automate-me, /bro, both formal-verification skills, /maintain-verification-skill, and /make-bot-ui.
- Upstream's per-role model table becomes /swarm's model roles, which its `scripts/target.py` resolves by each role's label in kebab case. Upstream's fast Grok defaults become the host's fast model, Sonnet in Claude Code, for the explorer, investigator, tooling, and worker roles and for "your fast code model", named `fast-code`. Its Opus defaults become the session's model, and its two-family panels become the session's model plus the counterpart. `reflect-judgment` stands for upstream's `reflect judgment, divergent, synthesizer`. The code roles keep the session's model where upstream defaults them to Grok, by the model roles revision of the repository's ADR 0001.
- Thermos's own `MAINTENANCE.md` owns its review contracts.

Matt Pocock:

- Upstream stages such as `in-progress` stay recorded in the catalog.
- Matt's interview, planning, implementation, testing, and review owners invoke /principles in the current phase and before completion, so Pstack's principles improve Matt's workflow without Pstack mode.

## Shared owners

One skill owns each shared discipline. Other skills invoke the owner rather than restating its rules, and a change to an owner is checked against its consumers in both suites.

- /writing-for-agents owns agent-instruction writing and skill mechanics.
- /domain-modeling owns project vocabulary, domain relationships, and qualifying ADRs, including existing legacy context and domain files.
- /codebase-design owns architectural vocabulary and seam reasoning.
- /tdd owns behavior-test discipline: red-green mechanics and test seams. /principle-test-behavior-not-implementation owns the test-quality criteria, and Pstack's bug-fix adapter adds before-and-after evidence.
- /code-review owns Standards and Spec review; Pstack's adversarial lenses add coverage of the same artifact.
- /pr owns PR description shape; Pstack owns its delivery playbook and evidence mechanics.
- /reply-shape owns the layout of replies to the user; a skill's own report format is laid out within it.
- /next-options owns how replies end.
- /swarm owns native host execution, isolation, bounded cross-vendor review, its T3 Code route, and disclosed fallback.
- /review-loop owns cross-model review rounds, finding verification, and the fix-and-re-review loop.
- /thermo-nuclear-review owns the correctness and security audit that /thermos and /review-loop run.
- /principles selects the principles for each phase in both suites, keeping each principle's rules in that principle.
- /maintain-skills owns library upkeep and coverage accounting.

## Deciding an upstream change

Adopt by default. Taking upstream's improvements is the reason these skills are sourced.

- **Adopt** a change as written when it already fits the library-wide adaptations.
- **Adapt** a change by applying the library-wide adaptations, such as a renamed skill's local name, host translation, and owner delegation, or by keeping a recorded divergence whose reason still holds. Keep the change's intent. When it improves a discipline a shared owner holds, carry the improvement into the owner so both suites receive it, and keep the consumer delegating.
- **Exclude** a change only when it is specific to the author's own environment or product, or has evidence that it makes the skill worse. Record the reason; the reviewed-through position then covers it.
- **Hold** a change that needs a new service, wider authority, or a scope change, and ask the owner a question.
- **Upstream reverses a local divergence:** keep the divergence only when its reason outweighs upstream's stated reason, and record the comparison either way.
- **Converge:** when upstream now handles what a divergence was for, or a library-wide adaptation covers it, drop the divergence and take upstream's text.

Import each new upstream skill that does a job no local skill does, under its upstream name by the names rule above, unless the catalog excludes it or it needs owner approval. Judge the job by when the skill runs, what it is pointed at, and what it produces, not by its subject: a guide that loads while work is built and a review invoked afterwards do different jobs even when they share rules. When a local skill already does the same job, take nothing from it, not even a merge into that skill: exclude it, and propose uninstalling any installed copy. Hold a skill that does a new job but may not be worth maintaining, and ask the owner. Package an imported skill by the Add row of the change set in the repository's `CONTRIBUTING.md`. When upstream removes a skill without a successor, propose its retirement and a catalog exclusion with the removal commit as evidence, unless a local skill depends on it; then hold it and name the dependency.

The same test decides whether to adopt a skill the user installed from an untracked source. One that does a new job but needs no local change can stay installed from its upstream instead.

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

Record each decision where the next run reads it. Skill decisions go in the skill's `UPSTREAM.md` decision log. An excluded upstream skill or path goes in the catalog's `excludedNames` or `excludedPaths` with its reason; for a source without a catalog policy, it goes in the review history of that source's local skills. Owner answers from PR comments or chat are recorded the same way.

Anything that waits on the owner is a question: a held change, an upstream bug report to file, or a choice the contract leaves open. Ask it with your recommendation in runtime state and in each open maintenance PR's description. A held change counts as reviewed and waits there until the owner answers.
