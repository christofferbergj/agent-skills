# Scan

Read when changing the scan, reading its log, installing its timer, or adding a kind of source.

`node scripts/assistant.ts scan` runs with no model, on Node 24 or later and nothing else. For each organisation with a profile under `~/.config/org-assistant/`, it reads every source, compares what it finds with `snapshot.json`, turns each difference into a **change**, gathers changes in `pending.json`, and wakes the assistant thread with `t3 thread send` only when [the wake rules](rules.md#what-wakes-the-thread) say so. One timer runs it for every organisation, each in a process of its own, so a new organisation needs no new timer, and one broken profile or state folder fails only its own organisation.

## Sources

Each entry in the profile's `sources` names a `kind`, and each kind has one adapter in `scripts/sources/`:

| Kind     | Reads                                                                                                                                                                                               |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `linear` | The user's inbox as the event feed (never marked read), their open tickets with relations and status history, the tickets those are blocked by, and each listed team's changes since the last scan. |
| `slack`  | DMs and mentions, kept on a waiting list until the user answers, and a message count for the confirmed channels. Searches run one at a time, oldest first, since Slack limits bursts.               |
| `github` | Per repository, as its flags say: the user's open PRs with reviews and checks, review requests, issues, other open PRs, and releases, through `gh`.                                                 |
| `t3`     | Every thread that [counts](rules.md#what-wakes-the-thread): its status, latest run, and item count, so the scan sees when one waits, fails, finishes, stalls, or appears.                           |

Linear and Slack go through Executor's `probe.ts`, from the repository the source names, and only through the tools both the adapter and the source's `tools` list name; a source without `tools` calls nothing, and a tool whose name reads as a write (`mark_`, `save_`, `send`, `draft`, and the like) is refused even when listed. Every adapter keeps ids, states, counts, and staff names only, never a title or a message body. Slack's search pages are Markdown, which a message body can imitate: a page whose record headings don't number 1 to the page's own count, or with a record that lacks its fields, is read again one message per call, and the search then pages on from that page's next cursor; a one-message page that can't be read fails the source.

**Adding a kind**, such as `azure-boards` for Adapt's client trackers: write `scripts/sources/<kind>.ts` exporting an `Adapter`, a parser for its snapshot section and `scan(source, window, ctx)`, which returns the new section, its changes, and a note for the health line when a read left something out; give its source's fields a parser in `SOURCE_KINDS` in `profile.ts`, a case in `scanSource` in `sources/index.ts`, and its kinds of change entries in `KINDS` in `changes.ts`, with those it reports again at every scan while they hold in `STANDING`. The window is `resume` with the source's last section, or, on its first scan, `baseline`, which records one and returns no changes, or `since` a start. Parse every response at the boundary with the parsers in `parse.ts`; a shape the parser doesn't know fails the source. Until the adapter exists, a profile that names `azure-boards` fails that source on every scan, so the gap shows in the health line.

## Kinds

`KINDS` in `scripts/changes.ts` gives each kind its tier, as [the wake rules](rules.md#what-wakes-the-thread) define them, and marks the urgent ones that still wake on a weekend and past the day's sixth delta. Three kinds need a judgement the scan makes:

- A status change on the user's ticket counts as someone else's (`ticket.changed`) when the inbox holds a status notification for it, and as the user's own (`ticket.moved`, pulse) when it doesn't. A ticket closed or reassigned since the last scan still counts as theirs.
- Linear's tools don't say who changed a priority or due date, so those always count as `ticket.changed`, marked `by: unknown`.
- A T3 thread waits, fails, or finishes when its status or its latest run changed since the last scan, so a second run that ends the same way counts again. It is `thread.stalled` once it has run for an hour with the same item count; a new item, status, or run ends the stall, and the next one counts again. A finished or failed run is reported once, when it ends, and stays gathered while the thread is watched, even after its next run starts. Each scan reports a wait or a stall again while it holds, for up to 7 days from its first report, the time a delivered id is kept, so a new status or run takes a gathered one out.

A release is `release.awaited` when the ledger's `waits` names its repository, and the change names the waiting PRs, whose waits the run clears once it posts it. A PR of the user's first seen after the baseline counts its state as new, so one opened already red still wakes, and a new T3 thread that already waits wakes as waiting as well as counting as new.

## The batch

`pending.json` holds `sent`, the batch the last wake carried; `inline`, the batch a "scan now" froze; `gathered`, the changes since; the ids delivered in the last 7 days; and `meta`, what today already sent. A change's id is the same each time the scan sees the same event, so it joins once; a source reports a **standing** change, `STANDING` in `scripts/changes.ts`, again at every read that finds it still true, such as a DM still unanswered or a thread still waiting, and the scan's `found` counts only the changes it gathered anew. A pulse item, such as one team move or one channel message, has an id of its own like any change, and the post sums them; the wake message counts pulse items instead of listing them.

When the wake policy, `nextStep` in `scripts/policy.ts`, calls for a wake, the scan freezes the chosen changes as `sent` under an id no batch had before, such as `acme-20261126-1005-14`, and counts it in `meta`, all in one write of `pending.json`; then it writes `snapshot.json` and sends. A crash between the two writes only makes the next scan read the same events again. While `sent` is undelivered it stays frozen: later changes gather beside it, and an inline scan reports it as `in_flight` without touching it. A delta that quiet holds rejoins `gathered` when the overview comes due, so the overview carries it. A gathered change that stopped being true leaves before the next wake: a standing change its source's read didn't report again, such as a DM since answered or a thread wait answered in T3, and a new thread's change or a finished or failed run once the thread no longer counts, such as one since settled or archived. So does every waiting DM or mention when the budget left the user's replies unread to their end, since one of those may answer it, and every standing change of a source whose read failed, since it vouched for none; the next read that finds one still true reports it again under the same id, so it joins no batch twice. The run marks a batch delivered with `ledger <org> delivered <id>`; the scan also counts `sent` or `inline` delivered when the thread's last reply names its id. An inline batch stays frozen while the assistant thread runs or can't be read, since the run that froze it may still post it; once the thread is idle, an inline batch neither the ledger nor the last reply names returns to `gathered`, and so does the last one when a new "scan now" runs.

## Failure

- **A busy thread** (preparing, queued, starting, running, or waiting) gets nothing: the scan holds new wakes and resends until the thread is idle. Quiet and pause hold a resend as [the wake rules](rules.md#what-wakes-the-thread) say they hold a new wake.
- **An undelivered batch** on an idle thread is sent again at the first scan an hour after the scan that woke the thread, whatever the timer's pace, so a run that stopped before posting, such as at a usage limit, gets time to come back. The hour allows 5 minutes of slack, so a timer that starts a little early doesn't cost a whole step. An hour after the last try the profile's `retries` allows, one resend by default, it stops waking and exits 1, failing its unit, which the server's health alert pushes to the phone. A `t3 thread send` that exits non-zero is a failed try and gets no hour: the next scan sends again, and after the last try the unit fails at once and at every scan after.
- **A source**, or the assistant thread itself, that fails three scans in a row exits 1 the same way. A failed source keeps its last good section, so its changes arrive once it recovers, and its standing changes leave `gathered` until a good read reports them again, while frozen batches stay as they are; one that has never succeeded counts from its first attempt, or from the earlier start a `--since` gave it. An error shows as what failed and its category only, since a tool's error text can quote what it was reading: `sign-in expired`; `rate limited`; `failed`, with its HTTP status when there is one; `unexpected response`, with the field whose shape the scan doesn't know, or for a Slack page what it couldn't read; `no JSON in its output`; `failed unexpectedly`, with the error's type, for an error no parser caught, whose first stack frame goes to stderr; a tool outside the source's `tools`, or one that reads as a write; a missing repository; Executor printing no result, or a different number of results than calls; and a kind with no adapter yet. A profile or state file the scan can't read fails only its own organisation.
- **The stamp**: every scan writes `scan.stamp`. `assistant.ts status` warns when it is over 90 minutes old from 15 minutes after the window opens to its end, and when no overview was delivered within 30 minutes of the overview's time on a weekday outside a pause: 09:15 and 09:30 with the default schedule.
- **A missed scan** loses nothing short of a cap: cursors move only when a scan succeeds, and the overview and batch slots go out at the first scan after their time.
- **Caps** bound how much one scan reads. A day brings a few dozen items, so only an outage of days reaches one. A Linear read takes at most 20 pages: 1,000 inbox items, newest first, or 5,000 tickets of the user's list or of a team's. A read past its cap still moves its watermark, so what it didn't reach stays unread, and the source's health entry says so, such as `linear ok, inbox capped at 1,000: older items unread`; tickets of the user's it didn't reach keep their state from the last scan. Slack makes at most 40 calls an organisation's scan, shared by all its Slack sources, retries and one-message re-reads included. Four searches run in turn, DMs, mentions, the user's own replies, and the confirmed channels, each oldest first from its watermark: the whole second it stopped in, since Slack's search starts at a whole second, and the messages from then on it read, by channel and timestamp, which it skips. One the budget cut off goes on at the next scan from the second of the latest message it read, read before or not, so a message Slack indexed late in that second is still read; one that read to its end reaches back 10 minutes, for messages Slack indexed late. A DM or mention joins the waiting list until the user answers it or it is three days old, and one that joins with a time before the replies watermark moves that watermark back to it, since the replies after it were read before it waited. A reply takes the message it answers off the list whenever it is read, but only a scan whose replies search read to its end reports a message unanswered past the wait, as it does at every such scan. Once the budget runs out, the searches left wait for the next scan; when the replies search is among them or was cut off, no waiting message wakes or stays gathered; and the health entry says `slack ok, read budget used: resumes next scan`. A search the budget cut off having read messages only in the second it started at would start there again: the health entry says `slack ok, watermark stuck at …` instead.

The timer's log line names the batch id and counts its changes by kind, never a ref or text, and stderr names what failed without its ids, a call by its place in the profile, such as `repos[1] PRs` or `projects[0]`, never a repository's name or a path the profile gives. A dry run and an inline scan, whose output goes to the person or the run, list each change's id, kind, and ref.

## Dry run

`assistant.ts scan <org> --dry-run` reads the sources and prints what it would send, writing and sending nothing. On an organisation with no snapshot yet, add `--since 24h` to count changes from that long ago instead of recording a baseline.

## Timer

One user unit runs every organisation every 15 minutes from 09:00 to 23:45 Danish time. A scan runs no model and wakes the thread only as [the wake rules](rules.md#what-wakes-the-thread) say, so a faster timer brings urgent changes sooner without adding runs for the rest:

```ini
# ~/.config/systemd/user/org-assistant-scan.service
[Service]
Type=oneshot
ExecStart=%h/.local/share/mise/installs/node/24/bin/node %h/.agents/skills/org-assistant/scripts/assistant.ts scan
Environment=PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin

# ~/.config/systemd/user/org-assistant-scan.timer
[Timer]
OnCalendar=*-*-* 09..23:00/15:00 Europe/Copenhagen
Persistent=false

[Install]
WantedBy=timers.target
```

Point it at the installed skill, so a skill refresh updates what runs, and at a Node 24 install by path, since a timer has no shell to put mise's Node on its `PATH`. Where the machine declares its user timers in a config tool, such as `~/.config/mise/config.toml` on the servers, declare it there instead of writing the files by hand. Read its log with `journalctl --user -u org-assistant-scan`.

After a T3 update, `~/.local/bin/t3` can run the new version before the server restarts, and that CLI refuses to work with the older server. Where updates arrive that way, put first on the unit's `PATH` a folder whose `t3` runs the version of the running server, the one `pgrep -af '/runtime/versions/[^/]*/t3 serve'` names under `~/.t3/runtime/versions/`, and falls back to `~/.local/bin/t3`.
