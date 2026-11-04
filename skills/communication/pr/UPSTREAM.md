# pr: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/pr`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/pr).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Inherited attribution

Attribution-only source: https://github.com/humanlayer/skills

Attribution-only source: https://github.com/humanlayer/humanlayer

The frontmatter and `CREDITS.md` retain Dex Horthy and Humanlayer's credit for the earlier `show-me` template using these two repository identities. This repository imported Matt's adapted `pr` skill and tracks that version through Matt's source record above. The inherited credits are not independently tracked imports; Matt's reviewed revision never establishes a Humanlayer review baseline.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Keep the upstream description template and inherited source credit. Repository contribution formats take precedence, and publication follows the invoking grant.
- Evidence, in the template and its section, states when screenshots are due (a visible change on a view that is cheap to capture), lays them out as a `Before | After` table per view when the base branch shows the same state and as a table of the new states otherwise, and publishes them with `gh pr create` or `gh pr edit --attach`. Reason: owner request (#33, #35). Upstream never says when screenshots are due or where they go, so agents fell back to text evidence for visible UI changes; side-by-side tables spare reviewers scrolling between the two. States joined the rule on owner request, because a forced before for a state the base branch never reaches shows nothing. `scripts/pr-evidence.ts`, which committed screenshots to an images-only branch because `gh` could not attach them, was removed once GitHub CLI 2.99.0 (2026-09-01) added `--attach`.
- The who-did-what first line, the problem paragraph opening Summary, the evidence table by kind of change with its honesty rules, and the closing ELI5 section come from Hugo Richard's `pr-writing`, recorded below as a second source. The evidence table replaces upstream's "Screenshots are S-tier" and "Execution-based evidence is A-tier" tiers, and its bug-fix row keeps upstream's failing test named in pseudocode. Reason: owner request, 2026-11-04, after a trial on #67 where his evidence surfaced a behaviour change this skill's description had missed.
- Evidence opens with a review status line, `**Reviewed:**` or `**Not reviewed:**`, and a diff that changes UI source without a screenshot says `**Not verified on <surface>:**` with the reason; `scripts/check-evidence.ts` names what a body lacks, and the completion line requires it to pass. Reason: a 2026-11-02 analysis of the owner's threads found runs reporting "checks all passed" with no check on the real surface, and every path, Pstack or not, writes its PR body here. The template's screenshot rule never fired on refactors, so silence read as verified.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                       |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Fidelity check in both directions; the skill, `CREDITS.md`, and Codex metadata have no upstream delta since import. Recorded the /domain-modeling delegation. Restored upstream's `PR` display name in `agents/openai.yaml`, which read `Pr`. Catalog validation passes. |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                   |
| 2026-11-04  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | Merged in Hugo Richard's `pr-writing` as a second, principle-derived source (see below). Replaced `scripts/pr-evidence.ts` with `gh --attach`. Matt's source position is unchanged; this row records local divergences only.                                             |

## Second source: Hugo Richard's pr-writing

- Original author: Hugo Richard.
- Source repository: [HugoRCD/hr-folio](https://github.com/HugoRCD/hr-folio).
- Install route announced by the author: `npx skills add hugorcd.com --skill pr-writing`, which served the same file on 2026-11-04.
- Original skill: [`skills/pr-writing/SKILL.md`](https://github.com/HugoRCD/hr-folio/blob/f296fa2b7364a62b9e985f1c9d2f69be0654b857/skills/pr-writing/SKILL.md), for the who-did-what line, the skimmer's order, evidence by kind of change, the honesty rules, and the ELI5. His article [What My Pull Requests Look Like Now](https://hugorcd.com/writing/what-my-pull-requests-look-like-now) gives the reasons.
- Supporting sources: [`skills/document-pr/SKILL.md`](https://github.com/HugoRCD/hr-folio/blob/f296fa2b7364a62b9e985f1c9d2f69be0654b857/skills/document-pr/SKILL.md), reviewed for its `gh pr edit --attach` publication; its evidence map and HTML artifacts are left out.
- Tracking policy: upstream `main`, reviewed as a principle source under the adaptation contract's [principle-derived skills](../../agents/maintain-skills/references/ADAPTATION.md#principle-derived-skills).
- Imported from commit: `f296fa2b7364a62b9e985f1c9d2f69be0654b857`.
- Reviewed through commit: `f296fa2b7364a62b9e985f1c9d2f69be0654b857`.
- Fidelity checked through: `f296fa2b7364a62b9e985f1c9d2f69be0654b857`.
- Last upstream review: 2026-11-04.
- License: [Apache-2.0, copyright 2024-present Hugo Richard](LICENSE-pr-writing). Retain the notice with derived material.

### Local adaptations to preserve

The wording is first-party, inside Matt's template. Adopted principles:

- A quoted first line saying an AI agent wrote the change on the user's behalf, how much they shaped it (approved the approach, wrote the spec, or shaped the solution), and whether they have reviewed it, in place of a "Generated with…" footer.
- The skimmer's order: the problem in one paragraph opens Summary, and an ELI5 of two or three plain sentences closes the body.
- Evidence picked by kind of change: UI with video and phone width, the real output of the same command with its exit code, the same input for a bug, measured spread for performance, graded prompts for agent behaviour, and caller code for a new API.
- Honesty rules: before is the base or production, never a reverted copy; look at every capture; demo data only; say what failed or nobody checked; no exploit details for a public security fix.
- Captures stay outside the repository and are uploaded to the PR itself.

Deliberate departures:

- The handle comes from `gh api user` when that account is the user's own, rather than asking first, since every flow here runs on the user's own `gh` login.
- No step to show the draft and wait for the user's go-ahead: publication follows the invoking grant, as the library-wide authority rule sets.
- No rule against `Co-Authored-By` commit trailers: commits are outside a PR description, and the host sets their attribution.
- Matt's Summary visuals replace Hugo's "What changed" list, and Merge Danger replaces his "Details" section; the trial on #67 showed his list turning into a file-by-file account.
- Added an "Agent instructions or docs" evidence row, since most PRs in this library change only Markdown and his table had no row for them.
