# State

Read when a file's contents surprise you, when writing a profile, or when changing what the scan keeps.

## Profile

`~/.config/org-assistant/<org>/profile.json`, written at setup and kept off any synced history.

```json
{
  "org": "acme",
  "name": "Acme",
  "timezone": "Europe/Copenhagen",
  "thread": "<assistant thread id>",
  "executor": {
    "command": [
      "~/.local/share/mise/installs/node/lts/bin/node",
      "~/.config/executor/probe.ts",
      "client"
    ]
  },
  "schedule": {
    "window": ["09:00", "23:59"],
    "overview": "09:00",
    "batch_slots": ["13:00", "17:00"],
    "daily_deltas": 6,
    "slack_wait_minutes": 30,
    "retries": 1,
    "source_failures": 3
  },
  "sources": [
    {
      "name": "linear",
      "kind": "linear",
      "repo": "~/code/acme-web",
      "account": "<Executor account id>",
      "workspace": "acme",
      "teams": ["DEV"],
      "tools": [
        "tools.linear.get_notifications",
        "tools.linear.list_issues",
        "tools.linear.get_issue"
      ]
    },
    {
      "name": "slack",
      "kind": "slack",
      "repo": "~/code/acme-web",
      "account": "<Executor account id>",
      "me": "<the user's Slack id>",
      "workspace": "acme",
      "tools": ["tools.slack.mcp.slack_search_public_and_private"],
      "channels": [{ "id": "C0123", "name": "dev" }]
    },
    {
      "name": "github",
      "kind": "github",
      "me": "<the user's GitHub login>",
      "repos": [
        { "repo": "acme/web", "mine": true, "review_requests": true, "issues": true },
        { "repo": "acme/api", "open_prs": true, "releases": true }
      ]
    },
    {
      "name": "t3",
      "kind": "t3",
      "projects": [
        {
          "path": "~/code/acme-web",
          "provider": "<seat id>",
          "model": "<coding model>",
          "options": ["effort=high"]
        }
      ]
    }
  ],
  "people": { "file": "~/code/acme-web/docs/agents/people.md" },
  "privacy": { "rules": ["Never name or quote a practitioner, their email, or their user id."] }
}
```

- `org` is the folder's name, and `name` gives the thread's title, `✦ Acme assistant`.
- `thread` stays `""` until go-live, and the scan then sends nothing.
- `schedule` may be left out; the values above are its defaults. `retries` counts the resends of an undelivered batch before the unit fails, and `source_failures` the failed scans in a row before it does.
- A Linear or Slack source calls Executor through `executor.command`, from its `repo`, with its `account`, and only through the `tools` it lists. `channels` are the Slack channels the user confirmed.
- A Linear or Slack source's `workspace` is the slug in its URLs, `acme` in `https://linear.app/acme/issue/ENG-1` or `https://acme.slack.com`. `assistant.ts batch` builds ticket and message links from it, and shows the bare ref when it is left out.
- A thread launched in a T3 project runs on that project's `provider`, `model`, and `options`.
- A path may start with `~`.

The scan checks the profile when it loads it. A field it doesn't know, an unknown timezone, a time that isn't `HH:MM`, or a source that lacks what its kind needs fails that organisation alone, and the error names the field, such as `schedule.daily_delta: is not a field it knows`. Find the Executor tools and account ids with `probe.ts client search '{"query":"…"}'` run in the source's repository.

## State folder

`~/.local/state/org-assistant/<org>/`. Each file below has one writer; the empty lock files the paragraph after it describes are only taken and let go.

| File            | Writer                                                                | Holds                                                                                                                                                                                                                                                                                                                                                            |
| --------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `snapshot.json` | the scan                                                              | Each source's cursors and fingerprints, the Slack search watermarks (the user's replies among them), each a whole second and the messages from it on already read, and the waiting list, each T3 thread's status, run, and item count and the turn it reported, source health, where a source that hasn't succeeded yet starts counting, and the last scan time. |
| `pending.json`  | the scan                                                              | The frozen `sent` batch with its tries, the `inline` batch, the `gathered` changes, the ids delivered in the last 7 days, and `meta`: today's overview, delta count, and batch slots.                                                                                                                                                                            |
| `scan.stamp`    | the scan                                                              | The time of the last scan.                                                                                                                                                                                                                                                                                                                                       |
| `.lock-backend` | the first run that locks the folder, a scan or a ledger command, once | Whether the folder's locks use flock(1) or plain files.                                                                                                                                                                                                                                                                                                          |
| `ledger.json`   | you, through `assistant.ts ledger`                                    | The delivered batches, quiet and pause, mutes, the open call with its id and its queue, started threads, release waits, confirmed dependencies, leads, and a log of what the user was told, asked, and answered. A command run again, at any later time, leaves it as its first run did.                                                                         |
| `rules.md`      | you                                                                   | The user's rules for you, one numbered line each, in their words.                                                                                                                                                                                                                                                                                                |
| `radar.md`      | you                                                                   | The current picture in under 150 lines: open loops, live dependencies, pending offers, started threads.                                                                                                                                                                                                                                                          |

None of them holds a message body, a ticket title or description, or anything naming a practitioner. Times are UTC in the files and Danish time on screen. A scan holds `.lock`, and a ledger command that writes `.ledger.lock`, with flock(1) while it runs, so two scans, or two ledger edits, never write at once, and a scan never writes the ledger, so neither waits for the other. `show` and `call show` only read, and take no lock, since every write replaces its file whole. The kernel lets go of a lock when its process ends, however it ends. When it chooses a folder's backend, or the folder records flock, the run finds flock on its `PATH`, at `/usr/bin/flock` or `/bin/flock`, or where `ORG_ASSISTANT_FLOCK` names it. The first run to lock a state folder records in `.lock-backend` whether its locks use flock or plain files, so every caller on the machine takes the same lock; a run that can't use the recorded one fails its organisation, naming the file, and removing the file while nothing runs lets the next run choose again. Where flock isn't installed, as on a Mac, each lock is a file of its own, such as `.lock.held`, that the run creates and removes; one a crash leaves behind keeps later runs out until it is removed, and stderr says so.
