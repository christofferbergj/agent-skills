# Documentation consumer contracts

Read this reference only when a repository-local or installed skill, generator, adapter, or tool reads or writes repository agent documentation, or when its setup outputs remain in the repository.

## Trace the contract

- Read the current owning skill and the templates or references defining the output under review before judging its requirements.
- Treat required filenames, headings, fields, exact values, conditional presence, and selected project choices as an interface.
- Distinguish the canonical owner from generated output, discovery adapters, symlinks, lockfiles, and copies.
- Preserve apparently repetitive prose when a consumer parses it or evidence shows its automatic loading scope protects a required behavior. Reassess historical steering separately from those requirements.
- When the owner is unavailable, record a source gap and keep the unresolved contract out of the edit set.

Use the declared refresh workflow for source-managed material. An upstream finding is a successful outcome when the local repository does not own the source.

## Setup Matt Pocock's Skills

When `/setup-matt-pocock-skills` is installed or its outputs are present, use its current `SKILL.md` and seed templates as authority. Account for the selected root agent entry point and its `## Agent skills` block, `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, the chosen `CONTEXT.md` or `CONTEXT-MAP.md` layout, and the conditional triage-label block and `docs/agents/triage-labels.md`.

Preserve the repository's chosen root entry point, tracker workflow, request-surface flag, label mapping, domain layout, and conditional omissions. The triage block and document exist only when the triage skill is installed, and domain context files may be intentionally absent until created lazily. Do not add either merely to complete a shape. Use this paragraph only as a discovery pointer; the installed setup skill owns the exact current structure and values.
