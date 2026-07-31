# Repository guidance

Skills are organized under `skills/<category>/<skill-name>/`.

Every published skill must:

- contain a `SKILL.md` with string `name` and `description` fields;
- use a lowercase, hyphenated name that matches its directory;
- keep conditional reference material inside its own directory;
- appear in both the top-level `README.md` and its category `README.md`;
- keep Codex metadata in `agents/openai.yaml` synchronized with its invocation mode; and
- pass `npx skills@latest add . --list` and `git diff --check` before publication.

Invocation has two modes:

- **User-invoked** skills set `disable-model-invocation: true` and `policy.allow_implicit_invocation: false`. Their description is a short human-facing summary.
- **Model-invoked** skills omit both restrictions. Their description names the distinct branches that should trigger the skill.

Express dependencies as `/skill-name` prose invocation. Keep shared reference material with the skill that owns it; another skill reaches that material by invoking its owner. Because the Skills CLI does not install dependencies transitively, document required installation pairs in the top-level README.

Treat each skill as a predictable process. Ordered steps end with checkable, exhaustive completion criteria. Keep one source of truth for each rule, disclose branch-specific reference behind a precise pointer, and remove instructions that do not change agent behavior.
