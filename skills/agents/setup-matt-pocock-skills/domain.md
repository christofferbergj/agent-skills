# Domain docs

This is the shared documentation contract for every engineering entrypoint, including Pstack. Populate the roles below with this project's actual paths; retain existing names and contexts instead of creating parallel documents.

## Authoritative artifacts

- Vocabulary: `GLOSSARY.md`, or the existing configured context document.
- Context map: `GLOSSARY-MAP.md` when multiple contexts already need it.
- Domain relationships and invariants: the existing domain-model document, if separate from the vocabulary.
- Decisions: `docs/adr/`, plus configured context-scoped decision directories.

Read the relevant artifacts before exploration. Missing documents are created lazily when a term or decision needs a durable record. Invoke /domain-modeling when accepted terminology, relationships, ownership, contexts, or document paths change; it owns updates to these artifacts. Invoke /codebase-design for architectural vocabulary without renaming the project's domain concepts.

Respect existing `CONTEXT.md`, `context.md`, or `domain.md` roles. A file named `domain.md` can be either a model or consumer configuration; inspect its content. Keep one source of truth per role. Specs, tickets, prototypes, Pstack rationale documents, and evidence journals link to these records instead of copying them.

The coordinator owns canonical document edits; delegates propose changes. Read-only investigations and reviews report drift without edits. Surface conflicts with accepted decisions rather than silently overriding them.
