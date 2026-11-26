# Scan

Read when changing the scan, reading its log, installing its timer, or adding a kind of source.

`scripts/assistant.py scan` runs with no model. For each organisation with a profile under `~/.config/org-assistant/`, it reads every source, compares what it finds with `snapshot.json`, turns each difference into a **change**, gathers changes in `pending.json`, and wakes the assistant thread with `t3 thread send` only when [the wake rules](rules.md#what-wakes-the-thread) say so. One timer runs it for every organisation, so a new organisation needs no new timer.

## Sources

Each `[[sources]]` entry in the profile names a `kind`, and each kind has one adapter in `scripts/orgscan/sources/`:

| Kind     | Reads                                                                                                                                                                                               |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `linear` | The user's inbox as the event feed (never marked read), their open tickets with relations and status history, the tickets those are blocked by, and each listed team's changes since the last scan. |
| `slack`  | DMs and mentions, kept on a waiting list until the user answers, and a message count for each confirmed channel. Searches run one at a time, since Slack limits bursts.                             |
| `github` | Per repository, as its flags say: the user's open PRs with reviews and checks, review requests, issues, other open PRs, and releases, through `gh`.                                                 |
| `t3`     | Threads in the organisation's projects that wait on the user, and the threads the assistant started.                                                                                                |

Linear and Slack go through Executor's `probe.ts`, from the repository the source names, and only through the tools its `tools` list allows; a tool whose name reads as a write (`mark_`, `save_`, `send`, `draft`, and the like) is refused even when listed. Every adapter keeps ids, states, counts, and staff names only, never a title or a message body.

**Adding a kind**, such as `azure-boards` for Adapt's client trackers: write `sources/<kind>.py` with `scan(source, prev, ctx) -> (section, changes)`, add it to `ADAPTERS` in `sources/__init__.py`, and add its kinds of change to `changes.py`. `prev` is the source's last section, or None on its first scan, which records a baseline and returns no changes. Until the adapter exists, a profile that names `azure-boards` fails that source on every scan, so the gap shows in the health line.

## Kinds

`scripts/orgscan/changes.py` holds the table; this is its meaning. **Urgent** kinds still wake on a weekend and past the day's sixth delta.

| Kind                                                                                                                                                                                         | Tier  | Urgent |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------ |
| `ticket.assigned`, `ticket.mention`, `slack.waiting`, `pr.review_requested`, `issue.assigned`, `deadline.soon`                                                                               | now   | yes    |
| `ticket.unassigned`, `ticket.changed` (someone else's status, priority, or due-date change), `ticket.comment`, `ticket.unblocked`, `pr.changes_requested`, `pr.ci_failed`, `release.awaited` | now   | no     |
| `dependency.changed`, `ticket.new_in_project`, `thread.finished`, `thread.waiting`                                                                                                           | batch | no     |
| `ticket.moved` (the user's own status change), `team.pulse`, `slack.channel`, `pr.approved`, `pr.opened`, `pr.closed`, `release.new`, `issue.new`, `thread.waits_on_you`, `linear.other`     | pulse | no     |

A status change on the user's ticket counts as someone else's when the inbox holds a status notification for it; one without is taken as the user's own and becomes `ticket.moved`. Linear's tools don't say who changed a priority or due date, so those always count as `ticket.changed`, marked `by: unknown`. A release is `release.awaited` when the ledger's `waits` names its repository.

## The batch

`pending.json` holds `sent`, the batch the last wake carried, and `gathered`, the changes since. A change's id is the same each time the scan sees the same event, so it joins once: a change already gathered, in flight, or delivered in the last 7 days is skipped. `team.pulse` and `slack.channel` add their counts into one item per team or channel instead.

When decide() calls for a wake, the scan freezes the chosen changes as `sent`, with an id such as `fysioscout-20261126-1005` and an empty list of tries, writes its files, then sends. While `sent` is undelivered it stays frozen: later changes gather beside it and never join it. The run marks it delivered with `ledger <org> delivered <id>`; the scan also counts it delivered when the thread's last reply names its id.

## Failure

- **A busy thread** (running, starting, or waiting) gets nothing: the scan holds new wakes and retries until the thread is idle. A thread `t3 thread show` can't read counts as busy.
- **An undelivered batch** on an idle thread is sent once more at the next scan. After two tries it stops waking and exits 1, failing its unit, which the server's health alert pushes to the phone. A `t3 thread send` that exits non-zero is a failed try.
- **A source** that fails three scans in a row exits 1 the same way. A failed source keeps its last good section, so its changes arrive once it recovers; an Executor error that reads like an expired sign-in shows as `sign-in expired` in the health line.
- **The stamp**: every scan writes `scan.stamp`. `assistant.py status` warns when it is over 90 minutes old between 09:15 and the end of the window, and no overview by 09:30 on a weekday means the timer is broken.
- **A missed scan** loses nothing: cursors move only when a scan succeeds, and the overview and batch slots go out at the first scan after their time.

The scan's log line names batch ids, kinds, and refs, never text. Errors name the tool and its error text, cut short.

## Dry run

`assistant.py scan <org> --dry-run` reads the sources and prints what it would send, writing and sending nothing. On an organisation with no snapshot yet, add `--since 24h` to count changes from that long ago instead of recording a baseline.

## Timer

One user unit runs every organisation at five past each hour from 09:05 to 23:05 Danish time:

```ini
# ~/.config/systemd/user/org-assistant-scan.service
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/.agents/skills/org-assistant/scripts/assistant.py scan
Environment=PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin

# ~/.config/systemd/user/org-assistant-scan.timer
[Timer]
OnCalendar=*-*-* 09..23:05:00 Europe/Copenhagen
Persistent=false

[Install]
WantedBy=timers.target
```

Point it at the installed skill, so a skill refresh updates what runs. Where the machine declares its user timers in a config tool, such as `~/.config/mise/config.toml` on the servers, declare it there instead of writing the files by hand. Read its log with `journalctl --user -u org-assistant-scan`.
