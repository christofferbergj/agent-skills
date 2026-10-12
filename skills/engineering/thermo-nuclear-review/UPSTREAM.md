# thermo-nuclear-review: source and local adaptations

Correctness, security, developer-experience, and feature-gate review rubric.

## Source and credit

- Original author: Cursor. Source repository: [cursor/plugins](https://github.com/cursor/plugins), [Thermos plugin](https://github.com/cursor/plugins/tree/main/thermos).
- Original skill: [`thermos/skills/thermo-nuclear-review/SKILL.md`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/thermos/skills/thermo-nuclear-review/SKILL.md).
- Imported from commit: `1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def`.
- Reviewed through commit: `1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def`.
- Last upstream review: 2026-10-12.
- License: [MIT, copyright 2026 Cursor](./LICENSE). This copy retains the upstream notice; this repository's root license does not replace it.

- Original reviewer wrapper: [agents/thermo-nuclear-review-subagent.md](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/thermos/agents/thermo-nuclear-review-subagent.md). Its relevant scope and delegation rules are incorporated locally; the wrapper itself is not installed.

## Local adaptations to preserve

- Removed upstream `disable-model-invocation: true` so `/thermos` can invoke this dependency. Codex metadata allows implicit invocation.
- Added a review-only boundary: report introduced issues and proposed remedies; edits and published comments need a separate user request.
- Added direct completion without nested subagents when delegated. The original audit criteria, severity calibration, and requirement to read PR discussion only after the independent audit remain.

`agents/openai.yaml` is locally maintained host metadata. Formatting may differ from the original without changing the rubric.

## Maintenance

Follow the [manual upstream-update procedure](../thermos/MAINTENANCE.md). This repository owns the installed adaptation. Skills CLI reinstalls this copy; it does not merge future Cursor changes.

The reviewed-through commit is the comparison baseline for the next review, including changes deliberately skipped below. Advance it only after reviewing the full upstream delta for this skill and its supporting files. Keep the original import commit unchanged.

| Review date | Decision                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------- |
| 2026-10-12  | Imported the pinned source and applied the local adaptations above. No later upstream changes reviewed. |
