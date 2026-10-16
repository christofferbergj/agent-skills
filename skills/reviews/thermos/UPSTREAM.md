# thermos: source and local adaptations

Orchestrator for the two independent review passes.

## Source and credit

- Original author: Cursor. Source repository: [cursor/plugins](https://github.com/cursor/plugins), [Thermos plugin](https://github.com/cursor/plugins/tree/main/thermos).
- Original skill: [`thermos/skills/thermos/SKILL.md`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/thermos/skills/thermos/SKILL.md).
- Tracking policy: latest commit on the upstream `main` branch.
- Imported from commit: `1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def`.
- Reviewed through commit: `f713f14203cd6420cec13cd7c55c32d598dbab68`.
- Last upstream review: 2026-10-16.
- License: [MIT, copyright 2026 Cursor](./LICENSE). This copy retains the upstream notice; this repository's root license does not replace it.

## Local adaptations to preserve

- Replaced Cursor-specific named subagents with native Codex spawning and Claude Code built-in general-purpose agents. No separate custom agent installation is needed.
- Preserved explicit-only invocation with `disable-model-invocation: true` and Codex `policy.allow_implicit_invocation: false`.
- Added explicit dependency resolution, rubric delivery to child contexts, shared review scope and evidence, completion handling, and a disclosed sequential fallback.
- Kept reviewers read-only and independent, prohibited nested delegation, and required evidence-based deduplication without increasing severity merely because both reviewers agree.

`agents/openai.yaml` is locally maintained host metadata. Formatting may differ from the original without changing the rubric.

## Maintenance

Invoke `/maintain-skills` for whole-library upkeep and use the [Thermos compatibility guide](./MAINTENANCE.md) for suite-specific inputs and checks. Skills CLI reinstalls this adaptation; it does not merge future Cursor changes.

The reviewed-through commit is the comparison baseline for the next review, including changes deliberately skipped below. Advance it only after reviewing the full upstream delta for this skill and its supporting files. Keep the original import commit unchanged.

| Review date | Decision                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-12  | Imported the pinned source and applied the local adaptations above. No later upstream changes reviewed.                                                                                                                                                                                                                                                                                                                             |
| 2026-10-16  | Reviewed `f713f14203cd6420cec13cd7c55c32d598dbab68`: the complete Thermos tree, including reviewer wrappers, documentation, manifest, assets, and license, is unchanged. Retained native host execution, direct reviewers, and evidence-based synthesis. Repository checks pass; unchanged host behavior uses the recorded smoke evidence. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md). |
