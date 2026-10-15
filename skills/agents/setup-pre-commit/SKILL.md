---
name: setup-pre-commit
description: Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing.
---

# Set up commit checks

1. Inspect the package manager, runtime versions, existing hooks, formatter, linter, and umbrella check commands. Invoke /linting-alignment when tool ownership is unclear. Complete when the current toolchain and requested hook boundary are known.
2. Reuse the repository's formatter and existing hook manager. Add Husky and lint-staged only when they fit the project and are missing; install development dependencies through its package manager. Preserve existing prepare scripts and hooks. Complete when one owner exists for each check and unrelated configuration is unchanged.
3. Wire staged-file checks and the appropriate existing type/test checks using the project's commands. A repo using Oxfmt, Biome, or another formatter keeps it; Prettier is not an installation prerequisite. Avoid testing only staged fragments when the check requires the full project. Complete when the hook runs the requested checks without duplicating the toolchain.
4. Validate syntax and exercise the hook against a harmless isolated or already-authorized change. Preserve the initial staging state and report absent checks rather than inventing scripts. Commit only the scoped result when authorized. Complete when the hook has observed evidence and each changed configuration has a known owner.
