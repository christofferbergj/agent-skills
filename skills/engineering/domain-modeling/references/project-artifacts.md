# Shared project artifacts

Read this contract when resolving domain docs, reconciling an architecture decision, or handing work between a Matt or Pstack entrypoint. It governs project artifacts, not files inside installed skills.

## Resolve before writing

1. Read the invoking repository's `AGENTS.md`, `CLAUDE.md`, and existing pointers. Read `docs/agents/domain.md` when present, plus any configured issue-tracker and triage-label documents needed by the task. Follow a project's explicit paths before defaults. Complete when artifact roles and their authoritative locations are known.
2. Inspect the actual documents before classifying them. Current defaults are `GLOSSARY.md`, optional `GLOSSARY-MAP.md`, and `docs/adr/`. Existing `CONTEXT.md`, `context.md`, `DOMAIN.md`, or `domain.md` may hold vocabulary, domain relationships, or consumer configuration. Retain their case, format, and role; a filename alone does not establish its meaning. Complete when the selected context and each relevant artifact's purpose are explicit.
3. Use the configured files. If nothing defines a vocabulary location, use an existing glossary or legacy context document; create a root `GLOSSARY.md` lazily when the first term is settled. A context map selects relevant context-scoped documents. If competing documents disagree about ownership, report the conflict before overwriting either. Complete when one source of truth exists per role, with no parallel glossary created just for a different skill family.

## Persist the accepted model

Update the vocabulary artifact when a project term is resolved. Update an existing domain-model artifact when an accepted relationship, state, invariant, or ownership rule changes. Update consumer configuration such as `docs/agents/domain.md` only when paths, contexts, or reading rules change. These are distinct roles: a glossary stays free of implementation details; a model or decision document retains its established structure.

Architecture workflows invoke /codebase-design for design vocabulary and this skill for domain meaning. A type sketch, prototype, spec, or Pstack rationale points to the accepted model and qualifying ADRs rather than becoming a second copy of them. Proposals remain labeled as proposals until selected. Existing approved decisions and scope still govern implementation.

Only record ADRs that meet this skill's tradeoff, surprise, and reversal-cost criteria. Record an already-authorized qualifying decision without another save dialog; ask when the decision itself is unresolved. Preserve superseded decisions with a continuity pointer.

## Share work without sharing writes

The coordinating agent owns edits to canonical project docs. Delegates return proposed terms, relationships, conflicts, and evidence with their code or design results. Reconcile proposals before editing; independent worktrees do not make conflicting glossary edits safe. Finish a unit only when changed model facts, their implementation, and relevant documents agree, or the exact gap is reported.

Read-only investigation or review reads these artifacts and reports drift without changing them. A source skill is an instruction template; runtime work never edits installed templates or global skills.

## Specs, tickets, and evidence

Use the configured tracker and any existing spec or ticket graph as the work's source of truth. `/to-spec` and `/to-tickets` remain explicit user entrypoints. Pstack plans and execution ledgers link to those artifacts and acceptance criteria instead of publishing duplicate specs or tickets. Generate only artifacts the task needs.

External issue creation, comments, closure, labels, PRs, merges, deployments, and scheduling follow the user's grant for that action. Prepare local content when publication is not authorized. For multi-line forge content, use a structured tool argument or a UTF-8 body file; never interpolate it into shell code.
