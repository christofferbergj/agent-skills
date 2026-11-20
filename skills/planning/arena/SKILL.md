---
name: arena
description: "Use for Pstack design or artifact bakeoffs, blind judging, base selection, and grafting useful alternatives."
---

# Arena

Open a todolist with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on _this_ task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners from /swarm's `arena-runners` panel, by default Fable at `high`, Opus at `high`, and Gemini 4 Neon at `xhigh`, seated as its execution contract says: Gemini through T3 Code's Antigravity provider on both hosts, Fable and Opus as native subagents in Claude Code or through the Claude counterpart in Codex. An `auto` or `inherit-parent` entry is the parent model. If a seat cannot run or the host rejects its model, recover it as /swarm's execution contract says for panels and rejected models. Spawn more for multiple design directions, and repeat one model when the work is generation-bound, not judgment-sensitive. Pick each subagent's reasoning level through /swarm.
4. Give each candidate its own output location (a git worktree where possible, otherwise `/tmp/arena-<slug>/candidate-<n>/`), per /principle-separate-before-serializing-shared-state.

## Phase B: Fan out

Spawn all N subagents at once, in the background, through /swarm, each with the task, the path to the shared grounding, its own output path, and instructions to produce the artifact and a short rationale naming the alternatives it considered and what it rejected.

If a candidate produces no output, proceed with N-1 and note the dropout.

## Phase C: Cross-judge

After all Phase B candidates complete, spawn one readonly judge subagent from upstream's pool, Opus at `high`, then Gemini 4 Neon at `xhigh`, each moved by the budget. The judge is never from the parent's vendor, with Fable counting as Claude, so it is Claude Opus on the counterpart under Codex, then Gemini 4 Neon when Opus cannot run, and Gemini 4 Neon under Claude Code, through /swarm's T3 route to the Antigravity provider. When Gemini cannot run under Claude Code, judge on the Codex counterpart at Gemini's effort instead. Take only cross-vendor routes, never the same-vendor critic. When no judge in that order can run, a counterpart that resolves to `fallback` included, skip the judge, pick the base alone in Phase D, and say so. While you read in Phase D, the judge scores each candidate, by path label, on each rubric criterion and recommends a base.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per /principle-laziness-protocol.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per /principle-redesign-from-first-principles, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact like any other output, per /principle-prove-it-works. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
