---
name: pstack-tdd
description: "Use in a Pstack bug fix when a cheap regression test can demonstrate failing-before and passing-after behavior."
---

# Pstack bug-fix evidence

1. Identify the broken and intended behavior and a cheap executable regression path. Reuse an agreed public seam; invoke /tdd for the shared red/green and behavior-test discipline. Complete when the reproduction can distinguish this defect or the unavailable test path is explicit.
2. Preserve the failing-before command, revision, and result. Confirm it fails for the intended reason. If it passes or fails for an unrelated reason, correct the test or reproduction before editing the implementation. Then fix the defect and rerun the same regression. Do not create a broad brittle harness for a small reversible fix. Complete when observed before/after behavior and relevant nearby checks support the fix.
3. Report the original symptom, causal change, evidence, and any missing test or live-surface coverage. Complete when no skipped check is presented as a pass.

## If a failing test is impractical

Use the closest executable regression check instead: a targeted script, manual reproduction command, browser automation, snapshot comparison, log assertion, or focused integration check.

Prefer no new test over a bad test. A bad test is one that mostly tests mocks, encodes current implementation details, depends on timing or unrelated global state, needs expensive infrastructure for a small fix, or would be deleted immediately after proving the fix.

## Guardrails

- Do not change tests merely to match a wrong implementation.
- Do not weaken existing assertions unless the expected behavior has genuinely changed and the reason is clear.
- Keep the regression test focused on the bug. Avoid broad fixture churn or unrelated coverage expansion.
- If the bug is flaky, make the test deterministic where possible and document the signal being locked down.
- If the bug exposes a broader class of failures, first land the focused regression path, then consider additional sibling coverage.
