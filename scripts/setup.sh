#!/usr/bin/env bash
#
# Prepares a checkout for development: installs the tools pinned in mise.toml
# and the pnpm dependencies, whose prepare script installs the Husky pre-commit
# hook. Rerunning it is safe.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

mise trust mise.toml
mise install
mise exec -- pnpm install --frozen-lockfile

printf '\nSetup complete.\n'
