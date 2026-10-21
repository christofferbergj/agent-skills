---
name: git-guardrails
description: Set up Codex or Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset.
---

# Set up Git guardrails

## What Gets Blocked

- `git push` (all variants including `--force`)
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

When blocked, the agent sees a message telling it that it does not have authority to access these commands.

## Steps

1. Resolve the user's requested host, project/global scope, and blocked operations. Ask if user wants to add or remove any patterns from the blocked list. Inspect existing settings and actual hook capability before editing. Merely installing this skill changes no host settings. Complete when the target and policy are authorized and concrete.
2. Copy [the Python detector](scripts/block-dangerous-git.py) to the agreed hook location and verify Python 3 is available. Edit the copied detector for any added or removed patterns. It inspects ordinary literal Git shell commands, including common Git options and shell separators. It is an accidental-operation guardrail, not a complete shell sandbox: aliases, opaque scripts, indirect language runtimes, or unsupported host paths can bypass it. Use host permissions for enforcement. Complete when the detector passes its fixture cases and limitations match the requested policy.
3. Read the matching host reference below and merge a command hook into existing settings without replacing unrelated hooks. Resolve an absolute script path, or the host's documented project-directory form for a project hook; never build a command from untrusted issue text. Complete when the saved matcher and command use that host's documented schema.
4. Test harmless allowed and denied events using stdin fixtures; a denied fixture such as `git push origin main` should exit with code 2 and print a BLOCKED message to stderr, then verify the host actually invokes the hook without running a destructive command. Codex hooks require native review/trust; report a pending trust step accurately and never bypass it. Complete when observed host behavior matches the policy or activation remains an explicit gap.

## Host adapters

- For Codex, read [the Codex adapter](references/codex.md).
- For Claude Code, read [the Claude Code adapter](references/claude-code.md).

The optional `scripts/block-dangerous-git.sh` wrapper invokes the Python detector for existing shell-hook launchers. Both adapters use the same detector and JSON deny response. Run `python3 -m unittest discover -s scripts/tests -v` from this skill to exercise its bounded command coverage.
