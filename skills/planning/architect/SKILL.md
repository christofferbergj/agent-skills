---
name: architect
description: "Use for Pstack interface or module design, caller-first sketches, and implementation against a chosen shape."
---

Invoke /domain-modeling to resolve and read the invoking project's configured artifacts. Read-only investigations and reviews report documentation drift without edits; creation or implementation reconciles accepted model changes through that owner.

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Synthesize across multiple model perspectives, then fill in code against the chosen sketch.

## Start

Open a todolist with one entry per phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Run /how over the relevant subsystems. Naming a file isn't grounding. Produce the architectural explanation /how prescribes. If the design redefines ownership or layering, also run /why on the existing shape so the rationale becomes a constraint, not a guess.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

Complete when every system the new code touches has the architectural explanation /how prescribes, or the work is greenfield.

## Phase B: Sketch

Run /arena with the design-sketch task and the Phase A grounding artifacts. Pass [`references/runner-prompt.md`](references/runner-prompt.md) as each runner's prompt.

Choose the runners as /arena's Phase A does, through /swarm's panel of the session's model and the counterpart.

Design it twice. Require at least two structurally distinct candidates before synthesis, even when the first looks sufficient. This is /principle-exhaust-the-design-space made concrete. Whole-shape alternatives, not point fixes inside one shape.

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md) before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth, in /codebase-design's vocabulary. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. Its synthesis decision fills the rationale's "Synthesis decision" section.

Complete when at least two structurally distinct candidates were screened and /arena returned one synthesized design package.

## Phase C: Agree (opt-in)

Default: proceed directly to implementation with the synthesized design. No human checkpoint.

Opt in to a checkpoint when the invoker explicitly asks: "/architect with checkpoint," "stop and show me before implementing," or similar. Then surface the synthesized design and pause for sign-off.

The synthesis can ship as its own commit either way, as the "scaffold first" mode of /principle-foundational-thinking. Planned and scoped breakage during fill-in is fine, per /principle-outcome-oriented-execution. For adversarial pressure on the design before implementing, run /interrogate on the synthesized sketch.

If the human pushes back on the shape (in a checkpoint or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

Once the human has signed off on an interface, a later incompatible change to it, from a Phase D deviation or a Phase E scrap, goes back to them for sign-off before more code builds on it.

Complete when the synthesized design is accepted: by default, or by the human's sign-off when a checkpoint was requested.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code, pseudocode with logic. The synthesized sketch is the contract. Deviations from it are signal to surface, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

Use /tdd for behavior tests at the sketch's public seams when a practical test path exists.

Complete when no `not implemented` body or pseudocode remains in scope and every deviation from the sketch has been surfaced.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design, per /principle-redesign-from-first-principles and /principle-fix-root-causes.

The signal is a _pattern_, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems are legitimately complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Re-run /how over what's been built.
2. Redesign as if the new constraints had been day-one assumptions, per /principle-redesign-from-first-principles.
3. Subtract before adding, per /principle-subtract-before-you-add. The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and re-run /arena.

Complete when the implementation shows no pattern of friction, or the scrapped sketch has gone back through Phase B.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per [`references/rationale-template.md`](references/rationale-template.md), including the usage sketch and the synthesis decision.
