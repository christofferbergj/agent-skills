---
name: setup-agent-sign-in
description: Set up agent-browser sign-in for a project's test users, with each password kept in agent-browser's local vault. Use when a project has no documented agent login, when adding a test user or role, or when a saved login stops working.
---

# Set up agent sign-in

Agents sign in as test users through agent-browser's local vault. The user saves each login once per machine from their own terminal, so the password moves from their clipboard into the vault and stays out of the conversation, command arguments and script output. The project's login script signs a session in with `agent-browser auth login`, and its sign-in doc tells agents which role covers which case.

Name each saved login `<project>-<role>`: a short project slug and the app's own role name in kebab case, such as `fysioscout-clinic-admin`.

## Keep the password in the vault

These rules hold in every step, for the scripts and for you:

- The password reaches agent-browser only through `--password-stdin`, in a command the user runs in their own terminal. Ask for emails, URLs and roles in chat; the user types the password nowhere else.
- Read a saved login with `agent-browser auth show`, which prints its username and no password. Reach the vault only through `agent-browser auth` commands, leaving the files under `~/.agent-browser/` unread.
- Scripts send the output of `auth save` and `auth login` to `/dev/null` and print their own one-line result.
- On a login request, read only the status that `network requests` lists. Its detail view, a HAR recording, and an `eval` or `get value` on the password field expose the password, so sign-in uses none of them.
- A window handed to Computer Use gets a fresh profile with Chrome's password manager off, so no save-password prompt can show the password.

These rules keep the password out of transcripts and logs. The vault's key is readable by the user's own account, so tell the user they protect against accidents, not against an agent that sets out to decrypt the vault.

## Steps

1. **Find the setup.** Search the project's `AGENTS.md` and agent docs for a sign-in section, look for `scripts/*login*`, and run `agent-browser auth list`. When a setup exists, follow its doc: adding a role changes its role list and doc in step 4, and a login the environment rejects needs only a new save in step 5. Complete when you know whether a setup exists and which of its files change.
2. **Collect the facts.** For each role: its profile name, email, and the case it covers, such as which data or features the user has. For each environment: its login page, the API it reaches, whether the test users exist there, and whether writes are safe, such as a sandbox anyone may edit or shared team data to restore after a write. Note whether the users share one password. Take these from the repository, the client's test-user list, or the user. Complete when every role has a name, email and case, and every environment has a login page and a write rule.
3. **Probe the form.** Open the login page in its own agent-browser session and take a snapshot. Record the email, password and submit selectors, the form's shape from [login forms](references/FORMS.md), what a signed-in page looks like, and how a failed sign-in shows, such as an error URL or a `4xx` on the login request. Complete when the shape, the three selectors, the signed-in test and the failure signal are known, or the form is out of reach as login forms describes, in which case report that to the user and stop.
4. **Write the files.** Fill each template's `<placeholder>` values with the facts from steps 2 and 3:
   - `scripts/agent-browser-login.sh` from [the login template](references/agent-browser-login.sh), with the sign-in code for the form's shape and the failure signal from step 3.
   - `scripts/agent-browser-save-test-users.sh` from [the save template](references/agent-browser-save-test-users.sh), when the users share one password. Otherwise the sign-in doc gives one save command per role.
   - `scripts/computer-use-login.sh` from [the Computer Use template](references/computer-use-login.sh), when the project has a web UI that gets visual passes.
   - The sign-in doc from [the doc template](references/agent-sign-in.md), at `docs/agents/agent-sign-in.md` or as a section of the project's existing doc on manual testing.
   - One line in the project's `AGENTS.md`: read the sign-in doc to sign agent-browser or Computer Use in as a test user, or when a saved login is missing.

   Make the scripts executable. Complete when the only `<…>` left are the `<role>` and URL arguments in usage lines and examples, each script passes `bash -n`, and the doc lists every role from step 2.

5. **Hand over the save.** Give the user the exact command to run in their own terminal, with the real profile names, emails and selectors: copy the password, then pipe `pbpaste` into the save script or `agent-browser auth save … --password-stdin`. This is the one step only the user can do. Complete when `agent-browser auth list` shows every new profile.
6. **Prove sign-in.** For each role, in its own session from `agent-browser session id --scope worktree --prefix <project>-<role>`, run the login script against every documented environment and expect `Signed in as <project>-<role>`. Run it once for an unsaved role and expect the exit that names the missing login. When you wrote the Computer Use script, open one window with it and close it with `--close`. Close every session you opened. Complete when every role signs in on every documented environment, the unsaved role fails with its message, and no command output showed a password.

Report the roles and environments that signed in, the files written, and each failure with its cause.
