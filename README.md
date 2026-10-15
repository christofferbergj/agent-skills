# Agent Skills

[![skills.sh](https://skills.sh/b/christofferbergj/agent-skills)](https://skills.sh/christofferbergj/agent-skills)

Focused skills for coding agents. Each skill is small enough to understand, complete enough to run predictably, and designed to compose with the others.

## Install

Browse the available skills and choose which agents should receive them:

```bash
npx skills@latest add christofferbergj/agent-skills
```

To install the dependency-maintenance pair globally for Codex:

```bash
npx skills@latest add christofferbergj/agent-skills \
  --skill update-dependencies \
  --skill linting-alignment \
  --global \
  --agent codex \
  --yes
```

To install the agent-documentation pair globally for Codex:

```bash
npx skills@latest add mattpocock/skills \
  --skill writing-for-agents \
  --global \
  --agent codex \
  --yes

npx skills@latest add christofferbergj/agent-skills \
  --skill audit-agent-documentation \
  --global \
  --agent codex \
  --yes
```

The Skills CLI does not resolve dependencies between skills. Install both members of each pair: `update-dependencies` invokes `/linting-alignment` when a dependency update changes the lint or formatting stack, and `audit-agent-documentation` invokes `/writing-for-agents` during diagnosis and applies it to every changed agent document.

To install the self-contained test-audit skill globally for Codex:

```bash
npx skills@latest add christofferbergj/agent-skills \
  --skill test-audit \
  --global \
  --agent codex \
  --yes
```

The Thermos review suite requires all three skills. Install your local checkout globally for Codex and Claude Code:

```bash
npx skills@latest add /Users/christofferbergj/code/agent-skills \
  --skill thermos thermo-nuclear-review thermo-nuclear-code-quality-review \
  --global \
  --agent codex claude-code \
  --yes
```

Run `$thermos` in Codex or `/thermos` in Claude Code with the review scope. It launches two built-in subagents with the installed review rubrics and combines their findings. No Cursor plugin or custom agent registration is required. Hosts without available subagent tools use an explicitly labeled sequential fallback.

These are owned adaptations of [Cursor's MIT-licensed Thermos plugin](https://github.com/cursor/plugins/tree/main/thermos). Follow the [manual upstream-update guide](./skills/engineering/thermos/MAINTENANCE.md) for source comparisons, local adaptations, validation, and installation. Each skill's linked source record identifies its original file, pinned import, last reviewed commit, and update decisions.

Re-run the local install command after editing them; a local-path install is a snapshot, not a live link to this checkout. After publishing to your GitHub repository, replace the local source path with `christofferbergj/agent-skills` to use GitHub-backed updates. Do not install these same skill names from `cursor/plugins`, which would overwrite the adaptations.

## Pstack

The Pstack adaptation covers all 54 registered skills from [Lauren Tan's MIT-licensed Pstack](https://github.com/cursor/plugins/tree/main/pstack): 53 namespaced skills plus the existing `bro`. It includes 24 principles, 23 playbooks, native Codex and Claude Code execution, and a disclosed fallback when cross-vendor review is unavailable. The dormant Benny automation pack is outside this suite.

Install the complete dependency group for both hosts:

```bash
npx skills@latest add christofferbergj/agent-skills \
  --skill \
    pstack-architect pstack-arena pstack-automate-me pstack-benchmark-checklist pstack-blast-radius \
    bro pstack-correct pstack-create-verification-skill pstack-figure-it-out pstack-how \
    pstack-in-your-own-words pstack-interrogate pstack-ketchup pstack-maintain-verification-skill \
    pstack-make-bot-ui pstack-no-comments pstack-help pstack-mode pstack-recall pstack-reflect \
    pstack-setup pstack-sharpen pstack-show-me-your-work pstack-swarm pstack-tdd pstack-teach \
    pstack-technical-writing pstack-typescript-best-practices pstack-unslop pstack-why \
    pstack-principle-attack-the-premise pstack-principle-boundary-discipline \
    pstack-principle-build-the-lever pstack-principle-encode-lessons-in-structure \
    pstack-principle-exhaust-the-design-space pstack-principle-experience-first \
    pstack-principle-explain-the-number pstack-principle-fix-root-causes \
    pstack-principle-foundational-thinking pstack-principle-guard-the-context-window \
    pstack-principle-laziness-protocol pstack-principle-make-operations-idempotent \
    pstack-principle-migrate-callers-then-delete-legacy-apis pstack-principle-minimize-reader-load \
    pstack-principle-model-the-domain pstack-principle-never-block-on-the-human \
    pstack-principle-outcome-oriented-execution pstack-principle-prove-it-works \
    pstack-principle-redesign-from-first-principles \
    pstack-principle-separate-before-serializing-shared-state \
    pstack-principle-sequence-verifiable-units pstack-principle-subtract-before-you-add \
    pstack-principle-test-behavior-not-implementation pstack-principle-type-system-discipline \
  --global --agent codex claude-code --yes
```

Use `.` as the source while installing from this checkout before publication. Skills CLI does not resolve dependencies transitively; the complete group above is the supported installation for coordinated workflows and for invoking their helpers individually. Installing a local path creates a snapshot, so source edits require another install.

Invoke `$pstack-mode` in Codex or `/pstack-mode` in Claude Code for the current conversation. Give it a goal, observable done predicate, proof, and constraints. Use `pstack-help` for routing and `pstack-setup` for personal model roles. Installation does not activate a mode or modify host startup instructions.

The suite preserves evidence requirements while scaling parallelism to the task. Draft PRs are the default. Cross-vendor critics use the other authenticated CLI when available; independent native or sequential fallback is labeled. Bun-dependent PR/orchestration commands declare their prerequisites and use a runtime cache outside installed source. The webhook UI requires an existing receiver and defaults to localhost.

Read the [suite maintenance guide](skills/agents/pstack-mode/MAINTENANCE.md) for source comparisons, local adaptations, checks, checkpointing, and the weekly review contract. The [validation record](skills/agents/pstack-mode/VALIDATION.md) covers tested hosts and integration limits. Each skill retains its own `LICENSE` and `UPSTREAM.md`; the [suite index](skills/agents/pstack-mode/suite.json) includes `bro` so maintenance does not rely on a name prefix. `/maintain-skills` still requires `/writing-for-agents`, installed as documented below.

### Pstack skill inventory

| Skill                                                                                                                                              | Invocation    |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| [pstack-architect](skills/engineering/pstack-architect/SKILL.md)                                                                                   | Model or user |
| [pstack-arena](skills/engineering/pstack-arena/SKILL.md)                                                                                           | Model or user |
| [pstack-automate-me](skills/agents/pstack-automate-me/SKILL.md)                                                                                    | User          |
| [pstack-benchmark-checklist](skills/engineering/pstack-benchmark-checklist/SKILL.md)                                                               | Model or user |
| [pstack-blast-radius](skills/engineering/pstack-blast-radius/SKILL.md)                                                                             | Model or user |
| [bro](skills/communication/bro/SKILL.md)                                                                                                           | User          |
| [pstack-correct](skills/agents/pstack-correct/SKILL.md)                                                                                            | Model or user |
| [pstack-create-verification-skill](skills/engineering/pstack-create-verification-skill/SKILL.md)                                                   | Model or user |
| [pstack-figure-it-out](skills/engineering/pstack-figure-it-out/SKILL.md)                                                                           | Model or user |
| [pstack-how](skills/engineering/pstack-how/SKILL.md)                                                                                               | Model or user |
| [pstack-in-your-own-words](skills/communication/pstack-in-your-own-words/SKILL.md)                                                                 | Model or user |
| [pstack-interrogate](skills/engineering/pstack-interrogate/SKILL.md)                                                                               | Model or user |
| [pstack-ketchup](skills/communication/pstack-ketchup/SKILL.md)                                                                                     | Model or user |
| [pstack-maintain-verification-skill](skills/engineering/pstack-maintain-verification-skill/SKILL.md)                                               | Model or user |
| [pstack-make-bot-ui](skills/engineering/pstack-make-bot-ui/SKILL.md)                                                                               | Model or user |
| [pstack-no-comments](skills/engineering/pstack-no-comments/SKILL.md)                                                                               | Model or user |
| [pstack-help](skills/agents/pstack-help/SKILL.md)                                                                                                  | User          |
| [pstack-mode](skills/agents/pstack-mode/SKILL.md)                                                                                                  | User          |
| [pstack-recall](skills/agents/pstack-recall/SKILL.md)                                                                                              | Model or user |
| [pstack-reflect](skills/agents/pstack-reflect/SKILL.md)                                                                                            | Model or user |
| [pstack-setup](skills/agents/pstack-setup/SKILL.md)                                                                                                | Model or user |
| [pstack-sharpen](skills/agents/pstack-sharpen/SKILL.md)                                                                                            | Model or user |
| [pstack-show-me-your-work](skills/agents/pstack-show-me-your-work/SKILL.md)                                                                        | Model or user |
| [pstack-swarm](skills/agents/pstack-swarm/SKILL.md)                                                                                                | Model or user |
| [pstack-tdd](skills/engineering/pstack-tdd/SKILL.md)                                                                                               | Model or user |
| [pstack-teach](skills/communication/pstack-teach/SKILL.md)                                                                                         | Model or user |
| [pstack-technical-writing](skills/communication/pstack-technical-writing/SKILL.md)                                                                 | Model or user |
| [pstack-typescript-best-practices](skills/engineering/pstack-typescript-best-practices/SKILL.md)                                                   | Model or user |
| [pstack-unslop](skills/communication/pstack-unslop/SKILL.md)                                                                                       | Model or user |
| [pstack-why](skills/engineering/pstack-why/SKILL.md)                                                                                               | Model or user |
| [pstack-principle-attack-the-premise](skills/engineering/pstack-principle-attack-the-premise/SKILL.md)                                             | Model or user |
| [pstack-principle-boundary-discipline](skills/engineering/pstack-principle-boundary-discipline/SKILL.md)                                           | Model or user |
| [pstack-principle-build-the-lever](skills/engineering/pstack-principle-build-the-lever/SKILL.md)                                                   | Model or user |
| [pstack-principle-encode-lessons-in-structure](skills/engineering/pstack-principle-encode-lessons-in-structure/SKILL.md)                           | Model or user |
| [pstack-principle-exhaust-the-design-space](skills/engineering/pstack-principle-exhaust-the-design-space/SKILL.md)                                 | Model or user |
| [pstack-principle-experience-first](skills/engineering/pstack-principle-experience-first/SKILL.md)                                                 | Model or user |
| [pstack-principle-explain-the-number](skills/engineering/pstack-principle-explain-the-number/SKILL.md)                                             | Model or user |
| [pstack-principle-fix-root-causes](skills/engineering/pstack-principle-fix-root-causes/SKILL.md)                                                   | Model or user |
| [pstack-principle-foundational-thinking](skills/engineering/pstack-principle-foundational-thinking/SKILL.md)                                       | Model or user |
| [pstack-principle-guard-the-context-window](skills/engineering/pstack-principle-guard-the-context-window/SKILL.md)                                 | Model or user |
| [pstack-principle-laziness-protocol](skills/engineering/pstack-principle-laziness-protocol/SKILL.md)                                               | Model or user |
| [pstack-principle-make-operations-idempotent](skills/engineering/pstack-principle-make-operations-idempotent/SKILL.md)                             | Model or user |
| [pstack-principle-migrate-callers-then-delete-legacy-apis](skills/engineering/pstack-principle-migrate-callers-then-delete-legacy-apis/SKILL.md)   | Model or user |
| [pstack-principle-minimize-reader-load](skills/engineering/pstack-principle-minimize-reader-load/SKILL.md)                                         | Model or user |
| [pstack-principle-model-the-domain](skills/engineering/pstack-principle-model-the-domain/SKILL.md)                                                 | Model or user |
| [pstack-principle-never-block-on-the-human](skills/engineering/pstack-principle-never-block-on-the-human/SKILL.md)                                 | Model or user |
| [pstack-principle-outcome-oriented-execution](skills/engineering/pstack-principle-outcome-oriented-execution/SKILL.md)                             | Model or user |
| [pstack-principle-prove-it-works](skills/engineering/pstack-principle-prove-it-works/SKILL.md)                                                     | Model or user |
| [pstack-principle-redesign-from-first-principles](skills/engineering/pstack-principle-redesign-from-first-principles/SKILL.md)                     | Model or user |
| [pstack-principle-separate-before-serializing-shared-state](skills/engineering/pstack-principle-separate-before-serializing-shared-state/SKILL.md) | Model or user |
| [pstack-principle-sequence-verifiable-units](skills/engineering/pstack-principle-sequence-verifiable-units/SKILL.md)                               | Model or user |
| [pstack-principle-subtract-before-you-add](skills/engineering/pstack-principle-subtract-before-you-add/SKILL.md)                                   | Model or user |
| [pstack-principle-test-behavior-not-implementation](skills/engineering/pstack-principle-test-behavior-not-implementation/SKILL.md)                 | Model or user |
| [pstack-principle-type-system-discipline](skills/engineering/pstack-principle-type-system-discipline/SKILL.md)                                     | Model or user |

## Maintain

Invoke `$maintain-skills` in Codex or `/maintain-skills` in Claude Code from this repository for a periodic sanity check. It reads every skill, applies Writing for Agents, verifies tool references and practices against current evidence, and repairs stale guidance. It also checks sourced skills against their originals while preserving local adaptations and attribution. A named subset limits the pass; publication and refreshing global installations follow the user's existing authorization.

Install it with its Writing for Agents dependency for both hosts:

```bash
npx skills@latest add mattpocock/skills \
  --skill writing-for-agents --global --agent codex claude-code --yes
npx skills@latest add . \
  --skill maintain-skills --global --agent codex claude-code --yes
```

Run the local command from this repository's root, or use `christofferbergj/agent-skills` instead of `.` for the published version. Writing for Agents is a required dependency. New sourced skills need a provenance record following the [source-record convention](./skills/agents/maintain-skills/references/PROVENANCE.md); all skills are reviewed regardless of whether they have an upstream source.

Edit existing skills in this repository under `skills/<category>/<skill-name>/`. Add a new skill as another directory containing `SKILL.md`, add its Codex metadata in `agents/openai.yaml`, and list it in both this README and its category README.

Before publishing:

```bash
pnpm fmt:check
npx skills@latest add . --list
git diff --check
gitleaks dir . --redact --no-banner
```

Commit with a terse imperative title, push `main`, then refresh already-installed global skills:

```bash
npx skills@latest update update-dependencies linting-alignment \
  --global \
  --yes
```

`update` refreshes installed skills; it does not install a newly published one. Add a new skill once with:

```bash
npx skills@latest add christofferbergj/agent-skills \
  --skill <skill-name> \
  --global \
  --agent codex \
  --yes
```

## Skills

### User-invoked

These run only when you select them explicitly.

- **[audit-agent-documentation](./skills/agents/audit-agent-documentation/SKILL.md)** — Audit and improve agent documentation across a codebase while preserving project contracts.
- **[bro](./skills/communication/bro/SKILL.md)** — Restate the last message in plain human language, with no jargon.
- **[thermos](./skills/engineering/thermos/SKILL.md)** runs parallel correctness and maintainability reviews in Codex or Claude Code. Install both review skills with it.
- **[maintain-skills](./skills/agents/maintain-skills/SKILL.md)** checks every skill's writing, tools, docs, and practices, repairs stale guidance, and reconciles sourced skills with upstream. Install `/writing-for-agents` with it.
- **[update-dependencies](./skills/engineering/update-dependencies/SKILL.md)** — Update dependencies across repositories and monorepos, let the package manager check peer ranges, research releases, validate, and open a pull request when requested.

### Model-invoked

These can be selected explicitly or reached automatically when their trigger matches.

- **[linting-alignment](./skills/engineering/linting-alignment/SKILL.md)** — Align lint and formatting policy with the presets and tools that own it.
- **[test-audit](./skills/engineering/test-audit/SKILL.md)** audits test value and cleans up tests while preserving meaningful contracts. Supports focused reviews and exhaustive campaigns across languages and runners.
- **[thermo-nuclear-review](./skills/engineering/thermo-nuclear-review/SKILL.md)** audits branch correctness, security, developer experience, and feature-gate leaks.
- **[thermo-nuclear-code-quality-review](./skills/engineering/thermo-nuclear-code-quality-review/SKILL.md)** audits maintainability, structural simplification, and architecture boundaries.

## Design

- Repository policy wins over generic advice.
- Every ordered step ends with a checkable completion criterion.
- Conditional reference material stays beside its owning skill.
- Skill dependencies use `/skill-name` prose invocation rather than cross-folder file links.
- Publication is always an explicit user boundary.

## License

[MIT](./LICENSE)

The three Thermos adaptations include work by Cursor, copyright 2026, under the MIT license. Each skill retains Cursor's original `LICENSE` and an `UPSTREAM.md` attribution record. See the [source inventory](./skills/engineering/thermos/MAINTENANCE.md#sources-and-ownership).

The test-audit adaptation includes work by the OpenClaw Foundation, copyright 2026, under the MIT license. It retains the upstream [license notice](./skills/engineering/test-audit/LICENSE) and [source record](./skills/engineering/test-audit/UPSTREAM.md).

The Pstack adaptations include work by Lauren Tan, copyright 2026, under the MIT license. Each mapped skill retains the upstream license and a source record.
