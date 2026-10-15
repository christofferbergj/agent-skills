---
name: pstack-why
description: "Use for Pstack design rationale, regressions, historical constraints, or the evidence behind thresholds."
---

Invoke /domain-modeling to resolve and read the invoking project's configured artifacts. Read-only investigations and reviews report documentation drift without edits; creation or implementation reconciles accepted model changes through that owner.

# Why

Investigate why code has its current shape. Invoke /pstack-how for runtime behavior. Read [the epistemics framework](references/epistemics.md) before making confidence claims.

## 1. Anchor the question

Identify the target files, symbols, relevant commits, PRs, linked issues, and the user's actual question. Use `git blame`, rename-aware `git log --follow`, patch history, and accessible PR discussion. Complete when every investigator can start from the same code and history anchor.

## 2. Map evidence coverage

Discover the host's actual read-capable connectors. Cover source control, issue tracker, long-form documents, team chat, infrastructure observability, error tracking, and product analytics when available and relevant. Record unavailable, empty, and provably irrelevant categories separately. Read [the source index](references/source-playbook.md) for category-specific guidance.

Complete when each category has a source and investigator or an explicit gap or skip reason. A quiet source is a finding, not an excuse to omit it.

## 3. Investigate independently

Use /pstack-swarm for a source-specific investigator per available category. Supply [the investigator prompt](references/investigator-prompt.md), its matching `references/sources/` playbook, and the anchor. Defensive code additionally requires [incident and postmortem research](references/sources/incident-postmortem.md). Work is read-only; connector availability and permissions follow the host, with no assumption that enabling writes is needed to read.

Complete when each category returns cited findings, null results, competing explanations, and confidence, or an explicit tool failure. A genuinely trivial target can be answered inline after accounting for redundant categories.

## 4. Synthesize and present

Use [the synthesizer prompt](references/synthesizer-prompt.md), the confidence framework, anchor, question, and every result. Spot-check citations. Preserve the distinction between established facts, reasonable inference, competing hypotheses, and unknowns. Include one Sources consulted entry for every category. When this informs a change, derive Preserve, Change, Avoid, and Risk constraints.

Complete when the answer's confidence matches the evidence and every source gap remains visible.
