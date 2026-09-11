# Discovery and scope

Build the coverage map from the loading rules of each agent tool in use. A file's presence, its intended scope, and its inclusion in a running agent's context are separate facts.

Keep the search boundary from Step 1. A focused audit covers affected scopes and their relevant shared dependencies; a whole-codebase audit covers all first-party areas. When a shared rule changes, include every dependent stack in the impact assessment without inventorying unrelated content.

## Resolve loading behavior

- Record the task's launch directory, target files, active configuration, and instruction convention. Map automatic loading, explicit imports, optional pointers, and manual invocation separately.
- Check global and local overrides, fallback filenames, path matching, disabled rules or skills, discovery limits, and truncation where supported. Mark shadowed or unreachable guidance and identify its intended consumer before removing it.
- Verify nested loading for the actual tool. Starting at the root and working on a nested file may load guidance differently from starting in that file's directory. A Markdown link offers a route; it is not proof of automatic inclusion.
- Resolve relative links and imports using the consumer's base directory. Trace symlink targets, detect cycles, and record references that leave the repository boundary without expanding the edit scope.
- For Codex, check `AGENTS.override.md`, `AGENTS.md`, configured fallback filenames, and project instruction limits against the installed configuration and [official discovery guide](https://developers.openai.com/codex/guides/agents-md). For other tools, use their current official loading rules instead of assuming Codex behavior.

## Cover the codebase

- Map every first-party area in scope, including areas with no local instruction file, to the stacks that its supported agents receive.
- Include shared libraries, repository tooling, scripts, infrastructure, and nested projects even when no package workspace declaration covers them.
- Group areas only when their loading behavior, effective instructions, and consumers match. Keep every group's membership explicit.
- Record cross-area routes to shared guidance, templates, and generated outputs. Evaluate a cross-area task where guidance must compose.
- Check root and nested starting contexts where loading differs. Verify both that required guidance is reached and that unrelated branch detail stays conditional. Run an agent when uncertainty about changed loading behavior warrants it.

Discovery is resolved when each area and supported instruction convention maps to reviewed guidance or an explicit gap, with evidence for its loading behavior. If the runtime is unavailable, label the map as statically checked and leave runtime loading unverified.
