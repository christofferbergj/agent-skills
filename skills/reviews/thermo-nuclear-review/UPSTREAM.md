# thermo-nuclear-review: source and local adaptations

Correctness, security, developer-experience, and feature-gate review rubric.

## Source and credit

- Original author: Cursor. Source repository: [cursor/plugins](https://github.com/cursor/plugins), [Thermos plugin](https://github.com/cursor/plugins/tree/main/thermos).
- Original skill: [`thermos/skills/thermo-nuclear-review/SKILL.md`](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/thermos/skills/thermo-nuclear-review/SKILL.md).
- Tracking policy: latest commit on the upstream `main` branch.
- Imported from commit: `1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Cursor](./LICENSE). This copy retains the upstream notice; this repository's root license does not replace it.

- Original reviewer wrapper: [agents/thermo-nuclear-review-subagent.md](https://github.com/cursor/plugins/blob/1b6d44ff26d4e242f4e8f68c391e6d2f7ca16def/thermos/agents/thermo-nuclear-review-subagent.md). Its relevant scope and delegation rules are incorporated locally; the wrapper itself is not installed. Its Cursor `Task` orchestration and missing-skill fallback are replaced by the consumers' native delegation and rubric delivery (/thermos, /review-loop), and its output shape, prioritized findings with file and line evidence, is set by each consumer's reviewer task. Its "unless the user or parent explicitly asks" exception to nested delegation is dropped, because the Thermos contract keeps reviewers from delegating further.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Removed upstream `disable-model-invocation: true` so `/thermos` can invoke this dependency. Codex metadata allows implicit invocation.
- Added a review-only boundary: report introduced issues and proposed remedies; edits and published comments need a separate user request.
- Added the tracing method after the end-to-end rule: real inputs, a second run such as a retry, and every caller of a shared helper. It comes from Oliver Cederborg's shared review lenses (d3b51b8), adopted in /review-loop's counterpart brief and carried here, the owner of the correctness audit, so /thermos and /review-loop's same-model pass get it too (owner decision, 2026-10-30).
- Added direct completion without nested subagents when delegated. The original audit criteria, severity calibration, and requirement to read PR discussion only after the independent audit remain.

`agents/openai.yaml` is locally maintained host metadata. Formatting may differ from the original without changing the rubric.

## Maintenance

Invoke `/maintain-skills` for whole-library upkeep and use the [Thermos compatibility guide](../thermos/MAINTENANCE.md) for suite-specific inputs and checks. Skills CLI reinstalls this adaptation; it does not merge future Cursor changes.

The reviewed-through commit is the comparison baseline for the next review, including changes deliberately skipped below. Advance it only after reviewing the full upstream delta for this skill and its supporting files. Keep the original import commit unchanged.

| Review date | Decision                                                                                                                                                                                                                                                                                                                                                             |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-12  | Imported the pinned source and applied the local adaptations above. No later upstream changes reviewed.                                                                                                                                                                                                                                                              |
| 2026-10-16  | Reviewed `f713f14203cd6420cec13cd7c55c32d598dbab68`: the complete Thermos tree and this reviewer's wrapper have no delta. Retained the callable, read-only, direct-review adaptation and rubric. Repository checks pass; no runtime behavior changed. See the [library review](../../../docs/reviews/2026-10-16-whole-library-maintenance.md).                       |
| 2026-10-21  | Fidelity check at `190d28736eff128ec94f502a22c7fe0c4b56cd37`: the complete Thermos tree has no delta since import. Compared the skill and its wrapper in both directions; every local difference is a recorded adaptation or formatting. Recorded where the wrapper's orchestration, fallback, output shape, and nested-delegation exception went. No rubric change. |
