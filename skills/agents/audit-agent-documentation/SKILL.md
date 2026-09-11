---
name: audit-agent-documentation
description: Audit and improve repository agent documentation without weakening project contracts.
disable-model-invocation: true
---

# Audit agent documentation

Review the **instruction stack** an agent receives for the requested work. Trace its **documentation graph** through entry points, scoped guidance, references, skills, generators, and consumers. Preserve verified project contracts while revisiting historical steering and recommendations for current usefulness.

Infer the authorization mode from the request:

- **Audit** diagnoses and proposes changes without editing. Assessment and recommendation requests use this mode.
- **Improve** audits, makes focused edits, and validates them. Use this mode when asked to fix or improve documentation, or for an unqualified invocation of this skill.
- **Publish** improves, then completes the publication workflow in Step 6.

## 1. Set scope and authority

Resolve the repository root, worktree, branch, initial status, and governing instructions. Protect existing user changes. Record applicable ownership, setup, generation, and publication constraints.

Match coverage to the request. For a focused audit, inspect the named documents, their governing stack, and the owners and consumers needed to assess them. Expand only when evidence reveals a dependency or conflict that affects the finding. A repository-wide audit covers every first-party workspace and agent-documentation convention. Derive workspace boundaries from manifests and configuration.

Identify the intended agent environments and models from available configuration or user context. Record unknowns without assuming all contributors use the same model.

**Complete when:** the authorization mode, search boundary, governing instructions, protected changes, and target environments are recorded.

## 2. Trace the relevant graph

Find entry points and follow their inheritance, references, skill dependencies, setup outputs, generators, and discovery adapters within the declared scope. Exclude dependencies, build output, and vendored examples unless agents deliberately consume them. Keep the graph as working notes unless the user requests an artifact.

For each relevant document, identify its scope, load condition, owner, and consumers. Distinguish automatically loaded instructions from optional references and files merely present on disk. Resolve the configured loading path for each intended agent environment; record uncertain loading behavior for verification during diagnosis.

Read these references when their conditions apply:

- Multiple workspaces or nested instruction scopes are part of the audit: [MONOREPO-GRAPH.md](references/MONOREPO-GRAPH.md).
- A skill is being assessed: [SKILLS.md](references/SKILLS.md), including ordinary skills that do not produce agent documentation.
- A skill, generator, adapter, or tool consumes or produces the documentation under review, or retained setup outputs are involved: [CONSUMER-CONTRACTS.md](references/CONSUMER-CONTRACTS.md).

**Complete when:** every in-scope entry point and relevant dependency has an owner and load path, with unresolved discovery or source gaps recorded.

## 3. Diagnose and select changes

Read [AUDIT-RUBRIC.md](references/AUDIT-RUBRIC.md) and apply its criteria to each distinct in-scope instruction stack. Verify suspected defects and proposed factual changes against current repository evidence or a safe live check. Use history when intent is unclear and the repository's prescribed lookup tools when external documentation is needed.

Classify findings using the rubric. Select the smallest coherent change set, prioritizing incorrect or conflicting guidance, unnecessary context and work, and unclear decision boundaries. A clean audit may require no edits. Keep unresolved claims as gaps rather than filling them from memory.

**Complete when:** each finding has evidence, a classification, an owner, and a concrete behavioral consequence; each proposed edit has a justified scope and preserves verified contracts.

## 4. Execute the authorized mode

In Audit mode, turn the findings into an evidence-backed proposal and leave repository files unchanged.

In Improve or Publish mode, invoke `/writing-for-agents` before drafting agent-consumed documentation. Apply the focused changes through their owning sources and supported refresh paths. Preserve user work, selected project values, and consumer requirements. Keep each meaning in one authoritative place. Report upstream work when the owning source is outside the task's authority.

Continue authorized editing and validation through completion. When an action needs additional authorization, prepare the reviewable result first and identify the exact action and instruction requiring approval. A blocked edit does not prevent independent authorized work.

**Complete when:** the proposal or edits address every selected finding, with unresolved work explained and protected contracts intact.

## 5. Validate affected behavior

Read changed documents end to end and assess them in each affected instruction stack. Check changed links, anchors, commands, discovery routes, and consumer requirements in their documented context. Sample unaffected paths only when shared guidance or an unresolved concern could affect them.

Run applicable repository formatting, documentation, and integrity gates, then `git diff --check` and a final status review. In Audit mode, use read-only checks and record mutation-capable gates as unrun. Once checks pass, repeat or broaden them only for new changes, failures, or unresolved concerns.

For substantial changes to routing or decision boundaries, exercise representative requests, including a nearby request that should not activate a branch. Use an independent reviewer when available and authorized; otherwise perform a fresh rubric-based pass. Distinguish behavioral execution from a static walkthrough, and record exact blockers and unrun checks.

**Complete when:** every affected stack and applicable gate has a recorded result, each changed or proposed claim and route is verified or explicitly unverified, and final status matches the authorized mode and change set.

## 6. Finish and report

In Publish mode, read and complete [PUBLICATION.md](references/PUBLICATION.md) after local validation.

Report the outcome, behavioral improvements, coverage and exclusions, important retained contracts, unresolved conflicts or upstream work, and validation results. Include publication and hosted-check status when applicable. Reassess current evidence on later runs instead of treating this audit as permanent truth.

**Complete when:** the requested proposal, improvement, or publication is complete or has an exact blocker, and the user can distinguish verified results from unresolved work without the working notes.
