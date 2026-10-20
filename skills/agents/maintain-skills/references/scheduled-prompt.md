Run this repository's /maintain-skills from the default branch in the mode the scheduled task names. Work in a separate worktree for each maintenance branch, and leave the main checkout and its current branch untouched.

- **Upstream mode** runs daily with a 60-minute budget. Start wrapping up at minute 50.
- **Audit mode** runs weekly with a 90-minute budget. Start wrapping up at minute 75.

When the task names no mode, run audit mode if the state directory has no audit run from the last seven days, and upstream mode otherwise. Read the clock at each step boundary.

This task may commit, push the `skill-maintenance` and `skill-maintenance-process` branches (rebasing them with `--force-with-lease`), create or update one draft PR for each, and link those PRs to the run's thread. Merging, closing PRs, refreshing installed skills, changing scheduled tasks, production services, and other external messages stay with the owner.

Report proposed updates, decisions the owner must make, failures, and coverage still pending. A run with nothing to propose or ask needs no report.
