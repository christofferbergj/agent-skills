# Delta review effort on GPT-6.2 Sol, 2026-11-17

Historical evaluation record. Models, plan limits, and costs describe this snapshot; current routing lives in /swarm's `target.py` and the owner's Pstack configuration.

OpenAI released GPT-6.2 Sol on 2026-11-17 at GPT-6.1 Sol's token prices. The owner asked whether delta reviews should move from `high` to `xhigh` on the new model, since the price per token had not changed. Effort changes how many tokens a review uses, so the question was whether `xhigh` finds more on a delta review.

## Method

A throwaway clone of this repository at `644323c`, with no remote, received one commit, `d28d4d1`, presented as the fix for a round 1 finding: a configured effort such as `XHIGH` or `Max` skipped the `xhigh` cap in `skills/agents/swarm/scripts/target.py`. The commit made that fix and hid three defects. Each was shown by a run before any review started, and the swarm test suite passed at the commit.

| Defect                | What the commit did                                                                                                                                  | Proof                                                                                            |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Fix in one place only | Lowercased efforts in `resolve()` but not in `resolve_panel()` or `resolve_native()`, while a new help line claimed every effort matches in any case | An `arena-runners` seat configured `XHIGH` resolved to `high` at the commit                      |
| Unrequested change    | Changed the fallback test from `left < skipWhenLeft` to `<=`                                                                                         | At exactly 5% left, `review-full` ran on Codex at the base and returned `fallback` at the commit |
| Test without effect   | Added a test of the fix that used lower-case `max` and `ultra`                                                                                       | The test passed against the base `target.py`                                                     |

Four GPT-6.2 Sol reviewers ran at the same time as read-only T3 Code child tasks in plan mode, at standard speed, with one round 2 delta-review brief from /review-loop's reviewer brief: two at `high` and two at `xhigh`. The brief named the round 1 finding and its fix but not the planted defects. Credits are Sol's standard Work and Codex rates (50, 2.5, and 250 credits per million uncached input, cached input, and output tokens) applied to each run's final token totals in its Codex session log.

## Results

| Run          | Unrequested change | Test without effect | Fix in one place only | False findings | Credits | Minutes |
| ------------ | ------------------ | ------------------- | --------------------- | -------------- | ------- | ------- |
| H1 · `high`  | found              | found               | missed                | 0              | 5.5     | 2.1     |
| H2 · `high`  | found              | found               | partly                | 0              | 5.2     | 2.1     |
| X1 · `xhigh` | found              | found               | missed                | 0              | 5.9     | 2.1     |
| X2 · `xhigh` | found              | found               | missed                | 0              | 6.9     | 3.0     |

H2 showed that native roles still read efforts case-sensitively and called the new help line overbroad, but treated the native gap as pre-existing and asked for narrower wording instead of a wider fix. No run checked panel seats. Every finding came with a run that reproduced it.

## Conclusion

Both efforts found the same two defects in every run, and the defect that three runs missed was missed at both levels. `xhigh` averaged 6.4 credits a review against 5.35 at `high`, about 20% more, and took up to 3 minutes against 2.1. This agrees with the 2026-10-20 comparison on GPT-6.1 Sol, so delta reviews stay at `high`.

## Limits

Four runs on one fix commit can show that `xhigh` gave no clear gain, but not rule out a small one. The fixture is a 9-line change to one script; a larger fix commit could reward more depth. The runs measured detection only, not how clear or actionable each report was.
