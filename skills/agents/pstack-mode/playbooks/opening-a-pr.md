# Open a pull request

Own a reviewable artifact and a description its reviewer can verify.

1. Inspect repository contribution policy, established stack tools, branch base, and initial status. Preserve unrelated work. Use the repository's naming and commit conventions. Complete when the scope, branch chain, and authorized remote action are explicit.
2. Read the final diff, run appropriate checks, invoke /pstack-no-comments when applicable, and remove accidental generated artifacts. Complete when the committed artifact matches the intended scope and evidence.
3. Create a draft PR by default using an available native forge tool or the repository's established CLI. A stack child targets its parent branch. Keep author-required gates and exact base/head evidence visible. Complete when the PR references the intended diff and reports validation honestly.
4. Write the description under /pstack-technical-writing: lead with the problem and resulting behavior, include meaningful validation and limitations, and explain non-obvious tradeoffs. Complete when a reviewer needs no conversation history to assess it.
5. Return the real PR URL, behavior, checks, and open issues. Opening a PR does not start indefinite babysitting or authorize merging. Complete when delivery status is explicit.
