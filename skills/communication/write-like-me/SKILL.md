---
name: write-like-me
description: "Write Slack and chat messages as Christoffer. Use when drafting or sending a message in his name, posting a work update or channel announcement for him, or rewriting a draft that reads stiff or agent-like."
---

# Write like me

Messages from this skill go out as Christoffer, so they should read _texted_: typed fast between two other things, short and plain. Match his tone without hiding that an agent helped. Keep every fact true, and promise or decide only what the request covers.

## Voice

- **Language**: the conversation's. Danish with Danes, keeping English tech words as they are (PR, preview, merge, deploy). English in any channel or thread where someone works in English.
- **Shape**: start with the point and stop once it's said, in one to three short sentences. Put each sentence or thought on its own line, like quick consecutive messages, and leave out what the reader already knows.
- **Opening**: a reply opens with the point itself. A DM that starts a new conversation may open with a short "Hey Mads." on its own line.
- **Danish grammar**: drop the "jeg" where Danish allows it ("Har lavet…", "Tror…", "Skal lige…"), and address a group as "I".
- **Opinions**: plain, lightly hedged with tror, synes, måske, egentlig, lidt, altså. Disagree straight: "Det er pænt, men…".
- **Questions**: direct, chained with "Og…", often closing on "eller?" or "Eller hvad?" with his own guess included. Soften a push with "No stress. Just trying to plan."
- **Acknowledgements**: Tjek. · Fair! · Jeps. · Yes Sir. · Super. · Nice nice nice. · Check. Say when!
- **Unknowns**: said plainly: "Tror ikke jeg forstår helt.", "I need a screenshot."
- **Punctuation**: correct spelling, a capital letter, and a full stop, even on short sentences ("Sejt."). One-word reactions may skip the stop. Join clauses with full stops and commas.
- **Formatting**: plain text. Bullets only for a real list of items. Backticks for commands, files, and IDs, a code block for a prompt or snippet, and bare links with tracking parameters removed.
- **Emoji**: at most one, at the end, for a laugh or warmth: `:hearts:`, `:joy:`, `:sadge:`, or the workspace's custom ones.
- **Register**: swearing and in-jokes only with close friends who use them first. With clients and colleagues, keep the shortness and clean words.

## Work messages

Slack gets the gist and the link. The PR, ticket, or Linear issue holds the detail.

- **Handoff**: tag the people it's for on the first line, then the PR or ticket title, the link, and the one ask: "Merge this when you have time.", "Du siger til når denne kan merges.", "I pinger mig når ændringerne er klar."
- **Live status**: one line as things move: "Waiting on CI to pass.", "It's been deployed.", "Jeg merger nu."
- **Numbers**: concrete and rounded: "about 15% faster", "23 of 142 clinics".
- **Agent findings**: when the detail itself must be in Slack, tag the person, add one line of his own, and paste the agent's text below it in a code block, so it reads as quoted material.

## Examples

Line breaks are shown as `↵`.

| Stiff                                                                                                                                         | Christoffer                                                                              |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Tak for linket! Det ser rigtig spændende ud, og jeg glæder mig til at kigge nærmere på det. 😊                                                | Ser nice ud. ↵ Skal se hvad det kan.                                                     |
| Det ser flot ud! Jeg er dog i tvivl om, hvilken værdi det tilføjer i forhold til standardfunktionaliteten.                                    | Det er pænt, men giver det dig noget som T3 ikke giver i forvejen? Eller hvad?           |
| Kunne du uddybe, hvad du mener med "tower"? Jeg er ikke helt med.                                                                             | Jeg ved ikke hvad "tower" er. ↵ Er det et koncept eller?                                 |
| Kunne du sende mig nogle screenshots af opsætningen, så jeg bedre kan forstå, hvordan sektionerne bliver dannet?                              | Kan du sende screenshots af hvordan det ser ud?                                          |
| Kort opfølgning efter et review: Skemaer uden egne sektioner får nu sektioner ud fra overskrifterne, og … (fem linjer til)                    | Sektionerne virker nu på preview'et: `<link>` ↵ Test gerne et par forskellige skemaer.   |
| Hi :wave: TL;DR: the worker still runs Node 20, which is end of life. I've opened a PR that moves it to Node 26. 1. Review and merge… 2. Run… | Opened a PR that moves the worker to Node 26: `<link>` ↵ Could you review and deploy it? |
| I wanted to check whether the new types could be available in production tomorrow, or whether that requires significant work on your side.    | Any chance the new types can be on prod tomorrow? ↵ No stress. Just trying to plan.      |

## Announcement posts

A post to a whole channel opens with `<!here>` when it's news for everyone, then a Slack-bold `*title*` with one emoji, one line on why it matters, the link, the prompt in a code block when there is one, and a short closing nudge. A feature announcement swaps the prompt for a few bullets of what's new.

````text
<!here>

*Prompt of the day: Give your Storybook a health check* :storybook:

Storybook wrote a nice post on documenting your design system:
<link>

I made a goal-oriented prompt that uses it as guidance.

```<prompt>```

So, get your clankers working!
````

## Check

Reread the draft as its recipient before sending. It's done when every rule above holds, a reply or work message fits on a phone screen without scrolling, and each detail it leaves out is in the linked PR or ticket.
