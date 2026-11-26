/**
 * The scan's only ways out: Executor tool calls through `probe.ts`, and the `gh` and `t3` CLIs.
 * Every Executor call must name a tool the profile's source lists under `tools` and must not look
 * like a write, so a profile typo can't make the scan change a source. Each response is parsed,
 * here or in its adapter, before anything reads it; a shape the parser doesn't know fails a source.
 */
import { spawnSync } from "node:child_process";
import { existsSync, statSync } from "node:fs";

import { type Parser, ShapeError, isRecord, parse } from "./parse.ts";

/**
 * A source that could not be read this scan, by what failed and its category; `auth` when its
 * sign-in looks expired. `cause` holds an unexpected error it stands in for, whose message is never
 * shown.
 */
export class SourceError extends Error {
  readonly auth: boolean;

  constructor(message: string, options: { auth?: boolean; cause?: unknown } = {}) {
    super(message, { cause: options.cause });
    this.auth = options.auth ?? false;
  }
}

const WRITE =
  /(^|[._])(mark|save|create|update|delete|archive|retire|restore|send|draft|schedule|post|add|remove|set|invite|upload|complete|react)[_a-z]*$/;
export const LIMITED = /\b429\b|limiting requests|rate.?limit/i;
const HTTP = /\bHTTP (\d{3})\b/;
const AUTH =
  /unauthori[sz]ed|reauth|re-auth|sign[ -]?in|log[ -]?in again|expired|invalid_auth|not_authed|token_revoked|\b401\b|connect(ion)? link/i;
const TIMEOUT = 300_000;

/**
 * A failed call or command, named by what failed and a category read from its error text: sign-in,
 * rate limit, or HTTP status. The text itself is dropped, since a tool's error can quote the ticket
 * or message it was reading.
 */
export function failure(what: string, text: unknown): SourceError {
  const words = typeof text === "string" ? text : text === undefined ? "" : JSON.stringify(text);
  if (AUTH.test(words)) return new SourceError(`${what}: sign-in expired`, { auth: true });
  if (LIMITED.test(words)) return new SourceError(`${what}: rate limited`);
  const status = HTTP.exec(words);
  return new SourceError(`${what}: failed${status ? ` (HTTP ${status[1]})` : ""}`);
}

/** A response read by `parser`; a shape it doesn't know fails the source, naming the field only. */
export function read<T>(parser: Parser<T>, value: unknown, what: string): T {
  try {
    return parse(parser, value);
  } catch (error) {
    if (error instanceof ShapeError) {
      throw new SourceError(`${what}: unexpected response${error.path ? ` at ${error.path}` : ""}`);
    }
    throw error;
  }
}

export type Ran = { code: number; stdout: string; stderr: string };

export function run(args: readonly string[], options: { cwd?: string; stdin?: string } = {}): Ran {
  const [command = "", ...rest] = args;
  const done = spawnSync(command, rest, {
    cwd: options.cwd,
    input: options.stdin ?? "",
    encoding: "utf8",
    timeout: TIMEOUT,
    maxBuffer: 64 * 1024 * 1024,
  });
  if (done.error !== undefined) return { code: 127, stdout: "", stderr: done.error.message };
  return { code: done.status ?? 1, stdout: done.stdout, stderr: done.stderr };
}

