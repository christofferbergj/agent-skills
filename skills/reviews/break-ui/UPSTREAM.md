# break-ui: source and adaptations

## Source and credit

- Original author: Emil Kowalski.
- Canonical source: [emilkowalski/skill](https://github.com/emilkowalski/skill). GitHub now serves the repository as `emilkowalski/skills` and redirects this name, with the same commits (checked 2026-11-14); the record keeps the name it was imported under.
- Original skill and resources: [`skills/break-ui`](https://github.com/emilkowalski/skill/tree/a81dbca07f2217b7103e510c0f13f8d5b017afc9/skills/break-ui), with `SKILL.md` and `CATALOG.md`.
- Tracking policy: upstream `main`; review the listed skill directory and the license.
- Imported from commit: `a81dbca07f2217b7103e510c0f13f8d5b017afc9`.
- Reviewed through commit: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Fidelity checked through: `0f2e23b32bb1265e84cff8d3e75785fec953fb1b`.
- Last upstream review: 2026-11-14.
- License: [MIT, copyright 2026 Emil Kowalski](LICENSE), retained from the [pinned upstream license](https://github.com/emilkowalski/skill/blob/a81dbca07f2217b7103e510c0f13f8d5b017afc9/LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.

`agents/openai.yaml`, this record, and the retained license are locally maintained packaging. The repository's `.prettierignore` keeps `CATALOG.md` byte-identical to upstream, because the formatter would trim the spaces its padded-name test value depends on.

## Maintenance

Compare future upstream changes against the reviewed-through revision for the listed directory and license. Record adopted, adapted, and excluded changes before advancing the baseline.

## Review history

| Date       | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-29 | `a81dbca07f2217b7103e510c0f13f8d5b017afc9` | Imported `SKILL.md` and `CATALOG.md` from the revision the Skills CLI had installed; the installed tree hash matched upstream's. Dropped the fixed greeting and routed redesign to `design-prototype`. Repository checks and catalog validation pass.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 2026-11-14 | `0f2e23b32bb1265e84cff8d3e75785fec953fb1b` | Delta `a81dbca..0f2e23b` on `skills/break-ui/` is `0f2e23b` (#51) alone, which fixes wrong APIs and cross-skill contradictions. Adopted as written: "no limit found" replaces "unbounded", Report before fixing names the fix invocations, Phase 3 gains a completion criterion, the initials fix skips name suffixes and drops the `Jo` example, the clamp row gives the working `-webkit-line-clamp` declarations, and the catalog uses `.test` emails, a firm `1M` compact form, and a 7-day relative-time threshold, drop the two-part `.co.uk` TLD, and remove a stray trailing comma. The license is unchanged. Fidelity passes in both directions: the only differences from upstream are the dropped greeting, the `design-prototype` route, and formatter output. |
| 2026-11-14 | `0f2e23b32bb1265e84cff8d3e75785fec953fb1b` | No upstream change. The greeting and the `design-prototype` route moved to the library-wide adaptations for Emil Kowalski's skills, which the library now adopts as one suite under the catalog's `emil` policy; this skill's text is unchanged. Fidelity passes in both directions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
