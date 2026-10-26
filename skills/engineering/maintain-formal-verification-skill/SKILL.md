---
name: maintain-formal-verification-skill
description: Bring a project's formal verification back in line with changed code and distinguish drift from defects.
disable-model-invocation: true
---

# Maintain a formal verification skill

Maintain the verification artifacts and project-local instructions, preserving the property's intended promise. Edit only models, harnesses, property files, and verification instructions; change product code only within an existing grant. When a property fails on the current code, report the failure and keep the property and model as the code requires; weakening either to pass hides the finding. Use isolated scratch copies for deliberate faults.

Give each check one outcome:

- **in sync:** no change since the sync commit alters what the check describes, and it passes.
- **updated:** the verification now describes the changed code, and it passes.
- **bug:** the verification describes the current code, and the code breaks the property. This is a code finding, not drift.
- **blocked:** the check could not be brought back in line or run; name the reason.

A check can be both updated and bug.

## 1. Resolve the checks and comparison

Find project-local skills that run a model checker, prover, or code-level verifier against named code, including drafts and generated-input fallbacks produced by /create-formal-verification-skill. Read the user's named target, or every matching skill. If none exists, tell the user to invoke /create-formal-verification-skill and stop this path. Preserve the distinction between generated-input testing and formal proof.

For each check, record the property, covered files and functions, source correspondence, bounds, assumptions, tool version, command, and last confirmed sync commit. Resolve the target commit and included uncommitted or untracked changes. If a sync commit is absent, use the last commit changing the verification as a provisional baseline and disclose the uncertainty; unavailable history leaves the comparison blocked.

Complete when every check has a reproducible target and comparison baseline, or a concrete prerequisite gap.

## 2. Establish the old result and code changes

Run each check before editing and preserve the output. Read every covered-code change and commit since its sync point, including included working changes. Follow moved or split functions and new writers to the guarded state. Check claimed irrelevance against the model or harness.

Classify each relevant change: no semantic effect, stale source correspondence, an intentionally changed promise with cited evidence, or a possible defect. A passing old model alone proves no correspondence to today's code.

Complete when every covered-code delta has a disposition and each check has a before result or an execution gap.

## 3. Update from the code

Invoke /writing-for-agents for instruction changes. Update models, harnesses, properties, and verification instructions from source before rerunning. Keep each indivisible model step traceable to an indivisible code operation. Change a property only when evidence establishes an intended promise change; record its old wording, new wording, and that evidence. Preserve bounds unless they no longer fit, and explain any reduction.

Complete when each update has source correspondence and a reason independent of whether it passes.

## 4. Rerun and prove the updated check

Record a pass within stated bounds, a counterexample, or an inconclusive result. Replay counterexamples against the real code. An impossible step indicates a modeling defect; fix the verification and record what was wrong. A feasible violation indicates a code defect: tell the counterexample as a sequence of steps in the code's names, state its harm in one sentence, and name the introducing commit when established. When a cheap reproduction against the real code shows the defect, add it to the report as evidence, outside product code. A timeout or incomplete exploration is inconclusive.

In an isolated scratch copy or worktree, make a realistic semantic fault in the covered code and run the documented check. Confirm that it detects the violation rather than only a changed hash or syntax error. If the original code already fails, the control must produce a distinguishable counterexample; another nonzero exit is insufficient. Restore the scratch code and rerun the updated check, reproducing this step's unmutated result: passing, or failing only on the counterexamples already recorded. An unrelated failure does not establish restoration. Clean owned scratch state while preserving evidence.

Complete when the check has a conclusive result, a semantic failing control, restored behavior, and cleanup evidence. Otherwise preserve useful model-only results and label readiness as draft with the missing proof.

## 5. Record freshness and hand off

For each check, update its covered code, commands, bounds, assumptions, and source-correspondence evidence. Advance its sync commit only after correspondence is established and step 4's conclusive rerun, semantic control, restoration, and cleanup are demonstrated for that exact committed snapshot. A preserved code counterexample is a conclusive finding; it does not claim the property passed. Blocked or inconclusive checks retain their prior sync commit. Record reviewed working changes and their fingerprints separately; a commit cannot stand for uncommitted content, whose committed freshness remains pending.

Follow the updated skill once as the next agent would. Report for each check its outcome, readiness as ready or draft, compared revisions and working changes, each verification edit with its reason, the rerun result, control and restoration evidence, each code defect, and remaining coverage, including new code the check should cover. Say which failures were verification drift and which were code defects; for a check that passed before the update and fails after, say the old pass described stale code. Put verification changes in a change separate from any product fix.

Complete when every check has an outcome with evidence or a named gap, retained or advanced freshness is justified, and the user can distinguish a code finding from verification drift and an executable skill from a draft.
