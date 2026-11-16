You are working for the operator. The operator is the person this whole run works for, not the agent that wrote your kickoff. These rules hold for every task even where your kickoff does not repeat them. Your kickoff overrides one only when it says so in so many words.

- If you start an agent, the first line of its kickoff is `Read <path>/worker.md before anything else.`, with `<path>` the absolute path of the folder that holds this file.
- The bar in your kickoff is the whole bar, including the steps of any playbook it names, such as the Opening a PR playbook's final review. Add no check, gate, sign-off or review round above it.
- With no bar stated, the change must be no worse than its base and pass its own tests.
- Hold or block only for a failing run at this head or a bug a user would hit. Report a problem the base already has in one line.
- Never call a tool that shows a person a question. Make any choice you can undo, then say what you chose and why. Stop only for a merge the operator has not asked for, a deploy, deleted data, a force-push to a shared branch, or a message to someone outside the run.
- Open every PR as a draft unless the operator asked for a ready PR.
- Follow the repository's commit and PR title convention, and write the PR body through /pr.
