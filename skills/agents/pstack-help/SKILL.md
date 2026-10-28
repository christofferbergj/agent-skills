---
name: pstack-help
description: "Explain Pstack installation, entrypoints, playbooks, prerequisites, and how to recover a run."
disable-model-invocation: true
---

# Pstack help

Answer the user's question about pstack, hand them a prompt they can send, and link the file the answer came from. For a help question, don't start the work. The user asked how, and a pstack run spends real tokens, so let them send the prompt.

A message that asks for work, such as "use pstack to fix this bug", is not a help question. Read /pstack-mode, do the work under it, and mention once that `/pstack-mode` (`$pstack-mode` in Codex) starts it directly next time.

This file maps questions to the skills and guide pages that hold the answers. Those files own the details. Read the file you route to before you quote it, and trust it when it disagrees with this map. The skills are installed copies the user may not be able to open, so give the user the file's public copy: [this library's README](https://github.com/christofferbergj/agent-skills/blob/main/README.md) links every skill. The guide pages are pstack's upstream guide, `https://github.com/cursor/plugins/blob/main/pstack/docs/guide/` followed by the page. It is written for Cursor, so its Cursor features don't apply here, and where it names `/poteto-mode`, `/poteto-help`, `/setup-pstack`, or `/tdd`, this library installs `/pstack-mode`, `/pstack-help`, `/pstack-setup`, or `/pstack-tdd`.

## Find out what they need

Infer the need from the message and the conversation. A named situation, such as "which skill reviews a PR?", goes straight to its section. If the need is still unclear, ask one multiple-choice question with these options, then answer only the section they pick:

- Get set up
- Start a task with `/pstack-mode`
- Pick a skill for a situation
- Fix a run that went wrong
- Make pstack my own

Check the state that changes the answer, and mention it only when it does:

- No `~/.config/pstack/config.json`, and no file at `PSTACK_CONFIG`, means `/pstack-setup` hasn't run for this user, so every role uses its default model.
- No `verify-*` skill or other app harness in the project means agents have no scripted way to drive the app. Mention `/create-verification-skill` when the question is about proving a change works.
- No formal verification skill in the project means no property is checked past what tests reach. Mention `/create-formal-verification-skill` when the question is about a race, an invariant, or another case tests rarely hit. When one exists and the code it covers changed after the commit it records as last in sync, mention `/maintain-formal-verification-skill` if the question touches that code.

When the configuration is missing and it matters, ask whether the user wants to pick a model for each role and a reasoning budget now. It matters when the user is new, the question is about setup or cost, or the answer depends on which models run. Ask at most once per chat. If the need is also unclear, ask both questions together. Offer two choices:

- Now: give them `/pstack-setup` to type, and answer their question too.
- Later: answer their question, and add one line saying every role keeps its default model until they run `/pstack-setup`.

## Get set up

1. Install the complete library with the Skills CLI command in the [README](https://github.com/christofferbergj/agent-skills/blob/main/README.md#install). The CLI doesn't install dependencies transitively, so a partial install needs the companions the README lists.
2. Run `/pstack-setup`. It asks for a reasoning budget, maps a model to each role, and writes a personal configuration file that delegates read when they start. Then it offers once each to generate a verification skill and a formal verification skill for the project, unless the project already has one.
3. Start a real task with `/pstack-mode`, a goal, and a check that can pass or fail.

Installing changes nothing until a skill loads. Entrypoints, such as `/pstack-mode`, load only when the user types them. Helpers also load when a Pstack task matches their description, principles when any task does, and both when a workflow runs them. The [usage guide](https://github.com/christofferbergj/agent-skills/blob/main/docs/usage.md) and guide page 1, `01-setup.md`, have the details. Offer to word their first prompt with them, per [`references/prompting.md`](references/prompting.md).

If cost is the worry, say where the tokens go and how to spend fewer. pstack spends extra tokens on subagents and review panels. Rerun `/pstack-setup` and pick a smaller budget or cheaper models. A role set to `auto` or `inherit-parent` runs on the chat's model, which saves tokens when the chat runs on a cheaper model. Save `/pstack-mode` for work that needs rigor.

pstack is built for Cursor. This library adapts it to Codex and Claude Code: type `$pstack-mode` in Codex or `/pstack-mode` in Claude Code, and the same for every other skill. Delegation, model roles, and cross-vendor review run through `/swarm` on each host's native tools, and a step that needs a Cursor-only feature, such as Bugbot or Automations, is translated or skipped with a one-line note.

Other tools can read the skills, because they use the Agent Skills format. But most workflow skills, including `/pstack-mode`, `/how`, `/why`, and `/teach`, spawn subagents through `/swarm`, which targets Codex and Claude Code, so those parts may not work there.

## Start a task with `/pstack-mode`

`/pstack-mode` matches the task to a playbook, copies the playbook's steps into the todo list, and runs the other skills as the steps need them. A step it skips stays in the list as `skip: <reason>`. A good prompt states the goal and how to tell it's done. It doesn't list skills, because a hand-written sequence tends to drop or reorder steps the playbook would keep. Read [`references/prompting.md`](references/prompting.md) before you help word one. Guide page 2, `02-poteto-mode.md`, has examples.

Invoking `/pstack-mode` activates it for the current conversation only. Installing it or invoking a helper directly doesn't activate it, and it doesn't carry into other chats, so start each new chat's task with `/pstack-mode`.

Mid-chat, "new task" makes the mode match a fresh playbook. `/pstack-mode` briefs the subagents its playbook steps spawn through `/swarm`. To get the same brief and model roles for a subagent of your own, ask for it through `/swarm`.

## Pick a skill

The default answer is `/pstack-mode`, which runs most of the others when its steps need them. Name a skill directly when the user wants more or less of something than the playbook gives. Read the skill before you recommend it, and give one example prompt.

Rows marked _user entrypoint_ load only when the user types them. Give the user the command to type, and don't load one to do its work yourself, apart from `/pstack-mode` for a work request, as above.

| The user wants to                                                                                                                                                                                    | Skill                                                     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Do any non-trivial task with rigor                                                                                                                                                                   | `/pstack-mode` (_user entrypoint_)                        |
| Check that the agent understood their goal and the problem before it starts                                                                                                                          | `/in-your-own-words`                                      |
| Get a prompt rewritten deeper, not bigger, before sending it: what a top professional would add, their raw material and methods, and an outside check. It returns the prompt and doesn't do the task | `/sharpen`                                                |
| Know how code works now, or where new code should live                                                                                                                                               | `/how`                                                    |
| Know why code is shaped this way, or where a number came from                                                                                                                                        | `/why`                                                    |
| Understand a change or subsystem, explained plainly                                                                                                                                                  | `/teach`                                                  |
| Catch up on their own recent work on a topic                                                                                                                                                         | `/recall`                                                 |
| Catch up on what changed in this chat since their last message, in plain words and small visuals, with every item waiting on them listed and decidable from the reply alone                          | `/ketchup`                                                |
| Catch up like `/ketchup`, in a short subtitled video of slides, with the waiting calls as text under it                                                                                              | `/ketchup-video`                                          |
| Know what a small diff could break outside itself                                                                                                                                                    | `/blast-radius`                                           |
| Settle types and module shape before code that crosses a function boundary                                                                                                                           | `/architect`                                              |
| Get several attempts at one brief, merged into the best one                                                                                                                                          | `/arena`                                                  |
| Run parallel checks over slices, or race workers, as subagents                                                                                                                                       | `/swarm`                                                  |
| Have different models review a diff and try to break it                                                                                                                                              | `/interrogate`                                            |
| Fix a bug test-first when a cheap local test exists                                                                                                                                                  | `/pstack-tdd`                                             |
| Apply TypeScript rules to `.ts` or `.tsx` work                                                                                                                                                       | `/typescript-best-practices`                              |
| Strip comments before review, using a reviewer that didn't write them                                                                                                                                | `/no-comments`                                            |
| Clean AI tells out of prose                                                                                                                                                                          | `/unslop`                                                 |
| Write docs, an RFC, a README, a PR description, or a commit message to a standard                                                                                                                    | `/technical-writing`                                      |
| Hear the last reply again in plain words                                                                                                                                                             | `/bro` (_user entrypoint_)                                |
| Give agents a scripted way to drive the app and prove behavior                                                                                                                                       | `/create-verification-skill`                              |
| Bring a verification skill and its feature map back in line with the app                                                                                                                             | `/maintain-verification-skill` (_user entrypoint_)        |
| Formally verify a race, invariant, or other property that tests rarely reach                                                                                                                         | `/create-formal-verification-skill` (_user entrypoint_)   |
| Bring a formal verification back in line after the code it covers changed, and learn whether a failure is drift or a bug                                                                             | `/maintain-formal-verification-skill` (_user entrypoint_) |
| Show a PM or designer what the user sees as a chart checked by a TLA+ model, with the shortest path to each state that breaks a rule                                                                 | `/statechart`                                             |
| Vet a performance number before reporting or acting on it                                                                                                                                            | `/benchmark-checklist`                                    |
| Run a large or cross-cutting change, or one to review after stepping away                                                                                                                            | `/figure-it-out`                                          |
| Keep a decision log during a run, and review it afterward                                                                                                                                            | `/show-me-your-work`                                      |
| Pick a model for each role and a reasoning budget                                                                                                                                                    | `/pstack-setup`                                           |
| Turn their own working habits into a personal mode skill                                                                                                                                             | `/automate-me` (_user entrypoint_)                        |
| Turn what a finished task taught into skill edits                                                                                                                                                    | `/reflect`                                                |
| Stop agents from repeating the same mistakes in this repo                                                                                                                                            | `/correct`                                                |
| Build a page whose buttons wake an existing agent webhook receiver                                                                                                                                   | `/make-bot-ui` (_user entrypoint_)                        |
| Find their way around pstack                                                                                                                                                                         | `/pstack-help` (_user entrypoint_)                        |

If an installed Pstack skill, one whose description names Pstack, is missing from the table, read its frontmatter and route by its description. A skill whose frontmatter sets `disable-model-invocation: true` is a user entrypoint. The `principle-*` skills are covered under principles below.

Close calls:

- `/how` explains what the code does. `/why` explains the reasons. `/teach` runs one or both and explains the result plainly.
- `/arena` gives every worker the same brief and merges the best parts. `/swarm` splits work into slices or a race and returns one report.
- `/architect` implements right after it settles the design. Add "with checkpoint" to review the design before it writes code.
- `/interrogate` reviews the diff. `/blast-radius` looks for breakage outside the diff and proves the one fact that makes the change safe.
- `/recall` rebuilds context across recent chats. `/ketchup` covers only this chat since the user's last message. Resuming one specific chat or branch is the Session pickup playbook.
- `/figure-it-out` designs one rigorous run. The Orchestrate playbook runs a program that spans days and many PRs. The Autonomous run playbook drives one task to a finish condition.

Not in pstack:

- `/loop` is a Claude Code built-in.
- pstack has no `/orchestrate` skill. Orchestrate is a `/pstack-mode` playbook. If the slash menu shows `/orchestrate`, another plugin or skill source provides it.

## Playbooks and principles

Playbooks are step lists inside `/pstack-mode`, not skills, so they have no slash command. Inside `/pstack-mode`, describing the task picks one, and these phrases name one directly:

- "babysit this pr" or "check on pr 123" runs Babysit. It drives the PR to merge-ready and stops there. It doesn't merge unless the user asks to merge, land, or ship.
- "land the stack" runs Shipping.
- "take over this branch" runs Session pickup.
- "pause safely" runs Pause safely.
- "full autopilot on this queue" runs Autopilot-full. "autopilot, don't merge" runs Autopilot-stack.
- "run the eval playbook" runs Eval.

Without `/pstack-mode`, a phrase such as "babysit this pr" can start another installed skill for the same job instead. `/pstack-mode` lists every playbook and when it applies. Guide page 6, `06-verify-and-ship.md`, covers opening, babysitting, and landing a PR.

pstack has no planning skill. The host's plan mode works alongside it. For work that spans phases or stacked PRs, asking `/pstack-mode` for a plan runs its Multi-phase plan playbook, which writes the plan and doesn't implement it. For a design question, the Prototype playbook or `/architect` settles it in code first.

Principles are one-rule skills that `/pstack-mode` reads through `/principles` and cites in its replies. The user rarely invokes one. They steer with the names instead, as in "apply prove it works. show me the real output." Typing `/principle-<name>` still loads one on demand. Guide page 8, `08-principles.md`, lists them.

## Fix a run that went wrong

| Symptom                                                  | Fix                                                                                                                                                                                                               |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The mode stopped applying after a few turns              | Invoke `/pstack-mode` again with the task, and start each task in a new chat with it.                                                                                                                             |
| A question got treated as the next step of the last task | Say "new task", or say the turn doesn't need the mode.                                                                                                                                                            |
| A new model choice had no effect                         | Check that `/pstack-setup`'s file reads back with the choice in the current host's section. A model the host rejects falls back to its default, with a note.                                                      |
| Runs cost more than expected                             | See the cost paragraph under Get set up.                                                                                                                                                                          |
| A skill didn't load on its own                           | Entrypoints load only when the user types them. Helpers load when a Pstack task matches their description, principles when any task does, and both when `/pstack-mode` runs them, and it doesn't run every skill. |
| Parallel agents overwrote each other                     | Give each agent its own worktree. `/swarm` does this for every writer.                                                                                                                                            |
| An overnight run moved but finished nothing              | A loop needs a check that can pass or fail, not a duration. See guide page 7, `07-overnight.md`.                                                                                                                  |
| The reply claims success from a green build              | Ask for the real command, flow, stored value, or profile. That's the prove-it-works principle.                                                                                                                    |

For a run that drifts, [`references/prompting.md`](references/prompting.md) has one-line steers. Guide page 10, `10-recipes-and-pitfalls.md`, has more pitfalls and the recipes worth copying.

## Make pstack my own

- `/automate-me` drafts a personal mode skill from the user's own history, to use alongside `/pstack-mode`.
- `/reflect` after a session turns its lessons into skill edits the user approves.
- `/pstack-mode write a skill for <workflow>` runs the authoring playbook. The eval playbook tests a skill change blind.
- Fix a misbehaving skill in its own PR, not inside the feature work where it went wrong.
- `/maintain-skills`, run from this library's source repository, updates the whole library from upstream and audits it. Read the saved maintenance automation for its current cadence and model.

Guide page 9, `09-make-it-yours.md`, covers each of these.

## Reply

Lead with the answer. Give at most one example prompt in a code block, adapted from [`references/recipes.md`](references/recipes.md) when one fits, then the link to that file. Keep it short unless the user asked for the whole map.
