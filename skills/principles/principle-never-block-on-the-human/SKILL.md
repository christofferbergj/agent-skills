---
name: principle-never-block-on-the-human
description: "Apply when tempted to ask 'should I do X?' on reversible work."
---

# Never Block on the Human

The human supervises asynchronously. Agents must stay unblocked. Make reasonable decisions, proceed, and let the human course-correct after the fact. Since code changes are reversible and reviewable, a wrong decision usually costs less than blocking.

- Proceed, then present. Do the work, show the result. Don't ask "should I do X?" Do X, explain why.
- Make the system self-healing. When you notice a problem, log it and fix it in the next round.
- Irreversible actions (force-push, delete production data, send external messages) require the user's authorization. Honor authorization already given for that action; ask only when it is missing.
- Authorized reversible actions (write code, edit notes, split tasks) should proceed without blocking.
- Product direction, interview confirmation, and explicitly requested approval checkpoints come from the human. Proceed within the accepted phase and scope; a later incompatible change to an approved contract returns to that decision gate. Execution within the grant should not block.
