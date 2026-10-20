# Contributing

Keep skills self-contained and organize them by purpose. Repository rules live in [AGENTS.md](AGENTS.md); category definitions live in [skills/README.md](skills/README.md).

## Add, move, or remove a skill

Use `skills/<category>/<skill-name>/`. Preserve existing invocation names when moving a skill. Keep its instructions, metadata, references, scripts, assets, licenses, and provenance together.

A skill's identity is repeated across files that change with it:

| Change                   | Also update                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Add                      | Root `README.md` (category list, plus a "Start here" row for an entrypoint), the category `README.md`, `agents/openai.yaml`, and a companion row naming the skills it invokes. A sourced skill also needs `UPSTREAM.md` and `LICENSE`; one from a mapped suite (Matt Pocock, Pstack, Thermos) also needs its catalog or `suite.json` mapping, and a user-facing Pstack entrypoint needs `/pstack-help` routing. |
| Change the description   | `agents/openai.yaml` `short_description` and both README rows.                                                                                                                                                                                                                                                                                                                                                  |
| Move to another category | Both category READMEs, the root README links, and the local `directory` entries in the [suite catalog](skills/agents/maintain-skills/catalog.json) and [Pstack index](skills/agents/pstack-mode/suite.json). Upstream paths and revisions identify the source and stay unchanged.                                                                                                                               |
| Remove                   | Both README listings and companion rows, any shared-owner registration, and every `/skill` invocation of it. For a skill from a mapped suite, remove its mapping from the catalog or `suite.json`, and add its upstream name and the reason to `excludedNames` under its source in the catalog.                                                                                                                 |
| Make it a shared owner   | The owners table in [the architecture](docs/architecture.md), the owners list in the [adaptation contract](skills/agents/maintain-skills/references/ADAPTATION.md), and `owners` in the catalog. A test keeps the three equal.                                                                                                                                                                                  |

Find a skill's consumers with `git grep -n '/<skill-name>\b'`; Pstack's playbooks under `skills/agents/pstack-mode/` call shared owners too.

## Validate

Install the tools pinned in `mise.toml` with `mise install`, then run `pnpm install` and every gate with:

```bash
pnpm check
```

`scripts/check.sh` lists what it runs.

`pnpm install` also installs a Husky pre-commit hook that formats staged files with Oxfmt through lint-staged.

## Upstream maintenance

Use this repository's `/maintain-skills` with `/writing-for-agents` and `/pstack-swarm`. Follow the [adaptation contract](skills/agents/maintain-skills/references/ADAPTATION.md), [maintenance guide](skills/agents/maintain-skills/MAINTENANCE.md), and [provenance convention](skills/agents/maintain-skills/references/PROVENANCE.md). For integration changes, read [how the source families compose](docs/architecture.md). The scheduled prompt owns scheduled budgets and permissions; the scheduled tasks own cadence and model.

Keep changes reviewable. Commit, publish, merge, and refresh global installations only within the user's authorization.
