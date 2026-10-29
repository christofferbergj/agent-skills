#!/bin/bash
#
# Opens a visible agent-browser window signed in to <app> as a test user, for Computer Use to
# drive. Computer Use cannot read agent-browser's vault, so this script signs the window in with
# scripts/agent-browser-login.sh and hands it over. The password never reaches the screen.
# <sign-in-doc> owns when to use it.
#
# Usage: scripts/computer-use-login.sh <role> [app-url]
#        scripts/computer-use-login.sh --close <role>
#

set -euo pipefail

usage=$'Usage: scripts/computer-use-login.sh <role> [app-url]\n       scripts/computer-use-login.sh --close <role>'
close=false
if [[ ${1:-} == --close ]]; then
  close=true
  shift
fi
role="${1:?$usage}"
app_url="${2:-}"
repo=$(cd "$(dirname "$0")/.." && pwd)

# One window per role and worktree, so rerunning the script finds the window it opened.
session=$(cd "$repo" && agent-browser session id --scope worktree --prefix "<project>-$role-visual")
# Chrome's own password manager would offer to save the password in a bubble that can reveal it,
# so the window gets a profile with the password manager turned off.
profile="${TMPDIR:-/tmp}/$session-profile"

is_open() {
  agent-browser session list --json | node -e '
    const { data } = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
    process.exit(data.sessions.includes(process.argv[1]) ? 0 : 1);
  ' "$session"
}

if $close; then
  if is_open; then
    agent-browser --session "$session" close >/dev/null
  fi
  # The session leaves the list a moment after close returns; a rerun before then would reuse it.
  deadline=$((SECONDS + 10))
  while is_open && ((SECONDS < deadline)); do sleep 0.5; done
  rm -rf "$profile"
  echo "Closed $session."
  exit 0
fi

# The profile and the visible window apply only when the session launches; an open session keeps its own.
if ! is_open; then
  rm -rf "$profile"
  mkdir -p "$profile/Default"
  printf '%s\n' '{"credentials_enable_service": false}' >"$profile/Default/Preferences"
fi

AGENT_BROWSER_SESSION="$session" AGENT_BROWSER_HEADED=1 AGENT_BROWSER_PROFILE="$profile" \
  "$repo/scripts/agent-browser-login.sh" "$role" ${app_url:+"$app_url"}

echo "Drive the Google Chrome for Testing window titled \"$(agent-browser --session "$session" get title)\"."
echo "Session: $session"
echo "Close it when done: scripts/computer-use-login.sh --close $role"
