# project.md

The coordinator's memory for one project, at `~/.local/state/coordinator/<project>/project.md`. Start it with `scripts/project.py <folder> init`, and write decisions, learnings, Workers rows, and Listening lines with its `decide`, `learn`, `worker`, and `listen` commands. End a phase with `phase`, and start the next one on a parked project with `start`, as [phases](phases.md) says. `--help` shows each command. Its sections:

- **Goal**: the current phase's goal, one sentence a stranger could act on, its `Proof:`, and `Follow-ups:`, the scope drift workers found, kept out of the goal. `init`, `phase`, and `start` write it, and you edit it by hand when the plan or its follow-ups change. Record `Delivery: multi-pr` or the one-PR integration branch, original target base, and integrator as [one-PR delivery](one-pr.md#establish-ownership) specifies. Resolve legacy delivery through coordinator step 2, rather than inferring it from PR count. A parked project's Goal reads `Parked <date>: <reason>`, its Delivery line, and its Follow-ups, with no `Proof:`.
- **Phases**: one line per finished phase, `- <date> · <NN>-<slug>: <result> · phases/<NN>-<slug>.md`, which `phase` adds under Goal.
- **Decisions**: `<worker> asked <question> → <answer> · <source>`, the source being "the user: '<their words>'", the plan, standing rule <n>, or what a probe showed.
- **Workers**: one row per unit or subthread, with the columns below. A new row needs `--state`.
- **Learnings**: `<worker>: <lesson a sibling worker should know>`.
- **Listening**: `Heartbeat` and `Startup`, each a scheduled task id or none, and `Watches`, every watched PR with its owner on one line. `listen` replaces a whole line, so pass the full list.

## Workers

- **Proof**: the unit's evidence, which its brief's `Proof:` line repeats.
- **Thread**: the worker thread's `link`, verbatim as T3 returns it (`<t3-thread://…>`), which every card for that worker carries, with the newest `taskId` beside it for `task_status` and `task_cancel`, or the `environmentId` of a worker on another machine.
- **Branch or PR**: the worker's branch, then its PR once it opens one. In one-PR delivery, ticket rows name their integration base and result SHAs; the integrator row names its integration branch and latest checked SHA, then the sole PR link, retaining its checked SHA under Last side effect.
- **State**: `queued`, `overdue` (launched, not started by the startup deadline), `unknown` (its status read failed), `running`, `waiting` (on a call, a slot, a shared resource, or its PR open from an ended phase), `stuck`, `done`, `replaced by <worker>`, `absorbed into <worker>`, or `dropped` (after two retries, with the replan under Decisions). While a unit is on a retry, its state reads `running, retry <n>`. `project.py` refuses a state that doesn't start with one of these, and detail may follow it, as in `done: #12 MERGED`. One-PR tickets use `waiting: integration` after their checked result and `done: integrated at <SHA>` after acceptance; Waits on names the integrator or repair worker until accepted.
- **Waits on**: the call, credential, slot, shared resource, worker, or open PR (`#<n> open`) it waits for, with when it started waiting, or `—`. The queue of cards reads this column.
- **Last side effect**: the newest commit, push, or PR event seen, with its time, and the worker thread's `itemCount`. The heartbeat compares against it to find a stuck worker.

## Phase end

`phase` saves `project.md` byte for byte to `phases/<NN>-<slug>.md` in the project folder, numbering from `01`, so a wake reads only the current phase, and only the close, or an open one-PR delivery that needs an ended phase's evidence, reads the archives. It then empties Decisions and Learnings, removes each Result section, drops the Workers rows in a final state (`done`, `dropped`, `replaced by`, `absorbed into`), and writes the next phase's Goal or the parked one, keeping its `Delivery:` line and Follow-ups, since an open PR keeps its delivery's rules. Every other section and line carries over. A row whose cells don't match the header stays, and `phase` names it on standard error for you to fix by hand.

## Result

At the close, add `## Result` under Goal by hand: the integrated check's result (the head and base SHAs it checked, the tested tree, the checks it ran, and a pass, or the limitation the user accepted), what shipped in every phase, read from each archive under Phases, with each PR and its merge state, each worker's final state, and the follow-ups left open.
