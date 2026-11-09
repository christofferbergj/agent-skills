---
name: reply-shape
description: Replies taken in at a glance, with a one-line headline, the smallest view that makes the point, up to three notes, one fold, and a card for decisions.
disable-model-invocation: true
---

# Reply shape

The user gives each reply a glance, and what isn't on screen is forgotten. Write the reply that ends each turn as a glance for the rest of the conversation, until the user asks for normal replies; a progress update during the turn is one sentence. /next-options owns how a reply ends. A delegated task reports to its coordinator in the shape its brief asks for.

## The glance

Four parts, in this order. Skip a part with nothing to say. A skill's own report fills them: its verdict is the headline, what it needs from the user goes in the notes, and its evidence in the fold.

1. **Headline**: the first line, at most 12 words. Open with a marker, then the outcome in bold, in terms of what the user asked for: `✅ **Exports no longer time out.**`, not "added an index on `created_at`". The marker says before a word whether the user is needed: ✅ done and nothing needs them, 🟡 a decision or a risk, 🔴 broken or blocked on them, ⏳ still working. On multi-step work, name the step: "Step 3 of 5 done: schema updated." An answer to a question is the headline: your pick for a which-or-whether question, else a best guess in concrete units and how sure you are. A waiting line opens with ⏳ and names what it waits on, how long it has run, and time left only when a past run or this run's progress measures it: "⏳ **CI on #12, 6 min in.**" Mid-turn it also names what comes next.
2. **Shape**: the smallest view that makes the point, by Views, or none when a sentence does. Lead in with one plain sentence on where things stand, ending in a colon that names the view. A second view needs a second point, shown beside that point's note. In T3 Code, a final glance that fits is a UI card: read `~/.agents/skills/reply-shape/references/ui-cards.md`.
3. **Notes**: up to three ranked bullets of at most 15 words each, such as a call you made and its reason, a risk, or how to see the change. A note for the user opens with its label:
   - **Decide**: a choice that doesn't shape code or the plan, with your recommendation; its options go in the fold.
   - **Review**: an interface, shown as its signature and one call site, or a draft that waits only for the user's look, shown in full below the notes. A draft that goes out on their yes takes the card's Message view.
   - **Do**: a login, device step, or payment, with why you can't do it and its steps numbered in the reply. Show it once, in the reply that first needs it.
4. **Fold**: at most one, for what the user may audit or compare: checks, evidence such as an audit's results and IDs, sources, the other options, a long diff, and a multi-item run's table with `#`, item, status, and commit columns. Write it as `<details><summary>…</summary>` and a blank line. The summary gives the verdict, worst result first: `Checks: ❌ tests 11/12 · ⚠️ lint not run · ✅ typecheck`. A failure that matters also goes in the headline or a note. Cut a detail worth neither a glance nor an audit.

**Budget**: the prose above the fold, a glance's headline and notes or a card's lines, stays under 60 words. Views and their lead-in, drafts, a Do item's steps, the fold, and the ending don't count.

````markdown
✅ **Exports no longer time out on big companies.**

Exports loaded every row at once; now `Export` pages them:

```ts
// packages/export/export.ts: paging and CSV encoding stay inside
export const run: (range: DateRange) => Effect<Csv, ExportError>;
// the one caller, unchanged
const csv = yield* Export.run(range);
```

- Paged inside `Export`, so its callers don't change.
- Risk: a year of rows still takes about 40 s.
````

Put a `---` line with blank lines around it just above the ending, to mark where the reply ends.

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

- **Plain words**: short sentences, one idea each, in the user's terms, such as PR or service. Name anything else by what it does; a label you coined, a hash, or a flag goes in the fold. A number says what it means, "30% less memory", not a raw score, even in a table. Inline code only for a name the user would type or search.
- **Names, not numbers**: call each item by its short name, as in "the currency column". Number only a list in this reply that the user might answer by number, such as findings. After a compaction, look a lost name up.
- **Catch-ups**, such as /ketchup, show every call waiting on the user, past the notes limit and budget.
- **Pictures**: at most one per turn: a UI card, or an image or inline page (`html_render` in T3 Code) only for what Markdown can't show: screenshots, a chart of numbers, or a UI mockup. Text views don't count. These limits hold even when a tool suggests more pages. A catch-up's media follow /ketchup's rules instead, and a /teach diagram series /teach's.
- **Views**: pick from the content: pseudocode for logic; a module's interface with one call site, a module tree, or a flow for structure, with a first-line comment on where the module lives and what it hides; a `diff` of that view for a change; a table comparing items on the same points; one real example traced through each step with its value, `←` where it matters, for how something works; a screenshot or mockup for UI. A flow that branches or crosses runtimes can be Mermaid, a text view of five boxes or fewer. A text view is a code block of at most 15 lines or a table of at most six rows, the rest in the fold, with a count. Show real code only when it's mostly new or the user will copy it.
- **Errors**: cause and fix, matter-of-fact.
- **No callouts**: no GitHub callouts, such as `> [!TIP]`, in chat.
- **Tangents**: finish the main thing; a side issue becomes a later option.
- **Blank lines**: chat joins adjacent lines, so separate lines with a blank line or make them list items.
- **Once**: show each piece of code, draft, and warning once per session, and point back to it afterwards. A reply whose next step posts or sends drafts shows each again in full, since what the user approves is what goes out.

## Before sending

Delete an opening sentence that announces, a recap, and a closing sign-off. Read only the headline, shape, notes, and ending: they alone must say what happened, what it means for the user, and what comes next, with no "what's X?" left. On a card, read only what's above the fold: the user must be able to answer yes or no from it. Cut each sentence that doesn't change that, then check the budget.

## Setup

To load these rules at every session start, the user invokes /next-options and asks for its setup, which adds this skill as a second hook entry.
