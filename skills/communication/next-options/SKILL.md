---
name: next-options
description: End replies with what comes next, as one plain line when the agent carries on, or up to three lettered options, the first one recommended, when the user decides.
disable-model-invocation: true
---

# Next options

The user skims replies and answers a choice with a letter. Follow these rules on every reply to the user for the rest of the conversation, until they ask for normal replies. A delegated task reports to its coordinator in the shape its brief asks for, without options.

## Pick the ending

Keep working through reversible steps inside the agreed scope, as /pstack-principle-never-block-on-the-human describes. When the turn ends, pick its ending by who moves next.

Offer lettered options, by Format, only when the work waits for the user's answer:

- at a point only the user can pass: a merge, deploy, force-push, or production write; a message to a person; a scope, interface, or product decision; a credential, payment, or physical step; a check that still fails after the root-cause fix; or an approval the active workflow keeps;
- after answering a question or a read-only request; or
- when only CI, bots, reviewers, or other threads are left.

Write a plain next step when you will carry on without the user's answer, because a subagent, delegated task, workflow, or watch you started will wake you. It is one line with no letter, list, or question, saying what you will do, what it waits on, and that nothing is needed: `**Next**: I'll write the report when the exploration agent finishes. Nothing needed from you.`

End finished work with **Done**: one line for a small task, or a few bullets of what is finished and what is still open. Add options after it only when a next step follows naturally.

## Format

```markdown
**Next**

- **`a` → fix 1 and 2, one commit each, and re-review until clean** · _recommended_
- `b` → also add the timeout test (3)
- `c` → open the draft PR now and track 3 as a follow-up
```

- **At most three options**, `a` to `c`. They are the turn's only question, so the reply doesn't also end on "Should I…?".
- **Only real choices**: each option is a step you won't take until the user picks it. Work you will do anyway is the plain next step, never an option, not even a lone `a`.
- **`a` is the recommendation**: bold only its option text and add the italic tag. It serves the session's goal, with side work under another letter, and names every push, post, PR, or issue it creates. It creates no issue, messages no person, and changes no PR's state unless the user asked for that this session.
- **Each option** is a step the user would naturally take next, in plain words that make sense on their own. Build options on PR, CI, thread, or issue state checked this turn, and drop what that state makes moot.
- **Do it yourself**: an option is never a step for the user while a CLI, an MCP server such as Executor, or computer control could do it. Hand over only credentials, payment, or physical actions, and say why.
- **Waiting**: when the next step waits on CI, bots, builds, or other threads, `a` is the next independent work, or the watch (`watch_pull_request` in T3 Code) when nothing else is left. A subagent or delegated reviewer that the step depends on is part of the work, so wait for it and end with the plain next step.
- **Leave out** filler such as stop, done, list what's open, or something else, and any option the user passed over in both of the last two lists, including a past `a`.

## Numbered items

Findings, questions, and open items keep their number for the whole session, and new items continue the count. The user can answer `3` to discuss item 3, `skip 3`, `?` for the current step and open items, a combination such as `a, skip 3`, or in their own words. These answers never get an option line.

## Workflow handoffs

When a stage of this library's flows finishes, the usual `a` is the next stage the user hasn't settled yet:

| Finished                                 | Usual `a`                                                                                        |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------ |
| /grill-with-docs                         | /to-spec                                                                                         |
| /to-spec                                 | /to-tickets, or a counterpart review of the spec through /review-loop for a consequential design |
| /to-tickets                              | /implement-spec                                                                                  |
| Implementation with review findings open | fix them and re-review                                                                           |
| A Clean review without a PR              | open a draft PR through /pr                                                                      |
| A draft PR                               | watch it, or address its review comments                                                         |

## Setup

To load these rules at the start of every Claude Code and Codex session, follow [the setup reference](references/setup.md) when the user asks.
