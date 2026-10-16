# Pstack maintenance compatibility entrypoint

Invoke /maintain-skills for repository-wide maintenance, including Pstack, Matt Pocock, other sourced suites, and first-party skills. It discovers local skills and provenance on each pass, delegates coverage in rolling waves, and prepares one validated update PR within the scheduled action grant.

This skill's `suite.json` remains the authoritative Pstack mapping; the combined catalog references it. Skill-local `UPSTREAM.md` records retain immutable import history and reviewed-through positions. [The original Pstack validation record](VALIDATION.md) documents the initial port; combined validation covers the integrated library.

The helper owned by /maintain-skills handles whole-repository inventory, source comparison, and checkpointing; suite mappings add candidate-addition policy rather than limiting local coverage. It reads this skill's mapping while also discovering every other upstream. The initial validation record's removed `scripts/suite.py` commands are historical evidence; use the maintenance owner's current commands.

Pstack's Bun tools retain immutable-source runtime preparation through `bun scripts/bootstrap.ts --print-runtime`. Run `bun test` and `bun run typecheck` in the returned directory. Focused Python tests remain under this skill's `scripts/tests/`, plus the owners /pstack-recall and /pstack-swarm. Execute changed owners rather than testing every prose-only skill.
