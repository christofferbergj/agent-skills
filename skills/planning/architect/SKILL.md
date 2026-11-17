---
name: architect
description: "Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use in a Pstack task for /architect, 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape."
---

Invoke /domain-modeling to resolve and read the invoking project's configured artifacts. Read-only investigations and reviews report documentation drift without edits; creation or implementation reconciles accepted model changes through that owner.

# Architect

Before writing code, trace every system the change touches, then sketch two different shapes for it (types, signatures, module boundaries) and pick the one where each piece of state has one owner, each task has one way to do it, and callers need to know least, judged in /codebase-design's vocabulary. Redesign instead of patching if workarounds repeat.

For a large or contested design, run /arena instead of sketching alone.

Write behavior tests at the chosen shape's public seams through /tdd when a practical test path exists.
