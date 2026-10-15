# Claude Code hook adapter

Merge a command hook into the agreed project `.claude/settings.json` or user `~/.claude/settings.json`, preserving existing handlers:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
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

Quote the resolved script path safely when it contains spaces. The detector reads the documented `tool_input.command` string and returns a `hookSpecificOutput.permissionDecision: deny` JSON response for its configured operations. Exit zero with no decision leaves normal host permissions in place.

Verify the actual host loads the selected settings and fires the hook on a harmless fixture command. Managed policies may constrain user hooks; expose an unavailable activation step rather than claiming protection. See the current [official Claude Code hooks reference](https://code.claude.com/docs/en/hooks).
