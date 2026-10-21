# Codex hook adapter

Verify the installed CLI's hook capability first. Codex loads `hooks.json` beside active config layers, commonly project `.codex/hooks.json` or user `~/.codex/hooks.json`. Project layers and non-managed hook definitions require native trust review.

Merge this shape using the resolved absolute detector path, preserving existing event handlers:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /absolute/path/block-dangerous-git.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

For a project hook, copy the detector to `.codex/hooks/block-dangerous-git.py` and resolve it from the git root, as the Codex documentation recommends: `python3 "$(git rev-parse --show-toplevel)/.codex/hooks/block-dangerous-git.py"`. Quote paths safely when they contain spaces. The documented hook reports shell and unified-exec calls as `Bash`, with the command in `tool_input.command`. The detector returns `hookSpecificOutput.permissionDecision: deny` or exits zero with no decision. Silence never grants approval.

Use Codex's `/hooks` interface to review and trust the exact configured hook. A syntactically valid file is not proof that an untrusted or disabled hook runs. Matching hooks from multiple layers all run; a project entry cannot replace or disable another source's policy.

Check the current [official Codex hooks documentation](https://developers.openai.com/codex/hooks/) when the installed schema differs. Some specialized tool paths are not covered; do not advertise complete enforcement.
