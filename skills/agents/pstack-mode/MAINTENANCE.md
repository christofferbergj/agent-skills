# Pstack maintenance compatibility entrypoint

Invoke /maintain-skills for the combined library's maintenance guide and catalog. The weekly review checks both Matt Pocock and Pstack, including shared artifacts, dependencies, and executable templates, and prepares one validated update PR.

This skill's `suite.json` remains the authoritative Pstack mapping; the combined catalog references it. Skill-local `UPSTREAM.md` records retain immutable import history and reviewed-through positions. [The original Pstack validation record](VALIDATION.md) documents the initial port; combined validation covers the integrated library.

The catalog helper owned by /maintain-skills is the only validation, source-comparison, and checkpoint engine. It reads this skill's mapping and applies the same rules to both source families. The initial validation record's removed `scripts/suite.py` commands are historical evidence; use the combined owner's current commands.

Pstack's Bun tools retain immutable-source runtime preparation through `bun scripts/bootstrap.ts --print-runtime`. Run `bun test` and `bun run typecheck` in the returned directory. Focused Python tests remain under this skill's `scripts/tests/`, plus the owners /pstack-recall and /pstack-swarm. Execute changed owners rather than testing every prose-only skill.
