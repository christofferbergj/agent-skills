# thermos: source and local adaptations

Orchestrator for the two independent review passes.

## Source and credit

- Original author: Cursor. Source repository: [cursor/plugins](https://github.com/cursor/plugins), [Thermos plugin](https://github.com/cursor/plugins/tree/main/thermos).
- Original skill: [`thermos/skills/thermos/SKILL.md`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/thermos/skills/thermos/SKILL.md).
- Tracking policy: latest commit on the upstream `main` branch.
- Imported from commit: `1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Cursor](./LICENSE). This copy retains the upstream notice; this repository's root license does not replace it.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Added explicit dependency resolution, rubric delivery to child contexts, shared review scope and evidence, completion handling, and a disclosed sequential fallback.
- Kept reviewers read-only and independent, prohibited nested delegation, and required evidence-based deduplication. Reversed upstream's heavier weighting of overlapping findings: severity follows verified impact, because two reviewers given the same evidence and model are not independent confirmation.

`agents/openai.yaml` is locally maintained host metadata. Formatting may differ from the original without changing the rubric.

## Maintenance

Invoke `/maintain-skills` for whole-library upkeep and use the [Thermos compatibility guide](./MAINTENANCE.md) for suite-specific inputs and checks. Skills CLI reinstalls this adaptation; it does not merge future Cursor changes.

The reviewed-through commit is the comparison baseline for the next review, including changes deliberately skipped below. Advance it only after reviewing the full upstream delta for this skill and its supporting files. Keep the original import commit unchanged.

| Review date | Decision                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-12  | Imported the pinned source and applied the local adaptations above. No later upstream changes reviewed.                                                                                                                                                                                                                                                                                                                             |
| 2026-10-16  | Reviewed `f713f14203cd6420cec13cd7c55c32d598dbab68`: the complete Thermos tree, including reviewer wrappers, documentation, manifest, assets, and license, is unchanged. Retained native host execution, direct reviewers, and evidence-based synthesis. Repository checks pass; unchanged host behavior uses the recorded smoke evidence. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md). |
| 2026-10-21  | Reviewed `190d28736eff128ec94f502a22c7fe0c4b56cd37`: the Thermos tree is unchanged since `f713f14`. First fidelity check: restored upstream's rule not to restate reviewer summaries already visible to the user, dropped two adaptations the library-wide Hosts and Packaging rules already cover, and recorded the reason for not weighting overlapping findings more heavily.                                                    |
