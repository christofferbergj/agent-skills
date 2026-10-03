---
name: update-dependencies
description: Update JavaScript and TypeScript dependencies with package-manager resolution, release research, validation, and an optional pull request.
disable-model-invocation: true
---

# Update dependencies

Treat dependency maintenance as a **sweep**: inventory owned version declarations, let the repository's package manager resolve the package graph, then validate and account for the result.

Invoke with `/update-dependencies Update dependencies` for a repository or its entire monorepo. Add `and open a pull request` to publish, or request an audit, selected packages, or latest major versions to change the scope. Infer workspace coverage from the repository.

Infer the authorization mode from the request:

- **Audit**: inventory and assess updates without changing files.
- **Improve**: the default; apply policy-compatible updates, validate them, and leave the result uncommitted.
- **Publish**: improve, then perform the requested publication. A pull-request request includes the branch, commit, and push needed to create it.

Repository instructions, manifests, and maintenance configuration own project policy. This skill supplies the process around them. When applicable authorities disagree and current repository evidence does not resolve the conflict, hold the disputed update and continue with unambiguous work.

## 1. Establish the maintenance contract

Resolve the Git root, current branch, worktree status, and every package-manager root inside the repository. Read applicable `AGENTS.md` and equivalent instructions from broadest to narrowest scope, then follow their routes to dependency, security, release, CI, generated-code, and validation guidance.

For each package-manager root, identify the manager and version from its declaration and lockfile. Record workspace boundaries, required scripts, update automation, version-range and peer policy, patched or generated artifacts, toolchain declarations, default branch, and publication rules. Use the repository's manager and version for resolution and validation.

Preserve existing user changes as an explicit boundary. In Audit mode, every command in the run must be read-only.

**Complete when:** every JavaScript or TypeScript package-manager root has a governing policy and command source, every existing dirty file is included or excluded deliberately, and any unsupported or conflicting root is identified without blocking independent roots.

## 2. Inventory every detected surface

Read [`references/dependency-surfaces.md`](references/dependency-surfaces.md) completely, then apply every section to each package-manager root. Record absent surfaces as absent rather than silently skipping them.

Use the installed manager's help before choosing outdated, audit, graph, and peer-diagnostic commands. Confirm whether peer issues cause failures, warnings, or require a separate check. For pnpm roots, read [`references/pnpm-resolution.md`](references/pnpm-resolution.md) before selecting commands or interpreting peer diagnostics. Inspect all owned workspace manifests rather than relying only on the root summary. Resolve dynamic versions to the declaration that supplies them, and count that declaration once.

Capture baseline peer diagnostics with the manager's supported check. If obtaining them requires resolution that writes files, use an isolated copy of the current manifests, lockfile, and configuration in Improve or Publish mode. In Audit mode, record unavailable diagnostics as a validation gap. Record baseline failures for the affected validation gates as well.

Maintain a working ledger with:

| Surface                              | Current   | Eligible target      | Risk                                                 | Policy or evidence           | Decision                         |
| ------------------------------------ | --------- | -------------------- | ---------------------------------------------------- | ---------------------------- | -------------------------------- |
| package, action, image, or toolchain | exact ref | exact ref or current | patch, minor, major, non-semver, security, or linked | repository or primary source | current, include, hold, or split |

Keep the ledger as working notes unless the user asks for an artifact. Reuse package and release evidence across workspace consumers; record differing targets or policies separately.

**Complete when:** every detected surface has one ledger entry or a documented owning source, and baseline peer diagnostics and affected checks are captured or have an exact availability gap.

## 3. Decide the sweep

Classify candidates by semver distance when semver applies and by runtime, tooling, CI, toolchain, or security impact. Treat majors, non-comparable refs, runtime-sensitive libraries, security remediations, package-manager or runtime upgrades, and changes with migration instructions as sensitive.

Build package candidates with the manager's workspace-aware commands. Let its resolver select eligible versions and evaluate declared peer ranges under existing configuration. Treat configured eligibility checks as authoritative when the command enforces them, including pnpm's `minimumReleaseAge`. Add manual checks only for policy the manager cannot enforce or repository instructions explicitly require.

Research official changelogs and release notes for every proposed direct dependency, catalog entry, override, and explicitly targeted transitive update across its current-to-target interval. Reuse that research across consumers and linked package families. Cover incidental transitive changes through the owning update; investigate them separately when diagnostics, advisories, or release notes identify a risk. Use the repository's prescribed documentation lookup mechanism. Record missing notes and the primary-source fallback used.

For sensitive updates, also identify required migrations and runtime or toolchain constraints. Use peer diagnostics to direct compatibility research; a major version difference alone does not establish a peer conflict. Package-manager resolution remains provisional until step 5 validates application behavior.

Give every candidate one outcome:

- **Include**: eligible under repository policy and ready for resolution and validation.
- **Hold**: stays unchanged for a demonstrated compatibility failure, policy restriction, or specific evidence gap.
- **Split**: needs a separately scoped migration and stays unchanged in this sweep.
- **Current**: already current, locally derived, or otherwise creates no update.

Treat linked declarations as one decision: runtime versions across local tooling and CI, package-manager pins across manifests and bootstrap files, and dynamically derived images across their source and consumer.

