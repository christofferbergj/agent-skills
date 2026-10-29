# Login forms

Match the login page to one shape, then use its save options and sign-in code. Every shape fills the password through `agent-browser auth login`, which waits for visible, editable fields and fills them inside the browser.

## One page

The email and password fields and the submit button sit on one page.

- **Save** with `--username-selector`, `--password-selector` and `--submit-selector`.
- **Sign in** with the login template's code as it stands:

  ```bash
  agent-browser auth login "$profile" --url "$login_url" >/dev/null
  ```

  `--url` points the saved login at the current environment's login page, so one saved login serves every environment that shares the test users.

## Email first, then password

The email goes on one screen and the password on the next, with the email shown read-only. Hosted providers such as WorkOS AuthKit work this way. `auth login` fills only editable fields, so it cannot complete the form on its own.

- **Save** with `--password-selector` and `--submit-selector` only.
- **Sign in**: the script types the email itself, waits for the password step, then points the saved login's username step at the password field. Replace the template's sign-in code with:

  ```bash
  agent-browser fill '<email-selector>' "$username" >/dev/null
  agent-browser press Enter >/dev/null
  agent-browser wait --url '<password-step-url-glob>' >/dev/null

  # <provider> ignores a submit that arrives right after the password step loads.
  sleep 3

  # `auth login` fills only editable fields, so its username step targets the password field;
  # the password fill then replaces that value.
  agent-browser auth login "$profile" --no-navigate --username-selector '<password-selector>' >/dev/null

  if ! wait_until_signed_in 15 && [[ "$(agent-browser get url)" == <password-step-url-glob> ]]; then
    agent-browser click '<submit-selector>' >/dev/null
  fi
  ```

  When the password step keeps the same URL, wait for its field instead: `agent-browser wait '<password-selector>'`. Keep the `sleep` and the retry click only when the probe shows the provider dropping an early submit.

- **Hosted pages**: when the provider runs on its own host, open the app's URL and let it redirect, then check that the browser reached the provider before typing the email.

## Out of reach

`auth login` cannot finish a sign-in that needs more than a saved password: company single sign-on with multi-factor prompts, a passkey, a captcha or bot check, or a magic link sent by email. Report the shape to the user with the routes that remain: a password-only test login on a test environment, or a check through Computer Use in the user's own browser.
