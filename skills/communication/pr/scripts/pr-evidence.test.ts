import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import { githubRepository, renderEvidence, uploadImages } from "./pr-evidence.ts";

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
