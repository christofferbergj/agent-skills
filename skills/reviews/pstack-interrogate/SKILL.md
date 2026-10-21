---
name: pstack-interrogate
description: "Use for Pstack adversarial review of a concrete diff or contested design with independent criticism."
---

Invoke /domain-modeling to resolve and read the invoking project's configured artifacts. Read-only investigations and reviews report documentation drift without edits; creation or implementation reconciles accepted model changes through that owner.

# Interrogate

Spawn one reviewer per configured model to adversarially review code changes. The adversarial signal comes from model diversity, not assigned personas. The deliverable is a synthesized verdict. Do NOT auto-apply changes.

1. Scope. Identify what to review from context. Complete when reviewers receive the same scope.
   - If the user points at specific files or a diff, use that.
   - If on a feature branch, run `git diff main...HEAD` (or the appropriate base branch) for the full changeset.
   - If the user's message references recent work, gather the relevant files.

   Package the diff or file contents with any surrounding context files the reviewers need to understand the code, including the originating spec and relevant tests.

2. Intent. Before spawning reviewers, state the intent in one clear paragraph from the user's message, commit messages, the PR description if one exists, and the code. If you're unsure about the intent, ask the user before proceeding. Complete when the intent paragraph is stated.
3. Spawn reviewers. For a code diff, invoke /code-review for Standards/Spec coverage unless equivalent evidence already covers the current artifact; the adversarial lens adds the remaining coverage and keeps its evidence distinct. Use /pstack-swarm to launch all reviewers at once, one per configured model, labeled Reviewer A, B, and so on, preferring cross-vendor criticism when available. Fill in [the reviewer prompt](references/reviewer-prompt.md) the same way for every reviewer with the stated intent, the diff or file contents, [the rubric](references/rubric.md), and [the code-quality lens](references/code-quality-review.md). Reviewers inspect directly, without edits, posting comments, or further delegation. Complete when each reviewer returns evidence-based findings or a stated failure.
4. Synthesize. As results come back, build a unified picture. Parse every reviewer's findings. Merge findings that describe the same issue differently, and note which models raised each one. Findings two or more models raised independently are the highest signal. Read a lone model's finding, but weight it accordingly. Note disagreements. If one model flags something and another explicitly says the opposite, that is context for the verdict. Verify each candidate finding against the code; agreement raises the signal but is not proof. Preserve the shared Standards/Spec reports as separate axes; their findings do not disappear into this lead's ranking. Complete when every finding is verified, merged, and attributed.
5. Lead judgment. You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator. Read [the lead-judgment framework](references/lead-judgment.md). Put every finding in one of four buckets, with the model(s) that raised it and a one-line rationale. Complete when every finding has a bucket.
   - **Act on**. Real issues affecting correctness, security, or maintainability given the actual goals. They would block a real PR.
   - **Consider**. Legitimate, but you're not sure they outweigh the cost of addressing them now. Worth the user's attention.
   - **Noted**. Technically valid but not actionable. Context-dependent, premature optimization, or low-impact at this stage.
   - **Dismissed**. Wrong, nitpicky, or missing context, with a brief reason.

## Output Format

### Intent

> [The stated intent paragraph from step 2]

### Reviewers

- Reviewer [label]: [model name], [N findings] (one bullet per reviewer)

### Act On

[Each: description, which models raised it, why it matters.]

### Consider

[Each: description, which models raised it, the tradeoff.]

### Noted

[Brief list.]

### Dismissed

[Each with a brief rationale.]

### Agreement Map

[Where models agreed and diverged, and what that pattern tells us.]
