import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, test } from "node:test";

const SCRIPT = join(import.meta.dirname, "packet.ts");
const IDENTITY = {
  GIT_AUTHOR_NAME: "test",
  GIT_AUTHOR_EMAIL: "test@example.com",
  GIT_COMMITTER_NAME: "test",
  GIT_COMMITTER_EMAIL: "test@example.com",
};

let repo: string;
let out: string;

function git(...args: string[]): string {
  return execFileSync("git", ["-C", repo, "-c", "commit.gpgsign=false", ...args], {
    encoding: "utf8",
    env: { ...process.env, ...IDENTITY },
  }).trim();
}

function write(path: string, text: string | Buffer): void {
  writeFileSync(join(repo, path), text);
}

function packet(...args: string[]) {
  const result = spawnSync(process.execPath, [SCRIPT, "--repo", repo, "--out", out, ...args], {
    encoding: "utf8",
  });
  return {
    status: result.status,
    json: result.status === 0 ? JSON.parse(result.stdout) : undefined,
    stderr: result.stderr,
  };
}

beforeEach(() => {
  repo = mkdtempSync(join(tmpdir(), "packet-repo-"));
  out = mkdtempSync(join(tmpdir(), "packet-out-"));
  git("init", "--quiet", "--initial-branch=main");
  write("app.ts", "export const a = 1;\n");
  write("pnpm-lock.yaml", "lockfileVersion: 1\n");
  git("add", ".");
  git("commit", "--quiet", "-m", "base");
});

afterEach(() => {
  rmSync(repo, { recursive: true, force: true });
  rmSync(out, { recursive: true, force: true });
});

test("a branch review diffs from the merge-base and leaves out lockfiles, binaries, and generated files", () => {
  const base = git("rev-parse", "HEAD");
  git("switch", "--quiet", "-c", "feature");
  write("app.ts", "export const a = 2;\n");
  write("pnpm-lock.yaml", "lockfileVersion: 2\n");
  write("logo.png", Buffer.from([0, 1, 2, 0, 255]));
  write(".gitattributes", "schema.gen.ts linguist-generated\n");
  write("schema.gen.ts", "export type Schema = {};\n");
  git("add", ".");
  git("commit", "--quiet", "-m", "change");
  git("switch", "--quiet", "main");
  write("other.ts", "export const b = 1;\n");
  git("add", ".");
  git("commit", "--quiet", "-m", "main moves on");

  const { status, json } = packet("--base", "main", "--head", "feature");

  assert.equal(status, 0);
  assert.equal(json.base, base);
  assert.deepEqual(json.files.map((file: { path: string }) => file.path).sort(), [
    ".gitattributes",
    "app.ts",
  ]);
  assert.deepEqual(
    Object.fromEntries(
      json.excluded.map((entry: { path: string; reason: string }) => [entry.path, entry.reason]),
    ),
    { "logo.png": "binary", "pnpm-lock.yaml": "lockfile", "schema.gen.ts": "generated" },
  );
  const diff = readFileSync(json.diff, "utf8");
  assert.match(diff, /export const a = 2/);
  assert.doesNotMatch(diff, /lockfileVersion|Schema|other\.ts/);
  assert.match(readFileSync(json.packet, "utf8"), /pnpm-lock\.yaml: lockfile/);
});

test("--only reviews only the named paths, and the size counts only the diff the packet holds", () => {
  const base = git("rev-parse", "HEAD");
  git("switch", "--quiet", "-c", "feature");
  write("app.ts", "export const a = 2;\n");
  mkdirSync(join(repo, "sub"));
  write("sub/one.ts", "export const one = 1;\nexport const two = 2;\n");
  write("sub/lock.json", "{}\n");
  git("add", ".");
  git("commit", "--quiet", "-m", "change");

  const { status, json } = packet("--base", "main", "--only", "sub/", "--only", "missing.ts");

  assert.equal(status, 0);
  assert.deepEqual(json.files.map((file: { path: string }) => file.path).sort(), [
    "sub/lock.json",
    "sub/one.ts",
  ]);
  assert.doesNotMatch(readFileSync(json.diff, "utf8"), /export const a/);
  assert.equal(json.size, git("diff", "--shortstat", base, "HEAD", "--", "sub"));
  assert.equal(json.size, "2 files changed, 3 insertions(+)");
  assert.equal(packet("--base", "main", "--only", "missing.ts").status, 2);
});

