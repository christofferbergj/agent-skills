# Engineering

Dependency and linting workflows for JavaScript and TypeScript, plus test audits and branch reviews across languages and runners.

The Thermos skills derive from Cursor's MIT-licensed plugin. See the [source records and manual update procedure](./thermos/MAINTENANCE.md) before incorporating upstream changes.

## User-invoked

- **[thermos](./thermos/SKILL.md)** runs parallel correctness and maintainability reviews using Codex or Claude Code subagents. Install `/thermo-nuclear-review` and `/thermo-nuclear-code-quality-review` with it.

- **[update-dependencies](./update-dependencies/SKILL.md)** — Resolve and validate dependency updates across repositories and monorepos, research releases, and open a pull request when requested. Install `/linting-alignment` with it.

## Model-invoked

- **[thermo-nuclear-review](./thermo-nuclear-review/SKILL.md)** audits correctness, security, developer experience, and feature-gate leaks introduced by a branch.
- **[thermo-nuclear-code-quality-review](./thermo-nuclear-code-quality-review/SKILL.md)** audits maintainability, structural simplification, and architecture boundaries introduced by a branch.

- **[linting-alignment](./linting-alignment/SKILL.md)** — Align lint and formatting policy with its owning presets and tools.
- **[test-audit](./test-audit/SKILL.md)** audits test value and cleans up tests while preserving meaningful contracts. Includes focused reviews and exhaustive repository or monorepo campaigns.

## Pstack adaptation

Install the complete dependency group from the [top-level README](../../README.md#pstack). The [suite maintenance owner](../agents/pstack-mode/MAINTENANCE.md) records shared update and validation contracts.

- [pstack-architect](./pstack-architect/SKILL.md).
- [pstack-arena](./pstack-arena/SKILL.md).
- [pstack-benchmark-checklist](./pstack-benchmark-checklist/SKILL.md).
- [pstack-blast-radius](./pstack-blast-radius/SKILL.md).
- [pstack-create-verification-skill](./pstack-create-verification-skill/SKILL.md).
- [pstack-figure-it-out](./pstack-figure-it-out/SKILL.md).
- [pstack-how](./pstack-how/SKILL.md).
- [pstack-interrogate](./pstack-interrogate/SKILL.md).
- [pstack-maintain-verification-skill](./pstack-maintain-verification-skill/SKILL.md).
- [pstack-make-bot-ui](./pstack-make-bot-ui/SKILL.md).
- [pstack-no-comments](./pstack-no-comments/SKILL.md).
- [pstack-tdd](./pstack-tdd/SKILL.md).
- [pstack-typescript-best-practices](./pstack-typescript-best-practices/SKILL.md).
- [pstack-why](./pstack-why/SKILL.md).
- [pstack-principle-attack-the-premise](./pstack-principle-attack-the-premise/SKILL.md).
- [pstack-principle-boundary-discipline](./pstack-principle-boundary-discipline/SKILL.md).
- [pstack-principle-build-the-lever](./pstack-principle-build-the-lever/SKILL.md).
- [pstack-principle-encode-lessons-in-structure](./pstack-principle-encode-lessons-in-structure/SKILL.md).
- [pstack-principle-exhaust-the-design-space](./pstack-principle-exhaust-the-design-space/SKILL.md).
- [pstack-principle-experience-first](./pstack-principle-experience-first/SKILL.md).
- [pstack-principle-explain-the-number](./pstack-principle-explain-the-number/SKILL.md).
- [pstack-principle-fix-root-causes](./pstack-principle-fix-root-causes/SKILL.md).
- [pstack-principle-foundational-thinking](./pstack-principle-foundational-thinking/SKILL.md).
- [pstack-principle-guard-the-context-window](./pstack-principle-guard-the-context-window/SKILL.md).
- [pstack-principle-laziness-protocol](./pstack-principle-laziness-protocol/SKILL.md).
- [pstack-principle-make-operations-idempotent](./pstack-principle-make-operations-idempotent/SKILL.md).
- [pstack-principle-migrate-callers-then-delete-legacy-apis](./pstack-principle-migrate-callers-then-delete-legacy-apis/SKILL.md).
- [pstack-principle-minimize-reader-load](./pstack-principle-minimize-reader-load/SKILL.md).
- [pstack-principle-model-the-domain](./pstack-principle-model-the-domain/SKILL.md).
- [pstack-principle-never-block-on-the-human](./pstack-principle-never-block-on-the-human/SKILL.md).
- [pstack-principle-outcome-oriented-execution](./pstack-principle-outcome-oriented-execution/SKILL.md).
- [pstack-principle-prove-it-works](./pstack-principle-prove-it-works/SKILL.md).
- [pstack-principle-redesign-from-first-principles](./pstack-principle-redesign-from-first-principles/SKILL.md).
- [pstack-principle-separate-before-serializing-shared-state](./pstack-principle-separate-before-serializing-shared-state/SKILL.md).
- [pstack-principle-sequence-verifiable-units](./pstack-principle-sequence-verifiable-units/SKILL.md).
- [pstack-principle-subtract-before-you-add](./pstack-principle-subtract-before-you-add/SKILL.md).
- [pstack-principle-test-behavior-not-implementation](./pstack-principle-test-behavior-not-implementation/SKILL.md).
- [pstack-principle-type-system-discipline](./pstack-principle-type-system-discipline/SKILL.md).
