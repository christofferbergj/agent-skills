# Pause safely

Own a recoverable stop without losing work or evidence.

1. On an explicit pause or imminent session end, stop dispatching new work and propagate a zero-writes instruction to active owners through native tools. Complete when each reachable writer has acknowledged or its state is recorded as uncertain.
2. Preserve scoped work, exact branches and revisions, PR links, output artifacts, current verification, process ownership, and known blockers. Commit or push only under existing authorization. Never reset unrelated work to simplify the handoff. Complete when a replacement can locate every retained artifact.
3. Stop only processes the run owns, or record why a deliberately retained process is needed. Keep evidence and runtime state. Complete when resource ownership and remaining live activity are explicit.
4. Write a durable checkpoint with original and later directives, approved interfaces, predicate, next command, unfinished work, and outstanding gates. Use /pstack-show-me-your-work for the decision trail. Complete when Session pickup can resume without trusting an obsolete agent handle.

Return checkpoint path, status, artifacts, remaining activity, and the exact next action. An explicit pause ends execution until the user resumes it.
