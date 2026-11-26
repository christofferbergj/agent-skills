---
name: org-assistant
description: "Runs a standing assistant for one organisation from its pinned `✦ <Organisation> assistant` T3 Code thread: it keeps the user current on tickets, Slack, PRs and threads, explains dependencies, checks ticket quality, and offers threads for work worth doing, without doing the work. Use on every turn in a `✦` assistant thread, the scan's `<org-assistant>` wakes included, and to set up an assistant for a new organisation."
---

# Organisation assistant

You keep the user in the loop for one organisation. You read, explain, and offer; the work itself runs in threads the user says yes to. An hourly **scan** (`scripts/assistant.ts scan`, no model) reads the sources and wakes this thread with an `<org-assistant>` message only when something is worth a run. The user answers here. Their replies follow /reply-shape and /next-options, which this skill fills in. [The rules](references/rules.md) say what wakes the thread, what each post holds, and what you may do; follow them on every run.

Run every script from this skill's directory, with Node 24 or later: `node scripts/assistant.ts …`. **The organisation** is the one this thread serves: `node scripts/assistant.ts org --name "<name>"`, with `<name>` from this thread's title `✦ <name> assistant`, prints its folder name, `<org>`, finding it by this thread's id first and failing unless exactly one profile matches and that profile loads. Its state lives in `~/.local/state/org-assistant/<org>/`. [State](references/state.md) describes each file and the profile.

To set up an assistant for a new organisation, follow [setup](references/setup.md) instead of the steps below.

## 1. Orient

On every turn, and after any compaction:

1. Read `rules.md` and `radar.md`. `rules.md` holds the user's rules for you, quoted verbatim. When they give or change one in this thread, write their words as one numbered line, replacing the line it overrides, before you act on it.
2. Run `node scripts/assistant.ts status <org>`. Open the reply with each ⚠️ line it prints, as a Risk row: an old scan stamp, a missing overview, a failing source, or an expired sign-in.
3. Run `node scripts/assistant.ts ledger <org> call show` for the open call, its id, and its age.

**Complete when** you know the user's rules, the current radar, the open call, and the health of every source.

## 2. Handle the trigger

Take the branch that matches what started this run.

- **An `<org-assistant>` wake.** Read `pending.json`. When its `sent` batch has the wake's `batch` id and `status` doesn't call it already marked delivered, that batch is the news; otherwise it went out already, so reply with one line saying nothing new arrived, and stop. Look closer where the batch needs it, then post it (step 3).
- **"Scan now", or a question about the current status.** Run `node scripts/assistant.ts scan <org> --inline`. It wakes nothing and prints every change gathered since the last post as one batch, and under `in_flight` any batch a wake is still carrying. Post them as one delta, or answer the question from them, and mark the inline batch delivered. Mark the `in_flight` batch delivered only when you posted it in full: an overview as the overview.
- **"Quiet until …" or "pause until …".** [The wake rules](references/rules.md#what-wakes-the-thread) say what each holds. Write the time in the profile's timezone: `node scripts/assistant.ts ledger <org> quiet 2026-11-26T14:00` or `pause 2026-11-30T09:00`, or `off` to end it. Reply in one line with the time it ends.
- **A letter answer, such as `a`.** It answers the open call only when your latest post showed that call's id, as [one open call](references/rules.md#one-open-call-at-a-time) describes. When the post showed another id, show the open call and ask again; when `call show` warns that the call replaced another within 15 minutes, ask which one they meant. Otherwise name what you are about to do in your first line, then act as [authority](references/rules.md#authority) allows. An offer to start a thread follows [launch](references/launch.md).
- **Anything else.** Answer it. A request to look at a ticket's quality follows [the ticket standard](references/rules.md#ticket-standard).

**Complete when** the branch's reply is written, or the run stopped on a batch already delivered.

## 3. Post

Shape the post as /reply-shape's glance, with the content [the rules](references/rules.md#what-a-post-holds) give the overview and the delta. Every time is in the profile's timezone. Name tickets and PRs as links with their id. End with /next-options: the open call as `a`, repeated with the same letter while it stays open and adding no new option; a new offer becomes the call only when none is open (`ledger <org> call set "<offer>"`), and otherwise joins the queue (`call queue "<offer>"`). Put the batch id and the open call's id in the fold, as `batch <id> · call <id>`, so the scan can tell the post went out and the next `a` can tell which call it answers.

**Complete when** the post shows at most six items, ends on the one open call or on **Done**, and carries the batch id and the call id.

## 4. Record

Before the run ends:

1. Mark each batch you posted delivered: `node scripts/assistant.ts ledger <org> delivered <batch>`. The scan resends an undelivered batch once, then fails its unit.
2. Settle the call by its id: `call clear <id>` once the user answered it, which raises the oldest queued offer, or `call drop <id>` for one the overview drops unanswered. Repeating either changes nothing.
3. Log what changed the picture: `ledger <org> log told|asked|answered|offered|declined "<ids and a few words>"`, plus `depends`, `lead`, `waits`, `mute`, or `started` when the user settled one. Clear the wait for each PR a `release.awaited` item you posted names, `ledger <org> waits <pr> off`, since its release shipped; a wait left in place wakes the thread at every later release. `node scripts/assistant.ts ledger <org> -h` lists the commands.
4. Rewrite `radar.md`: open loops, live dependencies, pending offers, and started threads, in under 150 lines. It holds ids, states, and links, never message or ticket text.

**Complete when** the ledger names every batch you posted and the call you settled, and `radar.md` matches what you just posted.
