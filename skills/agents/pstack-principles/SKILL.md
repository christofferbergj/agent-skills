---
name: pstack-principles
description: Select and apply Pstack principles during design interviews, spec writing, ticket planning, implementation, testing, and review.
---

# Shared Pstack principles

Apply principles inside the calling workflow. This skill selects existing principle owners; it neither activates /pstack-mode nor starts another coordinator. Each `/pstack-principle-*` skill owns its applicability and rules.

## 1. Establish the phase

Identify the caller's current phase, accepted scope, existing artifacts, approved interfaces, and action grant. For a standalone invocation, establish the same brief from the request. Complete when the artifact to produce or assess and its completion boundary are explicit.

## 2. Select the owners

Discover the complete installed `/pstack-principle-*` inventory through the host's skill index. If that index is partial, enumerate the configured skill roots and resolve duplicate installations before selecting. Evaluate every owner's description against the actual work in this phase, including work about to start. In planning, include the implementation being proposed; in review, include the changes being assessed. Read every matching skill in full and apply its rules to the current artifact. Use the descriptions as the selection rules, including for newly added principles; keep no second trigger catalog here.

Reuse an already-loaded owner only while its instructions and applicability remain current. A missing dependency is a named coverage gap, never an applied principle. Complete when every discovered owner has been considered and every applicable owner has been read, or its absence is reported.

## 3. Apply within the calling contract

Use the selected owners to change concrete design, code, test, or review decisions. Keep these composition boundaries:

- The user's accepted requirements, repository constraints, and action grants bind the work. A principle does not authorize a larger feature, a replacement spec, external publication, or a later workflow phase.
- An interview uses principles to sharpen recommendations and unresolved questions; its confirmation checkpoint remains. Spec writing synthesizes settled decisions and records unresolved conflicts as blockers. Ticket planning puts required preparation and migration gates in the existing graph. Implementation follows accepted decisions and raises a material contract change through the caller's decision gate.
- A requirement for a later phase becomes a constraint or evidence requirement in the current artifact. Distinguish planned checks and tools from completed implementation and observed proof.
- A review assesses the current artifact without editing it. Route findings through /code-review when it is the caller; preserve its separate Standards and Spec axes.

Resolve migration strategy through /pstack-principle-migrate-callers-then-delete-legacy-apis and test quality through /pstack-principle-test-behavior-not-implementation when their branches apply. The calling workflow retains its lifecycle, including /tdd's red/green mechanics and /code-review's assessment. Return to that workflow instead of invoking it recursively. Complete when each selected rule has a concrete application, an evidence-backed non-applicability decision, or an explicit unresolved conflict.

## 4. Carry the decisions

Record accepted decisions and required proof in the existing spec, tickets, or execution evidence. Reconcile domain changes through /domain-modeling within the existing edit grant. Keep one canonical artifact for each role.

For delegated implementation or review, pass the current phase, selected owner names, resolved instruction paths or contents, accepted decisions, and evidence requirements in the brief. Require workers to invoke /pstack-principles again when their work reveals a new applicable branch. Child discovery or inherited parent context is not proof that a worker received the rules. Complete when every affected worker and artifact carries the applicable decisions and checks.

## 5. Recheck before completion

Repeat selection when the phase, constraints, or observed failures change, and before declaring the phase complete. Verify the actual phase artifact through the selected owners. Completion requires every applicable rule to be satisfied or reported as a gap against that artifact. Report principles only when they changed a concrete choice; omit a ceremonial list of loaded skills.
