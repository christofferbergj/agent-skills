# prune-tests: source and adaptations

## Source and credit

- Original author: Maze, publishing as Caldo.
- Canonical source: [caldoai/skills](https://github.com/caldoai/skills).
- Original skill: [`skills/prune-tests/SKILL.md`](https://github.com/caldoai/skills/blob/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/skills/prune-tests/SKILL.md), the skill's only file.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `bd73b2ea5eb854ab8f0553fb41f77c8786f28f82`.
- Reviewed through commit: `bd73b2ea5eb854ab8f0553fb41f77c8786f28f82`.
- Fidelity checked through: `bd73b2ea5eb854ab8f0553fb41f77c8786f28f82`.
- Last upstream review: 2026-11-17.
- License: [MIT, copyright 2026 Maze](LICENSE), retained from the [pinned upstream license](https://github.com/caldoai/skills/blob/bd73b2ea5eb854ab8f0553fb41f77c8786f28f82/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- The skill is user-invoked, where upstream leaves it model-invoked. `test-audit` is model-invoked and takes requests to clean up or prune tests, keeping a test when the evidence is unclear and leaving production code alone; this skill deletes such a test, and production code kept only for it, in one pass, so it runs only when the user names it. Upstream's description is already the short summary a user-invoked skill carries, and no skill invokes this one.
- Step 1 invokes /principle-test-behavior-not-implementation, the owner of the test-quality criteria, before upstream's criteria, which stay as written because they state those criteria in this skill's own terms of what a test depends on, and add cases the owner doesn't hold: tests of removed code, duplicates, and what the type system or the browser already guarantees.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. The source repository's other skill at this revision is adopted as [untangle-codebase](../untangle-codebase/UPSTREAM.md); a new one enters only by the adaptation contract's rule for adopting skills.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-17 | `bd73b2ea5eb854ab8f0553fb41f77c8786f28f82` | Imported `SKILL.md` on the owner's request, at the commit that added it upstream, with the adaptation above. The request settles adoption, though two local skills also remove low-value tests and `test-audit`'s cleanup mode takes the same kind of request. `test-audit` records a decision with its evidence for every test, keeps a test when the evidence is unclear, has an independent subagent compare what survives, and leaves production code outside its scope; this skill decides each test in one pass by what it depends on, deletes or rewrites it, and deletes production code that existed only for the tests it removed. `untangle-codebase` removes such tests only as an optional last step of a whole-codebase refactor. To keep one model-invoked owner of test cleanup, this skill is user-invoked, with upstream's description unchanged. It dispatches no subagents and names no review, so neither /swarm nor /review-loop is routed. Fidelity passes in both directions: the only differences from upstream are the invocation mode and the owner invocation. Repository checks and catalog validation pass. |
