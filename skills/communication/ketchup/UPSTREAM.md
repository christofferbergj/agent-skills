# ketchup: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/ketchup/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/ketchup/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Render visuals with the host's available tools, falling back to links or plain text; upstream names `/visualize`.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                  |
| 2026-10-18  | `0b8e952052d482ee6de06deebf14d590d77b1b34` | Adapted the complete action-item coverage revision: size the reply to pending decisions, preserve every item and its evidence and risk, and keep the progress story short. Preserved the local name, model invocation, read-only recap scope, and plain-language owner reference. The former blanket 150-word cap is removed. Clarified automatic invocation and host rendering, and kept the recap read-only within an ongoing task. Independent grouped-decision, unavailable-media, and unchanged-state fixtures and repository gates pass. |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change since `0b8e952`. Checked current tools and conventions: no named tool, link, or Codex policy is stale, and /bro is cited for its voice only. Checked consistency with /reply-shape: its catch-up exemption covers every waiting call and captured screenshots and videos; drawn diagrams (up to six boxes, possibly several) are not exempt, raised as an owner question. Removed a record line that described upstream's own word budget rather than a divergence.                                                         |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | Dropped divergences now covered by the library-wide adaptations (#18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
