# pstack-ketchup-video: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/ketchup-video/SKILL.md`](https://github.com/cursor/plugins/blob/9580c23696ac8d7abed0c166f2f9918800afb819/pstack/skills/ketchup-video/SKILL.md).
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `9580c23696ac8d7abed0c166f2f9918800afb819`.
- Reviewed through commit: `9580c23696ac8d7abed0c166f2f9918800afb819`.
- Fidelity checked through: `9580c23696ac8d7abed0c166f2f9918800afb819`.
- Last upstream review: 2026-10-24.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE), retained from [pstack/LICENSE](https://github.com/cursor/plugins/blob/9580c23696ac8d7abed0c166f2f9918800afb819/pstack/LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Namespace: `ketchup-video` maps to `pstack-ketchup-video`, and its references to `/ketchup` name `/pstack-ketchup`.
- Invocation: model-invoked, where upstream sets `disable-model-invocation: true`. The contract makes Pstack helpers model-invoked, and this skill is not one of its user-invoked entrypoints or outward-effect skills: it writes only the video outside the repository. The description follows /pstack-ketchup's Pstack-scoped style.
- Embedding: the reply links the video file where the host cannot embed one, because a terminal host such as Claude Code's CLI shows no inline video. Upstream assumes an embedding host.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-24  | `9580c23696ac8d7abed0c166f2f9918800afb819` | Imported the new upstream skill (#797): body taken verbatim apart from the installed names and the link fallback for hosts that cannot embed video, with Pstack's license. Adapted the name, invocation mode, and description as recorded above. It invokes /pstack-ketchup, so the README lists that companion. Added its /pstack-help route, mirroring upstream's poteto-help row. Fidelity passes in both directions. |
