# break-ui: source and adaptations

## Source and credit

- Original author: Emil Kowalski.
- Canonical source: [emilkowalski/skill](https://github.com/emilkowalski/skill).
- Original skill and resources: [`skills/break-ui`](https://github.com/emilkowalski/skill/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills/break-ui), with `SKILL.md` and `CATALOG.md`.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `a81dbca07f2217b7103e510c0f13f8d5b017afc9`.
- Reviewed through commit: `a81dbca07f2217b7103e510c0f13f8d5b017afc9`.
- Fidelity checked through: `a81dbca07f2217b7103e510c0f13f8d5b017afc9`.
- Last upstream review: 2026-10-29.
- License: [MIT, copyright 2026 Emil Kowalski](LICENSE), retained from the [pinned upstream license](https://github.com/emilkowalski/skill/blob/a81dbca07f2217b7103e510c0f13f8d5b017afc9/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Upstream's "Initial Response" section is dropped. It made an invocation without a specific question answer with a fixed greeting and wait, which stalls a model invocation mid-task; /reply-shape and /next-options own how replies are laid out and end.
- Redesign routes to `design-prototype`, this library's owner of UI variant prototypes, instead of Emil Kowalski's `prototype`, which overlaps it and is not adopted.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging. The repository's `.prettierignore` keeps `CATALOG.md` byte-identical to upstream, because the formatter would trim the spaces its padded-name test value depends on.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. Emil Kowalski's other skills in the same repository are not tracked; a new one enters only by the adaptation contract's rule for adopting skills. Record adopted, adapted, and excluded changes before advancing the baseline.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                              |
| ---------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-29 | `a81dbca07f2217b7103e510c0f13f8d5b017afc9` | Imported `SKILL.md` and `CATALOG.md` from the revision the Skills CLI had installed; the installed tree hash matched upstream's. Dropped the fixed greeting and routed redesign to `design-prototype`. Repository checks and catalog validation pass. |
