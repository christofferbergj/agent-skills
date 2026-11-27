# Usage limits

A **usage limit** stops every thread on one provider instance, one of the user's accounts, until the reset time its notice names, as in `You've hit your 5-hour limit · resets 3pm`. A limit on this thread's own instance stops you too, so you next wake once the user moves this thread to another instance or the limit resets.

## Instance order

The project's **home** is the instance a standing rule names, which keeps it across phases and across a move of this thread. When no rule names one, append a rule that names this thread's instance as the home.

The order is the home, then the other instances of its driver that `orchestrator_capabilities` lists with `canRunChildTask: true`, in a standing rule's order when one gives it, then the other vendor. Within the driver a worker keeps its model and effort. On the other vendor it takes the model and effort a standing rule names, or else that vendor's first listed model at the worker's effort.

## On each wake this file is reached

1. **Record.** Rewrite Listening's `Limits` line with every instance a limit still holds, its reset time, and the id of the timer from step 3, as in `scripts/project.py <folder> listen Limits "claude_adapt until 2026-11-23T15:00+01:00 · timer <id>"`. Drop an instance whose reset time has passed, and set the line to none when no limit is left.
2. **Move.** Take each worker a limit stopped to the first instance in the order that `Limits` doesn't name: set it with `t3_thread_configure`, then send its brief and what its branch already holds with `t3_thread_send`, since T3 hands the new instance only a summary of the thread. A worker whose own instance is free again stays there and gets the same send. Either way its state stays `running`, and the send is not one of the stuck rule's two retries.
3. **Wait.** When `Limits` names every instance in the order, set each stopped worker `waiting` on the earliest reset, and set one `once` timer for that time, as SKILL.md's timer describes. Delete the timer once its wake has moved those workers.

A new worker starts on the first instance in the order that `Limits` doesn't name (SKILL.md step 3), so workers return to the home once its limit resets.

**Complete when:** `Limits` names each instance a limit holds with its reset time, or reads none; and every worker a limit stopped runs on an instance `Limits` doesn't name, or is `waiting` on a reset that a timer on the `Limits` line wakes you for.
