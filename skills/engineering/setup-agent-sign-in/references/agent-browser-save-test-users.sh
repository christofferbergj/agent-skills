#!/bin/bash
#
# Saves the test users below in agent-browser's local vault as <project>-<role>.
# They share one password, read once from stdin or a hidden prompt, so it never
# appears in arguments or output.
# <sign-in-doc> owns the setup.
#
# Usage: pbpaste | scripts/agent-browser-save-test-users.sh [role...]
#        scripts/agent-browser-save-test-users.sh [role...]   (prompts)
#

set -euo pipefail

# auth login replaces this URL with the target environment's login page.
login_url='<login-page-url>'

users='
<role>  <email>  <case-it-covers>
'

if [ -t 0 ]; then
  read -rsp 'Shared test-user password: ' password
  echo
else
  IFS= read -r password || true
fi
if [ -z "$password" ]; then
  echo 'No password on stdin. Copy the shared test-user password, then run: pbpaste | scripts/agent-browser-save-test-users.sh' >&2
  exit 1
fi

saved=0
while read -r role email _; do
  [ -n "$role" ] || continue
  if [ "$#" -gt 0 ] && [[ " $* " != *" $role "* ]]; then
    continue
  fi
  printf '%s' "$password" | agent-browser auth save "<project>-$role" --url "$login_url" \
    --username "$email" --password-stdin \
    --username-selector '<email-selector>' --password-selector '<password-selector>' \
    --submit-selector '<submit-selector>' >/dev/null
  echo "Saved <project>-$role ($email)."
  saved=$((saved + 1))
done <<<"$users"

if [ "$saved" -eq 0 ]; then
  echo "No role matched: $*. Roles are listed in $0." >&2
  exit 1
fi
