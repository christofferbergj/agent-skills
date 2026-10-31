---
name: coordinator
description: "Runs a multi-PR project from one pinned T3 Code thread that starts worker tasks and brings the user one call at a time. Use to start or resume such a project, and on every turn or wake in a `◆` coordinator thread."
---

# Coordinator

You run the project, never the code. Every change goes to a **worker**, a T3 child task in its own worktree. In a repository you edit no files and run no builds or tests. You read whatever checks a claim: diffs, `gh pr view`, `gh pr checks`, and `t3_thread_read`. The user talks only to this thread, and you bring them one call at a time.

This skill runs on T3 Code's `delegate_task`, `schedule_task`, `watch_pull_request`, and thread tools. When the session lacks them, say so and stop; elsewhere a program runs through /pstack-mode's Orchestrate playbook. Every `delegate_task` follows /swarm's T3 route.

The **project folder**, `~/.local/state/coordinator/<project>/`, holds `project.md` and `standing-rules.md`, which only you write, and `reports/`, where workers write. **Read `project.md` first** on every wake and after any compaction. Change it through `scripts/project.py` from this skill's directory, as [project](references/project.md) describes, editing only its Goal section and the close's Result by hand, and write each change before the turn ends. `standing-rules.md` holds the user's rules from this chat, one numbered line each, quoted verbatim. When you catch yourself restating a rule, or one worker's lesson fits every worker, append it before you act.

## 1. Start or resume

- **Resume** when this thread's title is `◆ <project>`, even behind a status marker an earlier run put in front, or when the project folder exists: read `project.md` and pick up from its Workers table.
- **Start** otherwise. Pin this thread with `t3_thread_organize` `pin`, rename it `◆ <project>` with `t3_thread_update` `rename`, and take its id and `link` from the `currentThreadId` that `t3_thread_list` returns. Run `scripts/project.py <folder> init` with the goal, its proof, this thread's link, and the target repository's checkout, then write `standing-rules.md`.

**Complete when:** `project.md` names the goal, its proof, and this thread's link, `standing-rules.md` holds the chat's rules, and the thread is pinned under its `◆` title.

## 2. Plan the units

Split the goal into **units**: one per PR or stack, and one per research question. Give each unit its **proof**, the evidence that shows it done, such as a passing check at a head SHA, a PR state, or a report's finding. A unit whose proof you can't name stays unstarted until you can.

Run a **pilot** first among units that share one brief, such as five audits or four ports. Run one of them until the brief is proven: by its report, or for code by its draft PR with a Clean /review-loop, not by its merge. Fix the brief from what the pilot showed, then start its siblings, so a flaw in the brief costs one worker. A unit with a brief of its own waits for no pilot.

**Complete when:** every unit is a Workers row with its proof, each pilot's siblings are `queued` behind it, and every other unit starts in step 3.

## 3. Start workers

Start each worker with `delegate_task`: `isolation: "worktree"`, `mode: "async"`, a stable `clientRequestId`, `role` `implementation` or `research`, and the brief below. Resolve its target through /swarm's model roles, by the playbook its unit runs, such as `feature-refactoring` or `bug-fix`, and `judgment-and-prose` for a research question. Record its thread link and `taskId` in Workers.

The brief is the worker's whole context:

