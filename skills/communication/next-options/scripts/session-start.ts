/**
 * SessionStart hook for Claude Code and Codex: load a reply skill's rules into each top-level
 * session, including resumes and compactions, so the rules survive both. Native subagents don't run
 * SessionStart, so they don't carry the rules. T3 Code's delegated tasks do run it, yet only their
 * parent reads their reports, so they skip the rules; other delegated tasks follow their brief's
 * report shape. Each hook entry loads one skill, so each stays within its own hook limit.
 *
 * usage: node session-start.ts [SKILL.md]   (default: next-options, the skill beside this script)
 */
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";

// Claude Code previews context past 10,000 characters and Codex past about 2,500 tokens;
// 8,000 characters of Markdown stays under both.
const LIMIT = 8_000;
const SETUP = /^## Setup\s*$/m;
const T3_STATE_DB = process.env.T3_STATE_DB ?? join(homedir(), ".t3", "userdata", "statev2.sqlite");

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

/**
 * True when T3 Code records the session as a delegated task's thread. The state database has no
 * versioned schema, so a missing, locked, or changed database reads as false and loads the rules.
 */
async function isT3DelegatedTask(sessionId: unknown): Promise<boolean> {
  if (typeof sessionId !== "string" || !sessionId) return false;
  try {
    const { DatabaseSync } = await import("node:sqlite");
    const db = new DatabaseSync(T3_STATE_DB, { readOnly: true, timeout: 1_000 });
    try {
      // A thread's payload names its own native session and, sometimes, another thread's head.
      const threads = db
        .prepare(
          `select distinct thread_id from orchestration_v2_projection_provider_threads
           where json_extract(payload_json, '$.nativeThreadRef.nativeId') = ?1
              or json_extract(payload_json, '$.nativeConversationHeadRef.nativeId') = ?1`,
        )
        .all(sessionId);
      return (
        threads.length === 1 && String(threads[0].thread_id).startsWith("thread:delegated-task:")
      );
    } finally {
      db.close();
    }
  } catch {
    return false;
  }
}

/** The session id from the host's SessionStart JSON on stdin, the only field the hook reads. */
function sessionId(): unknown {
  if (process.stdin.isTTY) return undefined;
  try {
    return JSON.parse(readFileSync(0, "utf8")).session_id;
  } catch {
    return undefined;
  }
}

if (!(await isT3DelegatedTask(sessionId()))) console.log(JSON.stringify(output()));
