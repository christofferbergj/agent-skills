# pstack-setup: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/setup-pstack/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/setup-pstack/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `99b609a72323b70204eab407c622f436e858e112`.
- Last upstream review: 2026-10-25.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Writes personal JSON at `~/.config/pstack/config.json`, or `PSTACK_CONFIG`, with one section per host, instead of Cursor's always-applied `pstack-models.mdc` rule. Repository overrides apply only when explicitly configured. Both hosts read the file; neither has always-applied rules.
- Effort is a separate option checked against the host's supported values, not a slug suffix, so the four budget labels and the slug-ladder fallback become a task budget mapped through those options.
- Panel role lists and the arena cross-judge pool are not configured here. /pstack-arena and its callers choose runners and a different-vendor judge through /pstack-swarm.
- Adds an optional review timeout and keeps credentials in the providers' stores.
- Asks for the counterpart reviewer's provider instance, model, full and delta effort, and speed, the Computer Use delegate's settings, and the Codex usage thresholds. /pstack-swarm's `scripts/target.py` resolves them on every route; only the provider instance is specific to its T3 route.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                              |
| 2026-10-20  | `88d47514b82e7c44f00f2b2a72ff6dd12158038c` | Adapted the formal-verification offer as an explicit user entrypoint when consequential properties lack suitable checks. Preserved personal host-separated configuration, inherited model defaults, and existing scope/authority. Reviewed the complete source delta and shared guide; cold formal-maintenance fixtures, repository gates and independent native review pass.                                                                              |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `88d4751`. First fidelity check: restored three dropped upstream rules (ask for models when none can be detected, drop and list retired roles, offer each verification skill once without pressing), recorded the config, effort, and panel host translations, and corrected the `review` entry note: every counterpart route reads it.                                                                                           |
| 2026-10-25  | `99b609a72323b70204eab407c622f436e858e112` | No upstream change in `pstack/skills/setup-pstack/` since `190d287`. Audited local commit `b3e012e` (#25). Step 3's added questions (Codex speed, the Computer Use delegate's settings, and the usage thresholds) and its pointer to /pstack-swarm's `scripts/target.py --help`, whose help lists those keys, are the recorded divergence. Every upstream rule survives or has a recorded divergence, and every recorded divergence is present and needed. |
