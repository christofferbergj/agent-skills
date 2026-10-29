# Agent sign-in

Agents sign in to <app> as test users through agent-browser's local vault. The user saves the logins once per machine, so the password stays out of the conversation, command arguments and output. Claude and Codex share the vault on the same machine.

## Test environment

- **Where**: <each environment the test users exist in, its URL, and the API it calls>.
- **Data**: <whether writes are safe: a sandbox anyone may edit, or shared data to restore after a write>. Before a write, confirm the request goes to <test-api-origin>.

## Roles

Each role is saved as `<project>-<role>`; `agent-browser auth list` shows which this machine has.

| Role     | Email     | Covers           |
| -------- | --------- | ---------------- |
| `<role>` | `<email>` | <case-it-covers> |

## Sign in

Give each role its own agent-browser session, because the script accepts an already signed-in session as it stands. Pass the role and, optionally, the app URL: <default-app-url> by default, a branch preview, or a local run.

```bash
export AGENT_BROWSER_SESSION="$(agent-browser session id --scope worktree --prefix <project>-<role>)"
scripts/agent-browser-login.sh <role> <app-url>
```

Sign-in is done when the script prints `Signed in as <project>-<role>`. On failure it exits non-zero and names the cause.

## Computer Use

Computer Use cannot read the vault, so it drives a window the script signed in. To check as a test user through Computer Use, open that window with the same role and URL arguments:

```bash
scripts/computer-use-login.sh <role> <app-url>
```

It prints the title of a signed-in `Google Chrome for Testing` window and its agent-browser session; rerunning it for the same role reuses that window. The window's profile turns Chrome's password manager off, so no save-password prompt can show the password. If the window returns to the login page, rerun the script instead of typing credentials.

- **Narrow widths**: agent-browser holds the page at the window's opening width, so resizing the window leaves the layout unchanged. Set the width with `agent-browser --session <session> set viewport 390 844`, and restore it with `set viewport 1440 900`.
- **Close**: `scripts/computer-use-login.sh --close <role>` closes the window and deletes its profile.

## Save the logins

Ask the user to copy the password and run this from their own terminal, so it moves from their clipboard straight into the vault:

```bash
<save-command>
```

Saving again replaces a login, which is also the fix when the environment rejects a saved password.
