# Set up an organisation

Read when the user asks for an assistant for an organisation that has no profile yet. Every step after the dry run changes something the user sees, so each waits for their go.

1. **Write the profile** at `~/.config/org-assistant/<org>/profile.toml`, as [state](state.md#profile) shows, with `thread = ""`. Take the repositories, Linear teams, and people file from the organisation's repository `AGENTS.md` and docs, and the Executor account ids from `probe.ts client search` run in that repository. List the user's Slack channels with `slack_list_user_channels` (`shared: "internal"`, `exclude_archived: true`) and propose the ones where their work is discussed; the user confirms the list.
2. **Dry-run the scan**: `scripts/assistant.py scan <org> --dry-run --since 24h`. Read its batch: each source should report ok, and the changes should match what the user would expect from the last day. Show the batch as ids, kinds, and counts.
3. **Simulate the failures** the scan's tests cover, against a copy of the state folder (`ORG_ASSISTANT_STATE` set to a scratch folder): a missed scan, an expired sign-in, a failed wake, and a busy thread, and check that nothing is lost or sent twice.
4. **With the user's go**, start the thread in the organisation's T3 project with the title `✦ <name> assistant`, on the organisation's own seat, and pin it. Put its id in the profile's `thread`, and write `rules.md` from the user's rules.
5. **With the user's go**, run one real scan (`scripts/assistant.py scan <org>`), which records the baseline, then enable the timer as [scan](scan.md#timer) shows if it isn't running yet. The next weekday overview is the first post.

**Complete when** the thread is pinned, the profile names it, the timer runs, and the first overview has posted.
