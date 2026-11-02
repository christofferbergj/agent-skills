import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import { checkEvidence, uiFiles } from "./check-evidence.ts";

const SCRIPT = path.join(import.meta.dirname, "check-evidence.ts");
const fixtures = new Set<string>();

afterEach(async () => {
  await Promise.all([...fixtures].map((fixture) => rm(fixture, { recursive: true, force: true })));
  fixtures.clear();
});

function git(cwd: string, args: string[]) {
  return execFileSync("git", args, { cwd, encoding: "utf-8" }).trim();
}

const REVIEWED = "**Reviewed:** review-loop Clean at abc1234, Codex 1 · Claude 2";
const body = (evidence: string) =>
  `## Summary\n\nA change.\n\n## Evidence\n\n${evidence}\n\n## Merge Danger\n\n**Door:** two-way\n`;

test("counts UI source as provable by screenshot, and leaves out tests, stories, and mocks", () => {
  assert.deepEqual(
    uiFiles([
      "src/app/page.tsx",
      "src/styles/site.css",
      "public/index.html",
      "src/lib/date.ts",
      "src/app/page.test.tsx",
      "src/Button.stories.tsx",
      "src/__mocks__/Card.tsx",
      "e2e/checkout.tsx",
    ]),
    ["src/app/page.tsx", "src/styles/site.css", "public/index.html"],
  );
});

test("a UI diff needs a screenshot or a Not verified line, and every diff needs a review status", () => {
  const ui = ["src/app/page.tsx", "src/lib/date.ts"];

  assert.deepEqual(checkEvidence(body(REVIEWED), ui), [
    "The diff changes UI (src/app/page.tsx), and Evidence has neither a screenshot nor a `**Not verified on <surface>:**` line.",
  ]);
  assert.deepEqual(
    checkEvidence(body(`${REVIEWED}\n\n![Page after](https://x/p.png?raw=true)`), ui),
    [],
  );
  assert.deepEqual(
    checkEvidence(
      body(`${REVIEWED}\n\n**Not verified on the dashboard:** needs a signed-in account.`),
      ui,
    ),
    [],
  );
  assert.deepEqual(checkEvidence(body("**Not reviewed:** docs-only change."), ["README.md"]), []);
  assert.deepEqual(
    checkEvidence(body("- **Before:** fails\n  **After:** passes"), ["src/lib/date.ts"]),
    ["Evidence doesn't open with a `**Reviewed:**` or `**Not reviewed:**` line."],
  );
});

test("accepts an inline image, an <img> tag, or a surface with a colon, read across line endings", () => {
  const page = ["src/app/page.tsx"];

  for (const proof of [
    '<img src="https://x/after.png" width="600">',
    "**Not verified on http://localhost:3000/users/:id:** needs a signed-in account.",
  ])
    assert.deepEqual(checkEvidence(body(`${REVIEWED}\n\n${proof}`), page), [], proof);
  assert.deepEqual(
    checkEvidence(body(`${REVIEWED}\n\n![After](https://x/a.png)`).replaceAll("\n", "\r\n"), page),
    [],
  );
});

test("ignores proof that doesn't render, and wants the review status first", () => {
  const page = ["src/app/page.tsx"];
  const missing = (proof: string) => checkEvidence(body(`${REVIEWED}\n\n${proof}`), page).length;

  assert.equal(missing("![After][after]\n\n[after]: https://x/after.png"), 1, "reference image");
  assert.equal(missing("`![After](https://x/a.png)`"), 1, "inline code");
  assert.equal(missing("~~~md\n![After](https://x/a.png)\n~~~"), 1, "tilde fence");
  assert.equal(missing("<!--\n![After](https://x/a.png)\n-->"), 1, "comment");
  assert.deepEqual(checkEvidence(`<!--\n${body(REVIEWED)}\n-->`, page), [
    "The body has no `## Evidence` section.",
  ]);
  assert.deepEqual(checkEvidence(body(`**Reviewed:** \`abc1234\``), ["src/lib/date.ts"]), []);
  assert.deepEqual(checkEvidence(body(`Tests pass.\n\n${REVIEWED}`), ["src/lib/date.ts"]), [
    "Evidence doesn't open with a `**Reviewed:**` or `**Not reviewed:**` line.",
  ]);
});

test("reads only the Evidence section, and names a missing one", () => {
  const elsewhere = `## Summary\n\n${REVIEWED}\n\n![Page](https://x/p.png)\n\n## Evidence\n\nTests pass.\n`;

  assert.equal(checkEvidence(elsewhere, ["src/app/page.tsx"]).length, 2);
  assert.deepEqual(checkEvidence("## Summary\n\nA change.\n", ["src/lib/date.ts"]), [
    "The body has no `## Evidence` section.",
  ]);
});

/** A clone whose `origin/HEAD` is `main`, with a feature branch that commits the given files. */
async function featureBranch(files: Record<string, string>) {
  const root = await mkdtemp(path.join(tmpdir(), "check-evidence-"));
  fixtures.add(root);
  const local = path.join(root, "local");
  git(root, ["init", "--quiet", "--bare", path.join(root, "remote.git")]);
  git(root, ["init", "--quiet", "--initial-branch=main", local]);
  git(local, ["config", "user.name", "Test"]);
  git(local, ["config", "user.email", "test@example.com"]);
  git(local, ["remote", "add", "origin", path.join(root, "remote.git")]);
  await writeFile(path.join(local, "readme.md"), "base\n");
  git(local, ["add", "."]);
  git(local, ["commit", "--quiet", "-m", "base"]);
  git(local, ["push", "--quiet", "origin", "main"]);
  git(local, ["remote", "set-head", "origin", "main"]);
  git(local, ["switch", "--quiet", "-c", "feature"]);
  for (const [name, text] of Object.entries(files)) await writeFile(path.join(local, name), text);
  git(local, ["add", "."]);
  git(local, ["commit", "--quiet", "-m", "change"]);
  return { root, local };
}

test("reads the branch's committed diff against the remote's default branch and exits 1 on a gap", async () => {
  // Git quotes this name in plain `--name-only` output, which hid its extension.
  const { root, local } = await featureBranch({
    "Økonomi.tsx": "export const Page = () => null;\n",
  });
  const file = path.join(root, "body.md");
  const run = () =>
    spawnSync(process.execPath, [SCRIPT, "--body", file], { cwd: local, encoding: "utf-8" });

  await writeFile(file, body(REVIEWED));
  const gap = run();
  assert.equal(gap.status, 1);
  assert.match(gap.stderr, /changes UI \(Økonomi\.tsx\)/);

  await writeFile(file, body(`${REVIEWED}\n\n**Not verified on the page:** no dev server.`));
  const passed = run();
  assert.equal(passed.status, 0, passed.stderr);
  assert.match(passed.stderr, /Evidence check passed for 1 changed files against origin\/main/);
});

test("a missing body or an unknown option is a usage error, apart from a gap", async () => {
  const { root, local } = await featureBranch({ "date.ts": "export const d = 1;\n" });
  const file = path.join(root, "body.md");
  await writeFile(file, body(REVIEWED));
  const run = (...args: string[]) =>
    spawnSync(process.execPath, [SCRIPT, ...args], { cwd: local, encoding: "utf-8" });

  for (const args of [[], ["--body", file, "--dry-run"], ["--body", file, "shots/"]]) {
    const usage = run(...args);
    assert.equal(usage.status, 2, args.join(" "));
    assert.match(usage.stderr, /usage: node check-evidence\.ts/);
  }
  assert.equal(run("--body", file).status, 0);
});
