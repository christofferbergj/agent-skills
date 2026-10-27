---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Invoke /principles for the design-interview phase before recommending a shape and as each round changes the design tree. Apply the selected owners to recommendations and unresolved questions within this interview; keep the user's decisions and confirmation checkpoint.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), invoke /swarm to dispatch a read-only investigation; when /swarm or delegation is unavailable, investigate directly. Don't ask the user for anything you could look up yourself. A question you could settle by running something, such as how a state model behaves or which approach is faster, is a fact too: settle it with a throwaway sketch, through /design-prototype for logic or a short measuring script for speed, and report the observed result in the next round as a settled decision the user can overturn. For a question about how something should look, build the variants through /design-prototype and ask with them in hand, recommending one. Keep sketches out of the user's uncommitted work, in a scratch directory or a throwaway worktree. Don't block on it: a running exploration or sketch is an unsettled prerequisite, so only the questions downstream of it wait for its result; ask the rest of the frontier now. The remaining _decisions_, product and preference calls no experiment can settle, are the user's: put each to them and wait.

Recheck /principles against the agreed design before declaring the frontier empty. The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
