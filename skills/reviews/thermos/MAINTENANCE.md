# Maintaining the Thermos adaptations

Use manual, selective updates. Cursor owns the original Thermos plugin; this repository owns the adaptations installed for Codex and Claude Code. Compare upstream changes against the last reviewed commit, port the useful changes, and preserve the host-specific behavior. Installing directly from `cursor/plugins` would replace these same-named skills rather than merge them.

To have an agent perform this process, invoke `$maintain-skills` in Codex or `/maintain-skills` in Claude Code from this repository. It discovers these source records and preserves the suite-specific contracts below. The commands in this guide remain available for manual maintenance.

## Sources and ownership

| Local skill                          | Upstream path in `cursor/plugins`                            | Provenance and local differences                                   |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------------ |
| `thermo-nuclear-review`              | `thermos/skills/thermo-nuclear-review/SKILL.md`              | [Source record](../thermo-nuclear-review/UPSTREAM.md)              |
| `thermo-nuclear-code-quality-review` | `thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | [Source record](../thermo-nuclear-code-quality-review/UPSTREAM.md) |
| `thermos`                            | `thermos/skills/thermos/SKILL.md`                            | [Source record](./UPSTREAM.md)                                     |

Each source record owns its import commit, reviewed-through commit, review date, and decisions. Each installed skill includes Cursor's MIT license. Keep those notices with the derived content, including when redistributing it. If upstream changes its license, assess that change before importing new content; retain notices required by already incorporated content.

The upstream `thermos/agents/` wrappers, plugin README, and changelog can contain relevant workflow changes even when a rubric does not change. They are review inputs, not additional files to install. Local `agents/openai.yaml` files are Codex metadata, not Cursor's reviewer definitions.

## Review upstream changes

Start with a clean working tree or separately save unrelated work. Use a branch for the update. The commands below run from this repository's root and keep downloaded sources outside the working tree.

```bash
git status --short
upstream_dir="$(mktemp -d "${TMPDIR:-/tmp}/thermos-upstream.XXXXXX")"
git clone --filter=blob:none https://github.com/cursor/plugins.git "$upstream_dir"
candidate_commit="$(git -C "$upstream_dir" rev-parse origin/main)"
git -C "$upstream_dir" log -10 --oneline -- thermos
```

Keep using this checkout and `candidate_commit` throughout the update, even if upstream moves again. The clone is not shallow, so the recorded historical baseline can be compared.

For each of the three skills, choose its name and copy its **Reviewed through commit** from its `UPSTREAM.md` into `old_commit`. Replace the placeholder before running these commands:

```bash
skill_name=thermo-nuclear-review
old_commit=PASTE_REVIEWED_THROUGH_COMMIT

git -C "$upstream_dir" log --oneline "$old_commit..$candidate_commit" -- thermos
git -C "$upstream_dir" diff "$old_commit" "$candidate_commit" -- \
  "thermos/skills/$skill_name" \
  thermos/agents thermos/README.md thermos/CHANGELOG.md thermos/LICENSE
```

This is the upstream delta to assess. Repeat with `thermo-nuclear-code-quality-review` and `thermos`, using each skill's own baseline. If a path was renamed or removed, inspect the plugin-wide diff to locate its replacement before proceeding:

```bash
git -C "$upstream_dir" diff --find-renames --stat "$old_commit" "$candidate_commit" -- thermos
```

To distinguish existing local adaptations from new upstream changes, compare the old upstream skill with the local copy:

```bash
git -C "$upstream_dir" show \
  "$old_commit:thermos/skills/$skill_name/SKILL.md" \
  > "$upstream_dir/$skill_name-baseline.md"
git diff --no-index -- \
  "$upstream_dir/$skill_name-baseline.md" \
  "skills/reviews/$skill_name/SKILL.md"
