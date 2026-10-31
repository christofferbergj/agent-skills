# coordinator: source and local adaptations

## Source and credit

- Original author: Oliver Cederborg.
- Source repository: [olivercederborg/skills](https://github.com/olivercederborg/skills).
- Original skill: [`coordinator/SKILL.md`](https://github.com/olivercederborg/skills/blob/3030e458624e66d3c744cfbb60e97381d352be20/coordinator/SKILL.md).
- Supporting sources: [`coordinator/references/`](https://github.com/olivercederborg/skills/tree/3030e458624e66d3c744cfbb60e97381d352be20/coordinator/references), whose `project.md` and `close.md` are adapted here, and [`coordinator/scripts/`](https://github.com/olivercederborg/skills/tree/3030e458624e66d3c744cfbb60e97381d352be20/coordinator/scripts), whose `project.py` and `test_project.py` are ported. The Standing rules convention comes from [`orchestrate/SKILL.md`](https://github.com/olivercederborg/skills/blob/3030e458624e66d3c744cfbb60e97381d352be20/orchestrate/SKILL.md)'s The brief.
- Tracking policy: upstream `main`, reviewed as a principle source under the adaptation contract's [principle-derived skills](../../agents/maintain-skills/references/ADAPTATION.md#principle-derived-skills).
- Imported from commit: `3030e458624e66d3c744cfbb60e97381d352be20`.
- Reviewed through commit: `3030e458624e66d3c744cfbb60e97381d352be20`.
- Fidelity checked through: `3030e458624e66d3c744cfbb60e97381d352be20`.
- Last upstream review: 2026-10-31.
- Inherited credits: upstream names Cursor Projects, Claude Code Projects, Lauren Tan's Pstack Orchestrate playbook, agentbox's hyperfocus inbox, and Johan's orchestrate-project (jokklan/skills#29) as its inspirations. This library tracks Pstack's Orchestrate through /pstack-mode's own record.
- License: [MIT, copyright 2026 Oliver Cederborg](LICENSE). Retain this notice with derived material, `scripts/project.py` and its tests included.

## Local adaptations to preserve

The wording is first-party, and `scripts/project.py` is ported with the changes below. These are the principles taken from the source and the deliberate departures.

Adopted principles:

- The coordinator runs the project and never the code. Every change goes to a worker, a T3 child task in its own worktree, and the coordinator checks each claim against the diff and the PR's live state.
- One pinned `◆ <project>` thread is the only place the user talks to. Its memory is a project folder holding `project.md`, edited through `project.py`, and the standing rules, read first on every wake and after compaction.
- Each unit has a proof before it starts, and among units that share one brief a pilot proves the brief before its siblings start.
- Two slots bound the workers that build at once, and a task that finishes an open PR goes ahead of queued units.
- Each launch is checked for a start within about two minutes, with `overdue` and `unknown` states, because nothing wakes the coordinator when a child starts.
- More work for a finished worker goes to its own thread, which keeps its worktree, branch, and conversation. On 2026-10-31 a Claude child recalled its first brief after such a send.
- Each wake handles the user's message, worker results, pending questions, and PR watch events. The coordinator owns every watch and hands each event to the PR's owner. An hourly heartbeat finds stuck workers, which are cancelled, waited out, and retried by cause in their own threads, and dropped after two retries.
- The coordinator answers what the plan, its decisions, the standing rules, or a probe settles, and brings the user one real call per reply, ordered stuck runs, calls, then Do items, showing the next card in the reply that sends an answer.
- A merge goes to the PR's owner with the user's go quoted in their words.
- The close runs an integrated check that merges every open branch onto trunk in a fresh worktree, gives every worker a final state, clears every timer and watch, and unpins the thread.

Departures:

- The project folder is `~/.local/state/coordinator/<project>/`, and the Standing rules convention and the brief's Scope and Context fields from upstream's `orchestrate` brief live in this skill, since the library ships no `orchestrate` skill. The brief leaves out that brief's Acceptance, Verify, and Timebox fields, because the unit's proof and the worker's /pstack-mode playbook cover them.
- Delegation follows /swarm's T3 route and model roles instead of upstream's `t3-delegation.md` and its Roles table. The report is the route's short message naming a report file, without upstream's numbered report block, its show-me-your-work calls item, or its `Project:` turn block. Each task in a worker's thread writes its own numbered report file, where upstream's random suffix let a later task in the same thread overwrite the first report.
- Workers build through /pstack-mode's playbooks, ending at a draft PR through its Opening a PR playbook, whose final review is /review-loop, unless a standing rule names another flow. Upstream runs its own router flow and autopilot.
- PR maintenance starts at a worker's code-ready result, where upstream watched a PR as soon as it opened, because /pstack-mode's Opening a PR playbook holds babysitting until the stack is built. Each later watch event gets one Babysit pass: the owner works /pstack-mode's Babysit playbook in `drive` mode as an Autopilot owner does, rebasing its own branch, reads status once instead of polling, since the coordinator keeps the watch, and pushes one wave. Babysit has no one-pass mode of its own. A merge is the user's call unless a standing rule grants it, offered as a card listing each PR in merge order, and landed by the owner through /pstack-mode's Shipping playbook. Upstream's per-repository trust values, its `merge-gate.py` hook, and `scripts/stack.sh where` are left out, because this library makes a merge a point only the user can pass.
- A worker returns a call as a question, problem, pick, and evidence, and the coordinator shows it as a decision card with a progress strip. The card's parts and the list of real calls are written out in the skill, because /reply-shape and /next-options are user-invoked and load only through their opt-in hook; /reply-shape lays the card out when active. Upstream's workers write the card themselves, and its cards carry a turn block for its tower. With an empty queue the coordinator posts a status line, and goes to the close or replans once nothing runs, where upstream ends on `done`.
- Upstream's `Mode:` and `Worker of:` brief lines, its `Project:` turn block, and the routine-stop and tower hooks that read them are left out, since this library ships neither upstream's router modes nor those hooks. /next-options' session hook already skips T3 delegated tasks.
- Workers on another machine (`references/across-machines.md`) are left out, because this user's T3 Code links no other machine, as /swarm's record also notes. Revisit when one is linked.
- Upstream's `references/workflow.md`, Oliver's builder workflow, is left out; this library's architecture document and /pstack-mode own the equivalent routing.
- A worker is stuck only when its thread stopped growing too, where upstream judged a worker with a branch by commits and PR activity alone, which would cancel a builder deep in a long review between commits. A startup error is retried at once, where upstream recorded it as the worker's state, which `project.py` refuses.
- Every timer's prompt opens with the user's gate for interval tasks when their instructions set one, because T3 Code replays the interval runs missed while the machine slept, so an unattended two-minute startup timer could fire hundreds of times on wake.
- Without T3 Code's tools the skill stops and points to /pstack-mode's Orchestrate playbook, which runs a program on any host.
- `project.py` drops upstream's `--mode` option and the header's `Mode:` field, adds a Proof column, because step 2 records each unit's proof in Workers and upstream's table had no place for it, and refuses a worker name holding `|`, which upstream wrote unescaped and then could not edit. The Goal section is edited by hand like the close's Result, since no command edits its follow-ups. Its tests sit under `scripts/tests/`, where `pnpm check` discovers them, and use `tempfile.TemporaryDirectory` like the library's other suites.
- The invocation mode matches upstream's model-invoked skill, so a heartbeat, a worker's completion, or a compaction reloads it in a coordinator thread.

Decide upstream changes to `coordinator/` by the principle-derived rules. Review changes to upstream's `orchestrate/SKILL.md` here only for its brief and Standing rules convention; /swarm's record reviews it and `shared/t3-delegation.md` for the T3 route.

## Maintenance

| Review date | Candidate revision                         | Decision                                                                                                                                                                         |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-31  | `3030e458624e66d3c744cfbb60e97381d352be20` | Adopted at the user's request as a first-party, principle-derived skill, with the departures above. `project.py` is ported without `--mode`, with a Proof column, and refusing ` | `in a worker name, and its eleven tests pass from`scripts/tests/`. A Claude child recalled its first brief after a `t3_thread_send`, which backs sending more work to a worker's thread. Every T3 tool the skill names was checked against this session's T3 Code tool schemas. Fidelity passes in both directions: each adopted principle is in upstream's skill at this revision, and every departure is present. |
