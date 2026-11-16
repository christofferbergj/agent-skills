---
name: architect
description: "Use for Pstack interface or module design: sketching types, signatures, and module boundaries before code, then implementing against the chosen shape."
---

Invoke /domain-modeling to resolve and read the invoking project's configured artifacts. Read-only investigations and reviews report documentation drift without edits; creation or implementation reconciles accepted model changes through that owner.

# Architect

Before writing code, trace every system the change touches, then sketch two different shapes for it (types, signatures, module boundaries) and pick the one where each piece of state has one owner, each task has one way to do it, and callers need to know least, judged in /codebase-design's vocabulary. Redesign instead of patching if workarounds repeat.

For a large or contested design, run /arena instead of sketching alone.

Write behavior tests at the chosen shape's public seams through /tdd when a practical test path exists. Once the user has approved a shape, an incompatible change to it goes back to them before more code builds on it.

Complete when the code in scope implements the chosen shape, or a repeated workaround sent it back for redesign.
