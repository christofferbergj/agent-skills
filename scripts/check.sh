#!/usr/bin/env bash
#
# Runs every repository gate: formatting, skill discovery, catalog and
# provenance validation, every Python, Node, and Bun test suite, whitespace,
# and secrets. Needs Python 3, Node 22.18 or newer, Bun, and gitleaks.
# Test suites are discovered from tracked files, so a new suite runs without
# editing this script.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

step() { printf '\n== %s\n' "$1"; }

# Runs a command quietly and prints its output only when it fails.
quiet() {
  local output
  output=$("$@" 2>&1) || { printf '%s\n' "$output"; return 1; }
}

step format
quiet pnpm -s fmt:check

step "skill discovery"
quiet npx -y skills@latest add . --list

step "catalog and provenance"
quiet python3 skills/agents/maintain-skills/scripts/catalog.py --root . validate

for suite in $(git ls-files 'skills/*/tests/test_*.py' | xargs -n1 dirname | sort -u); do
  step "python: $suite"
  python3 -m unittest discover -s "$suite"
done

node_tests=$(git ls-files 'skills/*.test.ts' ':!:skills/agents/pstack-mode/**')
step "node: $(echo "$node_tests" | wc -l | tr -d ' ') test files"
node --test $node_tests

step "pstack-mode: bun test and typecheck"
runtime=$(bun skills/agents/pstack-mode/scripts/bootstrap.ts --print-runtime | tail -1)
(cd "$runtime" && bun test && bun run typecheck)

step whitespace
# Diffing against the empty tree checks every tracked file as it is on disk.
git diff --check "$(git hash-object -t tree /dev/null)"

step secrets
gitleaks dir . --redact --no-banner

printf '\nAll checks passed.\n'
