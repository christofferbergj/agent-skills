---
name: pstack-how
description: "Use for Pstack code walkthroughs, subsystem behavior, or module placement and ownership questions."
---

# How

1. Interpret the question from repository context. For a single module or utility, use one focused explainer; for a cross-cutting subsystem, split into distinct evidence-gathering angles. Complete when the target and appropriate depth are explicit.
2. Use /pstack-swarm for the explainer or independent read-only explorers. Each explorer receives [the explorer prompt](references/explorer-prompt.md) and a distinct angle. Scale the wave to the task and host capacity. Complete when each angle returns source pointers, runtime flow, and gaps.
3. Give one explainer [the explainer prompt](references/explainer-prompt.md) and all findings. A simple task combines exploration and explanation. With no delegation, perform the same passes sequentially and disclose it. Complete when the explanation is supported by inspected code.
4. Present Overview, Key concepts, How it works, Where things live, and Gotchas where relevant. Lightly edit for clarity without replacing evidence with speculation. Complete when the reader can trace the subsystem and distinguish current behavior from rationale, which belongs to /pstack-why.
