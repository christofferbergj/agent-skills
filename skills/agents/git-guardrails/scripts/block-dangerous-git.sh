#!/usr/bin/env bash
set -euo pipefail
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Git guardrails require Python 3; hook input was not inspected.' >&2
  exit 2
fi
pstack_guardrail_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 "$pstack_guardrail_dir/block-dangerous-git.py"
