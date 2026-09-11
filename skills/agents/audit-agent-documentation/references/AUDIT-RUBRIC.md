# Agent documentation audit rubric

Apply this rubric to the declared audit scope during diagnosis and final review. It is a decision aid, not repository authority. Explicit user intent and verified project requirements govern the change set.

## Authority and contract integrity

- Trace each documentation node and edge to an owner, scope, consumer, and source of truth.
- Read the effective stack in precedence order instead of reviewing files in isolation.
- Identify which setup outputs, label vocabularies, issue workflows, domain routes, and generated instructions have consumer requirements or encode explicit project choices.
- Preserve exact values and repeated constraints when consumers depend on them.
- Distinguish those contracts from historical workarounds, recommendations, and incidental prose. Being consumed by an agent does not make every sentence an immutable requirement. Verify the behavior a constraint protects before preserving, narrowing, or removing it.
- Resolve a conflict from repository evidence only when ownership and intent are clear. Otherwise classify it as **Conflict**, quote both requirements, describe the consequence, and keep it out of the edit set.

The governing test is: "Would this change preserve every verified project requirement while making the effective stack more accurate or useful?"

## Correctness and freshness

Check that:

- Commands exist, accept the documented flags or output fields, and run from the stated directory.
- Inheritance, context pointers, and consumer routes resolve from every scope that relies on them.
- Discovery matches the intended agent environment. Check active configuration, launch directory, override and fallback filenames, and size limits before claiming an instruction is loaded. Record configured behavior separately from behavior observed in a running agent.
- Paths, package names, workspaces, owners, and architecture descriptions match the current repository.
- Consumer-required names, headings, fields, values, and conditional sections match their owning contract.
- Generated-file instructions point to the generator and editable source, not merely to a prohibition.
- External service or repository-state claims are checked live when safe and relevant.
- Examples still demonstrate the intended workflow rather than a superseded one.
- History supports surprising guidance that may encode a deliberate decision.

Treat the environment as a source of truth. Prose that merely caches a cheap lookup from manifests, configuration, directory structure, or `--help` output earns removal unless the copy materially improves the workflow.

Prefer verified absence to invented detail. If a source, environment, or live check is unavailable, state what could not be established and narrow the edit accordingly.

## Context value and progressive disclosure

Agent context is an instruction budget. Give always-loaded guidance only the facts and decisions that repay that cost.

### Root guidance

A useful root entry point usually contains:

- A one-line repository purpose and its global boundaries.
- Required toolchain choices that manifests and configuration do not encode.
- Non-standard setup, formatting, validation, and test commands.
- Repository-wide constraints and non-obvious gotchas.
- Precise routes to deeper guidance.

Treat these as candidates, not a required template. Route useful branch-specific procedures to narrower documentation; remove prose filesystem tours and facts that merely repeat cheap lookups.

### Scoped guidance

Place an instruction in a nested scope when it applies throughout that scope and would distract elsewhere. In a monorepo, keep shared navigation and tooling at the root and package-specific purpose, stack, and conventions in the narrowest reliable scope. Favor stable capabilities, boundaries, and domain concepts over volatile inventories of files. Retain a short root-level pointer when agents need to discover the scoped material.

### Routed reference

Move detailed procedures, lookup tables, examples, and volatile reference behind a context pointer whose wording names the material and the branch that requires it. Keep a required rule inline when routing would make compliance unreliable. Prefer authoritative source or code links over prose that mirrors them.

Progressive disclosure succeeds when the common path stays legible and every specialized path remains discoverable when it becomes relevant.

## Usefulness and actionability

Every retained instruction should change likely agent behavior. Look for:

- A concrete trigger, decision, command, invariant, or completion condition.
- Enough context to select the right branch without guessing.
- A positive target: what the agent should do and where it should repair a problem.
- Exact hard guardrails only where safety, data integrity, or workflow contracts require them.
- Rich repository references that let the agent inspect current truth.

Treat behaviorally inert instructions (**no-ops**), stale **sediment**, vague encouragement, generic software advice, obvious filesystem facts, and oversized example sets as removal candidates. Repair, route, merge, or remove them unless repository evidence shows they are load-bearing.

## Environment improvements

Look beyond prose edits when the evidence points to a stronger environmental fix:

