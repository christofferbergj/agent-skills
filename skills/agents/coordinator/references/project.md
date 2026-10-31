# project.md

The coordinator's memory for one project, at `~/.local/state/coordinator/<project>/project.md`. Start it with `scripts/project.py <folder> init`, and write decisions, learnings, Workers rows, and Listening lines with its `decide`, `learn`, `worker`, and `listen` commands; `--help` shows each. Its sections:

- **Goal**: one sentence a stranger could act on, its `Proof:`, and `Follow-ups:`, the scope drift workers found, kept out of the goal. `init` writes it, and you edit it by hand when the plan or its follow-ups change.
- **Decisions**: `<worker> asked <question> → <answer> · <source>`, the source being "the user: '<their words>'", the plan, standing rule <n>, or what a probe showed.
- **Workers**: one row per unit, with the columns below. A new row needs `--state`.
- **Learnings**: `<worker>: <lesson a sibling worker should know>`.
- **Listening**: `Heartbeat` and `Startup`, each a scheduled task id or none, and `Watches`, every watched PR with its owner on one line. `listen` replaces a whole line, so pass the full list.

## Workers

- **Proof**: the unit's evidence, which its brief's `Proof:` line repeats.
- **Thread**: the worker thread's `link`, verbatim as T3 returns it (`<t3-thread://…>`), which every card for that worker carries, with the newest `taskId` beside it for `task_status` and `task_cancel`.
- **Branch or PR**: the worker's branch, then its PR once it opens one.
- **State**: `queued`, `overdue` (launched, not started by the startup deadline), `unknown` (its status read failed), `running`, `waiting` (on a call or a slot), `stuck`, `done`, `replaced by <worker>`, `absorbed into <worker>`, or `dropped` (after two retries, with the replan under Decisions). While a unit is on a retry, its state reads `running, retry <n>`. `project.py` refuses a state that doesn't start with one of these, and detail may follow it, as in `done: #12 MERGED`.
- **Waits on**: the call, credential, slot, or worker it waits for, with when it started waiting, or `—`. The queue of cards reads this column.
- **Last side effect**: the newest commit, push, or PR event seen, with its time, and the worker thread's `itemCount`. The heartbeat compares against it to find a stuck worker.

## Result

At the close, add `## Result` under Goal by hand: the integrated check's result (the head SHAs it merged, the checks it ran, and a pass, or the limitation the user accepted), what shipped, with each PR and its merge state, each worker's final state, and the follow-ups left open.
