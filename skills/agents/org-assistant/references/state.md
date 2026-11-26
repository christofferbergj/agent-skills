# State

Read when a file's contents surprise you, when writing a profile, or when changing what the scan keeps.

## Profile

`~/.config/org-assistant/<org>/profile.toml`, written at setup and kept off any synced history. The scan reads a TOML subset: tables, arrays of tables, strings, numbers, booleans, arrays, and inline tables; write dates as strings.

```toml
org = "acme" # the folder's name
name = "Acme" # the thread's title is `✦ Acme assistant`
timezone = "Europe/Copenhagen"
thread = "<assistant thread id>" # empty until go-live: the scan then sends nothing

[executor]
command = [
  "~/.local/share/mise/installs/node/lts/bin/node",
  "~/.config/executor/probe.ts",
  "client",
]

[schedule] # optional; these are the defaults
window = ["09:00", "23:59"]
overview = "09:00"
batch_slots = ["13:00", "17:00"]
daily_deltas = 6
slack_wait_minutes = 30
retries = 1 # resends of an undelivered batch before the unit fails
source_failures = 3 # failed scans in a row before the unit fails

[[sources]]
name = "linear"
kind = "linear"
repo = "~/code/acme-web" # Executor is called from this repository
account = "<Executor account id>"
teams = ["DEV"]
tools = ["tools.linear.get_notifications", "tools.linear.list_issues", "tools.linear.get_issue"]

[[sources]]
name = "slack"
kind = "slack"
repo = "~/code/acme-web"
account = "<Executor account id>"
me = "<the user's Slack id>"
tools = ["tools.slack.mcp.slack_search_public_and_private"]
channels = [{ id = "C0123", name = "dev" }] # the channels the user confirmed

[[sources]]
name = "github"
kind = "github"
me = "<the user's GitHub login>"
repos = [
  { repo = "acme/web", mine = true, review_requests = true, issues = true },
  { repo = "acme/api", open_prs = true, releases = true },
]

[[sources]]
name = "t3"
kind = "t3"
projects = [
  { path = "~/code/acme-web", provider = "<seat id>", model = "<coding model>", options = [
    "effort=high",
  ] },
]

[people]
file = "~/code/acme-web/docs/agents/people.md"

[privacy]
rules = ["Never name or quote a practitioner, their email, or their user id."]
```

Find the Executor tools and account ids with `probe.ts client search '{"query":"…"}'` run in the source's repository. A launched thread uses its project's `provider`, `model`, and `options`.

## State folder

`~/.local/state/org-assistant/<org>/`. Each file has one writer.

| File            | Writer                             | Holds                                                                                                                                                                                                                                                                  |
| --------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `snapshot.json` | the scan                           | Each source's cursors and fingerprints, the Slack waiting list, source health, the first attempt of a source that hasn't succeeded yet, and the last scan time.                                                                                                        |
| `pending.json`  | the scan                           | The frozen `sent` batch with its tries, the `inline` batch, the `gathered` changes, the ids delivered in the last 7 days, and `meta`: today's overview, delta count, and batch slots.                                                                                  |
| `scan.stamp`    | the scan                           | The time of the last scan.                                                                                                                                                                                                                                             |
| `ledger.json`   | you, through `assistant.py ledger` | The delivered batches, quiet and pause, mutes, the open call with its id and its queue, started threads, release waits, confirmed dependencies, leads, and a log of what the user was told, asked, and answered. A command run twice leaves it as running it once did. |
| `rules.md`      | you                                | The user's rules for you, one numbered line each, in their words.                                                                                                                                                                                                      |
| `radar.md`      | you                                | The current picture in under 150 lines: open loops, live dependencies, pending offers, started threads.                                                                                                                                                                |

None of them holds a message body, a ticket title or description, or anything naming a practitioner. Times are UTC in the files and Danish time on screen. A scan holds `.lock` while it runs, so a timer scan and a "scan now" never write at once.
