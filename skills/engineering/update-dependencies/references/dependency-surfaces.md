# Dependency Surface Inventory

This taxonomy defines the version-bearing surfaces covered by the `update-dependencies` sweep. The main skill owns inventory actions, decisions, completion criteria, and validation.

Exclude dependency directories, caches, build output, and vendored examples unless the repository deliberately owns dependency declarations inside them.

## Package graph

Account for:

- Root and workspace `package.json` files, including production, development, optional, and peer dependencies.
- The lockfile owned by the detected package manager.
- Workspace catalogs, constraints, overrides, resolutions, package extensions, aliases, and protocol specifiers.
- Patched dependencies and the commands or tests that prove each patch still applies.
- Nested package-manager roots that are intentionally independent of the root workspace.

## Automation

Inspect tracked CI and automation configuration for external versioned references:

- GitHub workflow and composite-action `uses:` entries.
- Reusable workflows and external CI plugins, orbs, tasks, and setup actions.
- Bootstrap or release scripts that download a named tool version.

Local paths and repository-owned actions are not external dependencies. Record each external reference's tag, full-version, commit-SHA, or digest style and its owning policy.

## Containers and development environments

Inspect:

- `FROM` declarations in tracked Dockerfiles.
- Image declarations in Compose, CI containers and services, deployment manifests, and development-container configuration.
- Versioned development-container features or templates.

When an image tag is derived from a package, runtime, or shared variable, account for it under that owning declaration instead of inventing a separate update. Preserve the repository's tag-versus-digest policy.

## Runtimes and package-manager toolchains

Reconcile linked declarations across:

- `packageManager`, `engines`, `devEngines`, Corepack, and Volta configuration.
- Mise, asdf, nvm, Node-version, and other local toolchain files.
- CI matrices, container base images, deployment configuration, and bootstrap scripts.

Record every consumer of a shared runtime or package-manager declaration so linked versions can be assessed together.

## Security and supply-chain policy

Account for advisory output, the repository's documented remediation threshold, and any missing threshold.

Inspect Renovate, Dependabot, package-manager, registry, and CI configuration for:

- Allowed, ignored, grouped, or scheduled updates.
- Range, pinning, lockfile, registry, and integrity policy.
- Security-specific exceptions and their expiry or rationale.

## Generated and source-managed surfaces

Identify generated contracts, vendored sources, provenance locks, and refresh scripts affected by dependency installation or validation. Link each generated or patched artifact to its owning refresh path and verification command.

## Lint, format, and doctor stack

Detect the actual installed and imported stack rather than relying on a fixed package list:

- Ultracite and its selected backend.
- Oxlint, Oxfmt, ESLint, Prettier, Biome, and type-aware lint integrations.
- React Doctor and its lint integration.
- Loaded JavaScript lint plugins and shared workspace config packages.
- Root, shared, and scoped configuration files plus inline suppressions.
