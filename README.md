# Agent Skills

[![skills.sh](https://skills.sh/b/christofferbergj/agent-skills)](https://skills.sh/christofferbergj/agent-skills)

Focused engineering skills for coding agents. Each skill is small enough to understand, complete enough to run predictably, and designed to compose with the others.

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

The Skills CLI does not resolve dependencies between skills. Install both when using `update-dependencies`, because it invokes `/linting-alignment` when a dependency update changes the lint or formatting stack.

## Maintain

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

- **[update-dependencies](./skills/engineering/update-dependencies/SKILL.md)** — Sweep every JavaScript and TypeScript dependency surface, apply policy-compatible updates, and validate the result.

### Model-invoked

These can be selected explicitly or reached automatically when their trigger matches.

- **[linting-alignment](./skills/engineering/linting-alignment/SKILL.md)** — Align lint and formatting policy with the presets and tools that own it.

## Design

- Repository policy wins over generic advice.
- Every ordered step ends with a checkable completion criterion.
- Conditional reference material stays beside its owning skill.
- Skill dependencies use `/skill-name` prose invocation rather than cross-folder file links.
- Publication is always an explicit user boundary.

## License

[MIT](./LICENSE)
