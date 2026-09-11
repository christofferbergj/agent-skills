# Monorepo documentation graph

Read when multiple first-party workspaces or nested instruction scopes are part of the audit. Apply the boundary from Step 1: a repository-wide audit covers all first-party workspaces; a focused audit covers the affected scopes and their relevant shared dependencies.

## Build the coverage map

- Derive first-party workspace roots from authoritative manifests, build configuration, and generators. Include apps or services outside conventional folders; exclude dependencies, generated output, and vendored trees with an explicit reason.
- Find every in-scope agent entry point and resolve its effective instruction chain using the target agent's discovery rules, including user-level and repository-root guidance.
- Follow every routed context map, domain document, standard, setup output, and consumer contract required by that chain.
- Record cross-workspace edges to shared guidance, tooling, templates, and generated outputs. When a proposed change affects a shared rule, include every dependent stack in its impact assessment; inventory unrelated content only if the request covers it.
- Group workspaces only when their effective instruction stacks and downstream consumers are identical; retain the full membership of every group.

## Scope test

- Root guidance carries only shared purpose, navigation, tooling, and repository-wide contracts.
- Nested guidance carries only instructions that apply throughout its directory scope.
- A specialized branch remains discoverable from the nearest common path without loading its detail into unrelated workspaces.
- Shared mutable facts and explanations have one owner; short repeated constraints remain only when separate automatic loading makes them necessary.

The inventory is complete when every workspace or instruction scope inside the declared boundary is mapped, every distinct effective stack is evaluated, and every relevant cross-workspace edge has an owner and resolution result. For a repository-wide audit, account for every first-party workspace. Report exclusions and gaps explicitly.
