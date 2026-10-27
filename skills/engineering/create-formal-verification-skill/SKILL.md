---
name: create-formal-verification-skill
description: Generate a project-local skill that formally verifies one consequential property and detects relevant code changes.
disable-model-invocation: true
---

# Create a formal verification skill

Verify one property where a defect would harm users and tests rarely reach the failing case. Leave a project-local skill that lets the next agent check a relevant change without learning the verification language. This task generates verification artifacts. Report product defects separately and change product code only within an existing grant.

## 1. Choose the property from the code

Answer from the codebase, and ask the user only what you cannot observe. Start with the user's named area or bug. Otherwise inspect the repository for a consequential promise involving concurrency, retries, state machines, parsing, unsafe code, or another difficult case. Choose the strongest useful target rather than the easiest demonstration. State the property and the harm from violating it in one plain sentence each.

Complete when one target has source locations, a precise property, and an observable failure condition.

## 2. Let the question choose the tool

Inspect available tools and the repository's constraints. Choose a model checker, proof assistant, SMT-backed verifier, or other suitable tool at the lowest useful cost. Event ordering often suits a small design model. Memory safety, overflow, or data-structure invariants can suit a verifier that checks the code. If no verifier supports the language, say so and test the real code with generated inputs; distinguish that evidence from a formal proof. A property required at every size can need a proof. For concurrent or distributed designs, consider TLA+ alongside tools already used by the repository.

Prefer existing tools or a project-local installation developers can rerun. Record its reproducible version, installation command, verification command, and expected cost. Use current primary documentation for any unfamiliar tool. Explain why the tool answers this question.

Complete when the chosen tool runs locally. If a required tool cannot run, skip to step 6 and hand off a draft naming the missing prerequisite and unverified scope.

## 3. Verify the property and its limits

Make every model or proof element traceable to source. An indivisible model step must correspond to an indivisible operation in the code. Explain how code changes reach the check, such as verification of the code itself, generated models, or trace-conformance checks. A source-drift gate detects edits but does not establish semantic correspondence. State bounds, environmental assumptions, fairness assumptions where relevant, and omitted behavior. A pass establishes the property only within that scope.

Run the check and classify the outcome as a pass within its stated scope, a counterexample, or inconclusive. A timeout or incomplete exploration is inconclusive.

Show the property failing on a deliberately broken variant, such as a removed check or reordered step. When the original check already fails, a control must expose a distinct counterexample; another nonzero exit is insufficient. Explain each counterexample as a short sequence using the code's names. Keep current defects as findings rather than weakening the property until it passes.

If a conclusive result or distinguishable failing control cannot be obtained, skip to step 6 with a draft and the unresolved check.

Complete when the real check has a conclusive recorded result, each claimed property has a distinguishable failing control, and every modeling assumption is stated.

## 4. Generate the project-local skill

Invoke /writing-for-agents for the generated instructions and skill mechanics. Follow the repository's skill location and invocation conventions. Use a lowercase name, a description that identifies relevant changes, and real paths and commands without placeholders.

The generated skill must let a new agent identify whether a change touches the verified property, run the check, distinguish a code defect from a modeling error, and update the verification after an intended change. Include the property, covered files and functions, source correspondence, tool version, command, expected outcomes, bounds, assumptions, evidence location, and cleanup. Record the target committed snapshot and included working changes with their fingerprints. Leave a new check's sync commit pending until step 5 validates it; preserve any existing confirmed baseline. Add a concrete drift check or workflow trigger that requires reviewing the verification when its guarded code changes.

If the check is a TLA+ model, tell the next agent to read every result with /statechart. It shows each invariant violation the checker finds as its shortest path in plain words. When the check passes, /statechart draws a chart of how the system moves between states. Refer to /statechart by name. Its commands, options, and file paths change between releases and machines, so copy none of them into the generated skill or its scripts.

Complete when the generated skill and its supporting artifacts contain every instruction needed to rerun and interpret the check.

## 5. Prove the generated skill before handoff

Follow the generated skill as a new agent would. Use an isolated scratch copy or worktree to break the property in the guarded code. Confirm that the documented verification detects the semantic violation, using step 3's failing-control rule. If the check misses it, repair the verification or its connection to the code, never the scratch fault. A drift-only failure is insufficient. If semantic detection cannot be established, restore the scratch copy, preserve any model-only proof, and hand off the generated skill as a draft at step 6.

Restore the scratch copy, rerun, and confirm the original result: passing, or failing only on the findings already recorded. Preserve the evidence after cleanup.

Record the sync commit only after source correspondence, a conclusive rerun, semantic control, restoration, and cleanup are established for that exact committed snapshot. A preserved counterexample is a valid conclusive finding, not a property pass. Record reviewed working changes separately; their committed freshness remains pending. A draft retains its prior confirmed baseline or leaves a new sync commit pending.

Complete when a realistic code mutation fails the documented check, restoration reproduces the original result, and owned scratch state is cleaned. A skill that was never run remains a draft.

## 6. Hand off

Report the checker's outcome separately from the generated skill's readiness. A pass establishes the property within its stated scope; a counterexample is a finding; an inconclusive result establishes neither. The generated skill is ready only after its rerun, semantic negative control, restoration, and cleanup pass. Otherwise label it a draft, including when only a design model has been proved without code conformance.

Return the generated skill when available, the property, tool choice, bounds, assumptions, command, results, counterexamples, and remaining coverage in plain words. For a draft, identify the missing prerequisite or proof and next check. Tell the user to invoke /maintain-formal-verification-skill after covered-code changes that skipped the verification. Suggest a second target only when the investigation found a close one.

Complete when the user can distinguish the check's outcome and scope, any findings, and a ready skill from a draft with a concrete next check.
