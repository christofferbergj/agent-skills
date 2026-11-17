### Opening a PR

Invoked at the end of every other playbook.

Work from a git worktree off trunk, and keep unrelated work out of it. Rebase into small, landable commits. Run a deslop pass over the diff with the repository's or host's cleanup tool, when one exists, before commit.

**Final review.** Run /review-loop for the final review of your own implementation before opening the PR. When the user names another review, such as /thermos, run it as well and pass its evidence to /review-loop, which still gives the final verdict. The reply that posts the PR quotes that verdict line with its reviewer counts, such as `Codex 2 · Claude 3`, or the single-model label and its reason.

Title: follow the repository's commit and PR title convention, naming a real symbol when one carries the change. Body: write it through /pr.

Stack follow-ups by base branch. Open PRs as drafts unless the user asked for a ready PR, through the run's PR tool with the draft state set explicitly. Without one, use `gh pr create --draft`, or the equivalent of the repository's established forge CLI. Opening a PR does not start a babysit.
