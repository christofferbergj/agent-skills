# reframe: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/reframe/SKILL.md`](https://github.com/cursor/plugins/blob/2dd5c0ccc5b207dc23a69759871a35954082cbf7/pstack/skills/reframe/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `2dd5c0ccc5b207dc23a69759871a35954082cbf7`.
- Reviewed through commit: `41e400932eca14f289e7db717a70455256b6d388`.
- Fidelity checked through: `41e400932eca14f289e7db717a70455256b6d388`.
- Last upstream review: 2026-11-25.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-11-24  | `2dd5c0ccc5b207dc23a69759871a35954082cbf7` | Imported upstream's new skill (#1324, Pstack 0.15.47) as written: learning a field's expert terms and neighboring fields' terms for what the user builds, with checked links, is a job no local skill does; /domain-modeling sharpens a project's own vocabulary, /sharpen rewrites a prompt's depth, and /animation-vocabulary names motion effects only. Kept upstream's name, body, description, and user-invoked mode, which the library-wide Pstack adaptation for skills that hand back rewritten text now names. Packaged with `agents/openai.yaml`, listings, the `suite.json` mapping, and a /pstack-help row taken from upstream's poteto-help row with the _user entrypoint_ tag, as /sharpen's row has. Fidelity check passes in both directions. |
| 2026-11-25  | `41e400932eca14f289e7db717a70455256b6d388` | Adopted upstream `9e278fe` (#1326, Pstack 0.15.48) as written: when the description could name more than one problem, list the two or three it could be, each with its term and the sign that tells it apart, then teach the likeliest and say why. The description and /pstack-help row stay, because upstream changed neither the skill's description nor poteto-help's row. Fidelity check passes in both directions.                                                                                                                                                                                                                                                                                                                                      |
