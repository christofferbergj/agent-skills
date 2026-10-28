Run the copy of this repository's /maintain-skills on the default branch, in the mode the scheduled task names, or the one `begin` picks when it names none. Work in the maintenance worktrees its guide describes, and leave the main checkout and its current branch untouched.

- **Upstream mode** has a 60-minute budget. Start wrapping up at minute 50.
- **Audit mode** has a 90-minute budget. Start wrapping up at minute 75.

Read the clock at each step boundary.

This task may commit, push the `skill-maintenance` and `skill-maintenance-process` branches by the guide's push rule, create or update one draft PR for each, and link those PRs to the run's thread. When `scripts/check-installs.py` reports installed skills stale against the default branch, it refreshes them as `AGENTS.md` says. Merging, closing PRs, changing scheduled tasks, production services, and other external messages stay with the owner.
