/**
 * Blocks /usage-review from publishing private identifiers to this public repository. Scans the
 * branch's added lines, its commit messages, and the PR title and body, and reports each hit by
 * class and position only, never the matched text.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { homedir } from "node:os";
import { join } from "node:path";
import { parseArgs } from "node:util";

export type HitClass = "github-url" | "ticket-id" | "email" | "project-title" | "private-name";

export interface Hit {
  readonly class: HitClass;
  readonly where: string;
}

export interface Rules {
  /** `owner/repo` paths that may appear: this repository and every upstream source it credits. */
  readonly allowedRepos: ReadonlySet<string>;
  /** Lowercased project titles and owner-listed private names. */
  readonly projectTitles: readonly string[];
  readonly privateNames: readonly string[];
}

/** Standards and encodings that share a ticket id's shape. */
const NOT_TICKETS = new Set(["UTF", "ISO", "RFC", "SHA", "ES", "ECMA", "WCAG", "IEEE", "HTTP"]);

function contains(line: string, term: string): boolean {
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^\\p{L}\\p{N}])${escaped}($|[^\\p{L}\\p{N}])`, "iu").test(line);
}

export function scanLine(line: string, where: string, rules: Rules): Hit[] {
  const hits: Hit[] = [];
  for (const match of line.matchAll(/github\.com\/([\w.-]+)\/([\w.-]+)/gi)) {
    const repo = `${match[1]}/${match[2].replace(/\.git$/, "")}`.toLowerCase();
    if (!rules.allowedRepos.has(repo)) hits.push({ class: "github-url", where });
  }
  for (const match of line.matchAll(/\b([A-Z][A-Z0-9]+)-\d+\b/g))
    if (!NOT_TICKETS.has(match[1])) hits.push({ class: "ticket-id", where });
  if (/[\w.+-]+@[\w-]+\.[\w.-]+/.test(line)) hits.push({ class: "email", where });
  if (rules.projectTitles.some((t) => contains(line, t)))
    hits.push({ class: "project-title", where });
  if (rules.privateNames.some((n) => contains(line, n)))
    hits.push({ class: "private-name", where });
  return hits;
}

export function scan(text: string, source: string, rules: Rules): Hit[] {
  return text.split("\n").flatMap((line, index) => scanLine(line, `${source}:${index + 1}`, rules));
}

/** Every `owner/repo` a tracked `UPSTREAM.md` names, plus this repository. */
export function creditedRepos(root: string, self: string): Set<string> {
  const files = execFileSync("git", ["-C", root, "ls-files", "*UPSTREAM.md"], { encoding: "utf8" })
    .split("\n")
    .filter(Boolean);
  const repos = new Set([self.toLowerCase()]);
  for (const file of files)
    for (const match of readFileSync(join(root, file), "utf8").matchAll(
      /github\.com\/([\w.-]+)\/([\w.-]+)/gi,
    ))
      repos.add(`${match[1]}/${match[2].replace(/\.git$/, "")}`.toLowerCase());
  return repos;
}

/** T3 project titles, leaving out this repository's own and the non-identifying ones. */
export function privateProjectTitles(db: DatabaseSync, repoName: string): string[] {
  const rows = db.prepare("select title from projection_projects").all() as { title: string }[];
  return rows
    .map((row) => row.title.trim().toLowerCase())
    .filter(
      (t) =>
        t.length >= 4 && !t.startsWith(".") && t !== "no project" && t !== repoName.toLowerCase(),
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
  const dbPath =
    values.db ?? process.env.T3_STATE_DB ?? join(homedir(), ".t3", "userdata", "statev2.sqlite");
  const db = new DatabaseSync(dbPath, { readOnly: true, timeout: 5_000 });
  const rules: Rules = {
    allowedRepos: creditedRepos(root, self),
    projectTitles: privateProjectTitles(db, self.split("/")[1]),
    privateNames: existsSync(values.names)
      ? readFileSync(values.names, "utf8")
          .split("\n")
          .map((l) => l.trim().toLowerCase())
          .filter(Boolean)
      : [],
  };
  db.close();

  const git = (...args: string[]) =>
    execFileSync("git", ["-C", root, ...args], { encoding: "utf8" });
  const hits: Hit[] = [];
  const diff = git("diff", "--unified=0", "--no-color", `${values.base}...HEAD`);
  let file = "";
  let line = 0;
  for (const row of diff.split("\n")) {
    if (row.startsWith("+++ ")) file = row.slice(6);
    else if (row.startsWith("@@")) line = Number(row.match(/\+(\d+)/)?.[1] ?? 0);
    else if (row.startsWith("+") && file)
      hits.push(...scanLine(row.slice(1), `${file}:${line++}`, rules));
  }
  for (const sha of git("rev-list", `${values.base}..HEAD`).split("\n").filter(Boolean))
    hits.push(...scan(git("log", "-1", "--format=%B", sha), `commit ${sha.slice(0, 7)}`, rules));
  if (values["pr-title"]) hits.push(...scan(values["pr-title"], "pr-title", rules));
  if (values["pr-body"])
    hits.push(...scan(readFileSync(values["pr-body"], "utf8"), "pr-body", rules));

  for (const hit of hits) console.log(`${hit.class}\t${hit.where}`);
  if (hits.length > 0) process.exit(1);
  console.log("public-check: no private identifiers found");
}
