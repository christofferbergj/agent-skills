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

For a feature or a bug, start with `pstack-mode` and give it the goal and how you will know it works. It plans through code: open design questions get prototypes and `architect` sketches rather than a written plan. When an effort should be written down and split into tickets first, use `grill-with-docs` → `to-spec` → `to-tickets` → `implement-spec`; `pstack-mode` can pick up the accepted spec and tickets. Relevant Pstack principles apply in both, and implementation ends with `review-loop`, where the other vendor's model reviews the change and the agent fixes what holds until a round is clean.

| You want to                               | Start with                                 |
| ----------------------------------------- | ------------------------------------------ |
| Build a feature or fix a bug              | `pstack-mode`                              |
| Clarify an idea and capture decisions     | `grill-with-docs`                          |
| Write a spec or split it into tickets     | `to-spec`, then `to-tickets` as needed     |
| Implement agreed work                     | `implement` or `implement-spec`            |
| Review a change                           | `review-loop`, `code-review`, or `thermos` |
| End replies with the next step or choices | `next-options`                             |
| Shape replies for skimming and action     | `reply-shape`                              |
| Maintain this library                     | `maintain-skills`                          |

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
- [automate-me](skills/agents/automate-me/SKILL.md)
- [chief-of-staff](skills/agents/chief-of-staff/SKILL.md)
- [figure-it-out](skills/agents/figure-it-out/SKILL.md)
- [git-guardrails](skills/agents/git-guardrails/SKILL.md)
- [maintain-skills](skills/agents/maintain-skills/SKILL.md)
- [principles](skills/agents/principles/SKILL.md)
- [pstack-help](skills/agents/pstack-help/SKILL.md)
- [pstack-mode](skills/agents/pstack-mode/SKILL.md)
- [pstack-setup](skills/agents/pstack-setup/SKILL.md)
- [recall](skills/agents/recall/SKILL.md)
- [reflect](skills/agents/reflect/SKILL.md)
- [retro](skills/agents/retro/SKILL.md)
- [setup-matt-pocock-skills](skills/agents/setup-matt-pocock-skills/SKILL.md)
- [show-me-your-work](skills/agents/show-me-your-work/SKILL.md)
- [swarm](skills/agents/swarm/SKILL.md)
- [wizard](skills/agents/wizard/SKILL.md)
- [writing-for-agents](skills/agents/writing-for-agents/SKILL.md)

### Planning and design

- [architect](skills/planning/architect/SKILL.md)
- [arena](skills/planning/arena/SKILL.md)
- [codebase-design](skills/planning/codebase-design/SKILL.md)
- [design-prototype](skills/planning/design-prototype/SKILL.md)
- [domain-modeling](skills/planning/domain-modeling/SKILL.md)
- [grill-me](skills/planning/grill-me/SKILL.md)
- [grill-with-docs](skills/planning/grill-with-docs/SKILL.md)
- [grilling](skills/planning/grilling/SKILL.md)
- [how](skills/planning/how/SKILL.md)
- [improve-codebase-architecture](skills/planning/improve-codebase-architecture/SKILL.md)
- [loop-me](skills/planning/loop-me/SKILL.md)
- [research](skills/planning/research/SKILL.md)
- [sharpen](skills/planning/sharpen/SKILL.md)
- [to-questionnaire](skills/planning/to-questionnaire/SKILL.md)
- [to-spec](skills/planning/to-spec/SKILL.md)
- [to-tickets](skills/planning/to-tickets/SKILL.md)
- [triage](skills/planning/triage/SKILL.md)
- [wayfinder](skills/planning/wayfinder/SKILL.md)
- [why](skills/planning/why/SKILL.md)

### Implementation and tooling

