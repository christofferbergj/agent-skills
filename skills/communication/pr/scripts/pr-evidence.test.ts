import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtemp, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import {
  checkEvidence,
  githubRepository,
  renderEvidence,
  uiFiles,
  uploadImages,
} from "./pr-evidence.ts";

const BASE = "https://github.com/acme/shop/blob/abc123";
const desktop = (file: string) => ({ file, width: 2560, height: 1720 });
const phone = (file: string) => ({ file, width: 780, height: 1688 });
const fixtures = new Set<string>();

afterEach(async () => {
  await Promise.all([...fixtures].map((fixture) => rm(fixture, { recursive: true, force: true })));
  fixtures.clear();
});

function imagesPerRow(markdown: string) {
  return markdown
    .split("\n")
    .filter((line) => line.startsWith("| !["))
    .map((line) => line.split("![").length - 1);
}

function git(cwd: string, args: string[]) {
  return execFileSync("git", args, { cwd, encoding: "utf-8" }).trim();
}

test("puts each before and after pair side by side under its view, in input order", () => {
  const markdown = renderEvidence(
    [
      desktop("/tmp/run/03-product-step-before.png"),
      desktop("/tmp/run/05-contact-after.png"),
      desktop("/tmp/run/07-product-step-after.png"),
      desktop("/tmp/run/summary-before.png"),
      desktop("/tmp/run/summary-after.png"),
    ],
    BASE,
  );

  assert.equal(
    markdown,
    `**Product step**

| Before | After |
| --- | --- |
| ![Product step before](${BASE}/03-product-step-before.png?raw=true) | ![Product step after](${BASE}/07-product-step-after.png?raw=true) |

**Summary**

| Before | After |
| --- | --- |
| ![Summary before](${BASE}/summary-before.png?raw=true) | ![Summary after](${BASE}/summary-after.png?raw=true) |

**After only**

| Contact |
| --- |
| ![Contact](${BASE}/05-contact-after.png?raw=true) |
`,
  );
});

test("shows views without a before in one table, two to a row, or three when all are portrait", () => {
  assert.equal(
    renderEvidence(
      ["contact", "crm-mismatch", "summary"].map((view) => desktop(`${view}-after.png`)),
      BASE,
    ),
    `**After only**

| Contact | Crm mismatch |
| --- | --- |
| ![Contact](${BASE}/contact-after.png?raw=true) | ![Crm mismatch](${BASE}/crm-mismatch-after.png?raw=true) |
| **Summary** |   |
| ![Summary](${BASE}/summary-after.png?raw=true) |   |
`,
  );

  const names = ["a", "b", "c", "d"].map((view) => `${view}-after.png`);
  assert.deepEqual(imagesPerRow(renderEvidence(names.map(desktop), BASE)), [2, 2]);
  assert.deepEqual(imagesPerRow(renderEvidence(names.map(phone), BASE)), [3, 1]);
  assert.deepEqual(
    imagesPerRow(renderEvidence([...names.slice(0, 3).map(phone), desktop("e-after.png")], BASE)),
    [2, 2],
  );
});

test("shows the states main never reaches under their view, headed by state name", () => {
  assert.equal(
    renderEvidence(
      [
        desktop("/tmp/run/02-contact-step--empty.png"),
        desktop("/tmp/run/03-contact-step--not-looked-up.png"),
        desktop("/tmp/run/04-contact-step--customer-found.png"),
        desktop("/tmp/run/product-step-before.png"),
        desktop("/tmp/run/product-step-after.png"),
        desktop("/tmp/run/product-step--no-offer.png"),
      ],
      BASE,
    ),
    `**Contact step**

| Empty | Not looked up |
| --- | --- |
| ![Contact step, empty](${BASE}/02-contact-step--empty.png?raw=true) | ![Contact step, not looked up](${BASE}/03-contact-step--not-looked-up.png?raw=true) |
| **Customer found** |   |
| ![Contact step, customer found](${BASE}/04-contact-step--customer-found.png?raw=true) |   |

**Product step**

| Before | After |
| --- | --- |
| ![Product step before](${BASE}/product-step-before.png?raw=true) | ![Product step after](${BASE}/product-step-after.png?raw=true) |

| No offer |
| --- |
| ![Product step, no offer](${BASE}/product-step--no-offer.png?raw=true) |
`,
  );
});

