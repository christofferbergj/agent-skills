# Combined library validation

Validated on macOS on 2026-10-15 against Matt Pocock's skills 1.3.1 at `49dd158d1076134a641b33efb035946536778336` and Pstack 0.15.25 at `e5136d82418d2db3165ea1050d17577cd618cc05`.

The exercised tools were Codex CLI 0.162.1, Claude Code 2.1.292, Bun 1.4.3, Node 24.22.0, Python 3.9.6, Git 2.54.0, and GitHub CLI 2.102.0. Other operating systems were not exercised. This record extends the [initial Pstack validation](../pstack-mode/VALIDATION.md).

## Packaging and source coverage

- Skills CLI discovers all 94 repository skills. Isolated installations for Codex and Claude Code contain the full library and matching supporting files. Global installations remain untouched.
- The catalog validates 86 mapped adaptations across two upstreams: 54 Pstack entries, including `bro`, and 32 Matt entries. All 32 Matt skills retain the exact upstream MIT notice, pinned import and reviewed revisions, and local adaptation decisions. Their 18 explicit entrypoints and 14 callable skills have consistent invocation metadata in both hosts.
- A full YAML parse validates Matt frontmatter and Codex policies. The bundled creator validator passes its supported field projection and scaffold checks; its minimal schema predates the repository's required host invocation fields, which are checked separately without altering source.
- Real comparisons against both pinned source trees report 54 and 32 unchanged tracked sources, no unmapped additions or removals, and the six intended Matt exclusions. The new comparison fixtures cover future additions, personal/beta categories, removals, moves, shared/license changes, unavailable baselines, and incomplete integration checkpoints.
- Repository formatting, Skills CLI discovery, the combined catalog validator, whitespace, and secret checks pass.

## Executable checks

After the Thermos repairs, all 134 automated tests pass: 76 Bun cases, 37 Pstack Python cases, ten combined-catalog cases, six Git-detector cases, and five wizard dotenv cases. The duplicated Pstack-only maintenance engine and its four tests were removed in favor of the combined owner. TypeScript checks pass for the Bun tools. Shell syntax checks pass for the wizard and hook launcher, and Node parses the dependency-cruiser template.

The Git detector denies ordinary literal destructive Git forms, including global options, combined force flags, shell separators and nested shell commands; it allows read-only commands and quoted mentions. Both documented host event shapes receive a denial, malformed input fails clearly, and command arguments stay out of denial messages. These are event fixtures, not live hook activation tests.

The wizard helper preserves fake literal values, whole multiline records, file permissions, and existing symlinks; repeated upserts remain idempotent. Unsupported values or quoting fail before writes. Fake values round-trip through Node's actual dotenv loader, and the Bash template uses the helper without printing saved values. The source audit also verified the candidate encoding against dotenv 16.6.1.

An isolated dependency-cruiser 18.6.0 fixture with compatible TypeScript 6 and Node 24.22.0 observes pass, failure on `tests-through-entrypoints`, then pass after removal of the violation, scanning three source modules and two dependencies. An initial incompatible compiler produced zero scanned modules with a successful exit; setup instructions now reject that result and require compiler compatibility.

Run the new focused checks from the source root:

```bash
python3 -m unittest discover -s skills/agents/maintain-skills/scripts/tests -v
python3 -m unittest discover -s skills/agents/git-guardrails/scripts/tests -v
python3 -m unittest discover -s skills/agents/wizard/tests -v
python3 skills/agents/maintain-skills/scripts/catalog.py --root . validate
```

The initial Pstack record gives the runtime and Python test commands; its removed Pstack-only `suite.py` command is historical. Use the combined catalog command above for current validation.

## Workflow exercises

| Exercise                                                 | Observed behavior                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Installed Pstack architect in an isolated legacy project | Resolved the configured vocabulary in `context.md` and state model in `domain.md`, implemented an accepted expiration event through the existing public seam, and updated both files without adding a duplicate glossary or an unnecessary ADR. An independent alternative and native blind judge ran. The expiration test failed before implementation; five final tests pass, including all nine terminal-state/event combinations.       |
| Installed Matt implement in Claude Code                  | Explicitly loaded installed instructions with customizations disabled, consumed an accepted local spec, reused its approved public seam, and implemented unavailable reserved funds. Updated the configured `GLOSSARY.md`. Two built-in `Agent` reviewers covered Standards and Spec against the same final file hashes; six tests pass. External reviewer CLIs were excluded by the fixture's grant and the workflow disclosed that limit. |
| Review freshness correction                              | The first Claude exercise disclosed a test edit after review. The owner instructions now refresh affected coverage after artifact changes. A fresh exercise delivered unchanged reviewed hashes and recorded minor, non-blocking observations without claiming they were fixed.                                                                                                                                                             |
| Combined maintenance                                     | Both immutable-source inventories compare successfully. Fixture checkpoints require both candidate SHAs, preserve pending coverage and integration status, and never write source baselines or claim a completed review.                                                                                                                                                                                                                    |
| Wayfinder charting after the Thermos repair              | An isolated project supplied two independent research tickets and local provider documentation. The coordinator dispatched two direct investigators, collected both cited notes, and closed both tickets. Investigators did not create nested coordinators. The map, ticket files, notes, source hashes, and unchanged glossary were inspected.                                                                                             |

The coordinator inspected actual diffs, reran both projects' tests, and checked whitespace. These are selected behavioral exercises, not evaluations of every expensive workflow. Private model transcripts and mutable test projects remain outside installed skill source.

The [Thermos review record](../../../docs/reviews/2026-10-15-combined-skills-thermos.md) records the independent correctness and maintainability passes, nine verified findings, and their repairs.

## Scheduled upkeep and limits

The existing `pstack-upstream-maintenance` heartbeat was updated in place as **Combined skill maintenance**. It remains active Monday at 09:00 in the host's Europe/Copenhagen timezone. The saved prompt names both repositories, the combined catalog and guide, additions/exclusions, shared-owner consumers, a 60-minute budget with wrap-up at minute 50, incomplete checkpoints, and one draft update PR. The existing action grant and quiet unchanged-run behavior remain intact. Until the initial combined library reaches the default branch, it reports that prerequisite instead of recreating the port.

No validation merged a PR, refreshed global skills, changed live host hooks, published tracker items, or configured a production service. Hook adapters use official host schemas; native Codex trust and actual activation must be verified when the setup skill is invoked. Git parsing remains a bounded accidental-operation guardrail. The orchestration frontier reports the optional Origin backend unavailable until its immutable PR-head schema is verified; it never substitutes a local branch SHA as forge proof. GitLab server/tier behavior, external tracker writes, every prototype UI branch, and the initial Pstack record's optional service integrations remain unexercised. Skills declare their prerequisites and preserve explicit gaps when these capabilities are unavailable.
