---
name: pstack-how
description: "Use for Pstack code walkthroughs, subsystem behavior, or module placement and ownership questions."
---

Invoke /domain-modeling to resolve and read the invoking project's configured artifacts. Read-only investigations and reviews report documentation drift without edits; creation or implementation reconciles accepted model changes through that owner.

# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Use /pstack-swarm for every explorer and explainer; each is read-only. With no delegation, perform the same passes sequentially and disclose it.

1. Assess complexity. If the scope is ambiguous, state your interpretation and explore. The user can redirect.
   - **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. Spawn one explainer that explores and explains in one pass, built from [the explainer prompt](references/explainer-prompt.md) without the explorer-findings section. Go to step 4.
   - **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

   When in doubt, take the simple path. Complete when the target and the path are explicit.

2. Explore (complex only). Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Spawn all explorers in a single message, each with [the explorer prompt](references/explorer-prompt.md) and its angle filled in. Complete when each angle returns source pointers, runtime flow, and gaps.
3. Synthesize (complex only). Once all explorers have returned, spawn one explainer with [the explainer prompt](references/explainer-prompt.md) and every explorer's findings filled in. Complete when the explanation is supported by inspected code.
4. Present the explainer's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it. The explanation uses the sections defined in the explainer prompt, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas. Complete when the reader can trace the subsystem and distinguish current behavior from rationale, which belongs to /pstack-why.
