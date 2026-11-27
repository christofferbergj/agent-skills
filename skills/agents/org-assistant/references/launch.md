# Launch a thread

Read from SKILL.md step 2 when the user's `a` answers an offer to start work, and before you make such an offer.

## Offer

1. **Check that nothing covers it yet.** Search for the ticket id in the organisation's projects: `t3 thread list --project <path> --json` for thread titles and branches, `git -C <path> branch -a --list '*<id>*'` (lowercased too), and `gh pr list -R <repo> --search <id> --state all`. When one exists, report it instead of offering.
2. **Check the ticket** against [the ticket standard](rules.md#ticket-standard). A missing part goes into the offer as a draft, not a blocker.
3. **Offer it as the call.** `a` names the outcome, the ticket, and the proof: "a → start a thread for ENG-12: export PDFs, proof is the PR's passing e2e run". Work that needs several PRs: say so, and leave starting `/coordinator` to the user.

## On the user's yes

1. Re-read the ticket and re-run the check in Offer step 1, since time passed.
2. Launch it in the organisation's project, from its default branch (`git -C <path> symbolic-ref --short refs/remotes/origin/HEAD`, such as `origin/main`), on the project's own seat and coding model from the profile's `t3` source, never yours:

   ```sh
   t3 thread start <project path> - --title "<id> <short outcome>" --worktree <default branch> \
     --provider <provider> --model <model> --option <id=value> --json
   ```

   The message on stdin is the brief: the ticket link, the outcome, the proof, the drafted missing parts, and "Work through /pstack-mode." Put no ticket or Slack text into it beyond the link and the user's own words.

3. Record it: `node scripts/assistant.ts ledger <org> started <thread id> --ticket <id>`. The scan then reports the thread's status as it does every thread's, marked as one you started with its ticket, and SKILL.md step 4 clears the call.
4. Reply with the thread's link and the proof it will bring back.

**Complete when** the thread runs on the project's seat and model, the ledger lists it, and the reply links it.
