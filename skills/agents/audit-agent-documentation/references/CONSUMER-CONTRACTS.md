# Consumer contracts

Read the current owning skill, tool, template, or schema before judging agent documentation it reads or writes. Use its implementation and repository selections to determine the contract.

## Trace ownership

- Identify the canonical source, generated output, discovery adapters, symlinks, locks, and refresh command.
- Trace required filenames, headings, fields, exact values, and conditions of presence or omission. A consumer can depend on prose as well as structured data.
- Preserve selected project choices and apparently repetitive instructions when parsing or separate loading depends on them.
- Recognize optional outputs and files created lazily. Their absence is a defect only when the owning contract requires them now.
- When the owner is unavailable, record the source gap and preserve the unresolved contract while continuing independent repairs.

Repair through the source and supported refresh path. If the owner is outside the edit scope, provide an upstream finding with the affected consumer and required change. Do not edit an installed copy as a substitute for changing its maintained source.

## Check skills and discovery

- Verify the skill's required metadata and directory naming against the ecosystem's specification and repository conventions.
- Match invocation policy to intended use. For model-invoked skills, evaluate descriptions against distinct trigger branches and unrelated prompts. For user-invoked skills, check that explicit invocation works and metadata disables implicit invocation where supported.
- Verify actual runtime behavior rather than assuming a frontmatter field has identical support in every tool. For Codex, consult the [official skills guide](https://developers.openai.com/codex/skills) for discovery and `agents/openai.yaml` policy.
- Trace dependencies to reachable skills or tools. Check installation instructions, invocation restrictions, disabled configuration, duplicate names, and missing capabilities.
- Verify scripts and references from their documented working directories, including paths that resolve relative to the installed skill.
- Keep common process steps in the skill entry point and conditional reference inside its owned package. Reference-only skills can remain sequence-free.

The contract review is complete when each affected input, output, and discovery route has a verified owner and preserved behavior, or an explicit unresolved gap.
