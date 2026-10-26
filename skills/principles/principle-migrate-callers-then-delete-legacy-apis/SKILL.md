---
name: principle-migrate-callers-then-delete-legacy-apis
description: "Choose migration strategy when an API or schema replaces an old contract: coordinated caller migration and deletion, or staged coexistence for real compatibility or release obligations."
---

# Migrate callers then delete legacy APIs

This owner chooses migration strategy and verification boundaries for both Matt's ticket flow and Pstack playbooks.

1. Inventory all callers and compatibility obligations, including external consumers, independently deployed versions, stored data, and rollout or rollback requirements. Complete when the old contract's consumers and required lifetime are known.
2. If callers are internal and the project can absorb a coordinated change, migrate every caller and delete the old API in one verification unit. Existing internal callers alone do not justify a compatibility layer. Several bounded tickets can contribute to that unit on an isolated integration branch. Complete when the plan covers every caller, obsolete-path deletion, and the unit's checks.
3. Use expand-contract only when a real compatibility obligation or required independently green release makes coexistence necessary. Add the new form, migrate consumers in checked batches, and remove the old form after the obligation ends. Give every temporary adapter a removal condition and an owning ticket. Complete when the reason for coexistence and its exit gate are explicit.
4. Declare the checks for each ticket or migration phase and the final integration unit. Planned, scoped, reversible breakage may exist inside an isolated unit; passing phase checks can unblock the next ticket inside it. Work outside that unit remains blocked until its full static, runtime, and contract checks pass. Preserve an already-approved rollout contract; seek a decision before changing it. Complete when intermediate progress and final acceptance cannot be confused.
5. Update tests for the accepted contract. Preserve distinct behavioral regressions while deleting tests that only protect the retired implementation. Complete when the caller inventory is exhausted, required compatibility is honored, obsolete paths are removed at their declared gate, and the final unit's checks pass.
