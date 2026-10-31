/**
 * Build a review packet: pinned revisions, the files under review, and a diff without lockfiles,
 * binaries, or generated or vendored files. Run `node packet.ts --help`.
 *
 * `--working` snapshots the working tree into an unreferenced commit through a temporary index,
 * so reviewers read an immutable revision while the user's index, stash, and branch stay as they were.
 */
import { execFileSync } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  rmSync,
  statSync,
  utimesSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { basename, isAbsolute, join, resolve } from "node:path";
import { parseArgs } from "node:util";

const USAGE = `usage: node packet.ts --repo <dir> [--base <ref> | --since <ref>] [--head <ref> | --working]
                      [--only <path>]... [--keep <path>]... [--out <dir>]

  --base <ref>   review from the merge-base of <ref> and the head (default: the default branch)
  --since <ref>  review exactly the changes after <ref>, such as the last reviewed head
  --head <ref>   the revision under review (default: HEAD)
  --working      snapshot staged, unstaged, and untracked changes as the revision under review
  --only <path>  review only this file or folder, from the repository root (repeatable)
  --keep <path>  keep this lockfile, binary, or generated or vendored file in the diff (repeatable)
  --out <dir>    write the packet here (default: a new temporary directory)

Prints JSON naming the packet, its revisions, its size, and its reviewed and excluded files.`;

const LOCKFILES = new Set([
  "bun.lock",
  "bun.lockb",
  "Cargo.lock",
  "composer.lock",
  "deno.lock",
  "flake.lock",
  "Gemfile.lock",
  "go.sum",
  "mix.lock",
  "npm-shrinkwrap.json",
  "package-lock.json",
  "Package.resolved",
  "Pipfile.lock",
  "Podfile.lock",
  "poetry.lock",
  "pnpm-lock.yaml",
  "pubspec.lock",
  "uv.lock",
  "yarn.lock",
]);
const GENERATED = /\.min\.(?:js|css)$|\.map$|\.pb\.go$|_pb2\.py$|\.generated\./;
const VENDORED = /(?:^|\/)(?:vendor|node_modules|third_party)\//;
const SNAPSHOT_IDENTITY = { NAME: "review-loop", EMAIL: "review-loop@localhost" };

type Options = {
  repo: string;
  base?: string;
  since?: string;
  head?: string;
  working: boolean;
  only?: string[];
  keep?: string[];
  out?: string;
};
type Change = { status: string; path: string };
type Exclusion = { path: string; reason: "lockfile" | "binary" | "generated" | "vendored" };

class UsageError extends Error {}

function git(
  repo: string,
  args: string[],
  options: { env?: NodeJS.ProcessEnv; input?: string } = {},
): string {
  return execFileSync("git", ["-C", repo, ...args], {
    encoding: "utf8",
    env: options.env ?? process.env,
    input: options.input ?? "",
    maxBuffer: 512 * 1024 * 1024,
  });
}

function commit(repo: string, ref: string): string {
  try {
    return git(repo, ["rev-parse", "--verify", "--quiet", `${ref}^{commit}`]).trim();
  } catch {
    throw new UsageError(`${ref} does not name a commit in ${repo}`);
  }
}

