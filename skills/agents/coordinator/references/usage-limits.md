# Usage limits

A **usage limit** stops every thread on one provider instance, one of the user's accounts, until the reset time its notice names, as in `You've hit your 5-hour limit · resets 3pm`. A limit on this thread's own instance stops you too, so you next wake once the user moves this thread to another instance or the limit resets. A run that ended on such a notice follows this file, and no send here counts among the stuck rule's two retries.

## Instance order

The project's **home** is the instance a standing rule names, which keeps it across phases and across a move of this thread. When no rule names one, append a rule that names this thread's instance as the home.

The order is the home, then the other instances of its driver, in a standing rule's order when one gives it, then the instances of the counterpart vendor: Codex for a Claude home, and Claude for a Codex home. It holds only instances `orchestrator_capabilities` lists with `canRunChildTask: true`. An instance in the order is **free** when Listening's `Limits` line doesn't name it.

A worker's target on an instance is that instance as `providerInstanceId`, with the model and effort a standing rule names for it, or else the ones /swarm's `long-running` role resolves with `--parent` set to the instance's host. When the role prints no model, take the instance's first listed model at the worker's effort.

## On a wake that reaches this file

1. **Record.** Set `Limits` to every instance a limit still holds with its reset time, keeping the timer id the line already names, as in `scripts/project.py <folder> listen Limits "claude_adapt until 2026-11-23T15:00+01:00 · timer <id>"`. Leave out an instance whose reset time has passed.
2. **Resume.** While an instance is free, resume each worker a limit stopped. Read its thread's status first, and go on only when its newest run still ended on the limit. Set the first free instance's target with `t3_thread_configure`, or leave a worker whose own instance is free where it is. Then resend the task the limit interrupted with `t3_thread_send`: that send in full, with its inputs and decisions and what the branch already holds, since T3 hands a new instance only a summary of the thread. Each send takes a slot as step 3's Slots says. A worker stays `waiting`, on the reset or the slot, until its send succeeds, and then reads `running` with Waits on `—`.
3. **Wait.** While no instance is free, set each stopped worker `waiting` on the earliest reset, and keep one `once` timer for that time, as SKILL.md's timer describes: keep the timer `Limits` names when it is set for that time; otherwise delete it, set a new one, and write its id on the line.
4. **Clear.** Once no limit is left and no worker waits on a reset, delete the timer `Limits` names and set the line to none.

**Complete when:** `Limits` names each instance a limit holds with its reset time, or reads none; every worker a limit stopped is `running` on a free instance, `waiting` on a slot, or `waiting` on a reset that the one timer `Limits` names wakes you for.
