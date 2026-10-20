# reply-shape: source and local adaptations

## Source and credit

- Original author: Oliver Cederborg.
- Source repository: [olivercederborg/skills](https://github.com/olivercederborg/skills).
- Original skill: [`reply-shape/SKILL.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/reply-shape/SKILL.md), for its sections, decision card, writing rules, and pre-send check.
- Supporting sources: [`reply-shape/references/views.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/reply-shape/references/views.md), [`reply-shape/references/pictures.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/reply-shape/references/pictures.md), and [`reply-shape/scripts/check-mermaid.mjs`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/reply-shape/scripts/check-mermaid.mjs), reviewed and left out below.
- Tracking policy: upstream `main`, reviewed as a principle source under the adaptation contract's [principle-derived skills](../../agents/maintain-skills/references/ADAPTATION.md#principle-derived-skills).
- Imported from commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Reviewed through commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Fidelity checked through: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Last upstream review: 2026-10-20.
- Attribution-only source: https://gist.github.com/olivercederborg/92236670065aaa661db221f22203ded5 is Oliver's handover gist. Its `reply-shape-SKILL.md` matches the tracked file at the imported commit, apart from a catch-up rule that /pstack-ketchup's own rules cover.
- Attribution-only source: https://github.com/humanlayer/skills holds Dex Horthy's `show-me`, whose smallest-view principle, pseudocode and trees with diffs of them, becomes the Views rule. /pr already carries that catalog through Matt Pocock's adaptation, so neither copy is tracked here.
- Attribution-only source: https://github.com/ayghri/i-have-adhd is the ancestor of Oliver's `reply-shape`, imported there at `839872f9d1cd634fed642b4589ce7226199cc15f`. Its rules to lead with state, state errors matter-of-factly, cap lists, and drop preambles, recaps, and closers reach this skill through Oliver's version, which is tracked instead.
- License: [MIT, copyright 2026 Oliver Cederborg, with Ayoub Ghriss's MIT notice for the ancestor](LICENSE). Retain both notices with derived material.

## Local adaptations to preserve

The wording is first-party. These are the principles taken from the source and the deliberate departures.

Adopted principles:

- A status line first, with a traffic-light marker and a bold verdict; questions about which, when, whether, or why get their answer there, and requests to act are done.
- Changed, Needs you with Decide, Review, and Do items, and Details folded per topic with a verdict-first summary.
- A decision card of about twelve lines when a reply exists to get one decision.
- The writing limits: three sentences per paragraph, five visible list items, one picture per turn, one inline code span per sentence, each piece shown once, and the pre-send check.

Departures:

- The ending belongs to /next-options, so this skill keeps only the closing rule above it and defines no next-step or Done format of its own.
- The views and pictures references and the Mermaid checker are left out to keep the rules small enough to load at every session start; the picture rule and the decision card's view keep one line each.
- Oliver's code rule, a small diff after the prose, becomes a Views rule taken from `show-me`: pseudocode and trees, with a diff of that view for a change, and real code only when most of it is new or copyable.
- The Skills line is left out, since it adds a line to every reply without helping the user act on it.
- The rules load through /next-options' SessionStart hook in a second entry with its own hook budget, rather than a second script.

`agents/openai.yaml` and this record are locally maintained.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep. Decide each upstream change to the tracked files by the principle-derived rules. Advance the reviewed-through position only after the delta is decided and checks pass.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                  |
| ----------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-20  | `e8db4fa3e2468a0b9e0297955367ff6efde28dee` | Adapted the reply layout, decision card, writing rules, and pre-send check as principles, with the ending deferred to /next-options. Left out the views and pictures references, the Mermaid checker, and the Skills line. The rules load through /next-options' hook within both hosts' per-hook limits. |
