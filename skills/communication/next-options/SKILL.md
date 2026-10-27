---
name: next-options
description: End replies with the next step, as one plain line when the agent carries on, or up to three lettered options when the user decides.
disable-model-invocation: true
---

# Next options

The user skims replies and answers a choice with a letter. Follow these rules on every reply to the user for the rest of the conversation, until they ask for normal replies. A delegated task reports to its coordinator in the shape its brief asks for, without options.

## Pick the ending

Keep working through reversible steps inside the agreed scope, as /principle-never-block-on-the-human describes. A question asking you to act ("can you…?") is an instruction: do it. A question about which, when, whether, or why gets an answer, and a change it implies becomes option `a` rather than an edit. When the turn ends, pick its ending by who moves next.

**You** move next when something you started will wake you: a subagent, delegated task, workflow, background command, or watch. End with a plain next step: one sentence of what you will do and what it waits on, as in `**Next**: I'll write the report when the exploration agent finishes.` Add `Nothing needed from you.` unless the reply already says so. When nothing will wake you, keep working in this turn.

**The user** moves next when the work waits for their answer. End with lettered options, by Format:

- at a point only the user can pass: a merge, deploy, force-push, or production write; a push to a branch someone else owns, or one that would dismiss an approval; a message to a person; a scope, interface, or product decision; a credential, payment, or physical step; a check that still fails after the root-cause fix; or an approval the active workflow keeps;
- after answering a question or a read-only request, when a follow-up needs their choice; or
- when only CI, bots, other people's reviews, or threads you didn't start are left, and nothing you started will wake you.

When the user's answer is needed while your own work runs, say in one line what is still running, then end with the options.

**Nobody** moves next when the work is finished. End with **Done**, without options: one line for a small task, or a few bullets of what is finished and what is still open. A finished stage whose next stage waits on the user's go ends with options instead, as Workflow handoffs lists.

**Under a full-autonomy grant**, such as "run until done" in /pstack-mode, decide each call the grant covers and report it rather than offering it. A scope, interface, or product call the grant leaves to the user gets a default you apply and report with its reason, saying in plain words what they could tell you instead, without a letter to type back. Every other point only the user can pass, from the list above, still waits for them and ends with lettered options.

## Format

```markdown
**Next**

- **`a` → fix 1 (currency column) and 2 (null dates), one commit each, and re-review until clean** · _recommended_
- `b` → also add 3 (timeout test)
- `c` → open the draft PR now and track 3 (timeout test) as a follow-up
```

- **At most three options**, `a` to `c`. They are the turn's only question, so the reply doesn't also end on "Should I…?".
- **Only real choices**: each option waits for the user's pick. Work you will do anyway, even a single remaining step, goes in the plain next step.
- **`a` is the recommendation**: bold only its option text and add the italic tag. It serves the session's goal, with side work under another letter, and names every push, post, PR, or issue it creates. It creates no issue, messages no person, and changes no PR's state unless the user asked for that this session.
- **Each option** is a step the user would naturally take next, in plain words that make sense on their own, naming each item it cites as in the example. Build options on PR, CI, thread, or issue state checked this turn, and drop what that state makes moot.
- **Do it yourself**: an option is never a step for the user while a CLI, an MCP server such as Executor, or computer control could do it. Hand over only credentials, payment, or physical actions, and say why.
- **Waiting**: when the next step waits on CI, bots, builds, or other threads, do the next independent work in scope first. When nothing else is left, `a` is the watch (`watch_pull_request` in T3 Code).
- **Manual checks**: before you end a turn on a PR watch, including after each wake, run `node ~/.agents/skills/next-options/scripts/pr-waiting-on.ts <PR>`, or the same script beside this skill where it is installed elsewhere. On `verdict: person`, such as Chromatic baselines that must be accepted or a deployment that waits for approval, the user moves next even while other checks run: stop the watch (`unwatch_pull_request` in T3 Code), put each item with its link under **Needs you**, and end with options. A check like this never finishes on its own, so waiting on it stalls the PR.
- **Leave out** filler such as stop, done, list what's open, or something else, and any option the user passed over in both of the last two lists, including a past `a`.

## Numbered items

Findings, questions, and open items keep their number for the whole session, and new items continue the count. A summary or handoff keeps each number with its name. The user can answer `3` to discuss item 3, `skip 3`, `?` for the current step and open items, a combination such as `a, skip 3`, or in their own words. These answers never get an option line.

## Workflow handoffs

When a stage of this library's flows finishes, the usual `a` is the next stage the user hasn't settled yet:

| Finished                                 | Usual `a`                                                                                    |
| ---------------------------------------- | -------------------------------------------------------------------------------------------- |
| /grill-with-docs                         | /pstack-mode to build the agreed design, or /to-spec when it should be split into tickets    |
| /to-spec                                 | /to-tickets, after a prototype for any open question that running something could settle     |
| /to-tickets                              | /implement-spec                                                                              |
| A Pstack prototype                       | build the recommended variant through Pstack's Feature playbook, or /architect for its shape |
| Implementation with review findings open | fix them and re-review                                                                       |
| A Clean review without a PR              | open a draft PR through /pr                                                                  |
| A draft PR                               | watch it, or address its review comments                                                     |

## Setup

To load these rules at the start of every Claude Code and Codex session, follow [the setup reference](references/setup.md) when the user asks.
