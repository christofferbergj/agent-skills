# untangle-codebase: source and adaptations

## Source and credit

- Original author: Maze, publishing as Caldo.
- Canonical source: [caldoai/skills](https://github.com/caldoai/skills).
- Original skill: [`skills/untangle-codebase/SKILL.md`](https://github.com/caldoai/skills/blob/f3cf47774975a7d9fca45730babf4ff7ad765ada/skills/untangle-codebase/SKILL.md), the skill's only file.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `f3cf47774975a7d9fca45730babf4ff7ad765ada`.
- Reviewed through commit: `f3cf47774975a7d9fca45730babf4ff7ad765ada`.
- Fidelity checked through: `f3cf47774975a7d9fca45730babf4ff7ad765ada`.
- Last upstream review: 2026-11-14.
- License: [MIT, copyright 2026 Maze](LICENSE), retained from the [pinned upstream license](https://github.com/caldoai/skills/blob/f3cf47774975a7d9fca45730babf4ff7ad765ada/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences. By the Hosts adaptation, step 5 dispatches its subagents, and any the tips use, through /swarm. By the Review adaptation, step 5's completion list ends with /review-loop's review of the whole refactor.
- The Tests branch of step 4 invokes /principle-test-behavior-not-implementation, the owner of the test-quality criteria, before upstream's three cases, which stay as written because they state those criteria in this skill's own terms of what gives a piece a reason to change.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. The source repository ships no other skill at this revision; a new one enters only by the adaptation contract's rule for adopting skills.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-14 | `f3cf47774975a7d9fca45730babf4ff7ad765ada` | Imported `SKILL.md` on the owner's request, with the adaptations above. The Skills CLI had installed this skill from upstream on 2026-11-05; the installed copy was byte-identical to this revision, and the adopted copy replaces it. It does a job no local skill does: `improve-codebase-architecture` scans a codebase and proposes one deepening, while this skill carries a whole-codebase refactor through to the end. Fidelity passes in both directions: the only differences from upstream are the three owner invocations and formatter output. Repository checks and catalog validation pass. |
