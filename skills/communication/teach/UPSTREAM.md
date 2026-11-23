# teach: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/teach/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/teach/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9`.
- Fidelity checked through: `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9`.
- Last upstream review: 2026-11-23.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Run /how and /why in parallel through /swarm, and use the host's image-generation tool only when it has one; upstream assumes parallel skill runs and an image tool.

Local maintenance on 2026-10-27: step 5 takes upstream's text again. The divergence that continued the diagram series one diagram per turn under /reply-shape's picture limit is dropped, because /reply-shape now exempts a /teach series from that limit. This local repair leaves the upstream reviewed-through position unchanged.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                             |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `e5136d8`. First fidelity check: the local skill was a rewrite that dropped most upstream rules, including the build-up diagram series, the framing-label and pacing bans, the `why` narrowing contract, the target-density style rules, and the Reply line, and added an unrecorded change-on-request exception. Restored the upstream body with installed names, swarm delegation, and an image-tool condition; recorded the model-invoked mode.               |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 2026-11-16  | `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7` | Adopted upstream's removal of step 2's /why narrowing sentences (the slow full sweep and recorded skipped categories), which the one-file /why no longer has. Kept "Keep /why's confidence language intact", as upstream does. The /swarm and image-tool divergence still holds. Fidelity check passes in both directions.                                                                                                                                                                |
| 2026-11-23  | `7a583913eb1b8d1a0ee76753d1a2cf072e7b54f9` | Closeness re-check against `7a58391` under the owner's rule on #113, no upstream change since `bf0c7cd`. No SKILL.md change. Kept the recorded divergence, /how and /why run in parallel through /swarm and the image tool used only where the host has one, because Claude Code has no image-generation tool; kept as library-wide adaptations the model-invoked description scoped to Pstack tasks and slash invocations of /how, /why, and /unslop. Fidelity holds in both directions. |
