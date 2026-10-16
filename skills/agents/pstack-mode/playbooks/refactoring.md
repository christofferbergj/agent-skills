# Refactoring

Own the behavior contract. Structure changes; behavior stays fixed.

1. Invoke /codebase-design for interface and seam vocabulary and /domain-modeling for the configured artifacts. Identify observable contracts, callers, state ownership, and existing tests. Invoke /pstack-how and relevant domain and reader-load principles. Complete when the behavior to preserve and structural problem are explicit.
2. Choose a smaller coherent shape. Use /pstack-architect for boundary changes and /pstack-arena when several consequential shapes compete. Preserve approved-interface gates. Complete when the target shape and caller migration are concrete.
3. Make verifiable units, using codemods or scripts where they establish exhaustive coverage. Invoke /pstack-principle-migrate-callers-then-delete-legacy-apis for the migration strategy and gates. Use /pstack-swarm for disjoint work. Complete when every affected caller and required compatibility obligation is accounted for.
4. Run behavior checks against old and new states, including bugs if byte-identical or bug-compatible behavior was requested. Complete when the preserved contract has evidence and deviations are explicit.
5. Inspect the final structure and follow Opening a PR when authorized. Complete when obsolete paths are removed and the verification applies to the final artifact.

Return the structural change, preserved behavior, migration coverage, evidence, and any deliberate deviation.