- [correct](skills/engineering/correct/SKILL.md)
- [create-formal-verification-skill](skills/engineering/create-formal-verification-skill/SKILL.md)
- [create-verification-skill](skills/engineering/create-verification-skill/SKILL.md)
- [diagnosing-bugs](skills/engineering/diagnosing-bugs/SKILL.md)
- [implement](skills/engineering/implement/SKILL.md)
- [implement-spec](skills/engineering/implement-spec/SKILL.md)
- [linting-alignment](skills/engineering/linting-alignment/SKILL.md)
- [maintain-formal-verification-skill](skills/engineering/maintain-formal-verification-skill/SKILL.md)
- [maintain-verification-skill](skills/engineering/maintain-verification-skill/SKILL.md)
- [make-bot-ui](skills/engineering/make-bot-ui/SKILL.md)
- [pstack-tdd](skills/engineering/pstack-tdd/SKILL.md)
- [setup-pre-commit](skills/engineering/setup-pre-commit/SKILL.md)
- [setup-ts-deep-modules](skills/engineering/setup-ts-deep-modules/SKILL.md)
- [statechart](skills/engineering/statechart/SKILL.md)
- [tdd](skills/engineering/tdd/SKILL.md)
- [typescript-best-practices](skills/engineering/typescript-best-practices/SKILL.md)
- [update-dependencies](skills/engineering/update-dependencies/SKILL.md)

### Reviews

- [benchmark-checklist](skills/reviews/benchmark-checklist/SKILL.md)
- [blast-radius](skills/reviews/blast-radius/SKILL.md)
- [code-review](skills/reviews/code-review/SKILL.md)
- [interrogate](skills/reviews/interrogate/SKILL.md)
- [no-comments](skills/reviews/no-comments/SKILL.md)
- [review-loop](skills/reviews/review-loop/SKILL.md)
- [test-audit](skills/reviews/test-audit/SKILL.md)
- [thermo-nuclear-code-quality-review](skills/reviews/thermo-nuclear-code-quality-review/SKILL.md)
- [thermo-nuclear-review](skills/reviews/thermo-nuclear-review/SKILL.md)
- [thermos](skills/reviews/thermos/SKILL.md)

### Writing and explanation

- [bro](skills/communication/bro/SKILL.md)
- [in-your-own-words](skills/communication/in-your-own-words/SKILL.md)
- [ketchup](skills/communication/ketchup/SKILL.md)
- [ketchup-video](skills/communication/ketchup-video/SKILL.md)
- [next-options](skills/communication/next-options/SKILL.md)
- [pr](skills/communication/pr/SKILL.md)
- [reply-shape](skills/communication/reply-shape/SKILL.md)
- [teach](skills/communication/teach/SKILL.md)
- [technical-writing](skills/communication/technical-writing/SKILL.md)
- [unslop](skills/communication/unslop/SKILL.md)

### Principles

- [principle-attack-the-premise](skills/principles/principle-attack-the-premise/SKILL.md)
- [principle-boundary-discipline](skills/principles/principle-boundary-discipline/SKILL.md)
- [principle-build-the-lever](skills/principles/principle-build-the-lever/SKILL.md)
- [principle-encode-lessons-in-structure](skills/principles/principle-encode-lessons-in-structure/SKILL.md)
- [principle-exhaust-the-design-space](skills/principles/principle-exhaust-the-design-space/SKILL.md)
- [principle-experience-first](skills/principles/principle-experience-first/SKILL.md)
- [principle-explain-the-number](skills/principles/principle-explain-the-number/SKILL.md)
- [principle-fix-root-causes](skills/principles/principle-fix-root-causes/SKILL.md)
- [principle-foundational-thinking](skills/principles/principle-foundational-thinking/SKILL.md)
- [principle-guard-the-context-window](skills/principles/principle-guard-the-context-window/SKILL.md)
- [principle-laziness-protocol](skills/principles/principle-laziness-protocol/SKILL.md)
- [principle-make-operations-idempotent](skills/principles/principle-make-operations-idempotent/SKILL.md)
- [principle-migrate-callers-then-delete-legacy-apis](skills/principles/principle-migrate-callers-then-delete-legacy-apis/SKILL.md)
- [principle-minimize-reader-load](skills/principles/principle-minimize-reader-load/SKILL.md)
- [principle-model-the-domain](skills/principles/principle-model-the-domain/SKILL.md)
- [principle-never-block-on-the-human](skills/principles/principle-never-block-on-the-human/SKILL.md)
- [principle-outcome-oriented-execution](skills/principles/principle-outcome-oriented-execution/SKILL.md)
- [principle-prove-it-works](skills/principles/principle-prove-it-works/SKILL.md)
- [principle-redesign-from-first-principles](skills/principles/principle-redesign-from-first-principles/SKILL.md)
- [principle-separate-before-serializing-shared-state](skills/principles/principle-separate-before-serializing-shared-state/SKILL.md)
- [principle-sequence-verifiable-units](skills/principles/principle-sequence-verifiable-units/SKILL.md)
- [principle-subtract-before-you-add](skills/principles/principle-subtract-before-you-add/SKILL.md)
- [principle-test-behavior-not-implementation](skills/principles/principle-test-behavior-not-implementation/SKILL.md)
- [principle-type-system-discipline](skills/principles/principle-type-system-discipline/SKILL.md)