- **Navigation** — add or sharpen a context pointer when agents repeatedly struggle to find an authoritative source.
- **Automated checks** — move mechanically enforceable rules into repository-owned validation when a safe check can supply the same contract and repair path.
- **Implementation versus review** — keep implementation context lean; route coding standards to review or validation surfaces when implementers do not need them during exploration.
- **Information access** — preserve or add precise routes to logs, issue trackers, domain docs, and read-only service data that a workflow requires.
- **Tool economy** — replace a documented expensive lookup with a stable script or focused command only when current evidence shows recurring cost.

Keep a short discovery pointer when moving a contract out of prose would otherwise make it invisible. Propose changes to tooling or configuration outside the authorized documentation scope as follow-up work.

## Internal consistency and scope

Compare guidance as merged for representative work:

- Root plus each scoped `AGENTS.md` or equivalent.
- Agent entry point plus every required routed document.
- Skill trigger plus its steps, references, and repository setup contract.
- Canonical instruction plus each ecosystem-specific discovery adapter.

Check terminology, commands, precedence, ownership, and completion criteria. Short repetition can be a deliberate scope anchor when independent automatic loading makes the constraint materially more reliable; duplicated explanations and mutable facts should have one source.

Use the coverage boundary established by the audit. For multiple workspaces or nested scopes, follow [MONOREPO-GRAPH.md](MONOREPO-GRAPH.md).

## Judgment for capable agents

Judge steering against the models and agent environments that will consume it. An instruction redundant for one model may still help another. Treat claims about default behavior as hypotheses; use representative runs when removing model-dependent guidance would materially affect reliability, and record untested assumptions.

Check whether instructions cause unnecessary work or premature stopping:

- **Reading scope:** Replace unconditional document stacks and repository tours with task-specific read conditions. Retain mandatory reads when an invariant applies to every task in that scope.
- **Execution detail:** State outcomes and decision criteria where several approaches are reasonable. Preserve fixed procedures for fragile operations with a concrete failure mode.
- **Approval boundaries:** Identify the action and actual authority requiring approval. Separate preparation from the consequential action, respect authorization already given, and continue independent authorized work. Preserve real release, ownership, safety, and data-integrity boundaries.
- **Completion:** Define the requested result, relevant validation, and stopping condition. Flag review stops after an initial implementation when the request authorizes finishing. Persistence must remain within the requested scope and permissions, with bounded retries for risky or external actions.
- **Verification cost:** Separate required project gates from generic reminders to test. Match checks to changed behavior; broaden or repeat them only for new changes, failures, or unresolved concerns. Retain non-obvious test setup and environment constraints.

Where evidence confirms that a local workflow is isolated and disposable, document that fact and the permitted repair loop. Never infer production isolation from a command name or turn a past failure into a universal approval requirement.

Prefer a narrow correction supported by observed behavior. Stronger adjectives and additional steps need the same evidence as the instructions they replace.

## Finding classifications

Give each finding one disposition:

- **Keep:** Correct, useful guidance or a verified contract.
- **Add:** A verified missing invariant, route, or repair path.
- **Repair:** Useful intent with incorrect facts, vague wording, or broken discovery.
- **Narrow:** Valid guidance belongs in a smaller scope.
- **Route:** Conditional detail belongs behind a precise pointer.
- **Merge:** Repeated meanings need one authoritative source.
- **Remove:** Obsolete, contradicted, or behaviorally inert guidance.
- **Conflict:** Authorities disagree and evidence cannot resolve the choice.
- **Upstream:** The owning source or refresh path is outside the task's authority.

## Decision quality

Grade a proposed change with these questions:

1. **Evidence:** What current repository or live evidence supports it?
2. **Behavior:** Which likely agent action becomes more correct?
3. **Scope:** Is this the narrowest place that reliably carries the rule?
4. **Authority:** Who owns the content and how is it meant to change?
5. **Consistency:** What other instruction stacks or consumers does it affect?
6. **Durability:** Will it survive ordinary repository evolution?
7. **Discoverability:** Can the intended agent reach it at the right time?
8. **Verification:** How will the changed route or claim be exercised?

An edit earns its place only when these answers are concrete. A style-only rewrite, speculative cleanup, or unresolved ownership change stays out.

## Evidence boundary

This rubric is a packaged synthesis, not repository authority. Treat current repository evidence and applicable guidance as truth. Revisit external source material only when the user requests a fresh source review or a claim cannot be resolved locally; identify exact source gaps instead of substituting memory.
