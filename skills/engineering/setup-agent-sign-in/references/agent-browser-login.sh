#!/bin/bash
#
# Signs the current agent-browser session in to <app> as a test user, using the
# login saved in agent-browser's local vault. The password stays in the vault:
# it never appears in arguments or output.
# <sign-in-doc> owns the roles and setup.
#
# Usage: scripts/agent-browser-login.sh <role> [app-url]
#

set -euo pipefail

usage='Usage: scripts/agent-browser-login.sh <role> [app-url]'
role="${1:?$usage}"
app_url="${2:-<default-app-url>}"
profile="<project>-$role"
app_origin=$(printf '%s' "$app_url" | sed -E 's#^(https?://[^/]+).*#\1#')
login_url="$app_origin<login-path>"

# A signed-in page is on the app's origin and outside its sign-in and sign-out routes.
is_signed_in() {
  local url path
  url=$(agent-browser get url)
  [[ $url == "$app_origin"/* ]] || return 1
  path=${url#"$app_origin"}
  [[ $path != <login-path>* && $path != <logout-path>* ]]
}

# Prints the status of the newest login request, or nothing while it is pending.
login_status() {
  agent-browser network requests --filter <login-request-path> | awk '$2 == "POST" { status = $NF } END { print status }'
}

# Waits up to $1 seconds for a signed-in page, giving up early once the sign-in fails.
wait_until_signed_in() {
  local deadline=$((SECONDS + $1))
  while ((SECONDS < deadline)); do
    is_signed_in && return 0
    [[ $(login_status) == [45]* ]] && return 1
    sleep 1
  done
  return 1
}

username=$(agent-browser auth show "$profile" 2>/dev/null | awk '/^Username:/ { print $2 }' || true)
if [ -z "$username" ]; then
  echo "No saved login '$profile'. Ask the user to save it; see <sign-in-doc>." >&2
  exit 1
fi

# The login page sends an already signed-in session on into the app.
agent-browser open "$login_url" >/dev/null
agent-browser wait --fn "Boolean(document.querySelector('<email-selector>')) || !location.pathname.startsWith('<login-path>')" >/dev/null
if is_signed_in; then
  echo "Session is already signed in at $(agent-browser get url); use a separate session per role."
  exit 0
fi

agent-browser network requests --clear >/dev/null
agent-browser auth login "$profile" --url "$login_url" >/dev/null

if wait_until_signed_in 20; then
  echo "Signed in as $profile at $(agent-browser get url)."
  exit 0
fi

status=$(login_status)
case $status in
  401) echo "The login request for $profile ($username) returned 401: this environment rejects the saved email or password." >&2 ;;
  '') echo "Sign-in as $profile sent no answered login request; the browser is at $(agent-browser get url)." >&2 ;;
  *) echo "Sign-in as $profile did not reach a signed-in page (login request status $status); the browser is at $(agent-browser get url)." >&2 ;;
esac
exit 1