</details>

<details>
<summary>Required companions for smaller installations</summary>

Skills CLI does not install dependencies transitively. Install each companion's own companions too, including conditional ones before taking that branch. The complete-library install covers every row. Use it for unrestricted `pstack-mode` playbooks, which select further helpers as the task develops.

| Skill                                                                                                          | Required companions                                                           | Conditional companions                                                                                                                                                                       |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `audit-agent-documentation`                                                                                    | `writing-for-agents`                                                          | `pr` for publication                                                                                                                                                                         |
| `chief-of-staff`, `research`                                                                                   | `swarm`                                                                       |                                                                                                                                                                                              |
| `maintain-skills`                                                                                              | `writing-for-agents`, `swarm`, `pr`                                           |                                                                                                                                                                                              |
| `retro`                                                                                                        | `domain-modeling`, `writing-for-agents`                                       | `swarm` for delegation; `recall` for other sessions                                                                                                                                          |
| `setup-matt-pocock-skills`                                                                                     | `domain-modeling`                                                             | `codebase-design` for architecture work through the generated domain guidance                                                                                                                |
| `setup-ts-deep-modules`                                                                                        | `codebase-design`                                                             | `domain-modeling` for changed project ownership or vocabulary                                                                                                                                |
| `thermos`                                                                                                      | `thermo-nuclear-review`, `thermo-nuclear-code-quality-review`                 |                                                                                                                                                                                              |
| `grill-me`                                                                                                     | `grilling`                                                                    |                                                                                                                                                                                              |
| `grill-with-docs`                                                                                              | `grilling`, `domain-modeling`                                                 |                                                                                                                                                                                              |
| `grilling`                                                                                                     | `principles`                                                                  | `swarm` for environment-fact investigation; `design-prototype` for questions a sketch can settle                                                                                             |
| `codebase-design`                                                                                              |                                                                               | `domain-modeling` for accepted project-model changes; `arena` for interface alternatives                                                                                                     |
| `design-prototype`, `diagnosing-bugs`                                                                          | `domain-modeling`                                                             | `swarm` for delegation                                                                                                                                                                       |
| `improve-codebase-architecture`                                                                                | `domain-modeling`, `codebase-design`, `swarm`, `grilling`                     |                                                                                                                                                                                              |
| `loop-me`                                                                                                      | `domain-modeling`, `grilling`                                                 | `swarm` for delegation                                                                                                                                                                       |
| `to-spec`                                                                                                      | `domain-modeling`, `principles`                                               | `swarm` for delegation                                                                                                                                                                       |
| `to-tickets`                                                                                                   | `domain-modeling`, `principles`                                               | `swarm` for delegation; `principle-migrate-callers-then-delete-legacy-apis` for coordinated migration tickets                                                                                |
| `implement`                                                                                                    | `review-loop`, `domain-modeling`, `principles`                                | `tdd` where a useful test path exists; `swarm` for delegation; `pr` for authorized PR delivery                                                                                               |
| `implement-spec`                                                                                               | `tdd`, `review-loop`, `domain-modeling`, `principles`, `swarm`                | `pr` for authorized PR delivery; `principle-migrate-callers-then-delete-legacy-apis` for coupled migrations; `setup-matt-pocock-skills` when no tracker is configured                        |
| `triage`                                                                                                       | `domain-modeling`                                                             | `grilling` for unclear requests; `swarm` for delegation                                                                                                                                      |
| `wayfinder`                                                                                                    | `domain-modeling`, `grilling`                                                 | `research` for research tickets; `design-prototype` for prototype tickets; `swarm` for delegation                                                                                            |
| `tdd`                                                                                                          | `domain-modeling`, `principles`, `principle-test-behavior-not-implementation` | `codebase-design` for interface or seam decisions                                                                                                                                            |
| `code-review`                                                                                                  | `swarm`, `principles`                                                         | `setup-matt-pocock-skills` when the spec needs an unconfigured tracker                                                                                                                       |
| `review-loop`                                                                                                  | `code-review`, `thermo-nuclear-review`, `swarm`, `principles`                 | `principle-attack-the-premise` for a repeated class of finding; `pr` for draft PR delivery                                                                                                   |
| `test-audit`                                                                                                   | `swarm`, `principle-test-behavior-not-implementation`                         |                                                                                                                                                                                              |
| `pr`                                                                                                           | `domain-modeling`                                                             |                                                                                                                                                                                              |
| `next-options`                                                                                                 |                                                                               | `principle-never-block-on-the-human`; the stages its handoff table names                                                                                                                     |
| `reply-shape`                                                                                                  | `next-options`                                                                |                                                                                                                                                                                              |
| `setup-pre-commit`                                                                                             |                                                                               | `linting-alignment` when tool ownership is unclear                                                                                                                                           |
| `update-dependencies`                                                                                          |                                                                               | `linting-alignment` for an included lint or formatting stack update; `pr` for a requested pull request                                                                                       |
| `pstack-mode`                                                                                                  | `domain-modeling`, `principles`, `swarm`                                      | Install the complete library for all playbooks                                                                                                                                               |
| `pstack-setup`                                                                                                 |                                                                               | `swarm` for the review and Computer Use keys in `scripts/target.py --help`; `create-verification-skill`, `create-formal-verification-skill` for the step 5 offers                            |
| `architect`                                                                                                    | `codebase-design`, `domain-modeling`, `arena`                                 | `how` for existing-system grounding; `why` when ownership, layering, or historical constraints change; `tdd` at agreed public seams when useful; `interrogate` to review a sketch            |
| `arena`                                                                                                        | `swarm`                                                                       |                                                                                                                                                                                              |
| `no-comments`                                                                                                  | `swarm`                                                                       | `how` or `why` for disputed comment explanations; `architect` when a finding needs a new shape; `principle-fix-root-causes`, `principle-redesign-from-first-principles` for root-cause fixes |
| `automate-me`                                                                                                  | `recall`, `swarm`, `writing-for-agents`, `unslop`                             | `correct` for recurring mistakes                                                                                                                                                             |
| `figure-it-out`                                                                                                | `swarm`, `show-me-your-work`, `ketchup`                                       | `how`, `why` for grounding; `architect`, `arena` for contested boundaries                                                                                                                    |
| `how`                                                                                                          | `domain-modeling`, `swarm`                                                    |                                                                                                                                                                                              |
| `why`                                                                                                          | `domain-modeling`, `how`, `swarm`                                             |                                                                                                                                                                                              |
| `blast-radius`                                                                                                 | `domain-modeling`, `unslop`                                                   | `how`, `why` for explanation; `arena` for consequential changes                                                                                                                              |
| `interrogate`                                                                                                  | `domain-modeling`, `swarm`                                                    | `code-review` for Standards/Spec coverage; `principle-migrate-callers-then-delete-legacy-apis` for migration gates                                                                           |
| `create-formal-verification-skill`                                                                             | `writing-for-agents`                                                          | `statechart` for a generated TLA+ check                                                                                                                                                      |
| `maintain-formal-verification-skill`                                                                           | `writing-for-agents`                                                          |                                                                                                                                                                                              |
| `create-verification-skill`                                                                                    | `domain-modeling`                                                             |                                                                                                                                                                                              |
| `maintain-verification-skill`                                                                                  | `domain-modeling`, `swarm`                                                    |                                                                                                                                                                                              |
| `recall`                                                                                                       | `unslop`, `why`, `swarm`                                                      |                                                                                                                                                                                              |
| `teach`                                                                                                        | `unslop`                                                                      | `how` for behavior, `why` for rationale, at least one; `swarm` to run both in parallel                                                                                                       |
| `technical-writing`                                                                                            | `unslop`                                                                      |                                                                                                                                                                                              |
| `reflect`                                                                                                      | `swarm`                                                                       | `recall` when the active conversation is unavailable; `writing-for-agents` for substantive edits, description tuning, and new skills                                                         |
| `show-me-your-work`                                                                                            | `unslop`, `swarm`                                                             | `recall` for scoped session evidence                                                                                                                                                         |
| `ketchup`                                                                                                      | `bro`                                                                         |                                                                                                                                                                                              |
| `ketchup-video`                                                                                                | `ketchup`                                                                     |                                                                                                                                                                                              |
| `pstack-tdd`                                                                                                   | `tdd`                                                                         |                                                                                                                                                                                              |
| `typescript-best-practices`                                                                                    | `principle-type-system-discipline`                                            | `principle-boundary-discipline` for boundary validation                                                                                                                                      |
| `principles`                                                                                                   | All `principle-*` skills                                                      | `domain-modeling` for accepted domain changes; install the selected principles' companions below                                                                                             |
| `principle-boundary-discipline`, `principle-foundational-thinking`, `principle-redesign-from-first-principles` |                                                                               | `codebase-design` for module/interface reasoning; `domain-modeling` for accepted terminology, relationships, or ownership changes                                                            |
| `principle-model-the-domain`                                                                                   |                                                                               | `domain-modeling` when resolving project terminology, relationships, invariants, or ownership                                                                                                |
| `principle-type-system-discipline`                                                                             |                                                                               | `typescript-best-practices` for TypeScript syntax; `principle-boundary-discipline` for external-data parsing; `principle-encode-lessons-in-structure` for schema derivation                  |
| `principle-explain-the-number`                                                                                 |                                                                               | `benchmark-checklist` for performance numbers                                                                                                                                                |
| `principle-prove-it-works`                                                                                     |                                                                               | `show-me-your-work` for large or complex work requiring an auditable trail; `swarm` for a Computer Use check in a Claude session without that tool                                           |
| `principle-attack-the-premise`                                                                                 | `principle-build-the-lever`, `principle-laziness-protocol`                    | `principle-fix-root-causes` when the premise is confirmed                                                                                                                                    |
| `principle-build-the-lever`                                                                                    | `principle-laziness-protocol`                                                 | `principle-prove-it-works` for scripting verification itself                                                                                                                                 |
| `principle-outcome-oriented-execution`                                                                         |                                                                               | `principle-migrate-callers-then-delete-legacy-apis` for migrations with old and new contracts                                                                                                |
| `principle-sequence-verifiable-units`                                                                          |                                                                               | `principle-migrate-callers-then-delete-legacy-apis` for coupled migrations                                                                                                                   |

</details>

## License

[MIT](LICENSE). Adapted skills retain the notices and `UPSTREAM.md` records for Matt Pocock, Lauren Tan, Cursor, and the OpenClaw Foundation inside their own directories.
