---
name: pstack-show-me-your-work
description: "Use for Pstack decision trails, unattended runs, transcript audits, or review of evidence behind completed work."
---

# Show me your work

Keep one append-only TSV decision trail. Read [the header template](references/decision-log-template.tsv). Use `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>` from this skill directory; it timestamps and sanitizes cells, including spreadsheet formula prefixes.

1. Choose a task-scoped working log outside installed skill files. Keep it untracked unless the task calls for a committed audit artifact. When joining an existing log, start with a `start` row that identifies this run and the prior range it did not write. Complete when ownership and the log location are explicit.
2. Append meaningful decisions, pivots, verification outcomes, and blockers as they occur. Evidence is a resolvable artifact, source location, revision, or run result. Apply /pstack-unslop to the prose. Complete each checkpoint when its row points to evidence and the actual predicate state.
3. Audit only this run's stretches against its actual conversation and artifacts. Invoke /pstack-recall if scoped transcript discovery is needed. Supersede an inaccurate row with a new correction; preserve history. Complete when every claim resolves or is corrected and meaningful missing decisions have been added.
4. Use /pstack-swarm for an independent trail review, preferring another vendor. Ask for weak evidence, missed checks, risky choices, and gaps. Complete when the pass returns evidenced flags or its absence is disclosed.
5. Return the trail path and an Attention section naming the actual reviewer and flags with row or artifact references. Complete when the user can distinguish recorded work, reviewer findings, and unavailable evidence.
