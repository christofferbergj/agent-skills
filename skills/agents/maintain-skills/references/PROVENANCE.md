# Provenance records

Each sourced skill has one skill-local `UPSTREAM.md` as its provenance record; an existing equivalent record serves as that record. Record enough concrete source information to resolve and compare revisions without guessing.

Discover records and attribution links from every local skill, including skills outside a suite catalog and newly added directories. Reconcile these findings with the full local inventory. A catalog supplies suite-specific mappings and candidate-addition policy; it is not an allowlist of maintained sources. Classify a skill as first-party only after checking its instructions, supporting material, licenses, and repository history for external origins. Record unresolved attribution as pending source work.

For each original source, include:

- Original author and repository or canonical URL.
- Exact upstream skill path and relevant supporting files or directories.
- Tracking policy: branch name, release channel, or intentionally fixed version. Keep this separate from the pinned import URL.
- Original imported commit or provider revision, with a permanent source link.
- Reviewed-through commit or reproducible content snapshot, plus review date. This includes deltas deliberately excluded in the decision history.
- Fidelity checked through: the candidate revision at which the local adaptations list was last confirmed complete in both directions. A record without it awaits its first fidelity check.
- Retained license location and attribution obligations.
- Local adaptations to preserve: every way this skill diverges from the tracked upstream text beyond [the library-wide adaptations](ADAPTATION.md#library-wide-adaptations), including dropped, softened, or reversed rules and a changed invocation mode, each with its reason. Name the library-wide adaptations once instead of restating them. Review rows log decisions; they never replace this list. Also record local-only files and source-specific maintenance guidance.
- Review history naming the candidate revision, adopted/adapted/excluded changes, reasons for exclusions, and validation results. Keep incomplete attempts separate from completed baselines.

When adding a new source record, recover the original import from repository history or other verifiable evidence. Do not label today's upstream head as the historical baseline. If no baseline can be recovered, record the gap and request the missing source/version or authorization for a fresh full reconciliation; other sourced skills can still be updated.

For multiple sources within one skill, record paths, revisions, and decisions separately. A completed comparison of one source does not advance the others. If a source moves, preserve the old import identity and record verified continuity to the new location.

An inherited credit can identify an earlier template rather than a separately tracked import. When that distinction is established, add `Attribution-only source: https://github.com/owner/repo` to the owning provenance record and explain which adapted source is tracked instead. The helper exposes that ancestry without inventing a second review baseline. Unclassified credits remain pending; a credit link alone never establishes a completed upstream review.

List every upstream resource the skill depends on; a skill-body comparison alone cannot complete a multi-file source review. A source enters maintenance through its record, so a future source needs no catalog entry or hardcoded name. `test-audit` keeps its unknown historical import separate from its established reviewed-through position.
