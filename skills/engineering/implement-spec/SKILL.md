---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code."
disable-model-invocation: true
---

# Implement a spec

Implement the entire spec on one integration branch, treating its tickets as a dependency graph. One coordinator owns merges, canonical project artifacts, and tracker updates.

1. Read the full spec, tickets, blocking edges, existing branch state, and configured tracker. Reuse the current source of truth; missing tracker configuration can use local artifacts until external publication is authorized. Invoke /domain-modeling to resolve project docs and /pstack-principles for implementation before code changes. Complete when scope, accepted seams, branch base, ready frontier, and any declared migration verification units are explicit and the graph has no unresolved cycle.
2. Create or reuse an owned integration branch. Gather bounded shared exploration once when useful. Invoke /pstack-swarm to dispatch ready tickets within host capacity, each writer on its own worktree based on the verified integration revision. Explicitly delegate /tdd, /pstack-principles for implementation, resolved principle instructions, accepted design decisions, and acceptance criteria. Inspect a wrong worktree base and preserve its changes before repair; never reset unknown work. Complete when every running ticket has an owner, base, applicable principle owners, and evidence contract.
3. Inspect each terminal result, merge accepted changes serially, and update the frontier only after the declared ticket or migration-phase checks pass. For a coupled migration, use /pstack-principle-migrate-callers-then-delete-legacy-apis for the unit's completion and dependent-work gates. Writers return proposed domain edits; reconcile them through /domain-modeling before canonical docs change. Use the existing tracker graph and link execution evidence instead of duplicating tickets. Complete each ticket only at its declared verification boundary with its integrated acceptance evidence.
4. When all required tickets are integrated, recheck /pstack-principles for verification, run relevant whole-spec checks, and invoke /review-loop once at the final revision. Fix actionable findings and recheck affected behavior. Preserve equivalent review evidence only when it covers this exact artifact and both axes. Complete when the entire spec is demonstrated against the actual artifact or the validated subset and remaining blockers are explicit.
5. Deliver a draft PR by default when authorized, using /pr. Keep readiness, ticket closure, and merging at their explicitly authorized project boundaries; code on an unmerged branch is not automatically shipped. Use native worktree archive/removal for owned managed checkouts after inspecting preservation needs. Complete when all workers are accounted for, evidence survives, and no unknown work is removed.
