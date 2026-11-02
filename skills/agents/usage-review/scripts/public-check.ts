/**
 * Blocks /usage-review from publishing private identifiers to this public repository. Scans
 * every commit the branch would push (its message, the paths it touches, and the lines it adds)
 * plus the PR title and body, and reports each hit by class and position, never the matched text.
 *
 * Usage: public-check.ts [--base origin/main] [--pr-title <text>] [--pr-body <file>]
 *        [--names ~/.local/state/usage-review/private-names.txt] [--db <path>]
 * Exits 1 on any hit, and on any error, so a failed check never reads as clean.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { homedir } from "node:os";
import { join } from "node:path";
import { parseArgs } from "node:util";

import { stateDbPath } from "./extract.ts";

export type HitClass =
  | "github-url"
  | "ticket-id"
  | "email"
  | "project-title"
  | "private-name"
  | "binary-file";

export interface Hit {
  readonly class: HitClass;
  readonly where: string;
}

export interface Rules {
  /** Lowercased `owner/repo` paths that may appear: this repository and the upstreams it credits. */
  readonly allowedRepos: ReadonlySet<string>;
  /** Lowercased T3 project titles. */
  readonly projectTitles: readonly string[];
  /** Lowercased names the owner listed. */
  readonly privateNames: readonly string[];
}

const GITHUB = /github\.com[:/]+([\w.-]+)(?:\/([\w.-]+))?/gi;
/** Standards, encodings, and model names that share a ticket id's shape. */
const NOT_TICKETS = new Set([
  "UTF",
  "ISO",
  "RFC",
  "SHA",
  "ES",
  "ECMA",
  "WCAG",
  "IEEE",
  "HTTP",
  "GPT",
]);
/** RFC 2606 documentation domains, which name nobody. */
const RESERVED_DOMAIN = /(^|\.)(example\.(com|org|net)|test|invalid|example)$/i;

/** Percent-decoded and NFKC-normalized, so encoded and full-width forms read as plain text. */
function decoded(line: string): string {
  let text = line;
  try {
    text = decodeURIComponent(line);
  } catch {}
  return text.normalize("NFKC");
}

