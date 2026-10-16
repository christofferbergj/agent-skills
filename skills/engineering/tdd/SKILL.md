---
name: tdd
description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle: consult them before and during the loop, not after.

Resolve and read the configured vocabulary and relevant ADRs through /domain-modeling so test names and interfaces match the project's domain language.

Invoke /pstack-principles for the testing and implementation work in this slice before changing code. Recheck when a new design constraint or failure changes the applicable owners; continue the same red/green loop.

## What a good test is

Invoke /pstack-principle-test-behavior-not-implementation for the authoritative test-quality criteria. This owner supplies the red/green mechanics and seam selection.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Use agreed or established public seams.** Reuse seams from the approved spec, existing callers, or the invoking workflow. State what each chosen seam observes and misses. Ask when a new interface or unresolved acceptance decision changes the approved contract; do not repeat an already-resolved approval. If a practical regression path is unavailable, preserve the executable evidence and disclose that gap rather than building a brittle test harness.

When the shape of that interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), invoke /codebase-design for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

## Anti-patterns

- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Separate structural work from the red → green cycle.** Complete accepted prefactoring in its own verified unit before dependent behavior, or address structural findings after green during /code-review.

Complete a slice only when its failing-before evidence, passing-after behavior, and relevant checks agree with the accepted contract.
