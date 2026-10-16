# Initial Matt Pocock source audit

Historical investigation on 2026-10-15 against [mattpocock/skills at `49dd158d1076134a641b33efb035946536778336`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336), version 1.3.1. Read all 38 skill bodies, relevant resources, invocation and installation guidance, scope policy, and license. The findings below describe that pinned upstream, not defects asserted against the current adaptations. Current composition and source ownership live in the [library architecture](../architecture.md); import choices live in the catalog and skill-local source records.

## Source findings

The in-progress README omitted `chief-of-staff`, demonstrating why discovery must walk actual `SKILL.md` files. Experimental skills were public beta and could disappear; misc skills were frozen. There was no separate personal-skills bucket. [Source layout](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/CLAUDE.md), [omitted skill](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/in-progress/chief-of-staff/SKILL.md), [frozen policy](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/.out-of-scope/frozen-misc-skills.md).

The installed `prototype` belonged to Emil Kowalski, with `PICKER.md` rather than Matt's `LOGIC.md` and `UI.md`. This supported the local `design-prototype` rename. Upstream had renamed the `CONTEXT.md` convention to glossary artifacts in [commit d80fa0f](https://github.com/mattpocock/skills/commit/d80fa0f4ebe0c5714af0adf8670336065233ecc6); setup's `docs/agents/domain.md` was consumer guidance rather than a separate domain model.

The original host assumptions, execution authority, review freshness, tracker operations, HTML reports, pre-commit tools, and deep-module fixtures required local adaptation. Those decisions are retained with the affected skills in `UPSTREAM.md`, rather than as a second implementation plan here. The upstream maintainer's [link script](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/scripts/link-skills.sh) removed existing real skill directories before symlinking; it was not adopted as an installer.

## Original hook fixtures

Ran fake command strings through the original Claude hook; no Git mutation ran. `git push origin main` exited 2. It exited 0 for `git -C /tmp/fixture push origin main`, `git --no-pager push origin main`, `git clean -df`, and `git branch --delete --force example`. It also exited 0 when `jq` was absent and falsely blocked `echo "git push is denied"`. These observations matched the upstream frozen-skill limitations. The local adapters and their separate validation are documented by `/git-guardrails`. [Original hook](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/misc/git-guardrails-claude-code/scripts/block-dangerous-git.sh).

## Original dotenv fixtures

The pinned wizard template's shell-style apostrophe encoding truncated dotenv values. With fake input `it's literal`, its escaped output was read as `it` by Node v24.22.0 `process.loadEnvFile`. Its grep-based reader and upsert also mishandled multiline records. [Pinned template](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/wizard/template.sh).

A candidate encoding passed 13 fake-value round trips through Node v24.22.0 and dotenv 16.6.1. Cases covered empty values, whitespace, both quote types, trailing backslashes, dollar syntax, literal newlines, `#`, backticks, and a following sentinel variable. Unsupported quote mixtures, carriage returns, and NUL required rejection rather than value alteration. The local `/wizard` helper and tests own the resulting implementation; this experiment does not establish compatibility with other parsers or shell `source`. [Audited dotenv parser](https://github.com/motdotla/dotenv/blob/v16.6.1/lib/main.js).
