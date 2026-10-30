# code-review: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/code-review`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/code-review).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Fidelity checked through: `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa`.
- Last upstream review: 2026-10-29.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Select applicable principles through /principles for the pinned artifact and explicitly supply their instructions to reviewers while preserving independent Standards/Spec axes and read-only review.
- Pin both axes to one immutable artifact, including relevant untracked files for working reviews. Accept a local spec or task brief, preserve distinct Pstack lenses, and refresh affected coverage after fixes.
- Ask the user for a fixed point or spec only when scope is ambiguous or a missing spec prevents the assessment; otherwise reuse the caller's fixed point, propose the actual merge-base, and disclose "no spec available". Upstream asks whenever either is unspecified; the local form lets /review-loop and other workflows invoke the review without a pause.
- The Standards brief also asks for new helpers or flows that code outside the diff already provides, and the Spec brief for claims in the PR description, docs, or comments that the code doesn't back. Both come from Oliver Cederborg's shared review lenses (d3b51b8), adopted in /review-loop's counterpart brief and carried here, the owner of Standards and Spec, so same-model passes get them too (owner decision, 2026-10-30).
- Tell both reviewers to read the reviewed head through `git show` and `git diff` rather than checking it out. A Spec reviewer once ran `git checkout <head>` in the shared worktree while the caller was committing fixes, which detached HEAD.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                              |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Fidelity check in both directions; the skill has no upstream delta since import. Restored upstream's `/setup-matt-pocock-skills` pointer for a required but unprovided tracker. Recorded the softened fixed-point and spec questions. Other differences are recorded adaptations or formatting. Catalog validation passes.                                                                      |
| 2026-10-29  | `a496f5513d4a4cf889bc48e189e579f4b0bdf6aa` | Upstream `7739eae` (#1341) and `a496f55` (#1342) start every subagent with a fresh context window rather than a fork. Carried the rule into /swarm's execution contract, the delegation owner, so both suites receive it, including Codex's `fork_turns` and Claude Code's `fork` type. Adopted upstream's sentence as written beside the two parallel axes. Fidelity holds in both directions. |
