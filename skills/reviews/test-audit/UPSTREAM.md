# Test audit source and local adaptations

## Source and credit

- Original author: OpenClaw contributors. Source repository: [openclaw/openclaw](https://github.com/openclaw/openclaw).
- Tracking policy: manually review the listed files on upstream `main`; preserve the local adaptations below.
- Local import: [c60c10a54bda0a547d029b9696ef31f2a7611383](https://github.com/christofferbergj/agent-skills/commit/c60c10a54bda0a547d029b9696ef31f2a7611383), 2026-09-25. The commit records a port from a ChatGPT skill and attributes OpenClaw.
- Original upstream import revision: unrecorded. Neither local history nor the installed copy identifies it. [80930af448ebabc84174146b56bc106d37fab3b4](https://github.com/openclaw/openclaw/commit/80930af448ebabc84174146b56bc106d37fab3b4) predates the local import and contains both source files, but is not a proven import revision. Preserve this gap until evidence resolves it.
- Reviewed through: [71b5563397e95d67ad902f79a717559519010ac8](https://github.com/openclaw/openclaw/commit/71b5563397e95d67ad902f79a717559519010ac8), 2026-10-14. This fresh comparison baseline does not replace the unknown historical import.

Files reviewed at that revision:

| Upstream file                                                                                                                                                                     | Local disposition                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [.agents/skills/test-audit/SKILL.md](https://github.com/openclaw/openclaw/blob/71b5563397e95d67ad902f79a717559519010ac8/.agents/skills/test-audit/SKILL.md)                       | Adapted into `SKILL.md`; local audit and cleanup authority applies.              |
| [.agents/skills/test-audit/CAMPAIGN.md](https://github.com/openclaw/openclaw/blob/71b5563397e95d67ad902f79a717559519010ac8/.agents/skills/test-audit/CAMPAIGN.md)                 | Adapted into `references/campaign.md`.                                           |
| [.agents/skills/test-audit/references/audit.md](https://github.com/openclaw/openclaw/blob/71b5563397e95d67ad902f79a717559519010ac8/.agents/skills/test-audit/references/audit.md) | Shared value and evidence rules remain in the local main skill.                  |
| [docs/help/testing/writing-tests.md](https://github.com/openclaw/openclaw/blob/71b5563397e95d67ad902f79a717559519010ac8/docs/help/testing/writing-tests.md)                       | Boundary and cost context; repository-specific recipes and budgets excluded.     |
| [.agents/skills/openclaw-testing/SKILL.md](https://github.com/openclaw/openclaw/blob/71b5563397e95d67ad902f79a717559519010ac8/.agents/skills/openclaw-testing/SKILL.md)           | Proof-policy context; local commands and gates come from the audited repository. |

License: [MIT, copyright 2026 OpenClaw Foundation](./LICENSE), retained from the [pinned upstream license](https://github.com/openclaw/openclaw/blob/71b5563397e95d67ad902f79a717559519010ac8/LICENSE). Include the copyright and permission notice when redistributing upstream material; the repository's root license does not replace it.

## Local adaptations to preserve

- Model invocation supports focused or exhaustive audits and cleanup. Existing user authority determines edits and publication; there is no separate authoring mode.
- Assess contracts, credible failures, independent expectations, refactoring resilience, distinct feedback, and justified cost. Inspect suspicious patterns before deciding; uncertainty preserves tests.
- Use existing dependency seams and check double fidelity. Production fixes, API changes, and seam removal require separate scope; tests alone do not establish that a public export is obsolete.
- Derive commands and CI requirements from the audited project. Keep validation proportional; exclude fixed time budgets, line-count targets, mandatory mutation of every contract, and OpenClaw-specific proof or PR tooling.
- Keep campaign accounting separate from shared value rules. Actively delegate discovery and independent review, scaling to scope and capacity; retain the sequential fallback and checkable completion criteria.

`README.md`, `agents/openai.yaml`, `assets/icon.svg`, this record, and the retained license are locally maintained packaging.

## Maintenance

Compare future upstream changes against the reviewed-through revision for all listed files. Record adopted, adapted, and excluded changes and validation before advancing the baseline. Preserve the original import gap separately; recover its revision only from verifiable evidence. Upstream links are maintenance references, not runtime dependencies.

## Review history

| Date       | Candidate revision                                                                 | Decision                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-09-25 | Unknown upstream revision; local import `c60c10a54bda0a547d029b9696ef31f2a7611383` | Ported the ChatGPT adaptation with audit/cleanup routing, completion criteria, and a separate campaign reference. No upstream revision was recorded.                                                                                                                                                                                                                                                                                   |
| 2026-10-14 | `71b5563397e95d67ad902f79a717559519010ac8`                                         | Fully reviewed the listed source files to establish a fresh baseline. Retained behavior-preserving refactoring and independent boundary proof; expanded feedback, cost, and double-fidelity criteria. Excluded the upstream authoring mode, automatic production-seam deletion, mandatory parallel reviewers, fixed budgets, line-count goals, and repository-specific CI/PR rules in favor of the local scope and validation process. |

Validation for the 2026-10-14 update passed: `pnpm fmt:check`, `npx skills@latest add . --list`, `git diff --check`, and local Markdown link checks.

On 2026-10-15, added three-role discovery, reuse of subagents for batch audits, and independent preservation review, with scope and capacity fallbacks. This is a local workflow change; the upstream review baseline is unchanged. Formatting, skill discovery, and `git diff --check` passed.
