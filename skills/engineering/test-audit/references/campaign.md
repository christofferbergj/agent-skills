# Exhaustive test-audit campaign

Use this sequence for all tests in a repository, monorepo, or subsystem. The main skill owns authority, value criteria, ledger decisions, cleanup rules, validation, and reporting. This reference adds exhaustive accounting and coordination across batches.

## 1. Establish the inventory and baseline

Apply the main skill's discovery step across the entire requested scope. Cross-check filesystem discovery with runner configuration, workspace manifests, CI routing, and runner discovery output where available. Include shared packages, script checks, and separately routed suites.

Assign every in-scope test file to one batch based on the production behavior it owns. Map shared support and consumers across batches. Record exclusions and baseline execution status for every suite, including unavailable environments and their reasons.

Complete when every in-scope file belongs to a batch and every suite has baseline results or a recorded execution limit.

## 2. Read every test and maintain the ledger

Apply the main skill's evaluation step to every declaration, including setup, assertions, parameter rows, skipped tests, and disabled tests. Track unreviewed files explicitly. Suspicious patterns determine review order; the inventory determines review coverage.

Keep a durable ledger and checkpoint in an environment-approved location when work spans sessions. Record the starting revision, inventory, batch progress, decisions, and validation so another session can resume. Commit these artifacts only when requested or required by project policy.

Keep one ledger owner. When delegation is authorized and available, assign disjoint read-only scopes and serialize shared-file edits. Otherwise work sequentially.

Complete when every declaration or distinct case group has a decision and evidence, including explicit unresolved entries.

## 3. Reconcile coverage ownership across batches

Review redundant layers and cross-package contracts against actual assertions and inputs. Identify each affected contract's surviving owner and distinct risks retained elsewhere. List case transfers, files to retire, support to remove, and routing to preserve. Resolve conflicts between batch plans before editing shared support.

Complete when every planned removal satisfies the main skill's evidence requirements and shared-file plans agree. In audit mode, report the ledger and recommendations using Step 6 of the main skill. In cleanup mode, continue below.

## 4. Apply and validate each batch

Apply the main skill's cleanup and validation steps to each batch. Confirm repaired or transferred tests execute before removing their old coverage. Validate shared consumers before dependent edits and update decisions as evidence changes.

Complete when every authorized batch decision is applied or explicitly blocked, with focused validation results recorded. Keep unresolved decisions open and preserve their tests.

## 5. Review preservation afresh

Perform the main skill's preservation comparison across the complete original and surviving suites. Revisit the original tests and diff rather than relying solely on ledger conclusions. Use an independent reviewer when authorized and available; otherwise perform a separate pass yourself.

Complete when every suspected gap is restored or rejected with evidence, and remaining uncertainty preserves the affected coverage.

## 6. Reconcile and report

If the working revision changed, inspect added or modified tests and update the inventory before closing the campaign. Follow repository branch policy and preserve contracts introduced by concurrent changes.

Run final relevant suites and required gates against the final edits. Reconcile inventory totals with ledger decisions, distinguishing parameter declarations from expanded cases. Report reviewed, excluded, unresolved, and unreviewed counts separately from executed, skipped, failed, and unexecuted tests.

Complete when the inventory accounts for every in-scope declaration or distinct case group, validation reflects the final edits, and the main skill's report includes the ledger, blockers, and remaining work. Apply its completion criteria before describing cleanup as complete.
