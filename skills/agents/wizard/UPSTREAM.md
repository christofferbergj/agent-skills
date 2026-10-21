# wizard: source and adaptations

## Source and credit

- Original author: Matt Pocock.
- Canonical source: [mattpocock/skills](https://github.com/mattpocock/skills).
- Original skill and resources: [`skills/engineering/wizard`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/wizard).
- Tracking policy: upstream `main`; inspect the entire public skills inventory for additions, removals, category moves, and relevant shared documentation. Exclude personal skills and the recorded user exclusions.
- Imported from commit: `49dd158d1076134a641b33efb035946536778336` (1.3.1).
- Reviewed through commit: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Fidelity checked through: `5beb35b040e3de97e54fa9e386d7e42d15c295c2`.
- Last upstream review: 2026-10-21.
- Upstream stage: `engineering`. Experimental and frozen status is retained in the combined catalog.
- License: [MIT, copyright 2026 Matt Pocock](LICENSE). Retain the notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Copy envfile.py beside the wizard and require Python 3. Serialize literal dotenv values without shell evaluation, preserve complete multiline records and file modes, and verify the actual consumer; reject unsupported quoting before writes.
- Step 4 ends with a completion criterion (syntax checks, every value's destination and secret path, precise human-only stages) and points at the helper's unit tests.

Local maintenance on 2026-10-20: Make the Readline end-marker expansion explicit before a literal bracket; display/control bytes remain identical, Bash syntax and error-level ShellCheck pass. This local repair leaves the upstream reviewed-through position unchanged.

## Maintenance

Invoke `/maintain-skills` for the combined maintenance guide and catalog. Its source comparison includes both Pstack and Matt Pocock in one update review. Compare baseline, candidate, and local files; retain intentional adaptations rather than overwriting them. Imported history is immutable. Advance this reviewed-through position only when the relevant delta and shared inputs are resolved and required validation passes.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `49dd158d1076134a641b33efb035946536778336` | Imported the complete pinned skill and resources; adapted host execution, artifact ownership, and delivery boundaries for the combined library. Validate with the combined catalog and targeted workflow fixtures.                                                                                                                                                                                                     |
| 2026-10-21  | `5beb35b040e3de97e54fa9e386d7e42d15c295c2` | No upstream delta. Compared SKILL.md, `template.sh`, and Codex metadata in both directions: every upstream helper, stage rule, and hand-off step survives; the 0600 create mode and symlink write-through hold in `envfile.py`; the confirm rule follows the library-wide authority adaptation. Recorded the step-4 completion criterion. `bash -n`, ShellCheck 0.11.0 at error level, and the helper unit tests pass. |
