# Provenance records

Use a skill-local `UPSTREAM.md` as the source of truth. Existing equivalent records are valid; avoid creating a second competing record. Maintenance prose can supply context, but record enough concrete source information to resolve and compare revisions without guessing.

For each original source, include:

- Original author and repository or canonical URL.
- Exact upstream skill path and relevant supporting files or directories.
- Tracking policy: branch name, release channel, or intentionally fixed version. Keep this separate from the pinned import URL.
- Original imported commit or provider revision, with a permanent source link.
- Reviewed-through commit or reproducible content snapshot, plus review date. This includes deltas deliberately excluded in the decision history.
- Retained license location and attribution obligations.
- Local adaptations to preserve, local-only files, and source-specific maintenance guidance.
- Review history naming the candidate revision, adopted/adapted/excluded changes, reasons for exclusions, and validation results. Keep incomplete attempts separate from completed baselines.

When adding a new source record, recover the original import from repository history or other verifiable evidence. Do not label today's upstream head as the historical baseline. If no baseline can be recovered, record the gap and request the missing source/version or authorization for a fresh full reconciliation; other sourced skills can still be updated.

For multiple sources within one skill, record paths, revisions, and decisions separately. A completed comparison of one source does not advance the others. If a source moves, preserve the old import identity and record verified continuity to the new location.

The existing Thermos records follow this convention. They describe two callable review rubrics and an explicit-only orchestrator adapted for Codex and Claude Code. Their linked maintenance guide owns the suite-specific compatibility checks; discover and read it through those records instead of hardcoding the suite into the updater.
