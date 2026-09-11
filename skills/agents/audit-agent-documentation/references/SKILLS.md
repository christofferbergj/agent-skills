# Skill assessment

Apply these checks whenever a skill is in scope, including skills that do not read or write agent documentation.

## Discovery and dependencies

- Keep the description concise and specific to the actual task. For automatic selection, front-load the capability and distinct trigger branches; remove broad topic matches and synonymous triggers. Add exclusions only for likely misrouting.
- Compare neighboring descriptions for overlapping or contradictory triggers. Check an intended request and a nearby request that should not activate the skill. Consider how shortened descriptions affect selection in the target environment.
- Preserve the intended invocation mode and keep frontmatter and agent metadata consistent. Verify how the target agent discovers and invokes the skill rather than assuming metadata behaves identically across ecosystems.
- Check required metadata and directory naming against repository conventions and the target ecosystem. Account for disabled configuration and duplicate names when resolving selection.
- Require another skill or tool only when the workflow needs it. Verify availability, invocation support, and documented installation requirements. Route shared guidance through its owner instead of copying it.

## Instructions and resources

- Keep shared purpose, essential constraints, and branch selection in the entry point. Route substantial mode-specific procedures, examples, and schemas to references with explicit read conditions. A short, self-contained skill needs no additional routing layer.
- State outcomes and decision criteria for open-ended work. Retain fixed sequences, scripts, and exact parameters where deviation creates a concrete correctness or safety problem.
- Preserve completion criteria that distinguish success from partial work within the requested scope. Assess model-dependent steering using the rubric's judgment criteria.
- Inspect resource callers before removing or moving files. Verify linked resources and scripts in their documented working directory; retain assets and deterministic helpers when they serve the workflow.

Before accepting a routing change, account for intended selection, nearby non-selection, required references, and dependencies. Record whether this was checked through actual agent behavior or a static walkthrough.
