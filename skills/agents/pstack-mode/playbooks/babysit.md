# Babysit

Own the path to merge-ready, stopping where the user's authority ends.

1. Declare a mode before polling: `check` for one status pass, `threads-only` for requested comments, `drive` for getting a PR green, or `background` for triage during other work. A small or documentation-only PR defaults to `check`. Resolve the repository's forge and stack conventions. Complete when scope, mode, revisions, and deadline are explicit.
2. Work the lowest unmerged dependency first. Read higher-stack feedback and batch it without repeatedly restarting the frontier's checks. Complete each wave when known issues are triaged together.
3. Read `references/bugbot-triage.md` in this skill directory for automated-review findings. Verify each claimed defect, then fix within scope, dismiss with evidence, or surface a decision. Do not accept a finding solely because a bot repeated it. Complete when every relevant finding has a disposition.
4. Resolve authorized conflicts and inspect drift in affected callers, then review threads, then CI. Preserve scope and approved-interface gates. Classify infrastructure or flake before one fresh build; an identical repeat needs diagnosis, not blind retries. Complete when the frontier has a supported status and no hidden known defect.
5. On GitHub run `scripts/watch-pr/watch-pr --pr <number> --status-only` from this skill directory for `check`. For `drive`, pass a positive `--timeout` within the run's remaining budget, plus `--allow-draft` to assess checks without promoting the draft. Use `--stack` for a connected stack or a fixed `--queued-stack --stack-prs <bottom-to-top-list>` only when the task actually tracks that queue. On another forge, use its own status contract and disclose that the GitHub watcher was not used. Complete when a real terminal result, merge-ready state, or timeboxed checkpoint exists.
6. Treat author approval and draft status as human gates. Babysitting does not authorize a merge or marking a draft ready. Route an explicit landing request to Shipping. Complete when the user knows what is ready, blocked, or awaiting their action.

Return mode, frontier, exact revisions, check and review state, triage, and the next action. Answer a mid-run user question and continue within the original grant unless they stop the run.
