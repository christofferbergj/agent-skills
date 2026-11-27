# Usage limits

A **usage limit** stops every thread on one provider instance, one of the user's accounts, until the reset time its notice names, as in `You've hit your 5-hour limit · resets 3pm`. The limited instance is the `providerInstanceId` of the run that ended on the notice, which `t3_thread_read` lists. A limit on this thread's own instance stops you too, so you next wake once the user moves this thread to another instance or the limit resets.

Record each limit you see with `scripts/project.py <folder> learn "<instance>: usage limit until <reset time>"`. A limit holds its instance until that time and nothing after it. A limit you missed costs one failed launch, whose notice records it.

## Pick an instance

The project's **home** is the instance a standing rule names, which keeps it across phases and across a move of this thread. When no rule names one, append it: the instance the project's first worker ran on, or this thread's instance when no worker has run yet.

Every launch and every resend below takes the first **free** instance, one no recorded limit holds, in this order: the home, then the other instances of its driver, in a standing rule's order when one gives it, then the instances of the counterpart vendor, Codex for a Claude home and Claude for a Codex home. The order holds only instances `orchestrator_capabilities` lists with `canRunChildTask: true`. So work returns to the home once its limit resets.

Pass the instance as the target's `providerInstanceId`. On an instance of this thread's vendor a worker keeps the model and effort its role resolved. On the other vendor it takes the model and effort a standing rule names, or else that instance's first listed model at the same effort.

## Resend a stopped task

Move a worker whose run ended on a limit to the instance picked above with `t3_thread_configure`, unless it is already on it. Then resend the task the limit interrupted with `t3_thread_send`: that send in full, with its inputs and decisions and what the branch already holds, since T3 hands a new instance only a summary of the thread. The resend takes a slot like any later task (SKILL.md step 3) and leaves the worker's retry count as it was.

## When no instance is free

Until a reset, the accounts are a shared resource no task can take (SKILL.md step 3). Leave a unit that hasn't started `queued`, and set a stopped worker `waiting` on the earliest reset. Keep a `once` timer for that time, as SKILL.md's timer describes, recorded under Listening as `Reset`, until an instance is free. Then delete it, set that line to none, and launch or resend what waited.

**Complete when:** every launch and resend since the limit took the first free instance, or waits behind the `Reset` timer as `queued` or `waiting`.
