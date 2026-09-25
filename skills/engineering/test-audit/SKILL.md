---
name: test-audit
description: Audit test quality, repair weak or brittle tests, and consolidate redundant coverage. Use for focused test reviews or exhaustive test-suite cleanup across repositories and monorepos.
---

# Test audit

Optimize for confidence and maintenance cost. Preserve meaningful contracts. Treat suspicious test shapes as leads requiring investigation rather than deletion verdicts.

## 1. Set scope and authority

Use the user's existing instructions to determine scope and mode:

- **Audit:** Inspect, review, or recommend without editing.
- **Cleanup:** A request to clean up, prune, repair, or implement findings authorizes scoped test and test-support edits. Inspect first, then continue without asking for approval already given.
- **Campaign:** For all tests in a repository, monorepo, or subsystem, read [references/campaign.md](references/campaign.md). Use its exhaustive inventory and batch sequence with the criteria below. Campaign defines completeness; audit versus cleanup still determines editing authority.

For a bare invocation without a task, default to audit. Review the complete requested scope. Distinguish out-of-scope, unreviewed, and reviewed-but-blocked work. Continue independent work when a consequential decision is unresolved; ask only about the affected boundary.

Keep product behavior, public APIs, dependencies, CI gates, and coverage thresholds outside test cleanup unless separately authorized. Propose product fixes and production simplifications separately. Follow existing authorization for commits and publication.

Complete when the mode, in-scope tests, exclusions, and editing boundary are identified.

## 2. Discover the project and baseline

Read applicable root and scoped instructions, workspace manifests, test configuration, CI definitions, and relevant engineering documentation. Derive commands, package boundaries, and discovery rules from the project.

Identify unit, component, integration, contract, end-to-end, visual, property, architecture, and tooling tests actually present, including colocated tests and embedded examples executed by CI. Record shared fixtures and cross-package consumers. Exclude generated or vendored files only with a stated reason; inspect their generators or owning tests when relevant.

Record the starting revision and working-tree state when available. Run the relevant baseline commands before editing, using the same environment and selection intended for final validation. Distinguish product failures, flaky results, infrastructure failures, skipped tests, and tests not run. Investigate pre-existing failures while preserving meaningful coverage. Continue static inspection and independent work when execution is unavailable.

Complete when the requested scope has an inventory, discovered commands, and baseline results or explicit execution limits.

## 3. Evaluate and record decisions

