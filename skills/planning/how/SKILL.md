---
name: how
description: "Use for Pstack code walkthroughs, subsystem behavior, or module placement and ownership questions."
---

Invoke /domain-modeling to resolve and read the invoking project's configured artifacts. Read-only investigations and reviews report documentation drift without edits; creation or implementation reconciles accepted model changes through that owner.

# How

Explore the codebase to answer "how does X work?" questions.

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

1. Explain. Use /swarm to start one read-only subagent that explores and explains in one pass. Give it the user's question and this brief:

   > You are writing an architectural explanation for a senior engineer. Explore the codebase and write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model. They should understand the architecture well enough to start working in it confidently. You have read-only access to the codebase.

   With no delegation, explore and write the explanation yourself from the same brief, and disclose it. Complete when the explanation is supported by inspected code.

2. Present the subagent's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it. Complete when the reader can trace the subsystem and distinguish current behavior from rationale, which belongs to /why.
