/**
 * Where an organisation's profile and state live, and how the files are read and written. Each
 * state file has one writer: the scan writes snapshot.json, pending.json, and scan.stamp; the model
 * writes ledger.json through `assistant.ts ledger`; and the first run that locks the folder, a scan
 * or a ledger command, writes `.lock-backend` once, recording how the folder's locks are taken.
 * Every write replaces its file atomically; a scan holds `.lock` and a ledger command that writes
 * `.ledger.lock`, so two of either never run at once.
 */
import { spawnSync } from "node:child_process";
import {
  closeSync,
  linkSync,
  mkdirSync,
  openSync,
  readFileSync,
  renameSync,
  unlinkSync,
  writeFileSync,
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

/**
 * A JSON file's value read by `parser`, or null when the file doesn't exist. A file that isn't JSON,
 * or holds a shape the parser doesn't know, fails its organisation, named by its line or field.
 */
export function readJson<T>(file: string, parser: Parser<T>): T | null {
  const text = readText(file);
  if (text === null) return null;
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch (error) {
    if (!(error instanceof SyntaxError)) throw error;
    // V8's message can quote the text around the error, so only its line is kept.
    const line = errorLine(text, error);
    throw new FileError(file, `not valid JSON${line === null ? "" : ` (line ${line})`}`);
  }
  try {
    return parse(parser, value);
  } catch (error) {
    if (error instanceof ShapeError) throw new FileError(file, error.message);
    throw error;
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

/** A new file's name beside `file`, for text that replaces it, or is linked to it, in one step. */
const temporaryBeside = (file: string) => join(dirname(file), `.${process.pid}.${Date.now()}.tmp`);

/** Sorts each object's keys, so a file reads the same whatever order the scan built it in. */
const sorted = (_key: string, value: unknown) =>
  value !== null && typeof value === "object" && !Array.isArray(value)
    ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)))
    : value;

/**
 * Replaces `file` with `text` in one step: a crash leaves the old file or the new one, never half.
 */
export function writeText(file: string, text: string): void {
  try {
    mkdirSync(dirname(file), { recursive: true });
    const temporary = temporaryBeside(file);
    writeFileSync(temporary, text, { flag: "wx" });
    renameSync(temporary, file);
  } catch (error) {
    throw new FileError(file, `can't be written (${code(error) || "error"})`);
  }
}

export function writeJson(file: string, value: unknown): void {
  writeText(file, `${JSON.stringify(value, sorted, 1)}\n`);
}

let flockFound: string | null | undefined;

/**
 * flock(1), on PATH or where util-linux installs it, so a caller whose PATH lacks it still finds it;
 * macOS has none. ORG_ASSISTANT_FLOCK names it instead, when it is elsewhere.
 */
function findFlock(): string | null {
  const named = process.env.ORG_ASSISTANT_FLOCK;
  const places = named ? [named] : ["flock", "/usr/bin/flock", "/bin/flock"];
  flockFound ??=
    places.find((place) => spawnSync(place, ["--version"], { stdio: "ignore" }).status === 0) ??
    null;
  return flockFound;
}

/** How a state folder's locks are taken: by flock(1), found at `path`, or as plain files. */
type Backend = { kind: "flock"; path: string } | { kind: "file" };

/**
 * The backend `folder`'s locks use, recorded in its `.lock-backend` by the first run that locks it,
 * so every caller on the machine takes the same lock. A caller that can't use the recorded one fails
 * its organisation, naming the file.
 */
function backendOf(folder: string): Backend {
  const record = join(folder, ".lock-backend");
  let recorded = readText(record)?.trim();
  if (recorded === undefined) {
    // Linked into place, so of two first runs one records its backend and the other reads it.
    const temporary = temporaryBeside(record);
    writeFileSync(temporary, `${findFlock() === null ? "file" : "flock"}\n`, { flag: "wx" });
    try {
      linkSync(temporary, record);
    } catch (error) {
      if (code(error) !== "EEXIST") throw error;
    } finally {
      unlinkSync(temporary);
    }
    recorded = readText(record)?.trim();
  }
  if (recorded === "file") return { kind: "file" };
  // flock(1) is looked up only where the folder records it, so a plain-file folder never runs it.
  const path = recorded === "flock" ? findFlock() : null;
  if (path !== null) return { kind: "flock", path };
  throw new FileError(
    record,
    recorded === "flock"
      ? "records flock locks, and this run can't find flock(1); install it, or set ORG_ASSISTANT_FLOCK"
      : "names no lock backend (flock or file); remove it while nothing runs, and the next run records one",
  );
}

/** A lock this process holds, and how it lets go. */
type Held = { release(): void };

/** flock(1)'s exit when another process holds the file: EX_TEMPFAIL. */
const BUSY = 75;

/**
 * Takes `file` with the flock(1) at `path` on a descriptor this process keeps open, so the kernel
 * holds it.
 */
function flock(file: string, path: string, waitSeconds: number): Held | null {
  const handle = openSync(file, "a");
  const args = ["--wait", String(waitSeconds), "--conflict-exit-code", String(BUSY), "3"];
  const taken = spawnSync(path, args, {
    stdio: ["ignore", "ignore", "inherit", handle],
  });
  if (taken.status === 0) return { release: () => closeSync(handle) };
  closeSync(handle);
  if (taken.status === BUSY) return null;
  throw new FileError(file, `can't be locked (flock exit ${taken.status ?? taken.signal})`);
}

/**
 * Takes `lock` by creating `lock.held`, polling until `waitSeconds` pass; releasing removes it. The
 * name is its own, so the file a lock taken with flock leaves behind never reads as taken.
 */
function create(lock: string, waitSeconds: number): Held | null {
  const file = `${lock}.held`;
  process.stderr.write(
    `org-assistant: locks here are plain files, as ${join(dirname(lock), ".lock-backend")} ` +
      `records, so a ${file} a crashed run leaves behind keeps later runs out until it is removed\n`,
  );
  const deadline = Date.now() + waitSeconds * 1000;
  for (;;) {
    try {
      closeSync(openSync(file, "wx"));
      return { release: () => unlinkSync(file) };
    } catch (error) {
      if (code(error) !== "EEXIST") throw error;
    }
    if (Date.now() >= deadline) return null;
    sleep(500);
  }
}

/**
 * Runs `body` holding `file`, waiting up to ORG_ASSISTANT_LOCK_WAIT seconds (60) for whoever holds
 * it; returns "busy" when it stays taken. flock(1) takes it for this process, so the kernel lets go
 * however the process ends, and the file itself stays: nothing a dead process left can keep a later
 * run out. Where the folder's first run found no flock, as on a Mac, the lock is `file.held`,
 * created exclusively and removed when `body` ends.
 */
export function withLock<T>(file: string, body: () => T): T | "busy" {
  const waitSeconds = Number(process.env.ORG_ASSISTANT_LOCK_WAIT ?? 60);
  let held: Held | null;
  try {
    mkdirSync(dirname(file), { recursive: true });
    const backend = backendOf(dirname(file));
    held =
      backend.kind === "flock" ? flock(file, backend.path, waitSeconds) : create(file, waitSeconds);
  } catch (error) {
    if (error instanceof FileError) throw error;
    throw new FileError(file, `can't be locked (${code(error) || "error"})`);
  }
  if (held === null) return "busy";
  try {
    return body();
  } finally {
    held.release();
  }
}
