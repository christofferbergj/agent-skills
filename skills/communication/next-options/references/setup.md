# Load the rules in every session

A SessionStart hook in each host runs [`session-start.ts`](../scripts/session-start.ts), which reads an installed reply skill's `SKILL.md`, this one by default, and adds its rules to the session's context at every start, resume, clear, and compaction. Native subagents don't run SessionStart, so they don't carry the rules. Installing the skill changes no host settings; edit them only on the user's request.

1. Resolve the hosts the user wants, Claude Code, Codex, or both, and read their existing hooks: `~/.claude/settings.json` for Claude Code, and `~/.codex/hooks.json` or `[hooks]` in `~/.codex/config.toml` for Codex. Find any copy of these rules in global instructions, which would load twice. **Complete when:** the target files, their current SessionStart hooks, and any duplicate copy are known.
2. Resolve two absolute paths: the installed script, normally `~/.agents/skills/next-options/scripts/session-start.ts` after a global Skills CLI install, and a Node 22.18 or newer binary that per-project version managers don't switch, such as mise's `installs/node/lts/bin/node`. A project pinned to an older Node would otherwise fail the hook. For /reply-shape, the script's argument is that skill's installed `SKILL.md`, normally `~/.agents/skills/reply-shape/SKILL.md`. Run `echo '{}' | <node> <script> [argument]` for each skill. **Complete when:** each prints JSON whose `hookSpecificOutput.additionalContext` holds that skill's rules and no `systemMessage`.
3. Merge one entry per skill into each target's `SessionStart` list, keeping every existing hook, so each skill stays within its own hook limit. Both hosts use the same shape, with `<command>` as `<node> <script>`, followed by the argument for /reply-shape:

   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "hooks": [{ "type": "command", "command": "<command>", "timeout": 10 }]
         }
       ]
     }
   }
   ```

   Quote paths that contain spaces. Remove a duplicate copy of the rules from global instructions with the user's agreement. **Complete when:** each file parses and holds exactly one entry per skill.

4. Verify each host. Codex runs a new or changed hook only after it is trusted. The user trusts it in `/hooks`; when they ask you to, make the same app-server calls `/hooks` makes: `hooks/list` for the entry's `key` and `currentHash`, then `config/batchWrite` upserting `hooks.state.<key>.trusted_hash`. Never bypass trust with `--dangerously-bypass-hook-trust`. In a fresh session, answer a read-only question and check that the reply ends with `**Next**`, and opens with /reply-shape's status line when it is installed. **Complete when:** a fresh session on each host shows the rules, or the remaining step is reported.

To turn a skill's rules off, remove its entry. Skills CLI updates replace the installed `SKILL.md`, so new sessions pick up rule changes without editing the hook.
