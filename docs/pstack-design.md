# Pstack adaptation design

The user confirmed this initial Pstack design on 2026-10-15. Its source and host-execution decisions remain in force. The [combined-library decision](adr/0003-compose-shared-skill-disciplines.md) extends artifact ownership and dependencies to include Matt Pocock's skills. As updated on 2026-10-16, the current [repository maintenance guide](../skills/agents/maintain-skills/MAINTENANCE.md) governs one review covering every local skill and its upstreams. The suite validation records report exercised behavior and remaining integration limits.

## Result and scope

Maintain an owned Pstack adaptation in `agent-skills` for Codex and Claude Code. The initial inventory covers all 54 registered upstream skills, including the 24 principle skills, and their required prompts, references, scripts, and 23 playbooks. The three dormant Benny automation workflows are outside this scope.

The planning baseline is [upstream Pstack 0.15.25 at e5136d82418d2db3165ea1050d17577cd618cc05](https://github.com/cursor/plugins/tree/e5136d82418d2db3165ea1050d17577cd618cc05/pstack). The [friend's adaptation](https://claude.ai/artifact/XnTonYPG16kDKmoJyxKo2g), [Inside Pstack article](https://claude.ai/code/artifact/8ca0a07e-f9c3-4724-b49d-c002692bafe9), and [generic mirror](https://github.com/backnotprop/pstack) inform the design. Cursor's public repository remains the canonical source for upstream review.

## Ownership and maintenance

The [adaptation decision](adr/0001-maintain-an-owned-pstack-adaptation.md) records scope, names, adaptive effort, and autonomy. The [maintenance decision](adr/0002-review-pstack-updates-through-pull-requests.md) records update review, publication boundaries, and the schedule's history; saved automation settings own the current schedule and model.

Within repository-wide maintenance, use the upstream-to-local mapping for this suite, including the reused `bro` skill. Discover the full local inventory and all other upstreams independently of that mapping. Each adapted skill has a skill-local `UPSTREAM.md` with source paths, tracking policy, immutable import revision, reviewed-through revision, license attribution, local adaptations, and update decisions. Preserve upstream MIT notices with derived content.

Track upstream `main` within the `pstack/` directory. Compare the previous reviewed source, candidate source, and local adaptation before adopting changes. Preserve the recorded reasons for adapted or excluded behavior. The original imported revision stays fixed; only a completed review advances the reviewed-through revision.

## Packaging and installation

Create 53 new `pstack-*` skills and reuse the existing identical `bro` skill. Add source attribution and maintenance coverage to `bro` while preserving its explicit invocation behavior. The router is `pstack-mode`; creator-specific help and setup names become `pstack-help` and `pstack-setup`.

Keep skills under `skills/<category>/<skill-name>/`. Each skill includes a matching lowercase, hyphenated `name`, a string `description`, synchronized Codex metadata in `agents/openai.yaml`, and its required supporting files. List each skill in the root and owning category README.

Use `/skill-name` prose invocation for dependencies. Keep shared reference material with its owning skill and reach it through that owner. Bundle the Comment Sicko prompt with its owning adapted skill so custom Cursor agent registration is unnecessary.

Document a complete Skills CLI installation for both `codex` and `claude-code`, plus the dependency groups required by individual entrypoints. The CLI does not install dependencies transitively. Installed copies are installation outputs; source changes happen in this repository and require a later refresh to reach installed copies.

## Activation

Explicitly invoking `pstack-mode` activates the coordinated workflow for the current conversation. Helpers remain usable individually. Installation does not activate the mode or change startup instructions.

The router chooses a playbook, invokes its workflow and principle dependencies, gathers evidence, and produces the task's report or draft pull request. Preserve explicit user entrypoints. Skills callable by other skills use the repository's model-invoked dependency convention, with scoped descriptions. Keep both hosts' invocation metadata consistent with these roles.

## Workflow and host execution

Preserve each workflow's purpose, completion criteria, and evidence requirements. Adapt worker counts, model selection, and continuous loops to the task and available budget. Remove fixed prescriptions such as ten live agents for every planned pull request while preserving the checks that establish correctness.

Translate Cursor tool calls into each host's available native APIs. Pass delegates their scope, repository guidance, and required rubrics explicitly. Keep concurrent writers isolated in separate worktrees. Use host-managed worktree operations when available and preserve ownership checks during cleanup.

Use available browser, CLI, and app control tools for runtime verification. Cursor's named agents, cloud environment, persistent custom mode, and `cursor-team-kit` skills are not installation prerequisites. Document capability-dependent branches and their required tools.

Retain the tested Bun PR watcher and orchestration cores and their tests. Adapt the plan validator's policy checks and the worktree auditor's host discovery. Resolve paths from installed resources, keep mutable runtime state separate from skill source, and report missing prerequisites for commands that require Bun or other external tools.

## Review models

Prefer cross-vendor review through the other vendor's CLI when it is available. Otherwise use an independent native reviewer and disclose that the cross-vendor pass did not run. Installing the suite does not require subscriptions to both vendors.

Check CLI availability, authentication, supported arguments, and execution permissions before a cross-vendor pass. Use supported review restrictions and pass the scope and rubric explicitly. Record which review actually ran; native independent reviewers do not establish cross-vendor diversity.

Model settings use role intent and available host models, without fixed Cursor model slugs. Keep personal configuration outside installed instruction copies.

## Autonomy and delivery

Proceed autonomously within agreed scope. Pause when scope or an approved interface changes, or repeated failures require a decision. Deliver draft pull requests by default and honor existing authorization for merges, deployments, external messages, and other further actions. Repository and host policies govern their respective operations.

Missing required evidence remains an explicit verification gap. Continue independent authorized work and preserve a validated subset when possible. An incomplete check is never a passing verdict. Learning-driven instruction changes are prepared for review and do not silently change the current run's approved rules.

## Webhook UI

Require an existing receiver with documented request, authentication, and success contracts. Build the UI and server-side proxy around that contract. Use localhost by default and expose the UI through Tailscale only when requested. A missing receiver is an integration prerequisite; this adaptation does not add a new agent execution service.

## History and learning

Use both hosts' conversation history for the explicitly scoped repository. Keep ordinary `reflect` focused on the current conversation. Prepare learning-driven changes in the source repository for review.

Keep `recall` read-only. Generate or update personal mode instructions in the agreed source repository. Keep private configuration and raw execution history separate from published skill instructions; durable project documents follow the invoking repository's tracking policy.

## Scheduled maintenance

Use the [repository maintenance guide](../skills/agents/maintain-skills/MAINTENANCE.md) and its versioned scheduled prompt for current scope, authority, budget, and inventory-change policy. Saved automation settings own the schedule and model. `/maintain-skills` discovers every local skill and provenance record; the suite mapping supplies Pstack identities and addition policy, including the reused `bro`, without limiting coverage.

Each review checks the whole upstream tree for new, removed, or renamed skills and relevant changes to playbooks, wrappers, scripts, documentation, and licenses. Reuse one fetched source snapshot across the suite. Prepare validated changes on an isolated update branch and update an existing maintenance pull request when appropriate.

Keep changes whose required verification is unavailable held for later review. Report the exact gaps and preserve their old reviewed-through baselines. Checkpoint enough progress to resume unfinished coverage without presenting it as a completed review.

## Completion criteria

Implementation is complete when:

1. The mapping accounts for all 54 initial upstream skills, with 53 new names and the reused `bro`, plus all required supporting resources and playbooks.
2. Names, invocation policies, metadata, dependencies, licenses, source records, and README listings satisfy repository conventions.
3. Skills CLI discovers the full suite, and isolated installation for both hosts includes the required resources and dependencies.
4. Repository formatting, skill discovery, whitespace, and secret checks pass. Changed helper scripts pass their relevant tests and type checks.
5. Targeted smoke tests in both hosts exercise routing and delegation, an evidence-based workflow, cross-vendor review and its disclosed fallback, scoped history access, and the changed helper integrations. Optional external integrations use fixtures where practical; actual service behavior remains explicitly unverified until exercised with the required service.
6. A maintenance dry run verifies suite inventory comparison, selective updates, baseline handling, and checkpoint behavior. The final instructions and schedule reflect the agreed authority boundaries.
7. After final design confirmation, a local maintenance automation is created or an existing matching automation is updated. Verify its saved schedule, model, and prompt and report tested host versions and any remaining runtime limitations. The initial weekly schedule was later replaced by the standalone automation's saved settings.

Broad operating-system compatibility is claimed only for environments actually exercised. Current local CLI availability establishes a macOS baseline.

## Initial name mapping

| Upstream skill                                       | Local skill                                                 |
| ---------------------------------------------------- | ----------------------------------------------------------- |
| `architect`                                          | `pstack-architect`                                          |
| `arena`                                              | `pstack-arena`                                              |
| `automate-me`                                        | `pstack-automate-me`                                        |
| `benchmark-checklist`                                | `pstack-benchmark-checklist`                                |
| `blast-radius`                                       | `pstack-blast-radius`                                       |
| `bro`                                                | `bro`                                                       |
| `correct`                                            | `pstack-correct`                                            |
| `create-verification-skill`                          | `pstack-create-verification-skill`                          |
| `figure-it-out`                                      | `pstack-figure-it-out`                                      |
| `how`                                                | `pstack-how`                                                |
| `in-your-own-words`                                  | `pstack-in-your-own-words`                                  |
| `interrogate`                                        | `pstack-interrogate`                                        |
| `ketchup`                                            | `pstack-ketchup`                                            |
| `maintain-verification-skill`                        | `pstack-maintain-verification-skill`                        |
| `make-bot-ui`                                        | `pstack-make-bot-ui`                                        |
| `no-comments`                                        | `pstack-no-comments`                                        |
| `poteto-help`                                        | `pstack-help`                                               |
| `poteto-mode`                                        | `pstack-mode`                                               |
| `recall`                                             | `pstack-recall`                                             |
| `reflect`                                            | `pstack-reflect`                                            |
| `setup-pstack`                                       | `pstack-setup`                                              |
| `sharpen`                                            | `pstack-sharpen`                                            |
| `show-me-your-work`                                  | `pstack-show-me-your-work`                                  |
| `swarm`                                              | `pstack-swarm`                                              |
| `tdd`                                                | `pstack-tdd`                                                |
| `teach`                                              | `pstack-teach`                                              |
| `technical-writing`                                  | `pstack-technical-writing`                                  |
| `typescript-best-practices`                          | `pstack-typescript-best-practices`                          |
| `unslop`                                             | `pstack-unslop`                                             |
| `why`                                                | `pstack-why`                                                |
| `principle-attack-the-premise`                       | `pstack-principle-attack-the-premise`                       |
| `principle-boundary-discipline`                      | `pstack-principle-boundary-discipline`                      |
| `principle-build-the-lever`                          | `pstack-principle-build-the-lever`                          |
| `principle-encode-lessons-in-structure`              | `pstack-principle-encode-lessons-in-structure`              |
| `principle-exhaust-the-design-space`                 | `pstack-principle-exhaust-the-design-space`                 |
| `principle-experience-first`                         | `pstack-principle-experience-first`                         |
| `principle-explain-the-number`                       | `pstack-principle-explain-the-number`                       |
| `principle-fix-root-causes`                          | `pstack-principle-fix-root-causes`                          |
| `principle-foundational-thinking`                    | `pstack-principle-foundational-thinking`                    |
| `principle-guard-the-context-window`                 | `pstack-principle-guard-the-context-window`                 |
| `principle-laziness-protocol`                        | `pstack-principle-laziness-protocol`                        |
| `principle-make-operations-idempotent`               | `pstack-principle-make-operations-idempotent`               |
| `principle-migrate-callers-then-delete-legacy-apis`  | `pstack-principle-migrate-callers-then-delete-legacy-apis`  |
| `principle-minimize-reader-load`                     | `pstack-principle-minimize-reader-load`                     |
| `principle-model-the-domain`                         | `pstack-principle-model-the-domain`                         |
| `principle-never-block-on-the-human`                 | `pstack-principle-never-block-on-the-human`                 |
| `principle-outcome-oriented-execution`               | `pstack-principle-outcome-oriented-execution`               |
| `principle-prove-it-works`                           | `pstack-principle-prove-it-works`                           |
| `principle-redesign-from-first-principles`           | `pstack-principle-redesign-from-first-principles`           |
| `principle-separate-before-serializing-shared-state` | `pstack-principle-separate-before-serializing-shared-state` |
| `principle-sequence-verifiable-units`                | `pstack-principle-sequence-verifiable-units`                |
| `principle-subtract-before-you-add`                  | `pstack-principle-subtract-before-you-add`                  |
| `principle-test-behavior-not-implementation`         | `pstack-principle-test-behavior-not-implementation`         |
| `principle-type-system-discipline`                   | `pstack-principle-type-system-discipline`                   |
