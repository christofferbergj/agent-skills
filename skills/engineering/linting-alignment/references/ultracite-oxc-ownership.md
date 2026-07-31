# Ultracite and Oxc ownership

Use installed versions, effective configuration, and primary sources to answer the checks below. Treat upstream behavior as version-sensitive until the repository's installed source or current documentation proves it.

## Ultracite owns presets and orchestration

Ultracite supports multiple provider stacks. Detect the selected provider from the repository's entry config and command path instead of inferring it from the package name.

For an Oxlint provider, trace both repository-owned entry configs and the wrapper command:

- Identify which core, framework, formatter, and plugin presets each entry config imports or spreads.
- Verify whether the installed wrapper runs Oxfmt and Oxlint separately, then preserve those lanes in the baseline.
- Discover JavaScript-plugin preset membership from the installed export and verify that every selected package resolves from the declaring config.

Treat setup and initialization as generators. Inspect the installed generator source and review a disposable dry-run diff before allowing it to rewrite repository-owned entry configuration.

Sources:

- [Ultracite Oxlint provider](https://www.ultracite.ai/docs/provider/oxlint)
- [Ultracite configuration](https://www.ultracite.ai/docs/configuration)
- [Ultracite monorepos](https://www.ultracite.ai/docs/monorepos)
- [Ultracite command source](https://github.com/haydenbleasel/ultracite/tree/main/packages/cli/src/commands)
- [Ultracite Oxlint generator](https://github.com/haydenbleasel/ultracite/blob/main/packages/cli/src/linters/oxlint.ts)
- [Ultracite Oxfmt generator](https://github.com/haydenbleasel/ultracite/blob/main/packages/cli/src/linters/oxfmt.ts)

## Oxlint owns lint configuration

Resolve native plugins and JavaScript plugins as separate ownership edges. Inspect effective configuration to learn how an explicit native-plugin list affects defaults, and trace JavaScript-plugin packages, aliases, and collisions through the ESLint-compatible bridge.

Read the installed release's versioning policy before classifying an upgrade. Baseline every release that can change rules, defaults, JavaScript-plugin behavior, or type-aware behavior, regardless of semver distance.

Prove configuration discovery and inheritance with representative files before simplifying nested configuration. Determine:

- Which root or nested config each file resolves.
- Whether an explicit config path changes nested discovery.
- Whether child configs merge with parents or require an explicit extension.
- Which top-level properties `extends` carries and which, such as ignore propagation, the entry config must preserve explicitly.

Treat type-aware linting as a separate lane. Derive its companion package, TypeScript compatibility, program construction, root-only options, and monorepo build requirements from installed versions and current documentation.

Sources:

- [Oxlint configuration](https://oxc.rs/docs/guide/usage/linter/config.html)
- [Oxlint nested configs](https://oxc.rs/docs/guide/usage/linter/nested-config)
- [Oxlint built-in plugins](https://oxc.rs/docs/guide/usage/linter/plugins)
- [Oxlint JavaScript plugins](https://oxc.rs/docs/guide/usage/linter/js-plugins.html)
- [Oxlint type-aware linting](https://oxc.rs/docs/guide/usage/linter/type-aware)
- [Oxlint versioning](https://oxc.rs/docs/guide/usage/linter/versioning)

## Oxfmt owns formatting configuration

Treat Oxfmt as a separate executable with its own entry config, supported languages, ignore rules, discovery behavior, and output. Prove which config each representative file resolves and whether an explicit config path changes nested discovery.

Compare config-scoped ignore patterns, Git ignores, and Prettier-compatible ignore files at their actual scopes before replacing one mechanism with another. Verify representative generated, vendored, and workspace files.

Require a before-and-after formatting diff for every formatter update or option change. Keep mechanical reformatting separate when it would obscure policy or dependency changes.

Sources:

- [Oxfmt configuration](https://oxc.rs/docs/guide/usage/formatter/config.html)
- [Oxfmt ignore files](https://oxc.rs/docs/guide/usage/formatter/ignore-files)
- [Oxfmt language support](https://oxc.rs/docs/guide/usage/formatter/language-support)
- [Oxfmt unsupported features](https://oxc.rs/docs/guide/usage/formatter/unsupported-features)
