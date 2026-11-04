# Screenshots

Read this when Evidence holds screenshots or video. The [PR skill](../SKILL.md) says when they are due.

## Lay out

Show each view as a bold label, at most one sentence on what changed, and a `Before | After` table whose one row holds the two screenshots. Open the screenshots with one line naming their source, viewport, and baseline, such as "Mocked checkout at 1280px. Before is `main`, after is this branch." Show states the same way, with each state's name as its column heading, as in `Empty | Not looked up`: two screenshots to a row, or three for phone screenshots, with each later row's labels in the cell above it. Put each video on a line of its own, outside any table, since `gh` turns only a standalone video reference into a player.

## Capture and name

The project's verification skill says how to capture the base branch. Name a pair `<view>-before.png` and `<view>-after.png`, a view that is new `<view>-after.png`, and a state the base branch never reaches `<view>--<state>.png`, such as `contact-step--empty.png`, all in kebab case.

## Publish

1. Keep captures in one temporary directory outside the repository, with the body file beside them, and reference each by its relative path, as in `![Checkout before](./checkout-before.png)`.
2. From the PR's checkout, run `gh pr create` or `gh pr edit` (GitHub CLI 2.99 or newer) with `--body-file "$dir/body.md"` and one `--attach "$dir/<capture>"` per image or video, building every path from the same absolute `$dir`. `gh` matches a reference by its absolute path without resolving symlinks, so a differently spelled path is appended at the end instead of replacing the reference. It uploads each file and rewrites the matching reference in what it sends, leaving the file as it was.
3. Save the published body over the file with `gh pr view <number> --json body -q .body > "$dir/body.md"`, and make later edits from that file.
4. Check the rendered body with `gh api repos/<owner>/<repo>/pulls/<number> -H 'Accept: application/vnd.github.html+json' -q .body_html`. Every `<img>` `src` must start with `https://private-user-images.githubusercontent.com/`, and each sits where its reference was. A `./` source means its upload failed, since `gh` still updates the PR when some uploads fail. Asset URLs answer 404 without a GitHub login, so a plain `curl` can't check them.

When `gh` can't upload, such as on GitHub Enterprise Server or a base repository you can't write to, replace the captures with a `**Not attached:**` line that says why and describes what each capture showed.
