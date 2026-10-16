---
name: pstack-principle-sequence-verifiable-units
description: "Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer."
---

# Sequence work into verifiable units

Order work as a sequence of small units, each ending in a state you can check, and don't advance beyond a unit until its declared checks pass. For coupled migrations, invoke /pstack-principle-migrate-callers-then-delete-legacy-apis to define the unit and intermediate gates.

**Why:** A break caught at the unit that caused it is cheap to localize. A break caught after a batch is buried, and you have already built further on a broken base. Sequencing those same units into a delivery a reviewer can replay turns "trust me" into "watch it go red, then green."

**Execution.** In a sweep, migration, or any run of similar edits, verify each change at its declared gate before starting dependent work. Each unit is a before/after bracket: known-good state, one change, run the check, then proceed. Use the invoking workflow's verified base, including an integration revision; preserve unrelated work and existing branch ownership. When a lever does the edits, the per-unit check is nearly free. Run it anyway.

**Delivery.** Stack commits and PRs in the order that proves the work. The canonical shape is the failing test first, then the fix on top. Other story orders are a subtraction before the reshape, a baseline capture before the treatment, the scaffold before the feature. Intermediate proof commits can show red; the checked delivery unit includes the fix. Independently landed units must pass their acceptance gates.

The sequencing complement to the /pstack-principle-prove-it-works, which keeps each check real, and the /pstack-principle-build-the-lever, which makes the per-unit check cheap.
