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
- **[test-audit](./skills/engineering/test-audit/SKILL.md)** audits test quality, repairs weak tests, and consolidates redundant coverage. Supports focused reviews and exhaustive campaigns across languages and runners.
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
