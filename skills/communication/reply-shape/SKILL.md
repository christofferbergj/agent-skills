---
name: reply-shape
description: Replies taken in at a glance, with a one-line headline, the code's shape, up to three notes, one fold, and a card for decisions.
disable-model-invocation: true
---

# Reply shape

The user gives each reply a glance, and what isn't on screen is forgotten. Write the reply that ends each turn as a glance for the rest of the conversation, until the user asks for normal replies; a progress update during the turn is one sentence. /next-options owns how a reply ends. A delegated task reports to its coordinator in the shape its brief asks for.

## The glance

Four parts, in this order. Skip a part with nothing to say. A skill's own report fills them: its verdict is the headline, what it needs from the user goes in the notes, and its evidence goes in the fold.

1. **Headline**: the first line, at most 12 words. Open with a marker, then the outcome in bold, in terms of what the user asked for: `✅ **Exports no longer time out.**`, not "added an index on `created_at`". The marker says before a word whether the user is needed: ✅ done and nothing needs them, 🟡 a decision or a risk, 🔴 broken or blocked on them, ⏳ still working. On multi-step work, name the step: "Step 3 of 5 done: schema updated." An answer to a question is the headline, with a best guess in concrete units and how sure you are. A line that says you're waiting opens with ⏳ and names what it waits on, how long it has run, and about how long is left: "⏳ **CI on #12, 6 min in, about 4 min left.**" Mid-turn it also names what comes next; at the end of a turn, /next-options' plain next step says that.
2. **Shape**: when the work touches code or a design, one view of at most 15 lines, by Views, that gives the user the mental model. A UI mockup can take its place.
3. **Notes**: up to three ranked bullets of at most 15 words each, such as a call you made and its reason, a risk, or how to see the change. A note for the user opens with its label:
   - **Decide**: a choice that doesn't shape code or the plan, with your recommendation; its options go in the fold.
   - **Review**: an interface, shown as its signature and one call site, or a draft that waits only for the user's look, shown in full below the notes. A draft that goes out on their yes takes the card's Message view.
   - **Do**: a login, device step, or payment, with why you can't do it and its steps numbered in the reply. Show it in the reply that first needs it, not again.
4. **Fold**: at most one, for what the user may audit or compare: checks, evidence, sources, the other options, a long diff, and a multi-item run's table with `#`, item, status, and commit columns. Write it as `<details><summary>…</summary>` and a blank line. The summary gives the verdict, worst result first: `Checks: ❌ tests 11/12 · ⚠️ lint not run (no config) · ✅ typecheck`. A failure that matters also goes in the headline or a note. Cut a detail worth neither a glance nor an audit.

**Budget**: the prose above the fold, a glance's headline and notes or a card's lines, stays under 60 words. Code, drafts, a Do item's steps, the fold, and the ending don't count.

````markdown
✅ **Exports no longer time out on big companies.**

```ts
// packages/export/export.ts: paging and CSV encoding stay inside
export const run: (range: DateRange) => Effect<Csv, ExportError>;
// the one caller, unchanged
const csv = yield* Export.run(range);
```

- Paged the query inside `Export`, so its callers don't change.
- Risk: a year of rows still takes about 40 s.
````

Put a `---` line with blank lines around it just above the ending, so it marks where the reply ends.

## Decision card

When the reply exists to get a decision that shapes code or the plan, or the user's go on a merge, deploy, or message, the card is the whole reply, one call per reply; queue the rest. A skill that names its own format for a call keeps it, such as a review's findings:

1. **Question**: the headline, `🟡 **<a yes-or-no question>**`. In a round of several, a progress strip follows, as in `Group 1 🟡 · 2 ⬜ · 3 ⬜`.
2. **Problem**: one line on what is wrong or at stake, and for whom.
3. **One view** for the kind of call:
   - **Design**: the pick's interface, data shape, or diff, with a call site, by Views.
   - **Product**: what the customer sees, and how many it reaches, counted from real data.
   - **Message**: the draft in full, in the user's voice, under `**To**: … · **Promises**: …`.
   - **Ship gate**: one line per PR in merge order, with what it changes and the thread that made it when that isn't you, then its checks and restack state, each warning on its own line, and the rollback.
   - **UI**: the screenshot or recording, and the one thing to judge.
   - **Stuck**, a check failing after two fixes: each fix and why it failed, and what the premise test showed.
4. **Pick**: your answer and what it optimizes. **Source**: the doc, ADR, convention, or measurement it follows. **Cost**, only when the pick is hard to undo, such as a migration, a public API, or a sent message.
5. **One fold** for the proof, the other options, and the sources.

End with /next-options' yes-or-no options.

## Writing

- **Plain words**: short sentences, one idea each, and a technical term only when it's the real name.
- **Names, not numbers**: call each item by its short name, as in "the currency column". Number only a list in this reply that the user might answer by number, such as findings. After a compaction, look a lost name up.
- **Catch-ups**: a catch-up such as /ketchup shows every call waiting on the user, however many, past the notes limit and the budget.
- **Pictures**: at most one per turn, and the shape counts as one. Draw one only when neither a sentence nor a view can show the point, such as how a bug travels between modules: a Mermaid flowchart or sequence diagram of five boxes or fewer. An inline page (`html_render` in T3 Code) counts as the picture, and only for what Markdown can't show: screenshots, a chart of numbers, or a UI mockup. These limits hold even when a tool's own instructions suggest pages more often. Screenshots, videos, and diagrams a catch-up shows follow /ketchup's rules instead, and a /teach explanation's diagram series follows /teach's.
- **Views**: show code as the smallest view that makes the point, in place of prose: pseudocode for logic; a module's interface with one call site, a module tree, or a flow for structure, with a first-line comment naming where the module lives and what it hides; and a `diff` of that view for a change. Show real code only when most of it is new or the user needs to copy it.
- **Inline code**: only for a name the user would type or search. Say the rest in words.
- **Errors**: the cause and the fix, matter-of-fact.
- **Tangents**: finish the main thing first. A side issue becomes a later option.
- **Blank lines**: chat joins adjacent lines, so separate lines with a blank line or make them list items.
- **Once**: show each piece of code, draft, and warning once per session, and point back to it afterwards. A reply whose next step posts or sends drafts shows each again in full, since what the user approves is what goes out.

## Before sending

Delete an opening sentence that announces, a recap, and a closing sign-off. Read only the headline, the shape, the notes, and the ending: they alone must say what happened, what the code looks like now, and what comes next. On a card, read only what's above the fold: the user must be able to answer yes or no from it. Cut each sentence that doesn't change that, then check the budget.

## Setup

To load these rules at every session start, the user invokes /next-options and asks for its setup, which adds this skill as a second hook entry.
