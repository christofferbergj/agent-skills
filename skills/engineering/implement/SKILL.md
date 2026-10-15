---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

# Implement

1. Read the requested spec or tickets and state their identity, accepted scope, and test seams. Resolve the project's shared artifacts through /domain-modeling; consume them without reopening settled decisions. Complete when the work and its done predicate are grounded in the existing source of truth.
2. Implement vertical slices through /tdd where a useful test path exists. Reuse agreed seams and repository checks. Use /pstack-swarm only for useful bounded delegation, with isolated writers and one coordinator for canonical docs. Complete each slice when its observed behavior satisfies its acceptance criteria.
3. Reconcile accepted domain changes through /domain-modeling and inspect the full diff. Run relevant checks and invoke /code-review for the final artifact, reusing valid review evidence supplied by the caller. Resolve actionable findings; when a fix changes the reviewed artifact, refresh the affected review coverage and checks. Complete when implementation, docs, acceptance criteria, and review findings agree at the delivered revision or a gap is explicit.
4. Commit the scoped result when authorized and prepare a draft PR when requested or part of the existing grant. Invoke /pr for its description. Keep tracker closure tied to the project's actual completion boundary. Complete when the result is reviewable and delivery state is truthful.
