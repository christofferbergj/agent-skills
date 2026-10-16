# Library architecture

This repository owns one skill library, combining upstream adaptations with local workflows. Skills are grouped by task under `skills/<category>/<skill-name>/`, rather than by author. The [usage guide](usage.md) explains which workflow to choose; each `SKILL.md` defines its behavior.

## Sources and adaptations

| Source                                                                    | What it contributes                                                                            |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [Matt Pocock's skills](https://github.com/mattpocock/skills)              | Interviews, domain modeling, specs, tickets, implementation, and shared engineering workflows. |
| [Lauren Tan's Pstack](https://github.com/cursor/plugins/tree/main/pstack) | Task playbooks, design and coding principles, evidence requirements, and specialist helpers.   |
| [Cursor's Thermos](https://github.com/cursor/plugins/tree/main/thermos)   | Independent correctness and maintainability review rubrics.                                    |
| [OpenClaw](https://github.com/openclaw/openclaw)                          | The source material adapted into `test-audit`.                                                 |

These are owned adaptations, not live mirrors. Local changes translate Cursor-specific execution into supported host tools, preserve explicit user entrypoints, bound delegation, and connect shared artifacts and principles. First-party skills such as `pstack-principles` supply integration behavior. Each derived skill's `UPSTREAM.md` records its exact source, imported and reviewed revisions, local adaptations, and decisions; its `LICENSE` retains the upstream notice. Additional inherited credits stay with their owning skill.

Matt's `prototype` is named `design-prototype` to coexist with Emil Kowalski's separate `prototype`; `git-guardrails-claude-code` becomes `git-guardrails`. Pstack names use the `pstack-` prefix, apart from the reused `bro`. The [catalog](../skills/agents/maintain-skills/catalog.json) records Matt's mappings, upstream stages, and exclusions; Pstack's [suite index](../skills/agents/pstack-mode/suite.json) owns its mapping. Personal and course-specific Matt skills, explicit user retirements, and Pstack's dormant Benny service workflows remain excluded.

## How the workflows compose

Matt's familiar flow is `grill-with-docs` → `to-spec` → `to-tickets` → `implement-spec`. Its interview, planning, implementation, testing, and review owners invoke `/pstack-principles` in the current phase and before completion. The selector discovers installed principle descriptions, reads the applicable owners, and passes their resolved instructions to workers. Each principle keeps its rules in one place; the selector does not contain a second rule list.

`pstack-mode` is an explicit alternative coordinator for choosing and executing a task playbook. It uses the same selector and shared owners. It can implement an existing accepted spec and ticket graph, so switching coordinators does not start another planning process. Installation or an individual helper invocation does not activate the mode.

| Responsibility                                            | Shared owner         |
| --------------------------------------------------------- | -------------------- |
| Project vocabulary, domain artifacts, and qualifying ADRs | `/domain-modeling`   |
| Architecture vocabulary and interface depth               | `/codebase-design`   |
| Red/green testing mechanics                               | `/tdd`               |
| Standards and spec review                                 | `/code-review`       |
| PR descriptions                                           | `/pr`                |
| Host delegation, writer isolation, and review fallback    | `/pstack-swarm`      |
| Principle selection and composition                       | `/pstack-principles` |
| Whole-library upkeep and upstream review                  | `/maintain-skills`   |

Principles operate within the calling phase and accepted scope. An interview retains its confirmation boundary; planning does not become implementation. Migration strategy belongs to `/pstack-principle-migrate-callers-then-delete-legacy-apis`, and test-quality criteria belong to `/pstack-principle-test-behavior-not-implementation`; workflow owners defer to them rather than prescribing competing rules. Runtime proof uses the actual user or caller path through available tools, including browser or Computer Use controls when available. Missing proof remains an explicit gap.

## Shared project artifacts

`/domain-modeling` resolves the invoking project's conventions. New projects default to `GLOSSARY.md`, optional `GLOSSARY-MAP.md`, and `docs/adr/`; existing `context.md`, `CONTEXT.md`, or domain-model files retain their roles and names. Setup's `docs/agents/domain.md` points agents to these artifacts; it is consumer guidance, not a second domain model.

Both flows preserve one accepted spec and ticket graph. The coordinator reconciles canonical documents while delegates return proposals. Setup, personal model preferences, mutable runtime caches, and private execution history stay separate from installed instructions. Host-dependent workflows check their actual capabilities; installation alone does not establish runtime compatibility. See [agent compatibility](usage.md#agent-compatibility) and the [validation history](reviews/README.md) for tested branches and limits.

## Maintenance and publication

`/maintain-skills` discovers every local skill and its provenance, including first-party skills, unmapped sources, and future additions. The suite catalog adds integration and import policy; it does not limit coverage. One coordinator uses active subagents to inspect local skills, immutable upstream candidates, supporting resources, and consumers across families. Useful changes are adopted selectively while preserving documented local adaptations.

The [maintenance guide](../skills/agents/maintain-skills/MAINTENANCE.md) owns comparisons, checks, checkpoints, and baseline advancement. The [versioned scheduled prompt](../skills/agents/maintain-skills/references/scheduled-prompt.md) defines the recurring task's scope; saved automation settings own its cadence and model. Incomplete reviews retain their baselines. The scheduled task prepares a validated draft PR; merging and refreshing global installations require separate authorization.

Skills CLI installs snapshots of this repository, including each skill's supporting files. Refresh from this repository after publication; installing same-named upstream copies over the adaptations loses the integration. The [main README](../README.md#install) owns installation and required companion skills, [Contributing](../CONTRIBUTING.md) owns repository checks, and the [ADRs](adr/README.md) preserve design rationale. Dated research and review records are evidence for their recorded snapshots, not current operating instructions.