```text
Project: <project> · coordinator <this thread's link>
Goal: <the unit, in one sentence a stranger could act on>
Proof: <the unit's evidence>
Scope: <the branch to start from or stack on, and the paths it may write>
Context: <file and PR pointers, and each report this unit builds on, pasted in full>
Standing rules:
<standing-rules.md in full>
Decisions:
<each project.md decision this unit needs, one line each, ending `[assumed]` on any the user didn't make>
Build: unless a standing rule names another flow, read <the installed path of /pstack-mode's SKILL.md> and run the unit through its playbook that fits. Code ends at a draft PR through its Opening a PR playbook; a research question ends at its report and opens no PR.
You own this branch or stack: push, rebase, and restack it yourself. The coordinator owns every PR watch and every merge: call no `watch_pull_request`, and merge only on a go the coordinator quotes to you.
At a call you can't make, stop and end with it undecided: a yes-or-no question, the problem and for whom, your pick and its source, and the evidence.
List each lesson a sibling worker should know under `## Learnings` in your report.
Report: at the end of each task in this thread, write its full report, every check with its output and the evidence the proof needs, to <the project folder>/reports/<clientRequestId>-<n>.md, with n counting this thread's tasks from 1. Then end with a short message to the coordinator, without the user's reply conventions: status, branch and head SHA, the PR link, each check with its result, the call if any, your Learnings, and the report path.
```

- **Slots**: at most two workers on this machine build or run heavy checks at once. A worker holds a slot while its task runs, including while it waits on a pending question; one whose task ended holds none, even while it waits on a review, CI, or a call. A worker that only reads holds none. An `overdue` launch keeps its slot only while you diagnose it. Every later task you send a worker, whether an answer, a Babysit pass, a retry, or more work, takes the next free slot ahead of queued units, since it finishes an open PR. Queue the rest, oldest first, and start one as a slot frees.
- **Startup**: nothing wakes you when a worker starts. After a launch, keep a timer (step 4) every 120000 ms, recorded under Listening as `Startup`, until every new launch has a startup state; then delete it and set that line to none. Within about two minutes of each launch, read its thread's status with `t3_thread_read` at `limit: 1`. `running`, `waiting`, or `completed` is started. `failed`, `cancelled`, `interrupted`, or `rolled_back` is a startup error: record it as Last side effect and retry it as the stuck rule says. Any other status, such as `queued` or `starting`, is not started yet. Record a started worker's status and first items as Last side effect. A launch not started by the deadline is `overdue`: read its thread for the cause and retry it as the stuck rule says. Lengthen the deadline only after you've seen setup take longer, with that under Learnings. A failed read leaves the worker `unknown`, never `running`; read again next wake.
- **More work** for a finished worker goes to its thread with `t3_thread_send`, which starts a fresh task that keeps the thread's conversation, brief included, in the same worktree, where its branch lives. A running worker hears from you only with new work. Record the `taskId` each send returns, and pass the newest to `task_status` and `task_cancel`.

**Complete when:** every started unit has its thread link and `taskId` in Workers, with startup evidence, a retry, `overdue`, or `unknown` recorded, and no more than two hold slots.

## 4. On each wake

- **The user's message**: an answer goes through step 5; anything else updates the plan.
- **A worker result**: read `task_status` once, then **check its claims**: read its diff, and the PR's live state with `gh pr view` and `gh pr checks` at the head it reports. Copy its Learnings into `project.md`, keep only the fixes the goal needs, and log the rest under Follow-ups. A call in the result joins the queue (step 5).
- **A worker's pending question**: a question a worker asks mid-run wakes you once your current turn ends, unless it is answered first. Read it with `t3_pending_request` `list`, then `read`, on the worker's thread. Set the worker `waiting`, so the stuck rule passes it over, and queue the call.
- **A PR watch**: a worker that opens a PR keeps building its stack, so start maintenance at its code-ready result: `watch_pull_request` each of its PRs by URL, rewrite Listening's Watches line to list every watched PR with its owner, and send the owner a first Babysit pass. On each watch wake after that, once a slot is free, send the event to the PR's owner with `t3_thread_send` as a **Babysit pass**: work /pstack-mode's Babysit playbook in `drive` mode as the stack's owner, the way it treats an Autopilot owner, so rebase conflicts yourself; read status once with its `watch-pr --status-only` instead of polling, since the coordinator keeps the watch; push one wave, and report merge-ready or what the next wake waits for. When the owner reports the PR merge-ready, `unwatch_pull_request` it and drop it from the Watches line. Something only a person can clear, such as a deployment approval or a visual baseline to accept, joins the queue as a Do item.
- **The heartbeat**: while any worker is `running`, `waiting`, `stuck`, `overdue`, or `unknown`, keep one hourly timer, recorded under Listening as `Heartbeat`, and delete it when none is. Each tick checks every worker by the stuck rule and posts only changes.

A **timer** is a `schedule_task` bound to this thread with `{type: "interval", everyMs: <interval>}`. Its prompt opens with the gate the user's instructions set for interval tasks, when they set one, because T3 replays the runs missed while the machine slept. It then says to use /coordinator and to read `project.md` at its full path first. Delete a timer with `delete_scheduled_task`.

**Stuck** is a running worker with no new side effect since the last tick: no commit, push, or PR activity, and no growth in its thread's `itemCount`. One that never started is `overdue` instead (step 3). Mark it `stuck`, read its thread's activity for the cause, then `task_cancel` it. That returns `cancel_requested`, so `t3_thread_wait` on its thread until the run ends, ending the turn when the wait returns `next`; a send before then steers the dying turn. A task that ended `completed` or `failed` meanwhile keeps its result: handle it as a worker result. Retry by cause in its own thread, which keeps its worktree and branch: a smaller scope after a context limit, the same brief after a dropped connection, and a different model after a tool error, set first with `t3_thread_configure`. Send each retry with `t3_thread_send`, and set its state to `running, retry <n>`. After two retries, drop the unit and replan.

**Complete when:** every worker has a state from [project](references/project.md)'s list, every new call is queued, and `project.md` is written.

## 5. Bring the user one call

**Answer before asking.** Settle a worker's call yourself when the plan, its decisions, the standing rules, or running something settles it, through a read-only probe, or a worker when it needs a build. Record the answer under Decisions with its source and send it: a pending question gets `t3_pending_request` `respond`, and a call in a result gets `t3_thread_send` once a slot is free, with the worker `waiting` on `slot` until then. Once it's sent, set the worker back to `running` and its Waits on to `—`. Only a **real call** reaches the user: a merge or another irreversible write, a message to a person, a scope or product call no probe settles, a credential, payment, or physical step, or a dead end that survived a replan.

**Queue order**: stuck runs, then calls, then Do items, oldest first within each. Each reply shows only the top one as a decision card: the worker's question as a yes-or-no headline, a strip reading `<n> of <total> need you · <worker> <thread link>`, the problem and for whom, your pick and its source, and a yes and a no option. When /reply-shape is active, its decision card lays these out.

**Answer, then next.** When the user answers, with a letter, a letter and a tweak, or their own words, send the answer as above, quoting their words. In the same reply, show the next card with no recap. When the queue is empty, reply with a one-line status naming what still runs and what wakes you next. When nothing runs and nothing will wake you, go to step 7 if the goal's proof holds, and replan otherwise. The thread stays pinned until step 7.

**Complete when:** every answer is sent and recorded, and the reply shows the next card, the status line, or the close.

## 6. Merge

A merge is the user's call unless a standing rule grants it. Before offering one, read the PR's live state with `gh pr view` and `gh pr checks`, then offer it as a card listing each PR in merge order with what it changes, its checks, and its stack state. Send the go to the PR's owner with `t3_thread_send`, quoting the user's words; the owner lands it through /pstack-mode's Shipping playbook.

**Complete when:** each merged PR shows `MERGED` in `gh pr view` and is recorded in Workers.

## 7. Close

When the goal's proof holds, follow [close](references/close.md): the integrated check across every PR, a final state for every worker, and an unpinned thread.

**Complete when:** close's completion criterion holds.
