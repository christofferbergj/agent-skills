# Maintain an owned Pstack adaptation

The initial adaptation covers the 54 registered skills in upstream Pstack and their supporting playbooks, prompts, and scripts as an owned adaptation for Codex and Claude Code. The three dormant Benny automation workflows are outside this scope.

Preserve each workflow's purpose and evidence requirements. Adapt worker counts, model choices, and continuous loops to the task, available capabilities, and budget.

Namespace new skills as `pstack-*`, reuse the existing identical `bro` skill, and maintain an upstream-to-local mapping. This prevents collisions with other installed skills and makes upstream comparisons traceable.

Proceed autonomously within agreed scope. Pause when scope or an approved interface changes, or repeated failures require a decision. Deliver draft pull requests by default and honor existing authorization for further actions.
