---
name: pstack-architect
description: "Use for Pstack interface or module design, caller-first sketches, and implementation against a chosen shape."
---

# Architect

## 1. Ground

Invoke /domain-modeling to read the configured project docs, /codebase-design for architecture vocabulary, and /pstack-principles for design. Invoke /pstack-how on the surrounding system. Invoke /pstack-why if ownership, layering, or historical constraints will change. Greenfield work can skip existing-system archaeology with a reason. Complete when the relevant callers, invariants, and constraints are explained from evidence.

## 2. Sketch

Invoke /pstack-arena on types, signatures, module boundaries, and caller usage, with pseudocode or `not implemented` bodies. Supply [the runner prompt](references/runner-prompt.md), [rationale template](references/rationale-template.md), and [design red flags](references/design-red-flags.md) when applicable. Compare at least two materially different shapes before a consequential boundary locks in. Complete when a synthesized sketch is grounded in concrete calls and a scored comparison.

## 3. Agree when required

An initial approval checkpoint is opt-in. If the user requests one, present the interfaces and tradeoffs and wait. Once an interface is approved, a later incompatible change is a new decision gate. Reconcile settled terms, relationships, ownership, and qualifying decisions through /domain-modeling before implementation. Preserve existing context.md/domain.md roles and link them from the rationale. Complete when the chosen sketch and its canonical artifacts agree within the current grant and any requested approval exists.

## 4. Implement

Recheck /pstack-principles for implementation, then fill in the selected shape using the invoking repository's patterns and /tdd at agreed public seams when useful. Reconcile any accepted model change through /domain-modeling. Validate caller behavior and inspect the diff against the sketch. Complete when the implementation and its evidence satisfy the chosen contract.

## 5. Reconsider a failed shape

If implementation reveals that the boundary is wrong, explain the evidence and replace the sketch coherently. Pause before changing an approved interface. Complete when the design has been repaired or the unresolved decision is explicit.

Return the grounded sketch, alternatives, final interface, implementation evidence, and any approved-interface deviation.
