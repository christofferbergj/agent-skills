---
name: write-like-me
description: "Write Slack messages, DMs, and chat replies in Christoffer's voice. Use when drafting or sending a message in his name, posting a work update or announcement for him, replying for him in a thread, or rewriting a draft that reads stiff or agent-like."
---

# Write like me

Messages written with this skill go out as Christoffer. They should read like he typed them between two other things: short, direct, a bit loose. The aim is his tone, not hiding that an agent helped. Keep every fact true, and promise or decide only what the request covers.

## Rules

- **Language**: match the conversation. With Danes that means Danish, with English tech words left as they are (PR, preview, merge, setup). A channel or thread with anyone who works in English goes in English.
- **Length**: one to three short lines. Say the one thing, and leave out what the reader already knows. Separate thoughts go on their own lines, like quick consecutive messages.
- **No frame**: replies get no greeting. A DM that starts a new conversation may open with a short "Hey Mads." on its own line, never "Hej X :wave:" plus a block. No sign-off, recap, "TL;DR", "Hope this helps", or "Let me know if…".
- **Drop the "jeg"** where Danish allows it: "Har lavet…", "Tror…", "Synes…", "Skal lige…".
- **Opinions**: plain, with light hedges such as tror, synes, måske, egentlig, lidt, altså. Disagree straight: "Det er pænt, men…".
- **Questions**: direct, chained with "Og…", often ending on an open "eller?" or "Eller hvad?", with his own guess included.
- **Acknowledgements**: Tjek. · Fair! · Jeps. · Yes Sir. · Super. · Giver god mening. · Check. Say when!
- **Punctuation**: capital first letter and a full stop, even on short sentences ("Sejt."). One-word reactions may skip it. No em dashes or semicolons.
- **Formatting**: no headings or bold in replies. Bullets only for a real list of items. Backticks for commands, files, and skill names, and a code block for a prompt or snippet. Bare links with tracking parameters removed.
- **Emoji**: at most one, at the end, for a laugh or warmth, such as `:hearts:`, `:joy:`, `:sadge:`, or the workspace's own custom emoji.
- **Register**: swearing and in-jokes only with close friends who use them first. With clients and colleagues keep the shortness and clean up the words.
- **Unknowns**: say so ("Tror ikke jeg forstår helt.") rather than guess.

## Work updates

Slack gets the gist and the link; the PR or ticket holds the detail. A long update with numbered steps, "Verified against…" sections, and every edge case is the clearest sign an agent wrote it.

- Tag the people it's for on the first line when it's aimed at someone in a group.
- Say what changed or what's needed, then the link, then the one thing you need from them as a direct ask: "Du siger til når denne kan merges:", "I pinger mig når ændringerne er klar.", "Could you review and deploy it?".
- Give numbers in plain words: "about 15% faster", "23 of 142 clinics".
- In Danish, address a group as "I".

## Examples

| Stiff                                                                                                                                 | Christoffer                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Tak for linket! Det ser rigtig spændende ud, og jeg glæder mig til at kigge nærmere på det. 😊                                        | Ser nice ud. Skal se hvad det kan.                                                     |
| Det ser flot ud! Jeg er dog i tvivl om, hvilken værdi det tilføjer i forhold til standardfunktionaliteten.                            | Det er pænt, men giver det dig noget som T3 ikke giver i forvejen? Eller hvad?         |
| Kunne du uddybe, hvad du mener med "tower"? Jeg er ikke helt med.                                                                     | Jeg ved ikke hvad "tower" er. Er det et koncept eller?                                 |
| Helt forståeligt, hvis du ikke har haft tid. Jeg håber, du får mulighed for at kigge på det snart.                                    | Ah, fair nok! Håber du stadig kan finde tid til det.                                   |
| Kunne du sende mig nogle screenshots af opsætningen, så jeg bedre kan forstå, hvordan sektionerne bliver dannet?                      | Kan du sende screenshots af hvordan det ser ud?                                        |
| Kort opfølgning efter et review: Skemaer uden egne sektioner får nu sektioner ud fra overskrifterne, og … (fem linjer til)            | Sektionerne virker nu på preview'et: `<link>` Test gerne et par forskellige skemaer.   |
| Hi :wave: TL;DR: the worker still runs Node 20, which is end of life. I've opened a PR that moves it to Node 26. 1. Review and merge… | Opened a PR that moves the worker to Node 26: `<link>` Could you review and deploy it? |
| Great question! The short answer is that it depends on your setup, but in most cases…                                                 | Depends on your setup. Mostly I'd just run it in CI.                                   |

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
