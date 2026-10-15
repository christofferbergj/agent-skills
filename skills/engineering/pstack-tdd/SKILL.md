---
name: pstack-tdd
description: "Use in a Pstack bug fix when a cheap regression test can demonstrate failing-before and passing-after behavior."
---

# Pstack bug-fix evidence

1. Identify the broken and intended behavior and a cheap executable regression path. Reuse an agreed public seam; invoke /tdd for the shared red/green and behavior-test discipline. Complete when the reproduction can distinguish this defect or the unavailable test path is explicit.
2. Preserve the failing-before command, revision, and result, then fix the defect and rerun the same regression. Do not create a broad brittle harness for a small reversible fix. Complete when observed before/after behavior and relevant nearby checks support the fix.
3. Report the original symptom, causal change, evidence, and any missing test or live-surface coverage. Complete when no skipped check is presented as a pass.
