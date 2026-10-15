# Multi-phase or multi-PR plan

Own the executable plan. This request produces a plan, not its implementation.

1. Reuse any accepted spec, ticket graph, and configured domain artifacts; link to their authoritative locations instead of creating duplicate specs or tickets. Inspect the repository and settle empirical forks through Prototype. A genuinely trivial change can skip a plan with its reason. Complete when the intended behavior, constraints, and relevant evidence are concrete.
2. Ground independent slices through /pstack-swarm where useful and select the execution path: Autopilot full only with explicit merge authority, Autopilot stack for a reviewed stack, or Orchestrate for a standing program. Complete when ownership, dependencies, and authority are clear.
3. Use [the plan template](../references/plan-template.md) from this skill's own directory. Choose coverage lanes from actual surfaces, risks, and budget. Every lane names a scenario, evidence artifact, and pass predicate. Include applicable unit, live, and performance checks or a concrete reason for omission. Complete when every PR is an independently verifiable unit and its dependencies are explicit.
4. Run `node scripts/check-plan.mjs <plan.md>` from this skill directory and fix reported structural or evidence gaps. Complete when the plan passes the checker without weakening its actual acceptance criteria.
5. Hand back the plan, dependencies, human gates, evidence, and checker result. Complete when the user can approve execution against an auditable artifact. Start execution only under the user's go.
