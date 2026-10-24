# Repository guidance

Skills are organized under `skills/<category>/<skill-name>/`.

For project orientation, upstream ownership, or changes spanning skill families, read [the library architecture](docs/architecture.md).

Read skills from this repository's `skills/` tree, not from installed copies, which lag until a refresh. To refresh or check installed copies after a change, follow [Install and update](docs/usage.md#install-and-update). Vocabulary lives in `GLOSSARY.md` and decisions in `docs/adr/`; [the docs index](docs/README.md) separates current guidance from dated evidence. Before adding, moving, removing, or redescribing a skill, read [the change set in Contributing](CONTRIBUTING.md#add-move-or-remove-a-skill).

Every published skill must:

- contain a `SKILL.md` with string `name` and `description` fields;
- use a lowercase, hyphenated name that matches its directory;
- keep conditional reference material inside its own directory;
- appear in both the top-level `README.md` and its category `README.md`;
- keep Codex metadata in `agents/openai.yaml` synchronized with its invocation mode; and
- pass `pnpm check` before publication.

Invocation has two modes:

- **User-invoked** skills set `disable-model-invocation: true` and `policy.allow_implicit_invocation: false`. Their description is a short human-facing summary.
- **Model-invoked** skills omit both restrictions. Their description names the distinct branches that should trigger the skill.

Express dependencies as `/skill-name` prose invocation. Keep shared reference material with the skill that owns it; another skill reaches that material by invoking its owner. Because the Skills CLI does not install dependencies transitively, document required installation pairs in the top-level README.

For skills derived from external sources, maintain a skill-local `UPSTREAM.md` with source identity, tracking policy, imported and reviewed revisions, license attribution, local adaptations, and update decisions. `/maintain-skills` discovers these records; its [provenance guidance](skills/agents/maintain-skills/references/PROVENANCE.md) describes how to add or repair one.

Treat each skill as a predictable process. Ordered steps end with checkable, exhaustive completion criteria. Keep one source of truth for each rule, disclose branch-specific reference behind a precise pointer, and remove instructions that do not change agent behavior.

Use terse imperative commit titles without conventional-commit prefixes.
