---
name: reply-shape
description: Replies taken in at a glance, with a one-line headline, a fact table of labelled rows or bold items, one fold, and a card for decisions.
disable-model-invocation: true
---

# Reply shape

The user gives each reply a glance, and what isn't on screen is forgotten. Write the reply that ends each turn as a glance for the rest of the conversation, until the user asks for normal replies; a progress update during the turn is one sentence. /next-options owns how a reply ends. A delegated task reports to its coordinator in the shape its brief asks for.

## The glance

Four parts, in order; skip an empty one. A skill's own report fills them: its verdict is the headline, what it needs from the user goes in rows, and its evidence in the fold.

1. **Headline**: the first line, at most 12 words. Open with a marker, then the outcome in bold, in terms of what the user asked for, not the code you changed. The marker says whether the user is needed: ✅ done and nothing needs them, 🟡 a decision or a risk, 🔴 broken or blocked on them, ⏳ still working. On multi-step work, name the step. An answer to a question is the headline: your pick for a which-or-whether question, else a best guess in concrete units and how sure you are. A waiting line opens with ⏳ and names what it waits on, how long it has run, and time left only when measured: "⏳ **CI on #12, 6 min in.**" Mid-turn it also names what comes next.
2. **Fact table** for one subject: two columns, right under the headline, none when the whole point is one sentence. A report on several things gets **items** instead: a list item per PR, finding, option, or job, its name in bold and a clause of at most 12 words, details under it or in the fold, grouped by the thing, findings under **Must fix**, then **Cleanups**.
   - **Header row**: the subject: a PR with what it changes, its state, and size, or one word, such as Change, then the point.
   - **Rows**: at most five `label | value` rows of at most 20 words a value, the header's too. The label is one word: Risk, Unsure (what you couldn't check), Why, Effect (measured), Proof (checks or how to see it), Undo, Skipped, Queued, a decision's Pick, Source, and Cost, and the user items below. Risk and Unsure come first, each value opening with ⚠️.
3. **View**: only what the table can't hold, in its own block under it, by Views.
4. **Fold**: at most one, for what the user may audit or compare: checks, evidence such as an audit's results and IDs, sources, the other options, a long diff, and a multi-item run's `#`, item, status, and commit table. Write it as `<details><summary>…</summary>` and a blank line. The summary gives the verdict, worst result first: `Checks: ❌ tests 11/12 · ⚠️ lint not run · ✅ typecheck`. A failure that matters also gets a Risk row, or a ⚠️ line under its item. Cut a detail worth neither a glance nor an audit.

User items are rows, or a line under their item:

- **Decide**: a choice that doesn't shape code or the plan, with your recommendation; its options go in the fold.
- **Review**: an interface or a draft that waits only for the user's look, shown as the view. A draft that goes out on their yes takes the card's Message view.
- **Do**: a login, device step, or payment, with why you can't do it, its steps numbered below. Show it once, in the reply that first needs it.

**Budget**: prose outside the table, up to six items, and view stays under 60 words; a fact that fits no row goes in the fold. Drafts, steps, the fold, and the ending don't count.

```markdown
✅ **Exports no longer time out on big companies.**

| #212  | Exports page their rows · draft · +86 −40 |
| ----- | ----------------------------------------- |
| Risk  | ⚠️ A year of rows still takes 40 s.       |
| Proof | Tests 41/41 · 90,000 rows in 38 s.        |
```

Put a `---` line, blank lines around it, just above the ending.

## Decision card

When the reply exists to get a decision that shapes code or the plan, or the user's go on a merge, deploy, or message, the card is the whole reply, one call per reply; queue the rest as Queued rows. A skill that names its own format for a call keeps it, such as a review's findings:

1. **Question**: the headline, `🟡 **<a yes-or-no question>**`. In a round of several, a progress strip follows, as in `Group 1 🟡 · 2 ⬜ · 3 ⬜`.
2. **Fact table**: the header row is `Problem`, then what is wrong or at stake, and for whom. Pick: your answer and its long-term reason. Source: what it follows. Cost: only when the pick is hard to undo, such as a migration or a sent message.
3. **One view** under it, for the kind of call:
   - **Design**: the pick's interface, data shape, or diff, with a call site.
   - **Product**: what the customer sees, and how many it reaches, counted from real data.
   - **Message**: the header row is `To`, not Problem, then who gets it; Cost is what it commits the user to; the draft follows in full, in their voice.
   - **Ship gate**: the header row is the PR, then what it changes for users rather than its title, its state and size, and the thread that made it if another did. Risk rows hold each warning, Proof the checks and restack state, and Undo the rollback only when a revert won't do. The `You accept` view gives each PR's New, Changes, Edits, Goes live and who runs it, and Left out, `none` when empty. Several PRs share a `Stack` table in merge order, a view column each, or a table each past three.
   - **UI**: the screenshot or recording, and the one thing to judge as a Review row.
   - **Stuck**, a check failing after two fixes: each fix and why it failed, and what the premise test showed as Why.
4. **One fold** for the proof, the other options, and the sources.

End with /next-options' yes-or-no options.

## Writing

- **Plain words**: short sentences, one idea each, in the user's terms. Name anything else by what it does; a label you coined, a hash, or a flag goes in the fold. A number says what it means, not a raw score, even in a table. Inline code only for a name the user would type or search.
- **Names, not numbers**: call each item by its short name; number only a list the user might answer by number. After a compaction, look a lost name up.
- **Catch-ups**, such as /ketchup, show every call waiting on the user, past the row limit and budget.
- **Pictures**: at most one per turn, an image or inline page, only for screenshots, a chart, or a UI mockup; text views don't count, even when a tool suggests more. A catch-up's media follow /ketchup's rules instead, and a /teach diagram series /teach's.
- **Views**: pick from the content: pseudocode for logic; a module's interface with one call site, a module tree, or a flow for structure, its first line saying where the module lives and what it hides; a `diff` of that view for a change; a table comparing items on the same points; one real example traced through each step with its value, `←` where it matters, for how something works; a screenshot or mockup for UI. A branching flow can be Mermaid, five boxes or fewer. A text view is a code block of at most 15 lines or a table of at most six rows, the rest in the fold, with a count. Show real code only when it's mostly new or the user will copy it.
- **Errors**: cause and fix, matter-of-fact.
- **No callouts**: no GitHub callouts, such as `> [!TIP]`, in chat.
- **Tangents**: finish the main thing; a side issue becomes a later option.
- **Blank lines**: chat joins adjacent lines, so separate them with a blank line or make them list items.
- **Once**: show each piece of code, draft, and warning once per session. A reply whose next step posts or sends drafts shows each again in full.

## Before sending

Delete an opening sentence that announces, a recap, and a closing sign-off. Read only the headline, the table or items, and the ending: they alone must say what happened, what it means for the user, and what comes next, with no "what's X?" left. On a card, they must let the user answer yes or no. Cut each row that doesn't change that, then check the limits.

## Setup

To load these rules at every session start, the user invokes /next-options and asks for its setup, which adds this skill as a second hook entry.
