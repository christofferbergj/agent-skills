---
name: pstack-teach
description: "Use in a Pstack task to explain both how code works and why it has its shape in plain language."
---

# Teach

Explain what something is, how it works, and why it has its current shape. Teaching is read-only unless the user also requests changes.

1. Infer the reader's purpose and existing knowledge from the conversation. Choose the few concepts needed for that purpose. Complete when the explanation has a clear audience, question, and depth.
2. Read the relevant source, then invoke /pstack-how for behavior and /pstack-why for rationale. Narrow the investigation to the question; a small change may need only one. Use /pstack-swarm for independent investigations when useful. Preserve the rationale's confidence and disclosed source gaps. Complete when every explanatory claim has source evidence or an explicit uncertainty.
3. Lead with a plain definition and the smallest complete answer. Connect the general idea to the actual code, then explain the mechanism, reasons, and relevant limits. Use one name per concept. Complete when the reader can follow the behavior without decoding a list of symbols.
4. Show code, a diff, debugger state, or a diagram when it makes the mechanism clearer. Build a complicated flow in stages when that helps; use the host's available image tools for spatial explanations when appropriate. Complete when each illustration supports a concrete claim and remains legible.
5. Invoke /pstack-unslop and deliver the explanation itself. Use plain spoken sentences and preserve substantive uncertainty. In conversation, stop after a useful layer and let the reader steer; avoid quizzes, pacing announcements, stock framing, and a report about the teaching process. Complete when the answer addresses the question at the reader's requested depth.
