---
name: pstack-reflect
description: "Use for Pstack reflection on corrections in the current conversation and reviewable improvements to source skills."
---

# Reflect

1. Use the current conversation, not a repository-wide history sweep. Invoke /pstack-recall for scoped session discovery only if the host cannot provide the active conversation. Do not substitute the newest unrelated session for this one. Complete when the reviewed conversation and known evidence gaps are explicit.
2. Use /pstack-swarm for independent judgment, tooling, and divergent-review passes, adapting count to scope and budget. Supply the matching [judgment](references/judgment-reviewer.md), [tooling](references/tooling-reviewer.md), and [divergent](references/divergent-reviewer.md) prompts. Reviewers may follow cited evidence through read-capable tools. Complete when the lenses return proposals or a disclosed missing pass.
3. Synthesize with [the synthesizer prompt](references/synthesizer.md). Prefer architecture, types, lint, tests, or deterministic checks over another instruction. Route Accepted, Rejected, and Backlog explicitly. Complete when each proposal has evidence, ownership, routing, and a reason.
4. Present the proposals for review. Prepare skill changes in the agreed source repository, never by silently patching installed snapshots or the current run's rules. Apply only an approved subset within its grant. Backlog stays a local proposal unless tracker filing is authorized. Complete when every proposal is approved and applied, deferred, or rejected with a reason.
5. Validate affected source skills and report accepted edits, proposed backlog, rejected findings, and unverified behavior. Complete when reviewed source changes and installation status are clear.
