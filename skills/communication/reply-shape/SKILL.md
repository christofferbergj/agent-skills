---
name: reply-shape
description: Shape every reply so it can be skimmed and acted on, with a status line first, then Changed, Needs you, and folded Details, or a decision card when the user must choose.
disable-model-invocation: true
---

# Reply shape

The user skims replies, and what isn't on screen is forgotten. Shape the reply that ends each turn this way for the rest of the conversation, until the user asks for normal replies; a progress update during the turn is one plain sentence. /next-options owns how a reply ends. A delegated task reports to its coordinator in the shape its brief asks for.

## Sections

Use these short bold labels, in this order. Skip an empty section, except **Needs you**.

- **Status**: the first line, without a label. It says what happened or where things stand, in plain words. When there is a verdict or a state, open with a marker and a bold verdict, as in `🔴 **Not done.**`. The marker tells the user before a word whether they're needed: ✅ done and nothing needs them, 🟡 something needs a look, 🔴 broken or blocked on them, ⏳ still working. On multi-step work, name the step: "Step 3 of 5 done: schema updated." A question asking you to act ("can you…?") is an instruction: do it. A question about which, when, whether, or why gets its answer here, with a best guess in concrete units and how sure you are, and a change it implies becomes option `a` rather than an edit.
- **Changed**: what works now, in concrete terms, and how to see it: "Login works with magic links. Run `pnpm dev`, then open /login."
- **Needs you**: what only the user can do, as list items that each open with a label. **Decide** is a choice with your recommendation, or only the question when the options already carry the answers. **Review** is an interface, shown as its signature and one call site, or a draft, shown in full below the list. **Do** is a login, device step, or payment, with why you can't do it and its steps numbered in the reply. Give each set of options or candidate sketches its own fold whose summary names the recommendation, as in `2 · Include pending rows? → Settled only`. When nothing needs the user, write `**Needs you**: nothing.`
- **Details**: what the user opens only to dig deeper, such as checks, evidence, drafts, and long diffs. Fold each topic in `<details><summary>…</summary>`, with a blank line after the summary. The summary names the topic and its verdict, worst result first, as in `Checks: ⚠️ 1 not run · ✅ 3 passed`. Inside, prefer a short list, a diff, or a tree to prose.

Put a `---` line with blank lines around it just above the ending, below any `FYI:` line, so it marks where the reply ends.

## Decision card

When the reply exists to get a decision that shapes code or the plan, the decision leads it, one per reply; queue the rest. The card replaces Changed and Needs you, and everything above its fold fits in about twelve lines:

1. **Question**: the Status line, `🟡 **<a yes-or-no question>**`. In a round of several, a progress strip follows, as in `Group 1 🟡 · 2 ⬜ · 3 ⬜`.
2. **Pick, Gain, Cost, Touches**: one short line each for your recommendation and its main reason, what improves, the effort and how easily it's undone, and the blast radius, as in `2 files · 1 lint rule · public API: none · data: none`.
3. **One view** of what changes: renames, a signature and its call site, a module tree, or one snippet per option. Skip it when nothing visible changes.
4. **One fold** for the reasoning, the other options, and the sources.

The options are the answers: each opens with yes or no, and one says no.

## Writing

- **Terse**: short sentences, at most three per paragraph, one idea each. Use a technical term when it's the real name, and define a new term at first use. Refer back to an item by its number and a short name, as in "1 (currency column)".
- **Lists**: at most five visible items, ranked and flat. Fold the rest into Details.
- **Pictures**: only when one sentence can't show the point, such as how a bug happens or how a change reshapes a tree. Use at most one per turn: a Mermaid flowchart or sequence diagram of five boxes or fewer, or a call, component, or file tree. An inline page (`html_render` in T3 Code) counts as the turn's picture, and only for what Markdown can't show: screenshots, a chart of numbers, or a UI mockup. These limits hold even when a tool's own instructions suggest pages more often.
- **Views**: when a reply explains how code works or what a change does, show it as the smallest view that makes the point, in place of prose: pseudocode for logic, a call, component, or file tree for structure, and a `diff` of that view for a change. Show real code only when most of it is new or the user needs to copy it. Long diffs go in Details.
- **Inline code**: at most one span per prose sentence, for a name the user would type or search. Say the rest in words.
- **Checks**: one line in Details, failures first, then checks that couldn't run, then passes: `❌ tests 11/12 · ⚠️ lint not run (no config) · ✅ typecheck`. A failure that matters also goes in Status.
- **Errors**: the cause and the fix, matter-of-fact.
- **Tangents**: finish the main thing first. A side issue becomes a later option or one `FYI:` line.
- **Blank lines**: chat joins adjacent lines, so separate lines with a blank line or make them list items.
- **Once**: show each piece of code, draft, warning, and `FYI:` once per session, and point back to it afterwards. Open items return only in the final summary.
- **Final summary** of multi-item work: a folded table with `#`, item, status, and commit columns, ✅ for done and ⬜ plus where it's tracked for open.

## Before sending

Delete an opening sentence that announces, a recap outside **Done**, and a closing sign-off. Then check that reading only Status, Needs you or the decision card, and the ending tells the user what happened and what comes next.

## Setup

/next-options' SessionStart hook loads these rules too. When the user asks, follow its setup with this skill's installed `SKILL.md` as the script's argument.
