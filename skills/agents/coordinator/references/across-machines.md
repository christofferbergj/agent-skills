# Across machines

Read at coordinator step 1 before Start when /swarm's T3 route lists a linked machine, and at step 3 for a unit that needs another machine's tools.

Worktrees, timers, PR watches, and pending-question wakes stay on the machine that holds them, so the coordinator runs where its units build. This thread reaches only its own server's linked machines, as /swarm's T3 route describes under On another machine, so a coordinator on a machine that links to none runs every unit there.

## Placement

Pick the machine by what the units need, not by where this thread runs:

- a macOS machine when any unit needs macOS: Xcode, a simulator, a macOS-only check, or computer use. When the only such need is a report-only check, such as a computer-use pass, and this machine links to a reachable macOS machine, stay here and run that check as a worker there (below);
- otherwise a machine whose `t3_project_list` holds the repository and whose memory fits the units' builds and suites, preferring one other than the laptop the user works on, since a laptop sleeps.

On the wrong machine, before Start, offer starting there as a decision card. On a yes, `t3_thread_launch` with that machine's `environmentId`, `runtimeMode: "full-access"` when its units need full access, such as computer use, the repository's `projectId` from its `t3_project_list`, and a `message` that runs /coordinator with everything this chat agreed: the goal, its proof, the plan, the decisions, and the standing rules verbatim. Reply with the new thread's `link` and stop. Otherwise, or when that machine isn't linked from here or isn't `reachable`, start here and record why under Decisions. The coordinator keeps its project folder and reports on the machine it runs on. When T3 refuses that mode with `runtime_mode_escalation_denied`, because this thread's mode or the link's access is narrower, ask the user to start it on that machine instead.

## A worker on another machine

Start it as /swarm's T3 route describes under On another machine, with these changes to a worker:

- **Report-only**: it reads and checks, like a device check, a computer-use pass, or an audit, and opens no branch or PR, since its worktree and wakes would sit outside this coordinator's reach.
- **Brief**: its Report line asks for the report in its final message, as the T3 route says, instead of a report file.
- **Its state**: record its thread `link` and `environmentId` in Workers. Its end and its pending questions wake no one here, so startup, the tick's hourly reminder, and the stuck rule read its status, `itemCount`, and `pendingRequestCount` with `t3_thread_read` and that `environmentId`. Once it reads `completed`, handle its last message as a worker result.
- **Its tools**: it has no `taskId`, so `task_status` and `task_cancel` don't apply. Stop it with `t3_thread_interrupt`, answer a pending question with `t3_pending_request`, and send an answer to a call in its result, or more work, with `t3_thread_send`, each with its `environmentId`. Retry it as the T3 route says, under a new key.
