#!/usr/bin/env node
/**
 * Checks a PR body's Evidence section against the branch's committed diff and names what it lacks:
 * a review status line and a Limits line for any diff, and a screenshot, a "Not attached" line, or
 * a "Not verified" line for a diff that changes UI source. Run it from the PR branch's checkout.
 *
 * usage: node check-evidence.ts --body <file> [--base <ref>]
 *
 * `--base` defaults to the remote's default branch. Exits 1 on a gap and 2 on a usage error.
 */
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";

const USAGE = "usage: node check-evidence.ts --body <file> [--base <ref>]";
// UI source is what a screenshot can prove; tests, stories, and mocks render nothing a user sees.
const UI_SOURCE =
  /\.(?:tsx|jsx|vue|svelte|astro|html?|erb|hbs|ejs|pug|njk|liquid|css|scss|sass|less)$/;
const NOT_UI = /\.(?:test|spec|stories)\.[a-z]+$|(?:^|\/)(?:__tests__|__mocks__|e2e|stories)\//;
const EVIDENCE_SECTION = /^## Evidence[ \t]*\n([\s\S]*?)(?=^## |(?![\s\S]))/m;
// Comments and code don't render as evidence, so the checks read the body without them. Images
// count in the two forms PR bodies use: inline Markdown, as `gh --attach` rewrites it, and <img> tags.
const HIDDEN = /<!--[\s\S]*?-->|^(`{3,}|~{3,})[\s\S]*?^\1/gm;
const INLINE_CODE = /`[^`\n]+`/g;
const IMAGE = /!\[[^\]]*\]\([^)]+\)|<img\s/i;
const NOT_VERIFIED = /^\*\*Not verified on .+?:\*\*[ \t]*\S/m;
// Captures that were checked but that GitHub refused to host, described in words instead.
const NOT_ATTACHED = /^\*\*Not attached:\*\*[ \t]*\S/m;
const LIMITS = /^\*\*Limits:\*\*[ \t]*\S/m;
const REVIEW_STATUS = /^\*\*(?:Reviewed|Not reviewed):\*\*[ \t]*\S/;

class UsageError extends Error {}

/** The changed files a screenshot could prove: UI source, without tests, stories, or mocks. */
export function uiFiles(paths: string[]): string[] {
  return paths.filter((file) => UI_SOURCE.test(file) && !NOT_UI.test(file));
}

/**
 * What a PR body's Evidence section lacks for a diff, one problem per entry: a review status line
 * and a Limits line for any diff, and for a diff that changes UI source, a screenshot, a line
 * describing captures GitHub refused to host, or a line saying why the change was not verified on
 * its surface.
 */
export function checkEvidence(body: string, changedFiles: string[]): string[] {
  const visible = body.replaceAll("\r\n", "\n").replace(HIDDEN, "").replace(INLINE_CODE, "code");
  const evidence = EVIDENCE_SECTION.exec(visible)?.[1]?.trim();
  if (evidence === undefined) {
    return ["The body has no `## Evidence` section."];
  }
  const problems: string[] = [];
  if (!REVIEW_STATUS.test(evidence)) {
    problems.push("Evidence doesn't open with a `**Reviewed:**` or `**Not reviewed:**` line.");
  }
  if (!LIMITS.test(evidence)) {
    problems.push(
      "Evidence has no `**Limits:**` line naming what failed, couldn't run, or nobody checked.",
    );
  }
  const ui = uiFiles(changedFiles);
  const uiProof = [IMAGE, NOT_ATTACHED, NOT_VERIFIED].some((proof) => proof.test(evidence));
  if (ui.length > 0 && !uiProof) {
    const named = ui.length > 3 ? `${ui.slice(0, 3).join(", ")}, …` : ui.join(", ");
    problems.push(
      `The diff changes UI (${named}), and Evidence has no screenshot, \`**Not attached:**\` line, or \`**Not verified on <surface>:**\` line.`,
    );
  }
  return problems;
}

/** The branch a PR merges into when the caller names none: the remote's default, else `main`. */
function defaultBase(git: (args: string[]) => string): string {
  try {
    return git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"]);
  } catch {
    return "main";
  }
}

/** The problems with the body, against the branch's committed diff since its merge-base. */
function check(): string[] {
  const { values } = parseArgs({
    options: { body: { type: "string" }, base: { type: "string" } },
  });
  if (!values.body) {
    throw new UsageError("--body is required");
  }
  const git = (args: string[]) =>
    execFileSync("git", args, { cwd: process.cwd(), encoding: "utf-8" }).trim();
  const base = values.base ?? defaultBase(git);
  const mergeBase = git(["merge-base", base, "HEAD"]);
  // NUL-separated names arrive unquoted, whatever `core.quotePath` says about non-ASCII paths.
  const changed = git(["diff", "--name-only", "-z", "--no-renames", mergeBase, "HEAD"])
    .split("\0")
    .filter(Boolean);
  const problems = checkEvidence(readFileSync(values.body, "utf-8"), changed);
  if (problems.length === 0) {
    console.error(`Evidence check passed for ${changed.length} changed files against ${base}.`);
  }
  return problems;
}

if (import.meta.main) {
  try {
    const problems = check();
    if (problems.length > 0) {
      console.error(problems.join("\n"));
      process.exit(1);
    }
  } catch (error) {
    const usage =
      error instanceof UsageError ||
      (error as NodeJS.ErrnoException).code?.startsWith("ERR_PARSE_ARGS");
    console.error(usage ? `${(error as Error).message}\n${USAGE}` : (error as Error).message);
    process.exit(usage ? 2 : 1);
  }
}
