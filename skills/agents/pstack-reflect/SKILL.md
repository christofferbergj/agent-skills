---
name: pstack-reflect
description: "Use for Pstack reflection on corrections in the current conversation and reviewable improvements to source skills."
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/pstack-reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Before fanning out, find this conversation's transcript. Use the host's active conversation API when it exposes one. Otherwise invoke /pstack-recall to list this repository's recent Codex and Claude Code sessions and read a candidate. Do not glob across `~/.claude/projects/*/` or every Codex session. That crosses workspace boundaries and reads private chats from unrelated projects.

For each candidate, newest first, read its first user prompt, past host-injected context such as the AGENTS.md instructions Codex records as the first user message. Take the session whose first user prompt contains the conversation's opening user prompt. If none matches, pass a tight digest of the session instead.

Complete when the transcript path or the digest is fixed.

## 2. Spawn three reviewers in parallel

Use /pstack-swarm to start all three before waiting on any, as native subagents that keep the session's MCP and connector tools. Reviewers need MCP access to look up the tickets, chat threads, and observability traces the transcript references, and a tool-restricted reviewer has none. /pstack-swarm sets each subagent's model and effort from the user's configured roles, and otherwise the session's.

| Lens      | Prompt template                    |
| --------- | ---------------------------------- |
| Judgment  | `references/judgment-reviewer.md`  |
| Tooling   | `references/tooling-reviewer.md`   |
| Divergent | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in their result.

Complete when all three reviewers have returned findings, or a missing one is disclosed.

## 3. Synthesize

One subagent through /pstack-swarm, with the same MCP and connector tools as the reviewers. It spot-verifies citations through MCP. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

Complete when the synthesizer has returned that list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See /pstack-principle-encode-lessons-in-structure.

Complete when every remaining Accepted item is one only an instruction can carry.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting, when the user's existing authorization covers filing; otherwise list it in the summary as a proposal. Only the Accepted list waits for approval.

Edit each skill at its source, the repository /pstack-setup records or the one this skill was installed from, never the installed copy. Before approval, show each skill's destination. Never open a PR or push.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): draft it with /writing-for-agents, exercise it on a representative case, and revise until the case passes.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to /writing-for-agents and tune the description, the pointer that decides when the skill loads.
- `new skill via writing-for-agents: <kebab-name>`: hand creation to /writing-for-agents. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

Complete when every approved edit is applied and validated, and every other Accepted item is recorded as declined.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.

Complete when every reviewer finding appears in exactly one of these lines.
