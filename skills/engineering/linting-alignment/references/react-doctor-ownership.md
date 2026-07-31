# React Doctor ownership

Use installed versions, effective configuration, and primary sources to compare React Doctor's analyzer and plugin lanes. Treat upstream behavior as version-sensitive until the repository's installed source or current documentation proves it.

## Separate analyzer and plugin coverage

Trace the standalone CLI and lint plugin as distinct execution consumers. Determine which lint diagnostics each lane runs and which project-level analysis—such as dead-code, dependency, or security checks—exists only in the CLI.

Discover whether the repository uses the CLI, the plugin, both, or neither. Compare configured severities, ignores, scopes, project selection, and CI commands before deciding that either lane duplicates the other.

Verify which existing ESLint or Oxlint config formats the installed CLI adopts. Compare effective rules explicitly when the repository uses TypeScript entry configs, generated configs, or another format not covered by the current adoption contract.

Sources:

- [React Doctor overview](https://www.react.doctor/docs)
- [React Doctor config files](https://www.react.doctor/docs/configuration/config-files)
- [React Doctor ESLint and Oxlint plugins](https://www.react.doctor/docs/configuration/eslint-and-oxlint-plugins)
- [React Doctor CLI reference](https://www.react.doctor/docs/reference/cli-reference)
