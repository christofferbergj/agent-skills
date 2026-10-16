# Agent skills

[![skills.sh](https://skills.sh/b/christofferbergj/agent-skills)](https://skills.sh/christofferbergj/agent-skills)

One skill library for Codex and Claude Code, combining adaptations of Matt Pocock, Pstack, Thermos, and OpenClaw with local workflows.

## Install

Install the complete library from one source:

```bash
npx skills@latest add christofferbergj/agent-skills \
  --skill '*' --global --agent codex claude-code --yes
```

Use `$skill-name` in Codex and `/skill-name` in Claude Code. Installing the library does not activate Pstack mode. [Usage guide](docs/usage.md).

## Start here

| You want to                               | Start with                             |
| ----------------------------------------- | -------------------------------------- |
| Clarify an idea and capture decisions     | `grill-with-docs`                      |
| Write a spec or split it into tickets     | `to-spec`, then `to-tickets` as needed |
| Implement agreed work                     | `implement` or `implement-spec`        |
| Coordinate a substantial engineering task | `pstack-mode`                          |
| Review a change                           | `code-review` or `thermos`             |
| Maintain this library                     | `maintain-skills`                      |

## Browse by task

| Category                                                   | What you will find                                                                                                         |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| [Agent workflows](skills/agents/README.md)                 | Configure agents, coordinate work, maintain skills, and learn from completed sessions.                                     |
| [Planning and design](skills/planning/README.md)           | Understand a codebase, research a problem, clarify requirements, and choose a design.                                      |
| [Implementation and tooling](skills/engineering/README.md) | Build and debug software, configure development tools, and verify behavior.                                                |
| [Reviews](skills/reviews/README.md)                        | Assess code, architecture, tests, performance claims, and the effects of a change.                                         |
| [Writing and explanation](skills/communication/README.md)  | Explain work clearly, write technical documents, and edit prose.                                                           |
| [Principles](skills/principles/README.md)                  | Reusable Pstack principles for design, implementation, verification, and agent execution. Workflows select them as needed. |

[Repository documentation](docs/README.md) · [Contributing](CONTRIBUTING.md)

<details>
<summary>All skills by category</summary>

### Agent workflows

- [audit-agent-documentation](skills/agents/audit-agent-documentation/SKILL.md)
- [chief-of-staff](skills/agents/chief-of-staff/SKILL.md)
- [git-guardrails](skills/agents/git-guardrails/SKILL.md)
- [maintain-skills](skills/agents/maintain-skills/SKILL.md)
- [pstack-automate-me](skills/agents/pstack-automate-me/SKILL.md)
- [pstack-figure-it-out](skills/agents/pstack-figure-it-out/SKILL.md)
- [pstack-help](skills/agents/pstack-help/SKILL.md)
- [pstack-mode](skills/agents/pstack-mode/SKILL.md)
- [pstack-recall](skills/agents/pstack-recall/SKILL.md)
- [pstack-reflect](skills/agents/pstack-reflect/SKILL.md)
- [pstack-setup](skills/agents/pstack-setup/SKILL.md)
- [pstack-show-me-your-work](skills/agents/pstack-show-me-your-work/SKILL.md)
- [pstack-swarm](skills/agents/pstack-swarm/SKILL.md)
- [retro](skills/agents/retro/SKILL.md)
- [setup-matt-pocock-skills](skills/agents/setup-matt-pocock-skills/SKILL.md)
- [wizard](skills/agents/wizard/SKILL.md)
- [writing-for-agents](skills/agents/writing-for-agents/SKILL.md)

### Planning and design

- [codebase-design](skills/planning/codebase-design/SKILL.md)
- [design-prototype](skills/planning/design-prototype/SKILL.md)
- [domain-modeling](skills/planning/domain-modeling/SKILL.md)
- [grill-me](skills/planning/grill-me/SKILL.md)
- [grill-with-docs](skills/planning/grill-with-docs/SKILL.md)
- [grilling](skills/planning/grilling/SKILL.md)
- [improve-codebase-architecture](skills/planning/improve-codebase-architecture/SKILL.md)
- [loop-me](skills/planning/loop-me/SKILL.md)
- [pstack-architect](skills/planning/pstack-architect/SKILL.md)
- [pstack-arena](skills/planning/pstack-arena/SKILL.md)
- [pstack-how](skills/planning/pstack-how/SKILL.md)
- [pstack-sharpen](skills/planning/pstack-sharpen/SKILL.md)
- [pstack-why](skills/planning/pstack-why/SKILL.md)
- [research](skills/planning/research/SKILL.md)
- [to-questionnaire](skills/planning/to-questionnaire/SKILL.md)
- [to-spec](skills/planning/to-spec/SKILL.md)
- [to-tickets](skills/planning/to-tickets/SKILL.md)
- [triage](skills/planning/triage/SKILL.md)
- [wayfinder](skills/planning/wayfinder/SKILL.md)

### Implementation and tooling

- [diagnosing-bugs](skills/engineering/diagnosing-bugs/SKILL.md)
- [implement](skills/engineering/implement/SKILL.md)
- [implement-spec](skills/engineering/implement-spec/SKILL.md)
- [linting-alignment](skills/engineering/linting-alignment/SKILL.md)
- [pstack-correct](skills/engineering/pstack-correct/SKILL.md)
- [pstack-create-verification-skill](skills/engineering/pstack-create-verification-skill/SKILL.md)
- [pstack-maintain-verification-skill](skills/engineering/pstack-maintain-verification-skill/SKILL.md)
- [pstack-make-bot-ui](skills/engineering/pstack-make-bot-ui/SKILL.md)
- [pstack-tdd](skills/engineering/pstack-tdd/SKILL.md)
- [pstack-typescript-best-practices](skills/engineering/pstack-typescript-best-practices/SKILL.md)
- [setup-pre-commit](skills/engineering/setup-pre-commit/SKILL.md)
- [setup-ts-deep-modules](skills/engineering/setup-ts-deep-modules/SKILL.md)
- [tdd](skills/engineering/tdd/SKILL.md)
- [update-dependencies](skills/engineering/update-dependencies/SKILL.md)

### Reviews

- [code-review](skills/reviews/code-review/SKILL.md)
- [pstack-benchmark-checklist](skills/reviews/pstack-benchmark-checklist/SKILL.md)
- [pstack-blast-radius](skills/reviews/pstack-blast-radius/SKILL.md)
- [pstack-interrogate](skills/reviews/pstack-interrogate/SKILL.md)
- [pstack-no-comments](skills/reviews/pstack-no-comments/SKILL.md)
- [test-audit](skills/reviews/test-audit/SKILL.md)
- [thermo-nuclear-code-quality-review](skills/reviews/thermo-nuclear-code-quality-review/SKILL.md)
- [thermo-nuclear-review](skills/reviews/thermo-nuclear-review/SKILL.md)
- [thermos](skills/reviews/thermos/SKILL.md)

### Writing and explanation

- [bro](skills/communication/bro/SKILL.md)
- [pr](skills/communication/pr/SKILL.md)
- [pstack-in-your-own-words](skills/communication/pstack-in-your-own-words/SKILL.md)
- [pstack-ketchup](skills/communication/pstack-ketchup/SKILL.md)
- [pstack-teach](skills/communication/pstack-teach/SKILL.md)
- [pstack-technical-writing](skills/communication/pstack-technical-writing/SKILL.md)
- [pstack-unslop](skills/communication/pstack-unslop/SKILL.md)

### Principles

- [pstack-principle-attack-the-premise](skills/principles/pstack-principle-attack-the-premise/SKILL.md)
- [pstack-principle-boundary-discipline](skills/principles/pstack-principle-boundary-discipline/SKILL.md)
- [pstack-principle-build-the-lever](skills/principles/pstack-principle-build-the-lever/SKILL.md)
- [pstack-principle-encode-lessons-in-structure](skills/principles/pstack-principle-encode-lessons-in-structure/SKILL.md)
- [pstack-principle-exhaust-the-design-space](skills/principles/pstack-principle-exhaust-the-design-space/SKILL.md)
- [pstack-principle-experience-first](skills/principles/pstack-principle-experience-first/SKILL.md)
- [pstack-principle-explain-the-number](skills/principles/pstack-principle-explain-the-number/SKILL.md)
- [pstack-principle-fix-root-causes](skills/principles/pstack-principle-fix-root-causes/SKILL.md)
- [pstack-principle-foundational-thinking](skills/principles/pstack-principle-foundational-thinking/SKILL.md)
- [pstack-principle-guard-the-context-window](skills/principles/pstack-principle-guard-the-context-window/SKILL.md)
- [pstack-principle-laziness-protocol](skills/principles/pstack-principle-laziness-protocol/SKILL.md)
- [pstack-principle-make-operations-idempotent](skills/principles/pstack-principle-make-operations-idempotent/SKILL.md)
- [pstack-principle-migrate-callers-then-delete-legacy-apis](skills/principles/pstack-principle-migrate-callers-then-delete-legacy-apis/SKILL.md)
- [pstack-principle-minimize-reader-load](skills/principles/pstack-principle-minimize-reader-load/SKILL.md)
- [pstack-principle-model-the-domain](skills/principles/pstack-principle-model-the-domain/SKILL.md)
- [pstack-principle-never-block-on-the-human](skills/principles/pstack-principle-never-block-on-the-human/SKILL.md)
- [pstack-principle-outcome-oriented-execution](skills/principles/pstack-principle-outcome-oriented-execution/SKILL.md)
- [pstack-principle-prove-it-works](skills/principles/pstack-principle-prove-it-works/SKILL.md)
- [pstack-principle-redesign-from-first-principles](skills/principles/pstack-principle-redesign-from-first-principles/SKILL.md)
- [pstack-principle-separate-before-serializing-shared-state](skills/principles/pstack-principle-separate-before-serializing-shared-state/SKILL.md)
- [pstack-principle-sequence-verifiable-units](skills/principles/pstack-principle-sequence-verifiable-units/SKILL.md)
- [pstack-principle-subtract-before-you-add](skills/principles/pstack-principle-subtract-before-you-add/SKILL.md)
- [pstack-principle-test-behavior-not-implementation](skills/principles/pstack-principle-test-behavior-not-implementation/SKILL.md)
- [pstack-principle-type-system-discipline](skills/principles/pstack-principle-type-system-discipline/SKILL.md)

</details>

<details>
<summary>Required companions for smaller installations</summary>

Skills CLI does not install dependencies transitively. The complete-library install includes these companions; composed workflows can invoke further helpers.

| Entrypoint                    | Required companions                                                           |
| ----------------------------- | ----------------------------------------------------------------------------- |
| `audit-agent-documentation`   | `writing-for-agents`                                                          |
| `update-dependencies`         | `linting-alignment` when the lint or formatting stack changes                 |
| `maintain-skills`             | `writing-for-agents`, `pstack-swarm` |
| `thermos`                     | `thermo-nuclear-review`, `thermo-nuclear-code-quality-review`                 |
| `grill-me`                    | `grilling`                                                                    |
| `grill-with-docs`             | `grilling`, `domain-modeling`                                                 |
| `implement`, `implement-spec` | `tdd`, `code-review`, `domain-modeling`, `pstack-swarm`                       |
| Pstack architecture           | `codebase-design`, `domain-modeling`, and the Pstack design/execution helpers |
| `pstack-tdd`                  | `tdd`                                                                         |
| `tdd`                         | `domain-modeling`                                                             |
| Pstack PR delivery            | `pr`                                                                          |
| `research`, `code-review`     | `pstack-swarm`                                                                |
| `pr`                          | `domain-modeling`                                                             |
| `setup-pre-commit`            | `linting-alignment` when tool ownership needs resolution                      |

</details>

## License

[MIT](LICENSE). Adapted skills retain the notices and `UPSTREAM.md` records for Matt Pocock, Lauren Tan, Cursor, and the OpenClaw Foundation inside their own directories.
