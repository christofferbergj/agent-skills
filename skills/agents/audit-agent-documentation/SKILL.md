---
name: audit-agent-documentation
description: Audit and improve repository agent documentation without weakening project contracts.
disable-model-invocation: true
---

# Audit Agent Documentation

Treat the repository's agent guidance as one **instruction stack**: agents experience root guidance, scoped guidance, routed references, and skills together. Treat every document consumed by a workflow as a **contract**, even when it looks like ordinary prose.

Infer the authorization mode from the request:

- **Audit** — diagnose and propose changes without editing.
- **Improve** — the default; audit, make focused edits, and validate them.
- **Publish** — improve, then cross only the commit, push, or review boundaries the user explicitly requests.

Read [`references/AUDIT-RUBRIC.md`](references/AUDIT-RUBRIC.md) completely before judging the documentation. It is the evaluation reference for diagnosis and final review.

## 1. Establish authority and boundaries

Resolve the repository root, current worktree and branch, initial status, and the instruction files that govern the task. Read applicable `AGENTS.md` and equivalent agent instructions from the broadest scope to the most specific scope before examining candidates for change.

Mark existing user changes as protected. Record every explicit setup, generation, source-management, publication, and ownership rule that constrains agent documentation.

**Complete when:** the governing instruction chain, initial worktree boundary, and every protected or source-managed surface are identified.

## 2. Inventory the instruction stack

Search by role across every agent-documentation convention present. Account for:

- Root and nested entry points such as `AGENTS.md`, `CLAUDE.md`, and ecosystem-specific instruction surfaces.
- Documents and context maps reached from those entry points.
- Repository-local skills, their routed references, and discovery adapters.
- Setup outputs, provenance or lock manifests, generated guidance, and the sources or commands that own them.
- Nearby documentation and repository examples that reveal local conventions.

Exclude dependencies, build output, and vendored examples unless the repository deliberately exposes them to agents.

For each surface, record its scope, consumer, load condition, owner or source, and authoritative replacement path. Keep the inventory as working notes unless the user requests an artifact.

**Complete when:** every discovered agent-facing entry point is accounted for, every routed document required to understand its contract has been read, and the search boundary is explicit.

## 3. Verify documentation against reality

Treat each factual claim as a hypothesis. Verify relevant paths, scripts, package-manager commands, CLI fields, workspace boundaries, generated-file repair paths, symlink targets, and architecture claims against repository evidence or a safe live check. Use the repository's prescribed documentation lookup tool when external technical documentation is needed.

Use history and nearby examples when intent or ownership is unclear. For source-managed material, verify its provenance and refresh mechanism; route improvements through that mechanism or classify them as upstream work.

**Complete when:** every suspected defect and proposed factual change has current evidence, and every unverifiable claim is recorded as a gap rather than filled from memory.

## 4. Diagnose the merged stack

Apply every section of [`references/AUDIT-RUBRIC.md`](references/AUDIT-RUBRIC.md) to the guidance as an agent receives it: root plus scoped instructions and routed contracts for every discovered scope.

Classify each candidate:

- **Keep** — correct, useful, well-scoped, and worth its context.
- **Add** — a verified missing invariant, gotcha, route, or repair path has meaningful leverage.
- **Repair** — useful intent has stale facts, vague wording, a broken command, or a missing discovery seam.
- **Narrow** — valid guidance belongs in a smaller scope.
- **Route** — useful detail belongs behind a precise pointer.
- **Merge** — multiple rules express one contract and need one source.
- **Remove** — obsolete, contradicted, or behaviorally inert.
- **Conflict** — applicable authorities disagree and repository evidence does not resolve the choice safely.
- **Upstream** — improvement belongs in a generated, vendored, locked, or externally maintained source.

**Complete when:** every candidate has evidence, ownership, a classification, and either a justified destination or a justified decision to leave it unchanged.

## 5. Choose a focused change set

Select the smallest coherent set that preserves project-specific intent and required workflow semantics. Prioritize changes in this order:

1. Incorrect, stale, contradictory, unsafe, or undiscoverable guidance.
2. Always-loaded context that obscures higher-value instructions.
3. Vague direction that needs an actionable positive path.
4. Pure editorial preference, which normally stays unchanged.

**Complete when:** each planned edit has a concrete behavioral benefit, a verified basis, and the narrowest reliable owner and scope.

## 6. Execute the authorized mode

In **Audit** mode, leave the filesystem unchanged and turn the focused change set into an evidence-backed proposal.

In **Improve** or **Publish** mode, make the smallest coherent edits that realize the plan:

- Correct verified facts without changing the workflow they serve.
- Replace vague prohibitions with the desired action and repair path; retain hard guardrails where safety or contract integrity requires them.
- Prefer stable capabilities and domain concepts over brittle file tours.
- Link to authoritative source, code, or generated output instead of copying volatile detail.
- Preserve one canonical source and use the repository's supported discovery mechanism for other consumers.
- Apply generated or source-managed changes through their owning source and refresh path; leave a precise upstream finding when that path is outside the task's authority.

**Complete when:** Audit mode has a complete proposal and an unchanged filesystem; Improve or Publish mode has only intended agent-documentation changes, with protected semantics and user work intact and each meaning owned by one source.

## 7. Validate as a future agent

In Audit mode, use read-only checks, record mutation-capable gates as unrun, and confirm the final filesystem status matches the initial status. In Improve or Publish mode, read every changed document end to end. Then re-read every affected merged instruction stack and sample at least one unaffected stack for each instruction convention present. Verify that:

- Local links, anchors, paths, symlinks, and discovery entry points resolve.
- Commands and repair paths work in their documented context.
- Scope and precedence are unambiguous, with no new contradiction or orphaned reference.
- Generated or source-managed integrity checks pass.
- Repository formatting, documentation, and validation gates pass, followed by `git diff --check` and a final status review.

Use an independent reviewer when available; otherwise begin a fresh rubric-based pass after the draft is complete. Record exact blockers and unrun checks.

**Complete when:** every changed or proposed claim and route has been exercised or marked unverified, every applicable gate has a recorded result, and the final status matches the authorized mode and focused change set.

## 8. Report and publish if authorized

Lead with the outcome. Summarize:

- What changed or is proposed, and which agent behavior it improves.
- Important guidance deliberately retained, especially project-specific contracts.
- Conflicts, source gaps, or upstream work left unresolved.
- Validation performed, checks still pending, and whether hosted checks are settled or unknown.

A clean audit may produce no edits. Reassess the current repository and history on later runs instead of treating a prior audit as current truth.

In **Publish** mode, follow repository publication guidance and perform only the requested commit, push, or review action after local validation. Record the branch, target base, resulting URL or state where applicable, and whether hosted checks are settled or pending.

**Complete when:** the user can distinguish verified improvements, intentional non-changes, unresolved boundaries, and validation status without the hidden working notes, and any requested publication is complete or has an exact blocker.
