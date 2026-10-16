---
name: pstack-no-comments
description: "Use for Pstack comment review, unnecessary narration, or suppressions that conceal code problems."
---

# No comments

1. Resolve the requested files or diff and repository comment conventions. Complete when the critic's scope and applicable contract are fixed.
2. Use /pstack-swarm to dispatch an independent critic with [the comment-review prompt](references/comment-reviewer.md) and the scope. The critic reads nearby code, preserves required license and public-contract comments, and reports deletions and evidenced refactor targets without changing application code. Complete when each proposed deletion or refactor names a concrete location and reason.
3. Inspect findings. Preserve comments required by the repository or a verified external constraint. Apply warranted comment changes within scope; refactor only when the task authorizes it. Invoke /pstack-how or /pstack-why to resolve a disputed explanation. Complete when every finding is applied, retained with a reason, or explicitly left outside scope.
4. Run checks appropriate to the change and report files, deletion count, verified refactor flags, and skips. Complete when cleanup preserves behavior and required explanations.