/** The branch a review compares against when the caller names none. */
function defaultBranch(repo: string): string {
  try {
    return git(repo, ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"]).trim();
  } catch {
    const local = ["main", "master"].find((name) => {
      try {
        return Boolean(commit(repo, name));
      } catch {
        return false;
      }
    });
    if (local) return local;
    throw new UsageError("no default branch found; pass --base or --since");
  }
}

/** Commit the working tree, untracked files included, without touching the real index or refs. */
function snapshot(repo: string, only: string[] | undefined): string {
  const scratch = mkdtempSync(join(tmpdir(), "review-loop-index-"));
  const index = join(scratch, "index");
  const env = {
    ...process.env,
    GIT_INDEX_FILE: index,
    GIT_AUTHOR_NAME: SNAPSHOT_IDENTITY.NAME,
    GIT_AUTHOR_EMAIL: SNAPSHOT_IDENTITY.EMAIL,
    GIT_COMMITTER_NAME: SNAPSHOT_IDENTITY.NAME,
    GIT_COMMITTER_EMAIL: SNAPSHOT_IDENTITY.EMAIL,
  };
  try {
    // Start from the real index: it holds staged entries that `add` would skip, such as force-added
    // ignored files, and skip-worktree entries a sparse checkout leaves out of the working tree.
    const real = git(repo, ["rev-parse", "--git-path", "index"]).trim();
    const realPath = isAbsolute(real) ? real : join(repo, real);
    // Keep the index's timestamp, so Git still rechecks a file changed in the same second it was staged.
    if (existsSync(realPath)) {
      copyFileSync(realPath, index);
      const { atime, mtime } = statSync(realPath);
      utimesSync(index, atime, mtime);
    } else git(repo, ["read-tree", "HEAD"], { env });
    // An assume-unchanged entry tells `add` not to look at the file, which would hide its changes.
    const assumed = nulFields(git(repo, ["ls-files", "-v", "-z"], { env }))
      .filter((entry) => /^[a-z] /.test(entry))
      .map((entry) => `${entry.slice(2)}\0`);
    if (assumed.length > 0)
      git(repo, ["update-index", "--no-assume-unchanged", "-z", "--stdin"], {
        env,
        input: assumed.join(""),
      });
    // Stage only the --only paths that exist, so an unrelated file, such as a nested repository
    // without a commit, can't stop the snapshot, and a missing path doesn't fail `add`.
    const targets = (only ?? ["."])
      .filter(
        (path) =>
          path === "." ||
          existsSync(join(repo, path)) ||
          git(repo, ["ls-files", "--", `:(top,literal)${path}`], { env }).trim() !== "",
      )
      .map((path) => (path === "." ? path : `:(top,literal)${path}`));
    if (targets.length > 0) git(repo, ["add", "--all", "--", ...targets], { env });
    const tree = git(repo, ["write-tree"], { env }).trim();
    return git(
      repo,
      ["commit-tree", "--no-gpg-sign", "-p", "HEAD", "-m", "review-loop working snapshot", tree],
      { env },
    ).trim();
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
}

function nulFields(output: string): string[] {
  return output.split("\0").filter((field) => field !== "");
}

function changes(repo: string, base: string, head: string, scope: string[]): Change[] {
  const tokens = nulFields(
    git(repo, ["diff", "--name-status", "--no-renames", "-z", base, head, "--", ...scope]),
  );
  const result: Change[] = [];
  for (let index = 0; index < tokens.length; index += 2)
    result.push({ status: tokens[index], path: tokens[index + 1] });
  return result;
}

function exclusions(
  repo: string,
  base: string,
  head: string,
  scope: string[],
  paths: string[],
  keep: Set<string>,
): Exclusion[] {
  const binary = new Set(
    nulFields(git(repo, ["diff", "--numstat", "--no-renames", "-z", base, head, "--", ...scope]))
      .filter((line) => line.startsWith("-\t-\t"))
      .map((line) => line.slice(4)),
  );
  const attributes = new Map<string, Exclusion["reason"]>();
  const tokens = nulFields(
    git(
      repo,
      [
        "check-attr",
        `--source=${head}`,
        "--stdin",
        "-z",
        "linguist-generated",
        "linguist-vendored",
      ],
      { input: paths.map((path) => `${path}\0`).join("") },
    ),
  );
  for (let index = 0; index < tokens.length; index += 3) {
    const [path, attribute, value] = tokens.slice(index, index + 3);
    if (value === "set" || value === "true")
      attributes.set(path, attribute === "linguist-vendored" ? "vendored" : "generated");
  }
  return paths.flatMap((path): Exclusion[] => {
    if (keep.has(path)) return [];
    if (LOCKFILES.has(basename(path))) return [{ path, reason: "lockfile" }];
    if (binary.has(path)) return [{ path, reason: "binary" }];
    const attribute = attributes.get(path);
    if (attribute) return [{ path, reason: attribute }];
    if (VENDORED.test(path)) return [{ path, reason: "vendored" }];
    return GENERATED.test(path) ? [{ path, reason: "generated" }] : [];
  });
}

function parse(): Options | undefined {
  const { values } = parseArgs({
    options: {
      repo: { type: "string" },
      base: { type: "string" },
      since: { type: "string" },
      head: { type: "string" },
      working: { type: "boolean", default: false },
      only: { type: "string", multiple: true },
      keep: { type: "string", multiple: true },
      out: { type: "string" },
      help: { type: "boolean", short: "h", default: false },
    },
  });
  if (values.help) return undefined;
  if (!values.repo) throw new UsageError("--repo is required");
  if (values.base && values.since) throw new UsageError("pass --base or --since, not both");
  if (values.head && values.working) throw new UsageError("pass --head or --working, not both");
  return { ...values, repo: values.repo };
}

function build(options: Options) {
  const repo = git(resolve(options.repo), ["rev-parse", "--show-toplevel"]).trim();
  const only = options.only?.map((path) => path.replace(/\/+$/, ""));
  const head = options.working ? snapshot(repo, only) : commit(repo, options.head ?? "HEAD");
  const against = options.since ?? options.base ?? defaultBranch(repo);
  const base = options.since
    ? commit(repo, against)
    : git(repo, ["merge-base", commit(repo, against), head]).trim();
  const scope = only?.map((path) => `:(top,literal)${path}`) ?? ["."];
  const changed = changes(repo, base, head, scope);
  if (changed.length === 0)
    throw new UsageError(
      `no changes between ${base} and ${head}${options.only ? " in the --only paths" : ""}`,
    );
  const excluded = exclusions(
    repo,
    base,
    head,
    scope,
    changed.map((change) => change.path),
    new Set(options.keep),
  );
  const leftOut = new Set(excluded.map((entry) => entry.path));
  const reviewed = changed.filter((change) => !leftOut.has(change.path));
  if (reviewed.length === 0)
    throw new UsageError(
      "only lockfiles, binaries, or generated or vendored files changed; pass --keep for one central to the change",
    );

  const directory = options.out
    ? resolve(options.out)
    : mkdtempSync(join(tmpdir(), "review-loop-"));
  mkdirSync(directory, { recursive: true });
  const diff = join(directory, "diff.patch");
  const packet = join(directory, "packet.md");
  const pathspec = [...scope, ...excluded.map((entry) => `:(exclude,literal)${entry.path}`)];
  writeFileSync(diff, git(repo, ["diff", "--find-renames", base, head, "--", ...pathspec]));
  const size = git(repo, [
    "diff",
    "--shortstat",
    "--find-renames",
    base,
    head,
    "--",
    ...pathspec,
  ]).trim();
  const commits = git(repo, ["log", "--format=%h %s", `${base}..${head}`]).trim();
  writeFileSync(
    packet,
    [
      "# Review packet",
      "",
      `- Repository: ${repo}`,
      `- Base: ${base} (${options.since ? "exactly" : "merge-base with"} ${against})`,
      `- Head: ${head}${options.working ? " (working snapshot)" : ""}`,
      `- Diff: ${diff}, or \`git -C ${repo} diff --find-renames ${base} ${head}\` limited to the files below`,
      `- Size: ${size}`,
      "",
      "## Commits",
      "",
      commits || "(none)",
      "",
      `## Files under review (${reviewed.length})`,
      "",
      ...reviewed.map((change) => `- ${change.status} ${change.path}`),
      "",
      `## Left out of the diff (${excluded.length})`,
      "",
      ...(excluded.length > 0
        ? excluded.map((entry) => `- ${entry.path}: ${entry.reason}`)
        : ["(none)"]),
      "",
    ].join("\n"),
  );
  return {
    packet,
    diff,
    repository: repo,
    base,
    head,
    snapshot: options.working,
    size,
    files: reviewed,
    excluded,
  };
}

try {
  const options = parse();
  if (!options) console.log(USAGE);
  else console.log(JSON.stringify(build(options), null, 2));
} catch (error) {
  const usage =
    error instanceof UsageError ||
    (error as NodeJS.ErrnoException).code?.startsWith("ERR_PARSE_ARGS");
  const message = (error as { stderr?: string }).stderr?.trim() || (error as Error).message;
  console.error(JSON.stringify({ error: message }));
  if (usage) console.error(`\n${USAGE}`);
  process.exit(usage ? 2 : 1);
}
