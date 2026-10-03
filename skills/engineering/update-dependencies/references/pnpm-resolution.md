# pnpm resolution

Use this reference for pnpm package updates and peer diagnostics. The main skill owns decisions, warning triage, release research, validation, and publication.

## Choose commands from the installed version

Read `pnpm help update`, `pnpm help recursive`, `pnpm help install`, and help for the available peer checker. Consult matching-version official documentation when help does not establish behavior. Workspace coverage, catalog updates, and peer-check commands vary by version.

Read effective resolution policy from the repository's supported configuration locations. Include `autoInstallPeers`, `strictPeerDependencies`, `resolvePeersFromWorkspaceRoot`, `peerDependencyRules`, catalogs, overrides, package extensions, patches, release-age restrictions, and hooks that transform manifests. In pnpm 11, resolution settings moved from `.npmrc` to `pnpm-workspace.yaml`; `.npmrc` still supplies registry and authentication settings. Keep credentials out of captured evidence.

Use pnpm to evaluate peer ranges, including unions and prereleases. `autoInstallPeers` can supply missing non-optional peers, but conflicting requirements can prevent automatic installation. Root dependencies can supply peers when `resolvePeersFromWorkspaceRoot` permits it. Different workspace consumers can legitimately resolve different peer versions. pnpm does not search every package-release combination or prove runtime compatibility.

## Batch the workspace graph

Choose a command for the requested range policy and scope. These examples require support in the installed version and an approved candidate set:

| Scope                       | Within declared ranges                    | Latest majors when requested                       |
| --------------------------- | ----------------------------------------- | -------------------------------------------------- |
| Single package-manager root | `pnpm update`                             | `pnpm update --latest`                             |
| Entire workspace            | `pnpm -r --include-workspace-root update` | `pnpm -r --include-workspace-root update --latest` |

Verify root and workspace coverage against the inventory. `--workspace` updates links to local workspace packages; `--recursive` selects workspace projects for registry updates.

Batch related dependency names in one update command. Dependency arguments or exclusion patterns select dependencies; `--filter` selects workspace consumers. Use both when a held version belongs to only some consumers. Preserve independent roots and each root's lockfile ownership. Let pnpm perform workspace resolution instead of looping over every package and comparing its peers manually.

Preserve range operators and protocols. Use `--no-save` when policy calls for a lockfile-only refresh. Catalog-aware update support varies by version; confirm that the chosen command updates the owning default or named catalog and keeps `catalog:` consumers intact. If it cannot, edit the catalog declaration once and let pnpm resolve it. A catalog edit affects every consumer, including packages outside an update filter, so account for them in validation.

Published workspace `peerDependencies` declare support for downstream consumers. Evaluate changes to those support ranges separately from choosing the installed peer provider. Use peer-update flags only when changing that contract is in scope.

Allow pnpm's update or install command to enforce configured release eligibility. An outdated report's newest registry version is a candidate, not proof of eligibility. Research the version pnpm actually selects when it differs from that report.

## Obtain peer evidence

Capture command, manager version, exit code, and diagnostics before and after updates. Preserve workspace consumer, dependency path, required peer range, and resolved provider in issue comparisons. Reuse unchanged diagnostics across consumers with the same resolution context.

When the installed version provides `pnpm peers check`, use it to inspect the lockfile. Confirm freshness against current manifests and configuration; a check of an old graph cannot validate proposed versions. Use structured output when supported.

Reconcile the checker with warnings from resolution. If it reports clean after resolution warned, obtain detailed resolver diagnostics. A supported command-only `--strict-peer-dependencies` diagnostic pass can expose consumer, range, and provider without changing saved policy; interpret its failure against baseline warnings and existing acceptance policy. Run mutation-capable diagnostic passes in an isolated copy when their changes are outside the update. Record any remaining diagnostic gap for the affected group.

For versions with `--resolution-only`, `pnpm install --resolution-only --no-frozen-lockfile` reruns resolution and reports peer issues. Treat it as mutation-capable. Capture baseline output in an isolated copy of the current graph; use it on the updated graph when fresh diagnostics are needed. Resolution-only or lockfile-only work still needs a real install and application checks afterward.

A frozen or headless install can reuse the lockfile and skip resolution. It proves lockfile consistency, not a fresh peer-range assessment. Prefer the supported peer checker or an explicit resolution pass. A documented install dry run may provide fresh diagnostics when available; confirm its write behavior before using it in Audit mode. Keep Audit commands read-only and report unavailable checks.

`strictPeerDependencies` determines whether invalid peers fail commands. Existing `peerDependencyRules` can accept or suppress selected issues, so interpret output alongside effective policy. Successful resolution under those rules proves policy acceptance, not compatibility beyond declared ranges. Apply the main skill's warning triage and validation criteria.

## Primary sources

- [pnpm 10 update](https://pnpm.io/10.x/cli/update) and [pnpm 11 update](https://pnpm.io/11.x/cli/update) document update selection and version-range behavior.
- [pnpm recursive commands](https://pnpm.io/11.x/cli/recursive) documents workspace coverage.
- [pnpm 10 settings](https://pnpm.io/10.x/settings), [pnpm 11 settings](https://pnpm.io/11.x/settings), and [pnpm 11 peer settings](https://pnpm.io/11.x/settings/peer-dependencies) document configuration locations, resolution policy, and automatic-peer limitations.
- [pnpm 10 install](https://pnpm.io/10.x/cli/install), [pnpm 11 install](https://pnpm.io/11.x/cli/install), and [pnpm 11 peers](https://pnpm.io/11.x/cli/peers) document resolution and diagnostic commands.
