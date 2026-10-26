---
name: automate-me
description: "Create or update a personal Pstack mode from repository-scoped history and explicit preferences."
disable-model-invocation: true
---

# Automate me

A guided flow for turning the user's working conventions into a skill agents will follow. The output is one `-mode` skill tailored to them (e.g. `jay-mode`, `priya-mode`).

This skill orchestrates three others: a mining pass over history that /recall discovers (see step 1), /writing-for-agents (authoring), and /unslop (prose discipline). It sequences them. It doesn't replace them.

## Flow

### 0. Check for an existing skill

Look recursively for `*-mode/SKILL.md` matching the user's handle in the project's skill directories (such as `skills/`, `.agents/skills/`, and `.claude/skills/`) and the user's personal ones (`~/.agents/skills/`, `~/.codex/skills/`, and `~/.claude/skills/`). Mode skills can live in a personal category directory (`<skills-root>/<handle>/`), not only at the top level. An installed copy is a discovery input, not an edit target: find the source repository it was installed from and work there. If one exists, confirm intent with the host's structured question tool (unless they already said "update my skill" or similar):

- Update the existing skill (default for repeat runs)
- Start fresh (rare, ask why before doing it)

Update mode changes the rest of the flow:

- Step 1 mines only history since the skill was last edited (`git log -1 --format=%cI <path>`).
- Step 2 asks what's changed or missing, not what to capture from zero.
- Step 4 edits the existing file in place. Preserve sections the user hasn't contradicted. Revise ones with new evidence. Add new sections only for genuinely new rules.

Complete when the source path, the update-or-fresh choice, and the last-edit date are known.

### 1. Mine their history

Locate the active repository's transcripts before fanning out. Invoke /recall for scoped session discovery only, not its brief: it lists this repository's Codex and Claude Code sessions over the window you request. Use only those sessions. Don't read history from other repositories. That crosses workspace boundaries and reads private chats from unrelated projects.

Survey recent agent conversations within that scope for recurring patterns. Run multiple parallel subagents through /swarm across slices of history (e.g. last 2-4 weeks, split into 3 slices so each has enough material). Pick each subagent's model and effort for the job through /swarm's execution contract. Each slice mining subagent reads its sessions through /recall's repository-scoped reader, looks for the signals below, and returns a short structured list of patterns it saw with evidence pointers. Default signals worth hunting:

- Response preferences (length, tone, format, "dumb it down" corrections)
- Delegation habits (subagents, models, specialized workflows, parallelism)
- Verification posture (what "done" means, unit tests vs live repro, reviewers)
- Code and prose discipline (style, principles cited, lint/format tools)
- Process conventions (worktrees, commits, PRs, review/merge tooling)
- Meta preferences (fixing skills mid-task, proposing new ones)

Cross-check across slices before elevating a signal. Patterns seen in 2+ slices are high-confidence. Lone signals are weak and usually get dropped.

Complete when each slice has returned patterns with session pointers, or its gap is named.

### 2. Ask the user directly

Mining misses intent that hasn't come up yet. Use the host's structured multiple-choice question tool rather than asking the user to type from scratch.

Shape: one or two questions with 4-6 options each, allowing multiple selections for category questions. When the host's tool takes one choice per question or none exists, ask the same options as a numbered list and accept several numbers in one reply. Start broad ("Which areas matter most?"), then follow up on selected areas with specific options. After the structured rounds, one free-form chat question catches anything the options missed.

Don't dump 20 questions.

Complete when the user has answered the structured rounds and the free-form question.

### 3. Cluster findings

Group the combined signals into sections. Common ones (use only what applies):

- **Response style**: length, tone, format.
- **Autonomy**: how much to do without asking, MCP tool use.
- **Understand first**: which skills to reach for when scoping or investigating a change.
- **Subagents**: default, parallelism, model-to-task, specialized workflows.
- **Prose / code discipline**: principles, lint tools, style guides.
- **Review and verify**: repro posture, verification skills, live-testing tools.
- **Process**: git worktrees, commits, PRs, review/merge tooling.
- **Skills**: skill-authoring habits, fix-the-skill-first, proposing new skills.

Upstream's [`poteto-mode` skill](https://github.com/cursor/plugins/blob/190d28736eff128ec94f502a22c7fe0c4b56cd37/pstack/skills/poteto-mode/SKILL.md) shows the shape. Read it for granularity. Don't copy its content. The user's rules are not the same as poteto-mode's.

A recurring mistake the mining surfaces goes to /correct for structural prevention, not only to a mode rule.

Complete when every kept signal sits in one section or is handed to /correct.

### 4. Draft the skill

Use /writing-for-agents to author the skill. Placement:

- Path: preserve an existing mode skill's category. For a new mode, use `<skills-root>/<handle>/<handle>-mode/SKILL.md` when the repo has an established personal category for that handle. Otherwise default to `<skills-root>/<handle>-mode/SKILL.md` in the project (or a personal skill source if the user prefers a personal skill). `<skills-root>` is the repository's existing skill directory.
- Handle: the user's first name or chosen identifier.
- Frontmatter `description`: trigger on their name + `/<handle>-mode` + "work in their style", not on generic keywords like "write code" or "review PR".
- Frontmatter formatting: follow /writing-for-agents' YAML rules. Keep `description` as one YAML scalar. Quote it or use `description: >-` with indented continuation lines when punctuation or wrapping requires it.
- Frontmatter `disable-model-invocation: true` by default, mirrored in Codex's `agents/openai.yaml` as `policy.allow_implicit_invocation: false`. Opt out only if the user explicitly wants their mode to apply on every turn.
- Keep raw transcript quotes, organization details, and credentials out of the skill.

Complete when the draft exists at its path with valid frontmatter.

### 5. Iterate on prose

Apply /unslop and /writing-for-agents' writing guidelines to every line.

Show the draft to the user and take feedback. Expect multiple iterations. Cut ruthlessly. A mode skill is not a manual.

Complete when the user accepts the draft.

### 6. Land it

Work in a worktree off main. Commit following the repository's conventions and open a draft PR. Don't push to main directly.

Complete when the draft PR is open, or the user has the committed branch.

## Guardrails

- **Don't overfit to one conversation.** A preference stated once and contradicted another time is noise. Require multiple instances before codifying it.
- **Don't be clever.** Restating other skills' contents, inventing metaphors, or writing "poetic" prose for an agent reader is cost without benefit. Keep it operational.
- **Reference, don't inline.** Other skills the user relies on should appear as `/skill-name` invocations, not pasted excerpts. Same for any principle docs they maintain elsewhere.
- **Keep sections minimal.** Only add a section if the user has a specific, non-default rule there. "Communicate clearly" is not a section. "Short paragraphs. Tables when comparing options. Bullets only when items are genuinely parallel." is.
- **Name conventions generic.** Use "the user" or "the human" in imperatives, not the author's first name.
- **Don't force symmetry.** If a user has no process rules worth writing down, skip the Process section entirely.

## Evaluation

A `-mode` skill is subjective output. A test/iterate benchmark loop isn't useful here. Vibe-check with the user: does it read like them? Did it miss anything? Then ship.

Run a description-optimization loop only if the skill's trigger accuracy turns out to be a problem in practice.

## When not to use

- User wants a task-specific skill (not working conventions): /writing-for-agents alone, no mining required.
- User wants to capture one narrow workflow (e.g. "how I write commit messages"). That's a regular skill, not a mode skill.
