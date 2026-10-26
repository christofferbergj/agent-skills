---
name: no-comments
description: "Use for Pstack comment review, unnecessary narration, or suppressions that conceal code problems."
---

# No comments

Spawn Comment Sicko. Act on accepted findings.

Defer to Comment Sicko's fresh perspective.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree. Pass the repository's documented comment conventions with the scope.

## Steps

1. Use /swarm to spawn Comment Sicko with [its prompt](references/comment-reviewer.md). Pass the scope. Pick each subagent's reasoning level and speed for the job, per /swarm. Do not restate its rules. Complete when its report returns.
2. Inspect its report and diff. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. Before accepting thin `IMPORTANT` or `do not remove` kills or keeps, run /how or /why on their symbol. If a kill is ambiguous, do not restore. If a keep is refuted or still ambiguous, delete it. Revert and rerun one rejected report with the failure named. Reject a second, report it open, and fail /no-comments. Complete when every finding is accepted, rejected, or restored with its reason.
3. Fix trivial accepted flags directly by deleting a dead path, dropping a parameter, or using the real API. If any fix needs a shape, run /architect once for the accepted set and surrounding code. Stop at the sketch. Architect shapes. Step 4 implements. Complete when trivial flags are fixed and any needed sketch exists.
4. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. /principle-fix-root-causes and /principle-redesign-from-first-principles guide intent only. Neither authorizes widening the fence nor fixing instances outside it. Never bolt on symptom guards. Complete when every accepted flag is fixed in scope or reported open.
5. Constraint comments say `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. Offer the cheapest in-scope type, runtime, test, or CI lint. Wait for interactive approval. Unattended and eval require caller pre-approval. If approved, encode then delete. Otherwise delete, report the constraint open, and sketch out-of-scope work. Complete when every constraint comment is kept, encoded, or reported open.
6. Report the deletion count, restored comments, reruns, architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.
