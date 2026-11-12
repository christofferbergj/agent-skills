# council: source and adaptations

## Source and credit

- Original author: Theo Browne.
- Canonical source: [t3dotgg/tstack](https://github.com/t3dotgg/tstack).
- Original skill: [`skills/council/SKILL.md`](https://github.com/t3dotgg/tstack/blob/1085050f3baed1ac724caa4a8166145fb2ac88af/skills/council/SKILL.md), the skill's only file.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `1085050f3baed1ac724caa4a8166145fb2ac88af`.
- Reviewed through commit: `11e37a74d0a6868c121cd0910ab2b3bd9873b92a`.
- Fidelity checked through: `11e37a74d0a6868c121cd0910ab2b3bd9873b92a`.
- Last upstream review: 2026-11-12.
- License: [MIT, copyright 2026 Theo Browne](LICENSE), retained from the [pinned upstream license](https://github.com/t3dotgg/tstack/blob/1085050f3baed1ac724caa4a8166145fb2ac88af/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences. By the Hosts adaptation, members start through /swarm's T3 route in T3 Code, and elsewhere as /swarm's panel of the session's model and the counterpart. By the Review adaptation, a council inside an implementation workflow runs beside /review-loop, which still gives the final verdict.
- In T3 Code, members come from the session's providers rather than three fixed ones. Upstream seats one model from each of three providers, such as Claude Opus, GPT Sol, and Gemini Pro. Here every provider `orchestrator_capabilities` can run contributes its first listed model, one member per model maker, so a provider the user adds in T3 Code joins without an edit. T3 Code lists each provider's models in the user's model order over its own catalog order ([`listCapabilityModels`](https://github.com/pingdotgg/t3code/blob/9e85538535c8553901351112ab02dd1dd62db5ee/apps/server/src/mcp/OrchestratorMcpService.ts#L294-L337)), so the first listed model tops the list the user sees and can reorder. That settles flagship against daily use, such as GPT Sol over OpenAI's flagship GPT Astra, without naming models in the skill. The listing is read without `search`, because a search filters every provider's list, not only the one searched for. T3 Code's model manifest lists Antigravity's `gemini-3.8-flash-high` first, so a Gemini member sits as Pro only after the user moves Pro to the top of that provider's model order.
- Every route passes each member's model and `high` effort, and /swarm sets only a Codex member's speed, from its `review-full` target in Claude Code or its `judgment-and-prose` target in Codex. Without this, /swarm's contract passes the counterpart target's model and `xhigh` effort, and its default role gives a Codex member no speed.
- A member that fails after its route's one retry, or whose Codex target is `fallback`, is reported missing. /swarm's same-vendor route and closest-model retry would otherwise replace it, against upstream's "report it instead of substituting".
- A council needs two makers where upstream needs three, because the user runs only Claude and Codex.
- For a code review, each member gets the proof and report lines of /review-loop's reviewer brief, and its findings pass /review-loop's Verify and merge step before the summary. Upstream summarizes responses directly; /review-loop owns finding verification in this library, because reviewers make false claims, and its verify step drops a finding that comes without proof.
- Upstream's fix-and-review loop stays, and stops sooner where /review-loop's step 5 stops: after three rounds or at a finding that needs the user. /review-loop owns the fix-and-re-review loop, and an uncapped loop between two makers that disagree never ends.
- The PR section goes right after the description's Evidence section. Upstream places it before its PR skill's model and harness line, which /pr's template does not have, and /pr's ELI5 closes the description.
- The example table drops upstream's Gemini Pro row, since the user runs no Gemini provider.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. Theo Browne's other tstack skills are not tracked; a new one enters only by the adaptation contract's rule for adopting skills. Recheck the listing-order evidence above when T3 Code changes how `orchestrator_capabilities` orders models. When a driver other than Codex and Claude first runs a member, check that T3 Code's plan mode keeps it read-only: T3's ACP adapter enters plan mode only when the agent advertises one. Record adopted, adapted, and excluded changes before advancing the baseline.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ---------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-05 | `1085050f3baed1ac724caa4a8166145fb2ac88af` | Imported `SKILL.md` on the user's request, with the adaptations above. The member rule, applied to the live `orchestrator_capabilities` listing, seated `claude-opus-5-5` on `claudeAgent` and `gpt-6.1-sol` on `codex`, and a fresh Sonnet agent following the skill chose the same members, instances, and effort. Repository checks and catalog validation pass. A /review-loop round with Codex Sol and three Claude critics found the effort, failure, proof, loop, and placement gaps fixed here. |
| 2026-11-12 | `11e37a74d0a6868c121cd0910ab2b3bd9873b92a` | Adopted 11e37a7 ("act on results as they arrive") as written: check each result's findings as it lands and decide fixes while the other members run, edit nothing while a member still reviews the same checkout, and treat a non-blocking member's late result as feedback without recording its score. It fits the local Verify-and-merge step and /swarm's T3 route. Fidelity passes both directions.                                                                                                |
