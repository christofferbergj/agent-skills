---
name: principle-sequence-verifiable-units
description: "Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer."
---

# Sequence work into verifiable units

Order work as small units that each end in a state you can check, and do not advance beyond a unit until its declared checks pass. For coupled migrations, invoke /principle-migrate-callers-then-delete-legacy-apis to define the unit and intermediate gates.

In a sweep, migration, or run of similar edits, each unit is a bracket: known-good state, one change, run the check, proceed. Run the per-unit check even when a tool does the edits.

Deliver in the order that proves the work: the failing test first, then the fix. The subtraction before the reshape. The baseline before the treatment. Intermediate proof commits can show red; the checked delivery unit includes the fix, and each independently landed unit passes its acceptance gates.