When an included update touches Ultracite, a lint or formatter backend, React Doctor, a loaded JavaScript lint plugin, or a shared lint-config package, run the `/linting-alignment` skill before changing lint configuration. If that skill is unavailable, preserve configuration and hold any update whose safety depends on a config migration.

**Complete when:** every candidate has a policy and release-research outcome, sensitive includes have a migration and validation plan, every hold or split has an exact reason, and every detected lint-stack change has completed or safely deferred its alignment handoff.

## 4. Apply included updates

In Audit mode, keep the worktree unchanged and continue to validation and reporting.

In Improve or Publish mode, update coherent groups with the repository's package manager and inspect the diff between groups. Resolve coupled packages together across their workspace and catalog owners so an intermediate version mix does not become a blocker.

- A broad update command is allowed for a package-manager root only when every candidate it can select is **Include**.
- If any candidate is **Hold** or **Split**, batch included updates with dependency selectors, exclusions, and workspace filters that preserve held declarations. If supported selectors cannot separate the group, narrow it or hold the inseparable group.
- Preserve version-range policy, workspace and catalog protocols, aliases, overrides or resolutions, lockfile ownership, package-manager configuration, patches, automation pin style, and container tag-or-digest policy. Select updates beyond declared ranges only when the request or policy includes them.
- Apply runtime and package-manager upgrades only when the request or repository policy clearly includes them.
- Keep rejected probes and unrelated generated or source-managed changes out of the final diff.

After each package group, reconcile resolver warnings with the peer check and compare diagnostics with the baseline. Investigate contradictory output before treating the graph as clean. Treat the manager's declared-range evaluation and established repository exceptions as compatibility evidence. Classify reported issues:

- Retain updates whose peer requirements resolve under repository policy, then validate application behavior.
- Record unchanged baseline warnings and existing scoped exceptions without treating them as new regressions. Follow repository policy for whether they block publication.
- For new or worsened issues, trace the affected consumer, required range, resolved provider, and workspace scope. Try a coordinated in-scope update or supported compatible target before holding the affected group.
- Retain a new out-of-range warning only with targeted upstream compatibility evidence, permission under existing peer policy, and passing affected checks. Otherwise hold or split that group and continue independent updates.

Keep acceptance policy and exceptions at repository policy. Disabling checks, forcing past resolver errors, or adding peer suppressions requires an explicitly scoped policy change. An install's zero exit code alone is insufficient when the manager only warns about invalid peers.

Reconcile actual selected versions with the ledger and release research. Confirm every changed declaration maps to an **Include** and every **Hold** or **Split** declaration retains its original value.

**Complete when:** Audit mode leaves the graph unchanged and records proposed groups and diagnostic gaps; Improve or Publish mode has peer evidence for every included package group, a disposition for every reported issue, unchanged held and split declarations, and a diff containing only included updates and their required artifacts.

## 5. Validate the result

In Audit mode, run only repository-approved read-only checks. Skip installs, fix or formatting commands, generators, builds with owned output, and any validation entry point that can change the worktree; record each skipped gate and confirm the final filesystem status matches the initial status.

In Improve or Publish mode, install the resolved graph and run the repository's lockfile-consistency check and documented formatting, linting, type-checking, testing, build, generation, and validation gates that apply to the changed surfaces. In monorepos, include affected dependents and every consumer of changed shared catalogs or toolchain packages. Follow required repository-wide gates even when focused checks pass. In every mode, also:

- Run `git diff --check` in Git worktrees.
- Re-run the dependency inventory and peer check, and reconcile every remaining outdated item and peer issue with the ledger.
- Re-run the applicable security audit after a security remediation.
- Validate changed automation, container, patch, and generated-artifact surfaces with the repository's own tools or established checks.
- Run the validation required by `/linting-alignment` when the lint stack changed.
- Inspect status again after validation because installs and generators may create additional changes.

When a check fails, establish whether the included update caused it. Fix the update, hold it, or split it; keep unrelated baseline failures out of the sweep and record their exact evidence. A blocked update is not publishable.

**Complete when:** Audit mode records the validation required for every proposed include and preserves the initial filesystem; Improve or Publish mode has every applied include passing its applicable gates or removed with an exact blocker; the final ledger matches the filesystem; and the worktree contains only authorized changes.

## 6. Report and publish only when requested

Lead with whether the repository was already current, was updated successfully, or remains blocked. Summarize included, held, and split candidates; sensitive-update evidence; changed surfaces; security findings; and each validation result. Distinguish pending hosted checks from failures.

Audit mode ends with an unchanged worktree. Improve mode ends with the validated changes uncommitted and unpublished.

In Publish mode, follow repository guidance and harness constraints. Retain any current branch that satisfies those authorities. When publication needs a new branch and neither authority supplies a name, use `agent/YYYY-MM-DD-update-dependencies` as the fallback. Perform the requested boundary and its prerequisites:

- Stage and commit only the sweep's files for a requested commit or pull request.
- Push for a requested push or pull request.
- Create or update a requested pull request against the discovered base branch. Include release-source links, included and deferred updates, peer-diagnostic dispositions, and validation results. Report its URL and pending hosted checks.

Stop before publication when no changes remain or validation is blocked.

**Complete when:** the user can see the full accounted-for surface, every include/hold/split decision, the exact validation state, and either the requested publication result or the precise reason publication stopped.
