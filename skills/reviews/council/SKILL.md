---
name: council
description: Trigger this if the user says 'council'.
---

# Council

Before an audit, address outstanding PR comments, fix known issues, and run
relevant checks. Give council the updated implementation; do not defer known
fixes until reviews return. If the user wants to discard the implementation
and explore new ideas, skip fixes to code being replaced.

Bring in one delegate per model maker to help with the user's request, usually
for review or feedback. Use one strong model from each maker the session can
reach, at high reasoning effort. If the user's instructions name council
members, use those. Otherwise pick each maker's flagship in daily use, for
example Claude Opus and GPT Sol, which is not always its newest model.

In T3 Code, call `orchestrator_capabilities` without `search`, since a search
filters every provider's list. A named member runs on the provider that lists
it. Otherwise take every provider with `canRunChildTask: true`, and make its
first listed model its member: the top of its model list in T3 Code, which the
user can reorder there, decides over model names. Seat one member per maker,
the company a model's id names, such as `claude-` for Anthropic or `gpt-` for
OpenAI. Instances of one driver count once, chosen as /swarm's T3 route
chooses; when two providers' members share a maker, keep the maker's own
harness, such as Codex for OpenAI. Start every member in parallel through
/swarm's T3 route. Elsewhere, seat /swarm's panel: the session's model and the
counterpart.

On every route, pass each member's model and `high` effort. A Codex member
takes only its `serviceTier` from /swarm's `review-full` target in Claude Code,
or its `judgment-and-prose` target in Codex. If fewer than two makers are
reachable, or a member is unavailable, report it instead of substituting. A
member is unavailable when it still fails after its route's one retry, or when
its Codex target is `fallback`; take none of /swarm's other routes or models
for it.

Give each delegate the request and relevant context, and for a code review the
proof and report lines of /review-loop's reviewer brief. For review or
feedback, keep their work read-only. Collect their responses, verify each
finding as /review-loop's Verify and merge step does, and summarize the useful
findings, disagreements, and recommended next steps.

For a code review, ask each delegate for a score out of 10.
Count each full review pass as one round.
A fresh review after fixes starts a new round.

If the work ends in a pull request, put the results in the PR description.
Put this section right after the description's Evidence section:

```markdown
## Council review

Rounds: 2

| Delegate    | Round 1 | Round 2 |
| ----------- | ------- | ------- |
| Claude Opus | 7/10    | 9/10    |
| GPT Sol     | 8/10    | 10/10   |
```

If a delegate gives no score, write `no score`. Do not invent one.
If the PR is open, edit the description. Do not post a comment for this.
If there is no PR, put the same results in the final reply only.

If you agree with their recommendations, make the changes and request a fresh
review after. Continue this process until all delegates are satisfied with the
outcome, stopping sooner where /review-loop's step 5 stops.

Do not let repeated reviews result in scope creep. It is your job to fight to
keep scope limited.
