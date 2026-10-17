# Agent skills

[![skills.sh](https://skills.sh/b/christofferbergj/agent-skills)](https://skills.sh/christofferbergj/agent-skills)

Personal agent skills for planning, building, reviewing, and explaining software.

## Install

Install the complete library and choose your agents when prompted:

```bash
npx skills@latest add christofferbergj/agent-skills \
  --skill '*' --global
```

Invoke skills through your agent's skill picker or command syntax. [Usage guide and compatibility](docs/usage.md).

## Start here

For a feature, use `grill-with-docs` → `to-spec` → `to-tickets` → `implement-spec`. Skip stages that are already settled. Relevant Pstack principles apply automatically throughout this flow.

| You want to                               | Start with                             |
| ----------------------------------------- | -------------------------------------- |
| Clarify an idea and capture decisions     | `grill-with-docs`                      |
| Write a spec or split it into tickets     | `to-spec`, then `to-tickets` as needed |
| Implement agreed work                     | `implement` or `implement-spec`        |
| Let the agent choose and drive a workflow | `pstack-mode`                          |
| Review a change                           | `code-review` or `thermos`             |
| Maintain this library                     | `maintain-skills`                      |

## Browse by task

| Category                                                   | What you will find                                                                     |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| [Agent workflows](skills/agents/README.md)                 | Configure agents, coordinate work, maintain skills, and learn from completed sessions. |
| [Planning and design](skills/planning/README.md)           | Understand a codebase, research a problem, clarify requirements, and choose a design.  |
| [Implementation and tooling](skills/engineering/README.md) | Build and debug software, configure development tools, and verify behavior.            |
| [Reviews](skills/reviews/README.md)                        | Assess code, architecture, tests, performance claims, and the effects of a change.     |
| [Writing and explanation](skills/communication/README.md)  | Explain work clearly, write technical documents, and edit prose.                       |
| [Principles](skills/principles/README.md)                  | Design and coding principles selected by the workflows.                                |

[How the library fits together](docs/architecture.md) · [Repository documentation](docs/README.md) · [Contributing](CONTRIBUTING.md)

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
- [pstack-principles](skills/agents/pstack-principles/SKILL.md)
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

Skills CLI does not install dependencies transitively. Install each companion's own companions too, including conditional ones before taking that branch. The complete-library install covers every row. Use it for unrestricted `pstack-mode` playbooks, which select further helpers as the task develops.

| Skill                                                                                                                               | Required companions                                                                         | Conditional companions                                                                                                                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `audit-agent-documentation`                                                                                                         | `writing-for-agents`                                                                        |                                                                                                                                                                                                  |
| `chief-of-staff`, `research`                                                                                                        | `pstack-swarm`                                                                              |                                                                                                                                                                                                  |
| `maintain-skills`                                                                                                                   | `writing-for-agents`, `pstack-swarm`                                                        |                                                                                                                                                                                                  |
| `retro`                                                                                                                             | `domain-modeling`, `writing-for-agents`                                                     | `pstack-swarm` for delegation; `pstack-recall` for other sessions                                                                                                                                |
| `setup-matt-pocock-skills`                                                                                                          | `domain-modeling`                                                                           | `codebase-design` for architecture work through the generated domain guidance                                                                                                                    |
| `setup-ts-deep-modules`                                                                                                             | `codebase-design`                                                                           | `domain-modeling` for changed project ownership or vocabulary                                                                                                                                    |
| `thermos`                                                                                                                           | `thermo-nuclear-review`, `thermo-nuclear-code-quality-review`                               |                                                                                                                                                                                                  |
| `grill-me`                                                                                                                          | `grilling`                                                                                  |                                                                                                                                                                                                  |
| `grill-with-docs`                                                                                                                   | `grilling`, `domain-modeling`                                                               |                                                                                                                                                                                                  |
| `grilling`                                                                                                                          | `pstack-principles`                                                                         |                                                                                                                                                                                                  |
| `codebase-design`                                                                                                                   |                                                                                             | `domain-modeling` for accepted project-model changes; `pstack-arena` for interface alternatives                                                                                                  |
| `design-prototype`, `diagnosing-bugs`                                                                                               | `domain-modeling`                                                                           | `pstack-swarm` for delegation                                                                                                                                                                    |
| `improve-codebase-architecture`                                                                                                     | `domain-modeling`, `codebase-design`, `pstack-swarm`, `grilling`                            |                                                                                                                                                                                                  |
| `loop-me`                                                                                                                           | `domain-modeling`, `grilling`                                                               | `pstack-swarm` for delegation                                                                                                                                                                    |
| `to-spec`                                                                                                                           | `domain-modeling`, `pstack-principles`                                                      | `pstack-swarm` for delegation                                                                                                                                                                    |
| `to-tickets`                                                                                                                        | `domain-modeling`, `pstack-principles`                                                      | `pstack-swarm` for delegation; `pstack-principle-migrate-callers-then-delete-legacy-apis` for coordinated migration tickets                                                                      |
| `implement`                                                                                                                         | `code-review`, `domain-modeling`, `pstack-principles`                                       | `tdd` where a useful test path exists; `pstack-swarm` for delegation; `pr` for authorized PR delivery                                                                                            |
| `implement-spec`                                                                                                                    | `tdd`, `code-review`, `domain-modeling`, `pstack-principles`, `pstack-swarm`                | `pr` for authorized PR delivery; `pstack-principle-migrate-callers-then-delete-legacy-apis` for coupled migrations                                                                               |
| `triage`                                                                                                                            | `domain-modeling`                                                                           | `grilling` for unclear requests; `pstack-swarm` for delegation                                                                                                                                   |
| `wayfinder`                                                                                                                         | `domain-modeling`, `grilling`                                                               | `research` for research tickets; `design-prototype` for prototype tickets; `pstack-swarm` for delegation                                                                                         |
| `tdd`                                                                                                                               | `domain-modeling`, `pstack-principles`, `pstack-principle-test-behavior-not-implementation` | `codebase-design` for interface or seam decisions                                                                                                                                                |
| `code-review`                                                                                                                       | `pstack-swarm`, `pstack-principles`                                                         |                                                                                                                                                                                                  |
| `pr`                                                                                                                                | `domain-modeling`                                                                           |                                                                                                                                                                                                  |
| `setup-pre-commit`                                                                                                                  |                                                                                             | `linting-alignment` when tool ownership is unclear                                                                                                                                               |
| `update-dependencies`                                                                                                               |                                                                                             | `linting-alignment` for an included lint or formatting stack update                                                                                                                              |
| `pstack-mode`                                                                                                                       | `domain-modeling`, `pstack-principles`, `pstack-swarm`                                      | Install the complete library for all playbooks                                                                                                                                                   |
| `pstack-architect`                                                                                                                  | `codebase-design`, `domain-modeling`, `pstack-principles`, `pstack-arena`                   | `pstack-how` for existing-system grounding; `pstack-why` when ownership, layering, or historical constraints change; `tdd` at agreed public seams when useful                                    |
| `pstack-arena`                                                                                                                      | `pstack-swarm`                                                                              |                                                                                                                                                                                                  |
| `pstack-no-comments`                                                                                                                | `pstack-swarm`                                                                              | `pstack-how` or `pstack-why` for disputed comment explanations                                                                                                                                   |
| `pstack-automate-me`                                                                                                                | `pstack-recall`                                                                             | `pstack-correct` for recurring mistakes                                                                                                                                                          |
| `pstack-figure-it-out`                                                                                                              | `pstack-swarm`, `pstack-show-me-your-work`, `pstack-ketchup`                                | `pstack-how`, `pstack-why` for grounding; `pstack-architect`, `pstack-arena` for contested boundaries                                                                                            |
| `pstack-how`                                                                                                                        | `domain-modeling`, `pstack-swarm`                                                           |                                                                                                                                                                                                  |
| `pstack-why`                                                                                                                        | `domain-modeling`, `pstack-how`, `pstack-swarm`                                             |                                                                                                                                                                                                  |
| `pstack-blast-radius`                                                                                                               | `domain-modeling`, `pstack-unslop`                                                          | `pstack-how`, `pstack-why` for explanation; `pstack-arena` for consequential changes                                                                                                             |
| `pstack-interrogate`                                                                                                                | `domain-modeling`, `pstack-swarm`                                                           | `code-review` for Standards/Spec coverage; `pstack-principle-migrate-callers-then-delete-legacy-apis` for migration gates                                                                        |
| `pstack-create-verification-skill`                                                                                                  | `domain-modeling`                                                                           |                                                                                                                                                                                                  |
| `pstack-maintain-verification-skill`                                                                                                | `domain-modeling`, `pstack-swarm`                                                           |                                                                                                                                                                                                  |
| `pstack-recall`                                                                                                                     | `pstack-unslop`                                                                             | `pstack-why` for disputed decisions                                                                                                                                                              |
| `pstack-teach`                                                                                                                      | `pstack-unslop`                                                                             | `pstack-how` for behavior, `pstack-why` for rationale, at least one; `pstack-swarm` for useful independent investigations                                                                        |
| `pstack-technical-writing`                                                                                                          | `pstack-unslop`                                                                             |                                                                                                                                                                                                  |
| `pstack-reflect`                                                                                                                    | `pstack-swarm`                                                                              | `pstack-recall` when the active conversation is unavailable                                                                                                                                      |
| `pstack-show-me-your-work`                                                                                                          | `pstack-unslop`, `pstack-swarm`                                                             | `pstack-recall` for scoped session evidence                                                                                                                                                      |
| `pstack-ketchup`                                                                                                                    | `bro`                                                                                       |                                                                                                                                                                                                  |
| `pstack-tdd`                                                                                                                        | `tdd`                                                                                       |                                                                                                                                                                                                  |
| `pstack-typescript-best-practices`                                                                                                  | `pstack-principle-type-system-discipline`                                                   | `pstack-principle-boundary-discipline` for boundary validation                                                                                                                                   |
| `pstack-principles`                                                                                                                 | All `pstack-principle-*` skills                                                             | `domain-modeling` for accepted domain changes; install the selected principles' companions below                                                                                                 |
| `pstack-principle-boundary-discipline`, `pstack-principle-foundational-thinking`, `pstack-principle-redesign-from-first-principles` |                                                                                             | `codebase-design` for module/interface reasoning; `domain-modeling` for accepted terminology, relationships, or ownership changes                                                                |
| `pstack-principle-model-the-domain`                                                                                                 |                                                                                             | `domain-modeling` when resolving project terminology, relationships, invariants, or ownership                                                                                                    |
| `pstack-principle-type-system-discipline`                                                                                           |                                                                                             | `pstack-typescript-best-practices` for TypeScript syntax; `pstack-principle-boundary-discipline` for external-data parsing; `pstack-principle-encode-lessons-in-structure` for schema derivation |
| `pstack-principle-explain-the-number`                                                                                               |                                                                                             | `pstack-benchmark-checklist` for performance numbers                                                                                                                                             |
| `pstack-principle-prove-it-works`                                                                                                   |                                                                                             | `pstack-show-me-your-work` for large or complex work requiring an auditable trail                                                                                                                |
| `pstack-principle-attack-the-premise`                                                                                               | `pstack-principle-build-the-lever`, `pstack-principle-laziness-protocol`                    | `pstack-principle-fix-root-causes` when the premise is confirmed                                                                                                                                 |
| `pstack-principle-build-the-lever`                                                                                                  | `pstack-principle-laziness-protocol`                                                        | `pstack-principle-prove-it-works` for scripting verification itself                                                                                                                              |
| `pstack-principle-outcome-oriented-execution`                                                                                       |                                                                                             | `pstack-principle-migrate-callers-then-delete-legacy-apis` for migrations with old and new contracts                                                                                             |
| `pstack-principle-sequence-verifiable-units`                                                                                        |                                                                                             | `pstack-principle-migrate-callers-then-delete-legacy-apis` for coupled migrations                                                                                                                |

</details>

## License

[MIT](LICENSE). Adapted skills retain the notices and `UPSTREAM.md` records for Matt Pocock, Lauren Tan, Cursor, and the OpenClaw Foundation inside their own directories.