function contains(text: string, term: string): boolean {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^\\p{L}\\p{N}])${escaped}($|[^\\p{L}\\p{N}])`, "iu").test(text);
}

function repoOf(match: RegExpMatchArray): string {
  return `${match[1]}/${(match[2] ?? "").replace(/\.git$/, "")}`.toLowerCase();
}

function allowed(repo: string, rules: Rules): boolean {
  // An owner-only link is fine when that owner has an allowed repository.
  return repo.endsWith("/")
    ? [...rules.allowedRepos].some((r) => r.startsWith(repo))
    : rules.allowedRepos.has(repo);
}

function namesIn(text: string, where: string, rules: Rules): Hit[] {
  const hits: Hit[] = [];
  if (rules.projectTitles.some((t) => contains(text, t)))
    hits.push({ class: "project-title", where });
  if (rules.privateNames.some((n) => contains(text, n)))
    hits.push({ class: "private-name", where });
  return hits;
}

export function scanLine(raw: string, where: string, rules: Rules): Hit[] {
  const line = decoded(raw);
  const hits: Hit[] = [];
  for (const match of line.matchAll(GITHUB))
    if (!allowed(repoOf(match), rules)) hits.push({ class: "github-url", where });
  for (const match of line.matchAll(/\b([A-Z][A-Z0-9]+)-\d+\b/g))
    if (!NOT_TICKETS.has(match[1])) hits.push({ class: "ticket-id", where });
  for (const match of line.matchAll(/([\w.+-]+)@([\w-]+\.[\w.-]+)/g))
    if (!RESERVED_DOMAIN.test(match[2]) && !(match[1] === "git" && /^github\.com$/i.test(match[2])))
      hits.push({ class: "email", where });
  return [...hits, ...namesIn(line, where, rules)];
}

/** Scans each line, then the whole text once more for a name split across lines. */
export function scan(text: string, source: string, rules: Rules): Hit[] {
  const lines = text.split("\n");
  const hits = lines.flatMap((line, index) => scanLine(line, `${source}:${index + 1}`, rules));
  const named = new Set(hits.map((h) => h.class));
  const joined = namesIn(
    decoded(lines.join(" ").replace(/\s+/g, " ")),
    `${source}:across lines`,
    rules,
  );
  return [...hits, ...joined.filter((h) => !named.has(h.class))];
}

/**
 * Scans `git log -p` output: each commit's message, every path a diff header names, and each
 * added line, reading header lines as headers until the first hunk so a `++` content line
 * can't pass for one. A binary file can't be read, so it is a hit for a person to check.
 */
export function scanLog(log: string, rules: Rules): Hit[] {
  const hits: Hit[] = [];
  for (const commit of log.split("\u0000COMMIT ").filter(Boolean)) {
    const [header, ...rest] = commit.split("\u0000");
    const sha = header.slice(0, 7);
    const message = header.slice(header.indexOf("\n") + 1);
    hits.push(...scan(message, `commit ${sha}`, rules));
    let file = "";
    let inHunk = false;
    let line = 0;
    let added: string[] = [];
    const flush = () => {
      if (added.length)
        hits.push(
          ...scan(added.join("\n"), `${file}@${sha}`, rules).filter((h) =>
            h.where.endsWith("across lines"),
          ),
        );
      added = [];
    };
    for (const row of rest.join("\u0000").split("\n")) {
      const paths = row.match(/^diff --git a\/(.*) b\/(.*)$/);
      if (paths) {
        flush();
        file = paths[2];
        inHunk = false;
        hits.push(...scan(`${paths[1]}\n${paths[2]}`, `path@${sha}`, rules));
      } else if (!inHunk && row.startsWith("Binary files ")) {
        hits.push({ class: "binary-file", where: `${file}@${sha}` });
      } else if (row.startsWith("@@")) {
        inHunk = true;
        line = Number(row.match(/\+(\d+)/)?.[1] ?? 0);
      } else if (inHunk && row.startsWith("+")) {
        hits.push(...scanLine(row.slice(1), `${file}:${line++}@${sha}`, rules));
        added.push(row.slice(1));
      }
    }
    flush();
  }
  return hits;
}

/**
 * Every `owner/repo` an `UPSTREAM.md` names at the base revision, plus this repository. Read from
 * the base, never the branch under check, so a branch can't allow its own URLs.
 */
export function creditedRepos(root: string, base: string, self: string): Set<string> {
  const git = (...args: string[]) =>
    execFileSync("git", ["-C", root, ...args], { encoding: "utf8" });
  const files = git("ls-tree", "-r", "--name-only", base)
    .split("\n")
    .filter((path) => path.endsWith("UPSTREAM.md"));
  const repos = new Set([self.toLowerCase()]);
  for (const file of files)
    for (const match of git("show", `${base}:${file}`).matchAll(GITHUB))
      if (match[2]) repos.add(repoOf(match));
  return repos;
}

/** T3 project titles, leaving out this repository's own and the non-identifying ones. */
export function privateProjectTitles(db: DatabaseSync, repoName: string): string[] {
  const rows = db.prepare("select title from projection_projects").all() as { title: string }[];
  return rows
    .map((row) => row.title.trim().normalize("NFKC").toLowerCase())
    .filter(
      (t) =>
        t.length >= 3 && !t.startsWith(".") && t !== "no project" && t !== repoName.toLowerCase(),
    );
}

if (import.meta.main) {
  const { values } = parseArgs({
    options: {
      base: { type: "string", default: "origin/main" },
      "pr-title": { type: "string" },
      "pr-body": { type: "string" },
      names: {
        type: "string",
        default: join(homedir(), ".local/state/usage-review/private-names.txt"),
      },
      db: { type: "string" },
    },
  });
  const root = execFileSync("git", ["rev-parse", "--show-toplevel"], { encoding: "utf8" }).trim();
  const self = execFileSync(
    "gh",
    ["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
    {
      cwd: root,
      encoding: "utf8",
    },
  ).trim();
  const db = new DatabaseSync(stateDbPath(values.db), { readOnly: true, timeout: 5_000 });
  if (!existsSync(values.names))
    console.error(`public-check: no private names file at ${values.names}`);
  const rules: Rules = {
    allowedRepos: creditedRepos(root, values.base, self),
    projectTitles: privateProjectTitles(db, self.split("/")[1]),
    privateNames: existsSync(values.names)
      ? readFileSync(values.names, "utf8")
          .split("\n")
          .map((l) => l.trim().normalize("NFKC").toLowerCase())
          .filter(Boolean)
      : [],
  };
  db.close();

  const log = execFileSync(
    "git",
    [
      "-C",
      root,
      "log",
      "-p",
      "--text",
      "--no-renames",
      "--unified=0",
      "--no-color",
      "--format=%x00COMMIT %H%n%B%x00",
      `${values.base}..HEAD`,
    ],
    { encoding: "utf8", maxBuffer: 256 * 1024 * 1024 },
  );
  const hits = scanLog(log, rules);
  if (values["pr-title"]) hits.push(...scan(values["pr-title"], "pr-title", rules));
  if (values["pr-body"])
    hits.push(...scan(readFileSync(values["pr-body"], "utf8"), "pr-body", rules));

  for (const hit of hits) console.log(`${hit.class}\t${hit.where}`);
  if (hits.length > 0) process.exit(1);
  console.log("public-check: no private identifiers found");
}