```

`git diff --no-index` exits with status 1 when files differ; that is expected. A missing historical path needs investigation, not an empty replacement file.

## Integrate and record decisions

Port changes deliberately into the local files. Do not copy the latest plugin directory over the adaptations. For the two rubrics, most changes will be review criteria or examples. For `thermos`, translate workflow improvements into the existing Codex and Claude Code branches.

Preserve these local contracts unless intentionally changing the design:

- The two rubrics are model-invoked dependencies; `thermos` remains user-invoked. Keep frontmatter and Codex invocation metadata synchronized.
- Both reviewers receive the same scope and accessible evidence, plus their full rubric or its resolved path. Child skill discovery is not assumed.
- Use each host's available native tools. Cursor's named subagents and plugin installation are not prerequisites.
- Start both reviewers before waiting, collect both results, and disclose failed or sequential passes. Reviewer tasks do not create more subagents.
- Review requests return findings. They do not authorize edits or published comments. Deduplicate findings using evidence and calibrate severity independently of reviewer agreement.

For each reviewed skill, update its **Reviewed through commit** and date, and append a decision row with the candidate SHA and what was adopted, adapted, or deliberately skipped. Record a reason for skipped changes so the next maintainer does not accidentally reintroduce them. Preserve the original import commit and pinned import link. If the delta is empty, record that it was reviewed with no relevant changes. Do not advance a baseline for an incomplete review.

Review newly introduced supporting files for relevance and licensing before adding them. Keep required resources inside the owning skill directory so Skills CLI installs them with the skill. Update the README dependency list if the suite's required skills change.

## Validate and install

Run the repository checks from the root:

```bash
pnpm fmt:check
npx skills@latest add . --list
git diff --check
gitleaks dir . --redact --no-banner
```

Confirm discovery includes all three skills. Inspect invocation metadata against the contracts above. The bundled skill-creator validator may reject `disable-model-invocation` because its allowed-key list is older than this repository's convention; retain the explicit-only flag and check its boolean value and matching Codex policy directly.

Install the local versions together for validation and use:

```bash
npx skills@latest add . \
  --skill thermos thermo-nuclear-review thermo-nuclear-code-quality-review \
  --global --agent codex claude-code --yes
npx skills@latest list --global --agent codex claude-code
```

This copies the current checkout into `~/.agents/skills` for Codex and links Claude Code's entries in `~/.claude/skills` to those copies. It is not a live link back to this repository. Re-run the install after subsequent edits, including maintenance-document changes you want included in installed copies.

When instructions affecting review behavior or delegation change, smoke-test in both hosts on a small isolated change with a known defect and explicit scope. Invoke `$thermos` in Codex and `/thermos` in Claude Code. Inspect the tool activity as well as the final report: two distinct reviewers should start before either is awaited, each should receive its rubric, and synthesis should wait for both. Check that the known defect is reported, duplicates are combined, and no files or external comments are changed. Test the sequential fallback when that branch changes. Record host versions and any limitations; installation alone does not establish runtime compatibility.

The initial 2026-10-12 smoke test exercised Codex desktop's collaboration tools and Claude Code 2.1.287. Both launched and collected two independent reviewers on an isolated authorization-regression fixture. This does not guarantee every host version or configuration has delegation enabled.

## Publish and refresh

Commit the reviewed source changes, provenance records, and retained licenses together. Publish only when requested, following the repository's publication policy.

After publishing, you can switch from the local checkout to your GitHub source with:

```bash
npx skills@latest add christofferbergj/agent-skills \
  --skill thermos thermo-nuclear-review thermo-nuclear-code-quality-review \
  --global --agent codex claude-code --yes
```

For subsequent GitHub-backed refreshes:

```bash
npx skills@latest update thermos thermo-nuclear-review thermo-nuclear-code-quality-review \
  --global --yes
```

That refreshes your published versions. It does not check or merge Cursor's originals. Continue the manual review process here whenever you want to incorporate upstream changes. If an update needs reverting, restore the previous local version through Git and reinstall all three skills from that checkout.
