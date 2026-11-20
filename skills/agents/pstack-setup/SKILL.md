---
name: pstack-setup
description: "Use when configuring Pstack model roles, effort budgets, optional review providers, or source locations."
---

# Set up Pstack

Write `~/.config/pstack/config.json`, or the explicit `PSTACK_CONFIG` path, a personal file that sets Pstack's model per role for Codex and Claude Code. /swarm's `scripts/target.py` reads it on every spawn and holds the defaults it overrides.

## Steps

### 1. Detect available models

Enumerate the models and efforts you can pass to a subagent in this session: in Claude Code, the `model` and `effort` values the `Agent` tool schema lists; in Codex, the models and reasoning efforts its spawn tool accepts. That is the dependable source. If you cannot detect any, ask the user to paste the models they have access to. Never write a real model you have not confirmed is available. The aliases `inherit-parent` and `auto` are always valid even though they are not detected models. Also note whether the counterpart can run, through T3 Code's `delegate_task` or the other vendor's CLI, and whether Codex Computer Use is available.

### 2. Load current state

The default role-to-model mapping is what /swarm's `scripts/target.py` prints for each role. If the file already exists, read it and treat each host section's `budget` and role values as the current choices. Otherwise start from those defaults. Read repository overrides only when explicitly configured. An entry that `target.py --help` doesn't list, other than the schema version and source location, is retired, such as the roles `hardest-tasks`, `reflect-tooling`, or `how-explorer`, or the keys `codexUsage.fastWhileLeft` or a review timeout. Drop it. A `budget` of `unlimited` becomes `large`, because no role runs above `xhigh`.

Every other value is the user's choice and stays, including every `inherit-parent` or `auto` value. Tell the user which values you dropped or replaced.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer the host's question tool over free text. Offer these three options with these exact labels, and name the current budget when the file records one. With no file, say that `large` matches the skill defaults.

- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Apply it.** Write the budget as the host section's `budget`; /swarm's `target.py` applies it to every role and panel seat that keeps its default effort. Each role has a target effort, which is its default's effort moved by the budget. `large` keeps it, `medium` lowers it one step, and `small` lowers it two steps, on the ladder `xhigh` > `high` > `medium` > `low`. No role runs above `xhigh`, and a target at the bottom of the ladder stays there. Most defaults are at `xhigh`, and each budget label names where those land. A role the user set by model or effort keeps that choice, and `inherit-parent` and `auto` do not change.

**(c) Show the roles and confirm.** Show every role with the target `target.py` prints for it, marking any configured model not in the detected set as needing a choice. Also list each value step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models at `xhigh` or below plus `inherit-parent` and `auto` (both mean: this role runs on the parent chat model) as the options. Prefer the host's question tool. For panel roles (`arena-runners`, `interrogate-reviewers`) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count; /swarm runs a Claude entry under Codex through the counterpart and a `gemini-*` entry through T3 Code's Antigravity provider. Arena runs one judge from upstream's fixed pool, so it has no role here. `swarm-workers` is the default model for every worker unless a race or comparison assigns another model per arm.

Then ask for the settings /swarm's routes read, offering the default `target.py --help` shows for each: the counterpart reviewer's provider instance, model, full and delta review effort, and Codex speed; the Computer Use delegate's model, routine and hard effort, and speed; the hours of lead on even pace Codex delegates may take before leaving fast mode, the floor below which they leave it (percent kept per day left and its cap), and the percent of Codex usage left below which they skip Codex; and the source repository for learning-driven changes.

### 4. Validate

Every real model written must be in the detected set, or, for a panel seat or setting on another vendor, among that provider's models in T3 Code or the counterpart's, and at `xhigh` or below. `inherit-parent` and `auto` always pass. If a chosen real model is not available, stop and ask again.

### 5. Write the file

Write the file atomically, outside installed instructions, with a schema version, one section per host (`claude-code`, `codex`) holding its `budget`, `roles`, `review`, and `computerUse` entries, the `codexUsage` thresholds, and the source location, in the keys `target.py --help` shows. Write only the user's choices, so a role without an entry takes /swarm's default and deleting an entry returns it there. Keep credentials in the providers' existing stores, not this file. Overwrite the whole file so re-runs stay idempotent, then read it back and check that it matches the agreed choices.

### 6. Confirm

Tell the user the file was written and that /swarm reads it on every spawn, so it applies at once. Name any integration step 1 found missing. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke /create-verification-skill. On no, move on without pushing.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? Type /create-formal-verification-skill to generate one." On no, move on without pushing.
