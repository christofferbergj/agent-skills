# next-options: source and local adaptations

## Source and credit

- Original author: Oliver Cederborg.
- Source repository: [olivercederborg/skills](https://github.com/olivercederborg/skills).
- Original skill: [`reply-shape/SKILL.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/reply-shape/SKILL.md), for its next-step and Done endings.
- Supporting sources: [`replies.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/replies.md), which defines the lettered `Next` list, [`hooks/reply-shape-context.py`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/hooks/reply-shape-context.py), the SessionStart hook that loads it, and [`router.md`](https://github.com/olivercederborg/skills/blob/e8db4fa3e2468a0b9e0297955367ff6efde28dee/router.md), whose stops decide when the list appears.
- Tracking policy: upstream `main`, reviewed as a principle source under the adaptation contract's [principle-derived skills](../../agents/maintain-skills/references/ADAPTATION.md#principle-derived-skills).
- Imported from commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Reviewed through commit: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Fidelity checked through: `e8db4fa3e2468a0b9e0297955367ff6efde28dee`.
- Last upstream review: 2026-10-20.
- Attribution-only source: https://gist.github.com/olivercederborg/92236670065aaa661db221f22203ded5 is Oliver's handover gist. Its copies of these three files match the tracked repository at the imported commit, apart from a catch-up rule outside this skill's scope.
- Attribution-only source: https://github.com/ayghri/i-have-adhd is the ancestor of Oliver's `reply-shape`. This skill takes none of the layout rules that `reply-shape` kept from it, so Oliver's repository is tracked instead.
- License: [MIT, copyright 2026 Oliver Cederborg](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

The wording is first-party. These are the principles taken from the source and the deliberate departures.

Adopted principles:

- At most three lettered options, `a` recommended, as the turn's only question, offered only where the user must act, after a question, or while only external work remains.
- `a` names every push, post, or issue it creates and changes no PR or issue state the user didn't ask for.
- The agent does what a CLI, Executor, an MCP server, or computer control can do; waiting work offers independent work or a watch; filler and options passed over twice drop out.
- Items keep fixed numbers, and short answers such as `3`, `skip 3`, and `?` work without option lines.
- A SessionStart hook loads the rules into every top-level session in both hosts, including resumes and compactions. Both hosts' hook documentation gives native subagents their own SubagentStart event, so they skip the rules; on 2026-10-20 a fresh T3 Code Claude session received the installed hook's rules and recognized the delegated-task exemption, while Codex skips the hook until the user trusts it in `/hooks`.

Departures:

- Only the next-step and Done endings are taken. Reply-shape's Status, Changed, Needs you, Details, decision cards, and picture rules stay out until the user asks for them.
- Oliver's router stops become a list of points only the user can pass, beside /pstack-principle-never-block-on-the-human, which owns working on without asking.
- A handoff table names the usual next stage in this library's flows.
- The hook is TypeScript run by Node, reads the installed skill's own `SKILL.md` up to its setup pointer, and warns at 8,000 characters to stay under both hosts' context caps.
- The hook does not read T3 Code's internal state database to skip delegated child tasks. The rules and /pstack-swarm's briefs tell a delegated task to report without options, which avoids depending on an unversioned schema.

`agents/openai.yaml`, `references/setup.md`, the `scripts/` directory, and this record are locally maintained.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep. Decide each upstream change to the tracked files by the principle-derived rules. Advance the reviewed-through position only after the delta is decided and checks pass.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                             |
| ----------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-10-20  | `e8db4fa3e2468a0b9e0297955367ff6efde28dee` | Adapted the lettered `Next` list, the Done ending, and the SessionStart loader as principles. Ported the Python hook to TypeScript and replaced its T3 database lookup with brief-level reporting rules. Its two Node tests pass: the rules load within both hosts' limits, and a missing file warns instead of failing the session. |
