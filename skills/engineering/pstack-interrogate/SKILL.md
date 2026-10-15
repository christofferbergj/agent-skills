---
name: pstack-interrogate
description: "Use for Pstack adversarial review of a concrete diff or contested design with independent criticism."
---

# Interrogate

1. Resolve a concrete diff or artifact and its fixed base. Read the request or originating spec, surrounding contracts, and relevant tests. Complete when reviewers receive the same scope and user intent.
2. Use /pstack-swarm to dispatch independent reviewers with [the reviewer prompt](references/reviewer-prompt.md), [rubric](references/rubric.md), and [code-quality lens](references/code-quality-review.md). Prefer cross-vendor criticism when available. Reviewers inspect directly, without edits, posting comments, or further delegation. Complete when each pass returns evidence-based findings or a stated failure.
3. Read [the lead-judgment prompt](references/lead-judgment.md) and combine the completed reports. Verify each candidate finding against the code, deduplicate it, and calibrate impact without treating agreement as proof. Complete when every reported issue is actionable or rejected with a reason.
4. Apply pragmatic lead judgment. Return Intent, Reviewers, Act on, Consider, Noted, Dismissed, and Agreement map as useful. Distinguish correctness defects from preferences and identify missing passes. Complete when the user can decide what to fix from evidence; a review request alone does not authorize fixes.
