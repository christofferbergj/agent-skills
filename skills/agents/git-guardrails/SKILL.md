---
name: git-guardrails
description: Configure explicit Git-operation guardrails through supported Codex or Claude Code hooks when the user requests them.
---

# Set up Git guardrails

1. Resolve the user's requested host, project/global scope, and blocked operations. Inspect existing settings and actual hook capability before editing. Merely installing this skill changes no host settings. Complete when the target and policy are authorized and concrete.
2. Copy [the Python detector](scripts/block-dangerous-git.py) to the agreed hook location and verify Python 3 is available. It inspects ordinary literal Git shell commands, including common Git options and shell separators. It is an accidental-operation guardrail, not a complete shell sandbox: aliases, opaque scripts, indirect language runtimes, or unsupported host paths can bypass it. Use host permissions for enforcement. Complete when the detector passes its fixture cases and limitations match the requested policy.
3. Read the matching host reference below and merge a command hook into existing settings without replacing unrelated hooks. Resolve an absolute script path; never build a command from untrusted issue text. Complete when the saved matcher and command use that host's documented schema.
4. Test harmless allowed and denied events using stdin fixtures, then verify the host actually invokes the hook without running a destructive command. Codex hooks require native review/trust; report a pending trust step accurately and never bypass it. Complete when observed host behavior matches the policy or activation remains an explicit gap.

## Host adapters

- For Codex, read [the Codex adapter](references/codex.md).
- For Claude Code, read [the Claude Code adapter](references/claude-code.md).

The optional `scripts/block-dangerous-git.sh` wrapper invokes the Python detector for existing shell-hook launchers. Both adapters use the same detector and JSON deny response. Run `python3 -m unittest discover -s scripts/tests -v` from this skill to exercise its bounded command coverage.
