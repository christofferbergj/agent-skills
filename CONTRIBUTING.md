# Contributing

Keep skills self-contained and organize them by purpose. Repository rules live in [AGENTS.md](AGENTS.md); category definitions live in [skills/README.md](skills/README.md).

## Add or move a skill

Use `skills/<category>/<skill-name>/`. Preserve existing invocation names when moving a skill. Keep its instructions, metadata, references, scripts, assets, licenses, and provenance together.

List every skill in the root and category READMEs. For a category move, update local `directory` entries in the [suite catalog](skills/agents/maintain-skills/catalog.json) and [Pstack index](skills/agents/pstack-mode/suite.json). Upstream paths, imported revisions, and reviewed revisions identify the source and stay unchanged.

## Validate

Install repository tooling with `pnpm install`, then run:

```bash
pnpm fmt:check
npx skills@latest add . --list
python3 skills/agents/maintain-skills/scripts/catalog.py --root . validate
git diff --check
gitleaks dir . --redact --no-banner
```

Run focused tests when changing executable behavior. The maintenance helper's tests run with:

```bash
python3 -m unittest discover -s skills/agents/maintain-skills/scripts/tests -v
```

## Upstream maintenance

Use this repository's `/maintain-skills` with `/writing-for-agents` and `/pstack-swarm`. Follow the [adaptation contract](skills/agents/maintain-skills/references/ADAPTATION.md), [maintenance guide](skills/agents/maintain-skills/MAINTENANCE.md), and [provenance convention](skills/agents/maintain-skills/references/PROVENANCE.md). For integration changes, read [how the source families compose](docs/architecture.md). The scheduled prompt owns scheduled budgets and permissions; the scheduled tasks own cadence and model.

Keep changes reviewable. Commit, publish, merge, and refresh global installations only within the user's authorization.