test("vendored folders stay out, and --keep puts a left-out file back in the diff", () => {
  git("switch", "--quiet", "-c", "feature");
  write("app.ts", "export const a = 2;\n");
  write("pnpm-lock.yaml", "lockfileVersion: 2\n");
  mkdirSync(join(repo, "vendor"));
  write("vendor/lib.js", "export const lib = 1;\n");
  git("add", ".");
  git("commit", "--quiet", "-m", "change");

  const left = packet("--base", "main");
  assert.equal(left.status, 0);
  assert.deepEqual(
    Object.fromEntries(
      left.json.excluded.map((entry: { path: string; reason: string }) => [
        entry.path,
        entry.reason,
      ]),
    ),
    { "pnpm-lock.yaml": "lockfile", "vendor/lib.js": "vendored" },
  );

  const kept = packet("--base", "main", "--keep", "pnpm-lock.yaml");
  assert.equal(kept.status, 0);
  assert.deepEqual(
    kept.json.excluded.map((entry: { path: string }) => entry.path),
    ["vendor/lib.js"],
  );
  assert.match(readFileSync(kept.json.diff, "utf8"), /lockfileVersion: 2/);
});

test("--since reviews exactly the changes after a reviewed head", () => {
  write("app.ts", "export const a = 2;\n");
  git("commit", "--quiet", "-am", "first fix");
  const reviewed = git("rev-parse", "HEAD");
  write("app.ts", "export const a = 3;\n");
  git("commit", "--quiet", "-am", "second fix");

  const { status, json } = packet("--since", reviewed);

  assert.equal(status, 0);
  assert.equal(json.base, reviewed);
  const diff = readFileSync(json.diff, "utf8");
  assert.match(diff, /-export const a = 2;\n\+export const a = 3;/);
});

test("--working snapshots staged, unstaged, and untracked changes without touching the index or refs", () => {
  write("app.ts", "export const a = 2;\n");
  git("add", "app.ts");
  write("app.ts", "export const a = 3;\n");
  write("new.ts", "export const c = 1;\n");
  const before = {
    head: git("rev-parse", "HEAD"),
    status: git("status", "--porcelain"),
    refs: git("for-each-ref"),
  };

  const { status, json } = packet("--working", "--since", "HEAD");

  assert.equal(status, 0);
  assert.equal(json.snapshot, true);
  assert.notEqual(json.head, before.head);
  assert.equal(git("show", `${json.head}:app.ts`), "export const a = 3;");
  assert.equal(git("show", `${json.head}:new.ts`), "export const c = 1;");
  assert.deepEqual(
    {
      head: git("rev-parse", "HEAD"),
      status: git("status", "--porcelain"),
      refs: git("for-each-ref"),
    },
    before,
  );
});

test("--working with --only stages only the named paths", () => {
  const base = git("rev-parse", "HEAD");
  write("app.ts", "export const a = 2;\n");
  mkdirSync(join(repo, "unrelated"));
  execFileSync("git", ["-C", join(repo, "unrelated"), "init", "--quiet"]);
  symlinkSync("absent-target", join(repo, "link"));

  const { status, json, stderr } = packet(
    "--since",
    "HEAD",
    "--working",
    "--only",
    "app.ts",
    "--only",
    "link",
    "--only",
    "missing.ts",
  );

  assert.equal(status, 0, stderr);
  assert.deepEqual(
    json.files.map((file: { path: string }) => file.path),
    ["app.ts", "link"],
  );
  assert.equal(json.size, "2 files changed, 2 insertions(+), 1 deletion(-)");
  assert.equal(git("rev-parse", "HEAD"), base);
});

test("--working captures the working tree whatever the index flags say", () => {
  write(".gitignore", "secret.env\n");
  write("hidden.ts", "export const hidden = 1;\n");
  write("sparse.ts", "export const sparse = 1;\n");
  write("gone.ts", "export const gone = 1;\n");
  git("add", ".");
  git("commit", "--quiet", "-m", "fixtures");
  write("secret.env", "X=1\n");
  git("add", "--force", "secret.env");
  write("staged.ts", "export const staged = 1;\n");
  git("add", "staged.ts");
  write("app.ts", "export const a = 2;\n");
  write("untracked.ts", "export const u = 1;\n");
  git("update-index", "--assume-unchanged", "hidden.ts");
  write("hidden.ts", "export const hidden = 2;\n");
  git("update-index", "--skip-worktree", "sparse.ts");
  rmSync(join(repo, "sparse.ts"));
  rmSync(join(repo, "gone.ts"));

  const { status, json } = packet("--working", "--since", "HEAD");

  assert.equal(status, 0);
  assert.deepEqual(
    Object.fromEntries(
      json.files.map((file: { status: string; path: string }) => [file.path, file.status]),
    ),
    {
      "app.ts": "M",
      "gone.ts": "D",
      "hidden.ts": "M",
      "secret.env": "A",
      "staged.ts": "A",
      "untracked.ts": "A",
    },
  );
});

test("an empty diff fails before any reviewer starts", () => {
  const { status, json, stderr } = packet("--since", "HEAD");

  assert.equal(status, 2);
  assert.equal(json, undefined);
  assert.ok(JSON.parse(stderr.split("\n")[0]).error);
});
