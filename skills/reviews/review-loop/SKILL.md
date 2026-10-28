---
name: review-loop
description: "Use for a cross-model second opinion on a diff, branch, PR, or plan; to review, fix, and re-review until clean; and as the final review of implementation workflows."
---

# Review loop

Review a change with both models, verify what they report, fix it, and re-review until nothing actionable remains. The **counterpart** is the other vendor's model: Codex when Claude runs this skill, Claude Opus when Codex does. It catches the blind spots of the model that wrote the change. This skill coordinates: it verifies, merges, reports, and fixes, and adds no findings of its own.

/code-review owns the Standards and Spec rubric, /thermo-nuclear-review the correctness and security audit, /swarm dispatch and the counterpart route, and /principles selects the principles reviewers apply. Read [the reviewer brief](references/reviewer-brief.md) before dispatching a round.

## Authority

Inside an implementation workflow, such as /implement, /implement-spec, or a Pstack playbook, the loop applies its **fix** findings and re-reviews without asking between rounds. A standalone review request reports round 1 and waits; the user's go then runs the whole loop. Public comments, merges, and PR state changes keep their own authorizations.

## 1. Pin the target

Resolve one target: a PR, branch, commit range, or file set the user names; a plan or spec; the current branch against its stack parent or its merge-base with the default branch; or the working changes. Read the intent from the spec and tickets, the PR description, or the accepted request. List the repository's standards documents, and invoke /principles in review mode for the applicable owners.

For a code target, build the packet from this skill's directory with `node scripts/packet.ts --repo <repo>`, adding `--base <ref>`, `--since <ref>`, `--head <ref>`, or `--working` as the target needs (`--help` explains each; Bun also runs it). The packet pins immutable revisions, snapshots working changes into a commit without touching the index or stash, and lists lockfiles, binaries, and generated or vendored files while leaving them out of the diff. A bad ref or an empty diff stops here. Record the packet's size as the loop's **baseline**: the last line of `git apply --stat <diff.patch>`.

**Complete when:** the target, intent, standards documents, selected principles, and either the packet's base, head, and baseline or the plan's path are known.

## 2. Review

Round 1 is a full review by both models. A plan target gets only the counterpart's review, since the same-model passes assess code.

1. Dispatch the counterpart first, asynchronously and at full-review effort, through /swarm's counterpart route, with the brief filled in.
2. When Codex is the counterpart and the diff changes code that runs, not only prose, docs, or skill text, dispatch the **Codex correctness** pass beside it: its own asynchronous task with the full review's model, effort, and speed and the brief's Codex correctness line, under its own `clientRequestId` in T3 Code, or its own prompt and output files through the CLI. It runs beside passes the round already waits for. Retry it once on its route when /swarm's execution contract allows a retry, and take no other route, since the same-model correctness critic already covers that ground; skip it when /swarm resolves the counterpart to `fallback`.
3. Meanwhile, run both same-model passes in parallel on the packet's revisions, passing the resolved intent and standards. Skip a pass when equivalent evidence already covers this head and scope. A same-model /thermo-nuclear-review pass on an earlier head of this change, such as a /thermos run the user named, covers the correctness critic when every commit since only fixes that review's findings and a counterpart pass runs this round, since the counterpart reviews the fixed lines.
   - Invoke /code-review, with its Standards and Spec axes run by same-model critics.
   - Dispatch a same-model correctness and security critic through /swarm with /thermo-nuclear-review's rubric.

4. Collect the counterpart's reports. Every reviewer belongs to the round, so wait for each one before reporting.

When the counterpart's review fails after the route's retry and fallbacks, continue with the other passes and record it missing; label the round **single model**, with the reason, when no counterpart pass returned. A failed Codex correctness pass is a recorded gap, and the round goes on without it.

**Complete when:** every reviewer returned a terminal report or a recorded failure for the same revisions.

## 3. Verify and merge

Reviewers make false claims. Check each finding against the code at the head, or for a plan, against the plan and the code it cites: trace the path from a real input to the failure, confirm the cited rule or requirement, and check that the proposed fix fits the repository's conventions and the selected principles, since a true finding can carry a wrong fix. Drop a finding that does not hold, with a one-line reason, including a plan risk that no cited code or observed behavior supports. Agreement between reviewers raises attention, not certainty.

Group verified findings by root cause and number them; numbers continue across rounds. /code-review's own report stays separate by axis, and this grouping is the loop's report across all reviewers. Record who raised each (counterpart, Codex correctness, Standards, Spec, Correctness, a PR commenter a pass quoted, or several), its severity on the brief's scale, mapping a pass's own priorities onto it, and any severity disagreement as it stands. Give each a call:

- **fix**: in this change.
- **follow-up**: outside this change's scope; it goes in the PR description's open items.
- **skip**: with a few-word reason.

A finding the change did not cause or worsen is context, not a finding. One that nobody can reach yet, behind an off flag or an input the real configuration cannot produce, is Optional at most.

**Complete when:** every finding is verified or dropped, and each verified one has a group, a number, a severity, and a call.

## 4. Report

Lead with the round, the verdict, and reviewer counts, such as `🔴 **Blocked.** Round 1: a retry can charge twice. Codex 2 · Claude 3 · both raised 1.` The verdict is **Blocked** with any Blocker, **Needs cleanup** with only Cleanups, and **Clean** when nothing needs fixing. Then list each finding on one line, worst first: number, severity, what breaks in plain words, `path:line`, who raised it, and the call. Fold the checks, one evidence line per finding, and each dropped finding with its reason into a details block. A finding that needs the user, such as a design, scope, or product decision, also gets a short card: what breaks, for whom, and the smallest diff.

End by offering the next step: fixing and re-reviewing while findings remain, or delivering the draft PR through /pr once a round is Clean, when delivery is within the grant.

**Complete when:** the report alone shows what each reviewer found, what held up, and what happens next.

## 5. Fix and re-review

1. Apply each **fix** on the branch that owns it and run the focused checks, or edit the plan. When commits are authorized, commit each fix on its own.
2. **Cut first.** For code, rebuild the packet with `--since <round-1 base>` and the target's head option, and compare its size with the baseline. When it grew, read the growth and cut or narrow any added code that no fixed finding needs, such as a helper, option, guard, or test for a case the intent doesn't reach. Treat each cut as a fix from here on: apply, check, and commit it the same way, pass it to the next round, then measure again. Growth a fixed finding needs stays.
3. Run the next round on the delta with only the counterpart, at delta-review effort, as a new task, passing the previous findings and their fixes. For code, rebuild the packet with `--since <last reviewed head>`. The same-model passes and the Codex correctness pass run in round 1 only; the counterpart's delta review covers their ground on the fixed lines and is the refresh /code-review's completion rule asks for. For a plan, send the revised plan. Skip it when every fix was a local Cleanup or Optional item and its focused checks pass.
4. Report only what is new or still open, with the size among the checks in the details block, as `diff +120 −30 → +150 −30`.

Stop and report when a round is Clean, after three rounds, or when a finding needs the user. When a round repeats a class of finding an earlier round fixed, invoke /principle-attack-the-premise before another round. After three rounds without Clean, hand the open findings to the user; in an autonomous run, put them at the top of the PR description, report the branch as unverified, and continue. Delete the packet directories when the loop ends.

**Complete when:** a round is Clean, the user has fixed, deferred, or dropped every remaining finding, or the round cap is reached with the open findings reported; and every line of growth past the baseline belongs to a fixed finding or was cut, every applied fix is committed when commits are authorized, and the packet directories are gone.