test("names every unpairable or misnamed screenshot before laying anything out", () => {
  assert.throws(
    () =>
      renderEvidence(
        [
          desktop("Product.png"),
          desktop("after-contact.png"),
          desktop("01-summary-before.png"),
          desktop("02-summary-before.png"),
          desktop("02-summary-after.png"),
          desktop("billing-before.png"),
          desktop("03-contact--empty.png"),
          desktop("04-contact--empty.png"),
        ],
        BASE,
      ),
    {
      message: [
        "Product.png: name it <view>-before.png, <view>-after.png or <view>--<state>.png, in kebab case",
        "after-contact.png: name it <view>-before.png, <view>-after.png or <view>--<state>.png, in kebab case",
        "01-summary-before.png and 02-summary-before.png are both the before of summary",
        "03-contact--empty.png and 04-contact--empty.png are both the empty state of contact",
        "billing-before.png has no billing-after.png",
      ].join("\n"),
    },
  );
});

test("reads owner and name from HTTPS and SSH GitHub remotes", () => {
  assert.equal(githubRepository("git@github.com:acme/shop.git"), "acme/shop");
  assert.equal(githubRepository("https://github.com/acme/shop.git"), "acme/shop");
  assert.equal(githubRepository("https://github.com/acme/shop"), "acme/shop");
  assert.throws(() => githubRepository("https://gitlab.com/acme/shop.git"));
});

async function createRepository() {
  const root = await mkdtemp(path.join(tmpdir(), "pr-evidence-"));
  fixtures.add(root);
  const local = path.join(root, "local");
  const remote = path.join(root, "remote.git");
  git(root, ["init", "--quiet", "--bare", remote]);
  git(root, ["init", "--quiet", local]);
  git(local, ["config", "user.name", "Test"]);
  git(local, ["config", "user.email", "test@example.com"]);
  git(local, ["remote", "add", "origin", remote]);
  return { root, local, remote: (args: string[]) => git(remote, args) };
}

test("pushes images-only commits that fast-forward, so earlier image links keep resolving", async () => {
  const { root, local, remote } = await createRepository();
  const shot = path.join(root, "product-after.png");
  const upload = () =>
    uploadImages({
      cwd: local,
      remote: "origin",
      branch: "pr-images/42-checkout",
      files: [shot],
      message: "PR images",
    });

  await writeFile(shot, "first");
  const first = upload();
  assert.equal(upload(), first, "the same images reuse the existing commit");

  await writeFile(shot, "second");
  const second = upload();
  assert.equal(remote(["rev-parse", "refs/heads/pr-images/42-checkout"]), second);
  assert.equal(remote(["rev-parse", `${second}^`]), first);
  assert.equal(remote(["show", `${first}:product-after.png`]), "first");
  assert.equal(remote(["ls-tree", "--name-only", second]), "product-after.png");
});

test("runs when started through a symlink, as installed skills are", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "pr-evidence-"));
  fixtures.add(root);
  const script = path.join(root, "pr-evidence.ts");
  await symlink(path.join(import.meta.dirname, "pr-evidence.ts"), script);

  const run = spawnSync(process.execPath, [script], { encoding: "utf-8" });

  assert.equal(run.status, 1);
  assert.match(run.stderr, /Usage: node pr-evidence\.ts/);
});

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

test("--check reads the branch's committed diff against the remote's default branch and exits 1 on a gap", async () => {
  const { root, local } = await createRepository();
  await writeFile(path.join(local, "readme.md"), "base\n");
  git(local, ["add", "."]);
  git(local, ["commit", "--quiet", "-m", "base"]);
  git(local, ["branch", "-M", "main"]);
  git(local, ["push", "--quiet", "origin", "main"]);
  git(local, ["remote", "set-head", "origin", "main"]);
  git(local, ["switch", "--quiet", "-c", "feature"]);
  // Git quotes this name in plain `--name-only` output, which hid its extension.
  await writeFile(path.join(local, "Økonomi.tsx"), "export const Page = () => null;\n");
  git(local, ["add", "."]);
  git(local, ["commit", "--quiet", "-m", "page"]);
  const file = path.join(root, "body.md");
  const run = () =>
    spawnSync(
      process.execPath,
      [path.join(import.meta.dirname, "pr-evidence.ts"), "--check", "--body", file],
      { cwd: local, encoding: "utf-8" },
    );

  await writeFile(file, body(REVIEWED));
  const gap = run();
  assert.equal(gap.status, 1);
  assert.match(gap.stderr, /changes UI \(Økonomi\.tsx\)/);

  await writeFile(file, body(`${REVIEWED}\n\n**Not verified on the page:** no dev server.`));
  const passed = run();
  assert.equal(passed.status, 0, passed.stderr);
  assert.match(passed.stderr, /Evidence check passed for 1 changed files against origin\/main/);
});
