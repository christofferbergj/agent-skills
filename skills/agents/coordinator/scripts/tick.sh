#!/bin/sh
# Ticks every coordinator project on this machine: the timer in references/tick.md runs it
# every 10 minutes. `project.py <folder> tick --send` skips a project whose Heartbeat isn't
# `tick`, so this only touches what a coordinator turned on. One project's failure leaves the
# rest to run. Usage: tick.sh [coordinator folder, default ~/.local/state/coordinator]
root="${1:-$HOME/.local/state/coordinator}"
PATH="$PATH:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin"  # a timer starts with a bare PATH
export PATH
[ -d "$root" ] || exit 0  # no coordinator has run on this machine yet
here="$(cd "$(dirname "$0")" && pwd)"
for dir in "$root"/*/; do
  [ -f "$dir/project.md" ] && python3 "$here/project.py" "$dir" tick --send
done
touch "$root/.tick"
