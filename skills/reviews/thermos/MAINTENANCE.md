# Maintaining the Thermos adaptations

Invoke `/maintain-skills` from this repository for upstream comparison, integration, provenance updates, and publication checks. It includes Thermos in the same pass as Pstack and the rest of the library, reusing one fetched `cursor/plugins` checkout and immutable candidate. The coordinator owns source records and shared integration; comparison workers return evidence and proposals.

This guide owns Thermos-specific inputs, compatibility contracts, and smoke checks. The maintenance owner's guide governs the overall process; the root README governs installation and refreshes.

## Source inputs

| Local skill                          | Upstream path in `cursor/plugins`                            | Source record                                                   |
| ------------------------------------ | ------------------------------------------------------------ | --------------------------------------------------------------- |
| `thermo-nuclear-review`              | `thermos/skills/thermo-nuclear-review/SKILL.md`              | [Provenance](../thermo-nuclear-review/UPSTREAM.md)              |
| `thermo-nuclear-code-quality-review` | `thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | [Provenance](../thermo-nuclear-code-quality-review/UPSTREAM.md) |
| `thermos`                            | `thermos/skills/thermos/SKILL.md`                            | [Provenance](UPSTREAM.md)                                       |

Also compare the complete `thermos/` tree, including `agents/` wrappers, plugin documentation, manifest, assets, and license. Wrappers are review inputs, not custom agents to install. Local `agents/openai.yaml` files are Codex metadata. Each source record owns its immutable import, reviewed-through position, license attribution, local adaptations, and decisions.

## Compatibility contracts

Preserve these contracts when adopting upstream changes:

- The two rubrics are model-invoked dependencies; `thermos` is user-invoked. Frontmatter and Codex invocation metadata agree. `/review-loop` also runs `thermo-nuclear-review` as its same-model correctness critic and its Codex correctness pass, so check that consumer when the rubric's scope, review-only rule, or output changes.
- Both reviewers receive the same scope and accessible evidence, plus their full rubric or resolved path. Child skill discovery is not assumed.
- Execution uses the host's actual native tools. Cursor's named subagents and plugin installation are not prerequisites.
- Both reviewers start before either is awaited. Results disclose failed or sequential passes. Reviewers do not delegate further.
- Review requests return findings without edits or external comments. Synthesis deduplicates using evidence and calibrates severity independently of reviewer agreement.

## Verify behavior changes

For changes affecting review behavior or delegation, exercise both supported hosts on an isolated change with a known defect and explicit scope. Invoke `$thermos` in Codex and `/thermos` in Claude Code. Inspect tool activity as well as the report: two distinct reviewers start before either is awaited, receive their rubrics, and both finish before synthesis. Confirm the defect is reported, duplicate findings are combined, and files and external comments remain untouched. Exercise the sequential fallback when that branch changes.

Record host versions, the exact reviewed artifact, executed checks, and limitations. Installation alone does not prove runtime compatibility. The [combined validation record](../../agents/maintain-skills/VALIDATION.md) preserves earlier host exercises and unresolved integration limits.
