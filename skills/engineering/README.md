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
- **[test-audit](./test-audit/SKILL.md)** audits and cleans up tests while preserving meaningful coverage. Includes focused reviews and exhaustive repository or monorepo campaigns.