Use the [candidate patterns](#candidate-patterns) to prioritize inspection. Read each test's setup, assertions, parameter rows, relevant production paths, and overlapping coverage. Investigate callers, dependency contracts, CI routing, and history as needed. For each test, determine:

1. **Contract:** What observable behavior, invariant, or independent requirement does it protect?
2. **Regression:** What credible incorrect implementation would make it fail, and do its assertions detect that failure?
3. **Independence:** Can its expected result disagree with the implementation, or does the test manufacture both sides?
4. **Boundary:** Does it exercise a public interface or stable boundary suitable for that contract?
5. **Distinct contribution:** What risk does it cover that remaining tests do not?

Use requirements, documented interfaces, bug history, protocol rules, worked examples, and established caller expectations as evidence. Formal specifications are useful evidence, not a prerequisite for useful coverage. Missing documentation or history leaves uncertainty. If the intended behavior cannot be established, retain the test pending clarification and mark it unresolved.

Prefer the lowest-cost stable boundary that can expose the failure. Keep pure rules close to their implementation through stable interfaces; keep integration coverage for wiring, serialization, storage, lifecycle, and transport risks that isolated tests cannot reach. Keep critical workflows at the user boundary. Choose one primary owner per contract, while preserving distinct risks at other layers.

Retain snapshots, source inspections, exact text, geometry, call ordering, slow tests, and mocks when they independently protect an intentional contract, such as an accessible interaction, wire format, visual baseline, architecture rule, package surface, or migration. Distinguish verifying a published export contract from mechanically copying the current export list. Distinguish a useful fake boundary from a mock that implements the behavior being tested.

Maintain a concise ledger before editing. Group cases only when their evidence and decision match; split parameter rows with different rationales. Record skipped or disabled execution separately from value.

| Test or parameter cases | Contract / credible failure | Decision | Evidence and surviving coverage | Validation |
| ----------------------- | --------------------------- | -------- | ------------------------------- | ---------- |

Use these decisions:

- **KEEP:** Retain useful, distinct coverage.
- **REPAIR:** Preserve the contract while fixing assertions, setup, determinism, or the exercised boundary.
- **CONSOLIDATE:** Move necessary cases into a named surviving suite before removing duplication.
- **DELETE:** Remove only when evidence establishes no meaningful contract is lost, or an identified surviving test already protects it.
- **UNRESOLVED:** Preserve existing coverage; state the missing evidence or decision.

For DELETE and CONSOLIDATE, identify the exact surviving proof and compare inputs, negative cases, assertions, integration paths, and execution in CI. Alternatively, explain why the test protects no meaningful contract. Inspect history when available; record its absence honestly. For REPAIR, state what is currently undetected and how the new assertion exposes it. Overlapping names, setup, executed lines, pattern matches, and a green suite after deletion do not establish redundancy.

Complete when every in-scope test or distinct case group has a decision and evidence. In audit mode, proceed to Step 6 with recommendations; in cleanup mode, continue below.

## 4. Apply cleanup by behavior

Group edits by the behavior or subsystem that owns them. Transfer unique cases before deleting their old home. Choose table-driven cases or shared fixtures for readability and stable setup rather than line reduction alone.

Repair vacuous assertions, overly broad exception checks, setup that bypasses the behavior, and determinism problems. Keep mocks at suitable boundaries. Keep product switches and public exports outside test-only repairs. Lack of internal callers alone does not justify removing a public export. Fix flakiness at its cause while preserving assertions and meaningful scenarios; retries are not a substitute for that repair.

Remove newly unused fixtures, imports, snapshots, helpers, and setup. Preserve support used by other packages. Keep test discovery and existing CI routing correct when moving tests; do not weaken gates or quarantine tests to make the result green. Separate discovered product defects from test-maintenance edits unless fixing them is in scope.

For any new or rewritten test, answer the five value questions above. For a bug regression, demonstrate failure on the pre-fix behavior for the intended reason where feasible, then success after the fix. If that cannot be run, record the unverified claim.

Complete when every authorized decision is applied or explicitly blocked, unique cases have an owner, and newly unused support is removed without affecting shared consumers.

## 5. Validate preservation

Keep files stable during validation. Finish or stop the relevant run before editing its inputs, preserving unrelated processes and working changes.

1. Run the smallest affected suite, then relevant sibling and cross-package consumers and repository-required gates. Use commands discovered from the project.
2. Confirm moved tests are discovered and executed, and meaningful parameter cases remain represented.
3. Compare original coverage against surviving assertions. Check unique inputs, errors, boundary cases, security, accessibility, ordering, interactions, integration paths, and CI environments where applicable. Restore missing contracts at their appropriate owner.
4. For high-risk or ambiguous repairs, use a focused negative control or small temporary mutation to show that the retained test catches the intended failure. Work in isolation and restore only the changes made for that check, preserving user edits. Do not require exhaustive mutation testing for routine cleanup.
5. Run applicable formatting/static checks and inspect the final diff for accidental scope expansion, dead support, weakened assertions, and configuration changes.

Reconcile baseline and final results. Report commands, test selection, outcomes, and unavailable environments accurately. Cached results do not prove newly edited tests ran. Stop optional validation once concrete risks are addressed and required gates are satisfied.

Complete when every affected contract has surviving evidence or a recorded unresolved gap, and every required check has a result or explicit execution blocker.

## 6. Report

State whether the result is a read-only audit, completed cleanup, or partial work. Summarize decisions and representative findings; provide the complete ledger for exhaustive campaigns without pasting every KEEP into the chat. Include:

- Scope and inventory reconciliation, including exclusions and unresolved items.
- Deleted or consolidated coverage and what protects those contracts now.
- Repaired tests and retained false positives worth explaining.
- Baseline versus final validation, failures, skipped or unexecuted checks.
- Product defects or production simplifications requiring separate work.

Report review coverage separately from execution results. Test counts and line reductions do not prove safety.

Complete when the user can distinguish completed work from unresolved decisions and unverified claims. Claim completed cleanup only when every in-scope test is reviewed and every authorized decision is handled. Unresolved decisions make cleanup partial; qualify execution limits separately.

## Candidate patterns

Search for these leads, then apply Step 3 before deciding:

- Expected values computed by the same code under test; assertions comparing a declaration with a copy of itself.
- Mocks or fixtures that supply the behavior or result the production path should produce.
- Assertion-free execution with no meaningful success/failure contract; account for implicit assertions such as "does not throw."
- Source scans, snapshots, counts, private calls, or incidental copy that detect edits without identifying a broken contract.
- Duplicate cases or layers with no distinct failure mode.
- Tests that exercise helpers while missing the real entry-point wiring.
- Negative tests that pass because an earlier, unrelated guard rejects the input.
- Broad assertions that cannot distinguish the intended result from a meaningful failure.
- Timing sleeps, shared mutable state, test ordering, uncontrolled clocks or randomness, and leaked resources.
- Test-only exports or hooks, obsolete fixtures, skipped suites, and disabled assertions.
- Names that promise behavior the input and assertions never exercise.

## Provenance

Adapted from [OpenClaw test-audit](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) and its campaign workflow. This attribution is not a runtime dependency.
