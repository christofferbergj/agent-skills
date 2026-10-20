/**
 * SessionStart hook for Claude Code and Codex: load a reply skill's rules into each top-level
 * session, including resumes and compactions, so the rules survive both. Native subagents don't run
 * SessionStart, so they don't carry the rules; delegated tasks follow their brief's report shape.
 * Each hook entry loads one skill, so each stays within its own hook limit.
 *
 * usage: node session-start.ts [SKILL.md]   (default: next-options, the skill beside this script)
 */
import { readFileSync } from "node:fs";
import { basename, dirname, join } from "node:path";

// Claude Code previews context past 10,000 characters and Codex past about 2,500 tokens;
// 8,000 characters of Markdown stays under both.
const LIMIT = 8_000;
const SETUP = /^## Setup\s*$/m;

const path = process.argv[2] ?? join(import.meta.dirname, "..", "SKILL.md");
// A missing file has no frontmatter, so its directory names the skill in the warning.
const fallbackName = basename(dirname(path));

/** The skill's frontmatter name, which the hook names in its context and warnings. */
function skillName(text: string): string {
  const frontmatter = /^---\n([\s\S]*?)\n---\n/.exec(text)?.[1] ?? "";
  return /^name:\s*(\S+)/m.exec(frontmatter)?.[1] ?? fallbackName;
}

/** The rules: the skill body without its frontmatter and the setup pointer that follows them. */
function rules(text: string): string {
  const body = text.replace(/^---\n[\s\S]*?\n---\n/, "");
  const setup = body.search(SETUP);
  return (setup === -1 ? body : body.slice(0, setup)).trim();
}

/** The SessionStart output both hosts accept: context for the model and an optional warning. */
type HookOutput = {
  systemMessage?: string;
  hookSpecificOutput: { hookEventName: "SessionStart"; additionalContext: string };
};

function hookOutput(context: string, warning?: string): HookOutput {
  return {
    ...(warning ? { systemMessage: warning } : {}),
    hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: context },
  };
}

function output(): HookOutput {
  let text: string;
  try {
    text = readFileSync(path, "utf8");
  } catch (error) {
    const warning = `⚠️ ${fallbackName} couldn't load its rules from ${path} (${(error as NodeJS.ErrnoException).code}), so replies use the default format.`;
    return hookOutput(warning, warning);
  }
  const name = skillName(text);
  const context = `These are the user's reply rules from the ${name} skill. Follow them when replying to the user.\n\n${rules(text)}`;
  const oversized =
    context.length > LIMIT
      ? `⚠️ ${name} rules are ${context.length.toLocaleString("en")} characters, over the ${LIMIT.toLocaleString("en")}-character hook limit, so they load as a preview.`
      : undefined;
  return hookOutput(context, oversized);
}

// The host sends the session as JSON on stdin; nothing in it changes the rules.
if (!process.stdin.isTTY) readFileSync(0);
console.log(JSON.stringify(output()));