/** The JSON a CLI prints, which may follow a warning line, read by `parser`. */
export function runJson<T>(
  args: readonly string[],
  what: string,
  parser: Parser<T>,
  options: { cwd?: string } = {},
): T {
  const done = run(args, options);
  if (done.code !== 0) throw failure(`${what} (exit ${done.code})`, done.stderr || done.stdout);
  const starts = [...done.stdout.matchAll(/^[[{]/gm)].map((match) => match.index);
  for (const start of starts) {
    let value: unknown;
    try {
      value = JSON.parse(done.stdout.slice(start));
    } catch {
      continue;
    }
    return read(parser, value, what);
  }
  throw new SourceError(`${what}: no JSON in its output`);
}

/**
 * How a source reaches Executor: the command, the account, the repository to call from, its tools.
 */
export type ExecutorSource = { command: string[]; account: string; repo?: string; tools: string[] };
export type ToolCall = { path: string; input: Record<string, unknown> };

const textOf = (content: unknown) =>
  Array.isArray(content)
    ? content
        .map((part) => (isRecord(part) && typeof part.text === "string" ? part.text : ""))
        .join("")
    : "";

/** Calls Executor tools for one source, from the repository its profile names. */
export class Executor {
  readonly #source: ExecutorSource;
  readonly #allowed: ReadonlySet<string>;

  /** `tools` are the ones the adapter may call; only those the source also lists are allowed. */
  constructor(source: ExecutorSource, tools: readonly string[]) {
    this.#source = source;
    this.#allowed = new Set(source.tools.filter((tool) => tools.includes(tool)));
  }

  /** Each call's result, in order. Any refused, failed, or unreadable call fails the source. */
  call(calls: readonly ToolCall[]): unknown[] {
    return this.#results(calls).map((result) => {
      if (result instanceof SourceError) throw result;
      return result;
    });
  }

  /** Each call's result, or null for one that failed for any reason but an expired sign-in. */
  callEach(calls: readonly ToolCall[]): unknown[] {
    return this.#results(calls).map((result) => {
      if (result instanceof SourceError && result.auth) throw result;
      return result instanceof SourceError ? null : result;
    });
  }

  #results(calls: readonly ToolCall[]): unknown[] {
    if (calls.length === 0) return [];
    for (const { path } of calls) {
      if (!this.#allowed.has(path)) throw new SourceError(`${path} is not in this source's tools`);
      if (WRITE.test(path.slice(path.lastIndexOf(".") + 1))) {
        throw new SourceError(`${path} looks like a write, and the scan only reads`);
      }
    }
    const { command, account, repo } = this.#source;
    if (repo !== undefined && !(existsSync(repo) && statSync(repo).isDirectory())) {
      throw new SourceError(`its repository ${repo} is missing`);
    }
    const body = {
      calls: calls.map(({ path, input }) => ({ path, input: { accountId: account, input } })),
    };
    const done = run([...command, "call", JSON.stringify(body)], { cwd: repo });
    if (done.code !== 0) throw failure(`Executor (exit ${done.code})`, done.stderr || done.stdout);
    let execution: Record<string, unknown> | undefined;
    for (const line of done.stdout.split("\n")) {
      if (!line.startsWith("{")) continue;
      try {
        const printed: unknown = JSON.parse(line);
        const found =
          isRecord(printed) &&
          isRecord(printed.result) &&
          isRecord(printed.result.structuredContent)
            ? printed.result.structuredContent.execution
            : undefined;
        if (isRecord(found)) execution = found;
      } catch {
        continue;
      }
    }
    if (execution === undefined) throw new SourceError("Executor printed no result");
    if (!("value" in execution)) throw failure("Executor call", execution.error);
    const values = Array.isArray(execution.value) ? execution.value : [execution.value];
    if (values.length !== calls.length) {
      throw new SourceError("Executor returned a different number of results than calls");
    }
    return values.map((value, index) => {
      try {
        return unwrap(calls[index]?.path ?? "", value);
      } catch (error) {
        if (error instanceof SourceError) return error;
        throw error;
      }
    });
  }
}

/** One call's value: its structured content, or the JSON (or text) its text content holds. */
function unwrap(path: string, value: unknown): unknown {
  if (!isRecord(value) || value.ok !== true) {
    throw failure(path, isRecord(value) ? value.error : undefined);
  }
  const inner = "value" in value ? value.value : value;
  if (!isRecord(inner)) return inner;
  if (inner.isError) throw failure(path, textOf(inner.content));
  if (isRecord(inner.structuredContent) && Object.keys(inner.structuredContent).length > 0) {
    return inner.structuredContent;
  }
  if (Array.isArray(inner.content) && inner.content.length > 0) {
    const text = textOf(inner.content);
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }
  return inner;
}
