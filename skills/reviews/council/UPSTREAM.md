# council: source and adaptations

## Source and credit

- Original author: Theo Browne.
- Canonical source: [t3dotgg/tstack](https://github.com/t3dotgg/tstack).
- Original skill: [`skills/council/SKILL.md`](https://github.com/t3dotgg/tstack/blob/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/council/SKILL.md), the skill's only file.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `1085050f3baed1ac724caa4a8166145fb2ac88af`.
- Reviewed through commit: `1085050f3baed1ac724caa4a8166145fb2ac88af`.
- Fidelity checked through: `1085050f3baed1ac724caa4a8166145fb2ac88af`.
- Last upstream review: 2026-11-05.
- License: [MIT, copyright 2026 Theo Browne](LICENSE), retained from the [pinned upstream license](https://github.com/t3dotgg/tstack/blob/1085050f3baed1ac724caa4a8166145fb2ac88af/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences. Members start through /swarm's T3 route in T3 Code and through its native and cross-vendor routes elsewhere, by the Hosts adaptation.
- Members come from the session's providers rather than three fixed ones. Upstream seats one model from each of three providers, such as Claude Opus, GPT Sol, and Gemini Pro. Here every provider `orchestrator_capabilities` can run contributes its first listed model, one member per model maker, so a provider the user adds later joins without an edit. T3 Code sorts each provider's listing by the user's model order over its own catalog order ([`listCapabilityModels`](https://github.com/pingdotgg/t3code/blob/9e85538535c8553901351112ab02dd1dd62db5ee/apps/server/src/mcp/OrchestratorMcpService.ts#L294-L337)), so the first listed model is the one the user runs. That settles flagship against daily use, such as GPT Sol over OpenAI's flagship GPT Astra, without naming models in the skill. On 2026-11-05 the rule seated `claude-opus-5-5` and `gpt-6.1-sol`. T3 Code's catalog lists Antigravity's Gemini Flash first, so a Gemini member sits as Pro only after the user moves Pro to the top of that provider's model order.
- Each member runs on its own model at `high` effort, and /swarm's execution contract sets only a Codex member's speed, so /swarm's counterpart target cannot replace a member's model.
- A council needs two makers where upstream needs three, because the user runs only Claude and Codex.
- Findings pass /review-loop's Verify and merge step before the summary. Upstream summarizes responses directly; /review-loop owns finding verification in this library, because reviewers make false claims.
- The PR section goes at the end of the description. Upstream places it before its PR skill's model and harness line, which /pr's template does not have.
- The example table drops upstream's Gemini Pro row, since the user runs no Gemini provider.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. Theo Browne's other tstack skills are not tracked; a new one enters only by the adaptation contract's rule for adopting skills. Recheck the listing-order evidence above when T3 Code changes how `orchestrator_capabilities` orders models. Record adopted, adapted, and excluded changes before advancing the baseline.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                           |
| ---------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-05 | `1085050f3baed1ac724caa4a8166145fb2ac88af` | Imported `SKILL.md` on the user's request. Replaced the three fixed providers with members from the session's providers, verified findings through /review-loop, moved the PR section to the description's end, and dropped the Gemini Pro example. The roster rule, applied to the live listing, seated Opus 5.5 and GPT-6.1 Sol. |
