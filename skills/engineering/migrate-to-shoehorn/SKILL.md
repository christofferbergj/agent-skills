---
name: migrate-to-shoehorn
description: Migrate test files from `as` type assertions to @total-typescript/shoehorn. Use when user mentions shoehorn, wants to replace `as` in tests, or needs partial test data.
---

# Migrate test fixtures to Shoehorn

1. Inspect the requested test files, package manager, TypeScript setup, and fixture boundaries. Determine which assertions represent partial valid input and which deliberately construct invalid input. Complete when each targeted assertion has a concrete replacement purpose.
2. Verify the installed or selected `@total-typescript/shoehorn` API from its version-matched primary documentation. Use the repository's dependency workflow to install it as a development dependency only when needed. Complete when the package and relevant helper types are available in the test workspace.
3. Replace partial fixtures with `fromPartial`, intentionally malformed input with `fromAny`, or exact fixtures with `fromExact` when those APIs apply. These are fixture-construction helpers, not runtime validation or proof that incomplete data is valid. Keep them in tests and preserve the behavior the test observes. Complete when targeted assertions are replaced without weakening their meaningful checks.
4. Run relevant test and type checks and inspect the diff. Complete when the migration preserves behavioral coverage and production code has no new dependency on test-fixture helpers.
