/**
 * The organisation assistant's scan and state, with no model. `references/scan.md` and
 * `references/state.md` describe what each command reads and writes.
 *
 *   assistant.ts scan [ORG ...] [--dry-run] [--since 24h]
 *       scan each organisation (default: every profile) and wake its thread when there is news;
 *       --dry-run reads the sources, prints the batch it would send, and writes and sends nothing
 *   assistant.ts scan ORG --inline
 *       scan inside the assistant's own run ("scan now"): wake nothing, freeze everything gathered
 *       as one batch, and print it for the run to post
 *   assistant.ts status ORG
 *       the health line, the scan stamp's age, the batch in flight, and the holds
 *   assistant.ts ledger ORG COMMAND ...
 *       the model's edits to ledger.json; `assistant.ts ledger ORG -h` lists them
 *
 * Exits 1 when a unit should fail (two undelivered wakes, a source failing three scans in a row, or
 * an unreadable profile or state file), and 2 on a usage error. Times are UTC in files and the
 * profile's timezone on screen.
 */
import { join } from "node:path";
import { parseArgs } from "node:util";

import { COMMANDS, type Command, EMPTY_LEDGER, LedgerError, ledgerParser } from "./ledger.ts";
import { ShapeError } from "./parse.ts";
import type { Mode } from "./policy.ts";
import { loadProfile, orgs } from "./profile.ts";
import { scanOrg } from "./scan.ts";
import { status } from "./status.ts";
import { FileError, readJson, stateDir, writeJson } from "./store.ts";
import { HOUR, parseTime } from "./time.ts";

const USAGE = `usage: assistant.ts scan [ORG ...] [--dry-run] [--since 24h]
       assistant.ts scan ORG --inline
       assistant.ts status ORG
       assistant.ts ledger ORG COMMAND ...   (assistant.ts ledger ORG -h lists the commands)`;

class UsageError extends Error {}

function duration(text: string): number {
  const match = /^(\d+)([hd])$/.exec(text);
  if (match === null) throw new UsageError("--since takes a duration such as 24h or 2d");
  return Number(match[1]) * (match[2] === "d" ? 24 : 1) * HOUR;
}

function instant(text: string | undefined): Date {
  if (text === undefined) return new Date();
  const parsed = parseTime(text);
  if (parsed === null) throw new UsageError(`--now takes an ISO time, not ${text}`);
  return parsed;
}

function ledgerHelp(): string {
  const rows = Object.entries(COMMANDS).map(([name, command]) => ({
    words: [
      name,
      ...command.args.map((arg) => `<${arg}>`),
      ...command.options.map((option) => `[--${option}]`),
    ].join(" "),
    help: command.help,
  }));
  const width = Math.max(...rows.map((row) => row.words.length));
  return `usage: assistant.ts ledger ORG COMMAND ...\n\n${rows.map((row) => `  ${row.words.padEnd(width)}  ${row.help}`).join("\n")}`;
}

/** The ledger command `words` name, such as `call set`, and the arguments after it. */
function ledgerCommand(words: string[]): { name: string; command: Command; args: string[] } {
  for (const take of [2, 1]) {
    const name = words.slice(0, take).join(" ");
    const command = COMMANDS[name];
    if (command !== undefined && words.length >= take)
      return { name, command, args: words.slice(take) };
  }
  throw new UsageError(
    `unknown ledger command ${words.join(" ") || "(none)"}; assistant.ts ledger ORG -h lists them`,
  );
}

function ledger(org: string, words: string[], options: Record<string, unknown>, now: Date): string {
  const { name, command, args } = ledgerCommand(words);
  if (args.length !== command.args.length) {
    const wants = command.args.map((arg) => `<${arg}>`).join(" ") || "no arguments";
    throw new UsageError(`ledger ${name} takes ${wants}`);
  }
  const zone = loadProfile(org).timezone;
  const file = join(stateDir(org), "ledger.json");
  const book = readJson(file, ledgerParser) ?? EMPTY_LEDGER;
  let outcome: ReturnType<Command["execute"]>;
  try {
    outcome = command.execute(book, args, options, { now, zone });
  } catch (error) {
    if (error instanceof ShapeError) throw new UsageError(`ledger ${name}: ${error.message}`);
    throw error;
  }
  if (outcome.ledger !== undefined) writeJson(file, outcome.ledger);
  return outcome.out;
}

const NOW = { now: { type: "string" } } as const;
/** Each command's options; `--now` sets the time, for tests. */
const OPTIONS = {
  scan: {
    ...NOW,
    "dry-run": { type: "boolean" },
    inline: { type: "boolean" },
    since: { type: "string" },
  },
  status: NOW,
  ledger: {
    ...NOW,
    until: { type: "string" },
    ticket: { type: "string" },
    remove: { type: "boolean" },
    help: { type: "boolean", short: "h" },
  },
} as const;

const parse = <O extends (typeof OPTIONS)[keyof typeof OPTIONS]>(args: string[], options: O) =>
  parseArgs({ args, options, allowPositionals: true, strict: true });

function run(command: string | undefined, args: string[]): number {
  if (command === "scan") {
    const { values, positionals } = parse(args, OPTIONS.scan);
    if (values["dry-run"] && values.inline)
      throw new UsageError("a scan is --dry-run or --inline, not both");
    if (values.inline && positionals.length !== 1)
      throw new UsageError("--inline scans exactly one organisation");
    const mode: Mode = values["dry-run"] ? "dry" : values.inline ? "inline" : "timer";
    const options = { mode, since: values.since === undefined ? null : duration(values.since) };
    const at = instant(values.now);
    const codes = (positionals.length > 0 ? positionals : orgs()).map((org) =>
      scanOrg(org, at, options),
    );
    return Math.max(0, ...codes);
  }
  if (command === "status") {
    const { values, positionals } = parse(args, OPTIONS.status);
    const [org, ...more] = positionals;
    if (org === undefined || more.length > 0) throw new UsageError("status takes one organisation");
    process.stdout.write(`${status(org, instant(values.now))}\n`);
    return 0;
  }
  if (command === "ledger") {
    const { values, positionals } = parse(args, OPTIONS.ledger);
    const { now, help, ...options } = values;
    const [org, ...words] = positionals;
    if (help) {
      process.stdout.write(`${ledgerHelp()}\n`);
      return 0;
    }
    if (org === undefined) throw new UsageError("ledger takes an organisation and a command");
    process.stdout.write(`${ledger(org, words, options, instant(now))}\n`);
    return 0;
  }
  if (command === "-h" || command === "--help") {
    process.stdout.write(`${USAGE}\n`);
    return 0;
  }
  throw new UsageError(command === undefined ? "name a command" : `unknown command ${command}`);
}

const isParseError = (error: unknown) =>
  error instanceof TypeError && "code" in error && String(error.code).startsWith("ERR_PARSE_ARGS");

export function main([command, ...args]: string[]): number {
  try {
    return run(command, args);
  } catch (error) {
    if (error instanceof UsageError || isParseError(error)) {
      process.stderr.write(
        `assistant.ts: ${error instanceof Error ? error.message : error}\n${USAGE}\n`,
      );
      return 2;
    }
    if (error instanceof FileError || error instanceof LedgerError) {
      process.stderr.write(`assistant.ts: ${error.message}\n`);
      return 1;
    }
    throw error;
  }
}

if (import.meta.main) process.exitCode = main(process.argv.slice(2));
