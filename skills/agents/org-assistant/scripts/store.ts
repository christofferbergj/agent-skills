/**
 * Where an organisation's profile and state live, and how the files are read and written. Each state
 * file has one writer: the scan writes snapshot.json, pending.json, and scan.stamp; the model writes
 * ledger.json through `assistant.ts ledger`. Every write replaces its file atomically, and `.lock`
 * keeps a timer scan and an inline scan from running at once.
 */
import {
  closeSync,
  mkdirSync,
  openSync,
  readFileSync,
  renameSync,
  statSync,
  unlinkSync,
  writeFileSync,
  writeSync,
} from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";

import { type Parser, ShapeError, parse } from "./parse.ts";
import { sleep } from "./time.ts";

/** A profile or state file the scan cannot read: it fails its own organisation, not the others. */
export class FileError extends Error {
  constructor(file: string, problem: string) {
    super(`${file}: ${problem}`);
  }
}

export function expandHome(path: string): string {
  return path === "~" || path.startsWith("~/") ? join(homedir(), path.slice(1)) : path;
}

export function configRoot(): string {
  return expandHome(process.env.ORG_ASSISTANT_CONFIG ?? "~/.config/org-assistant");
}

export function stateDir(org: string): string {
  return join(expandHome(process.env.ORG_ASSISTANT_STATE ?? "~/.local/state/org-assistant"), org);
}

const code = (error: unknown) =>
  error instanceof Error && "code" in error && typeof error.code === "string" ? error.code : "";

/** A file's text, or null when it doesn't exist. */
export function readText(file: string): string | null {
  try {
    return readFileSync(file, "utf8");
  } catch (error) {
    if (code(error) === "ENOENT") return null;
    throw new FileError(file, `unreadable (${code(error) || "error"})`);
  }
}

/** A JSON file's value, or undefined when it doesn't exist. */
export function readJson(file: string): unknown {
  const text = readText(file);
  return text === null ? undefined : parseJson(file, text);
}

/** A file's value read by `parser`; a shape it doesn't know fails the file's organisation. */
export function parseFile<T>(file: string, parser: Parser<T>, value: unknown): T {
  try {
    return parse(parser, value);
  } catch (error) {
    if (error instanceof ShapeError) throw new FileError(file, error.message);
    throw error;
  }
}

/** JSON text's value; a syntax error names the file and the line, never the text around it. */
export function parseJson(file: string, text: string): unknown {
  try {
    return JSON.parse(text);
  } catch (error) {
    if (!(error instanceof SyntaxError)) throw error;
    const line = errorLine(text, error);
    throw new FileError(file, `not valid JSON${line === null ? "" : ` (line ${line})`}`);
  }
}

function errorLine(text: string, error: SyntaxError): number | null {
  const found = /at position (\d+)/.exec(error.message);
  let position = found ? Number(found[1]) : null;
  // V8 names no position for an unexpected token, so find the shortest prefix that fails on it.
  for (let end = 1; position === null && end <= text.length; end++) {
    try {
      JSON.parse(text.slice(0, end));
    } catch (prefix) {
      if (prefix instanceof SyntaxError && prefix.message.startsWith("Unexpected token")) {
        position = end - 1;
      }
    }
  }
  return position === null ? null : text.slice(0, position).split("\n").length;
}

/** Sorts each object's keys, so a file reads the same whatever order the scan built it in. */
const sorted = (_key: string, value: unknown) =>
  value !== null && typeof value === "object" && !Array.isArray(value)
    ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)))
    : value;

/** Replaces `file` with `text` in one step: a crash leaves the old file or the new one, never half. */
export function writeText(file: string, text: string): void {
  mkdirSync(dirname(file), { recursive: true });
  const temporary = join(dirname(file), `.${process.pid}.${Date.now()}.tmp`);
  writeFileSync(temporary, text, { flag: "wx" });
  renameSync(temporary, file);
}

export function writeJson(file: string, value: unknown): void {
  writeText(file, `${JSON.stringify(value, sorted, 1)}\n`);
}

function running(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return code(error) === "EPERM";
  }
}

/** Whether the lock someone left can be taken: its process is gone, or it never wrote one. */
function stale(file: string): boolean {
  try {
    const holder: unknown = JSON.parse(readFileSync(file, "utf8"));
    const pid =
      typeof holder === "object" && holder !== null && "pid" in holder ? holder.pid : null;
    if (typeof pid === "number") return !running(pid);
  } catch (error) {
    if (code(error) === "ENOENT") return false;
  }
  // A holder that crashed between creating the lock and writing its pid leaves it empty.
  return Date.now() - statSync(file).mtimeMs > 10_000;
}

/**
 * Runs `body` holding `folder/.lock`, waiting up to `waitMs` for another scan to finish; returns
 * "busy" when it stays taken. The lock holds this process's pid and start time, so a lock whose
 * process no longer runs is stale and taken over, and it is removed however `body` ends.
 */
export function withLock<T>(folder: string, waitMs: number, body: () => T): T | "busy" {
  mkdirSync(folder, { recursive: true });
  const file = join(folder, ".lock");
  const deadline = Date.now() + waitMs;
  for (;;) {
    try {
      const handle = openSync(file, "wx");
      writeSync(handle, JSON.stringify({ pid: process.pid, started: new Date().toISOString() }));
      closeSync(handle);
      break;
    } catch (error) {
      if (code(error) !== "EEXIST") throw error;
    }
    try {
      if (stale(file)) {
        unlinkSync(file);
        continue;
      }
    } catch (error) {
      if (code(error) !== "ENOENT") throw error;
      continue;
    }
    if (Date.now() >= deadline) return "busy";
    sleep(500);
  }
  try {
    return body();
  } finally {
    unlinkSync(file);
  }
}
