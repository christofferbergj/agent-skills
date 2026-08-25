# Monorepo Documentation Graph

Read this reference only when the repository has multiple first-party workspaces or distinct nested instruction scopes.

## Build the coverage map

- Derive first-party workspace roots from authoritative manifests, build configuration, and generators. Include apps or services outside conventional folders; exclude dependencies, generated output, and vendored trees with an explicit reason.
- Find every agent entry point inside each workspace and resolve its inheritance chain from user-level and repository-root guidance down to the narrowest scope.
- Follow every routed context map, domain document, standard, setup output, and consumer contract required by that chain.
- Record cross-workspace edges to shared guidance, tooling, templates, and generated outputs.
- Group workspaces only when their effective instruction stacks and downstream consumers are identical; retain the full membership of every group.

## Scope test

- Root guidance carries only shared purpose, navigation, tooling, and repository-wide contracts.
- Nested guidance carries only instructions that apply throughout its directory scope.
- A specialized branch remains discoverable from the nearest common path without loading its detail into unrelated workspaces.
- Shared mutable facts and explanations have one owner; short repeated constraints remain only when separate automatic loading makes them necessary.

The monorepo inventory is complete when every first-party workspace is mapped or explicitly excluded, every distinct effective stack is evaluated, and every cross-workspace edge has an owner and a resolution result.
