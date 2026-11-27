/**
 * The organisation assistant's scan and state, with no model. `references/scan.md` and
 * `references/state.md` describe what each command reads and writes.
 *
 *   assistant.ts scan [ORG ...] [--dry-run] [--since 24h]
 *       scan each organisation (default: every profile), each in a process of its own, and wake its
 *       thread when there is news; --dry-run reads the sources, prints the batch it would send, and
 *       writes and sends nothing
 *   assistant.ts scan ORG --inline
 *       scan inside the assistant's own run ("scan now"): wake nothing, freeze everything gathered
 *       as one batch, and print it for the run to post
 *   assistant.ts org [--name NAME]
 *       the organisation this assistant thread serves: the one whose profile names the thread in
 *       $T3CODE_THREAD_ID, or else the one named NAME, from the title `✦ NAME assistant`
 *   assistant.ts status ORG
 *       the health line, the scan stamp's age, the batch in flight, and the holds
 *   assistant.ts batch ORG [ID]
 *       the batch to post, as text: batch ID, or else the sent batch, or else the inline one, each
 *       item with its kind, link, age, and detail
 *   assistant.ts ledger ORG COMMAND ...
 *       the model's edits to ledger.json; `assistant.ts ledger ORG -h` lists them
 *
 * Exits 1 when a unit should fail (two undelivered wakes, a source failing three scans in a row, or
 * an unreadable profile or state file), when `org` finds no one organisation or `batch` doesn't find
 * batch ID, and 2 on a usage error. Times are UTC in files and the profile's timezone on screen.
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";

import { renderBatch } from "./batch.ts";
import { COMMANDS, type Command, EMPTY_LEDGER, LedgerError, ledgerParser } from "./ledger.ts";
import { ShapeError } from "./parse.ts";
import { pendingParser } from "./pending.ts";
import type { Mode } from "./policy.ts";
import { loadProfile, matchOrgs, orgs } from "./profile.ts";
import { scanOrg } from "./scan.ts";
import { status } from "./status.ts";
import { FileError, readJson, stateDir, withLock, writeJson } from "./store.ts";
import { HOUR, parseTime } from "./time.ts";

const USAGE = `usage: assistant.ts scan [ORG ...] [--dry-run] [--since 24h]
       assistant.ts scan ORG --inline
       assistant.ts org [--name NAME]
       assistant.ts status ORG
       assistant.ts batch ORG [ID]
       assistant.ts ledger ORG COMMAND ...   (assistant.ts ledger ORG -h lists the commands)`;

class UsageError extends Error {}

/** `org` found no organisation, or more than one. */
class LookupError extends Error {}

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
  // The words after a command are its operands, such as an offer's text, so none is echoed; nor is
  // a first word that doesn't read as a command's name.
  const [first = ""] = words;
  const named = /^[a-z]+$/.test(first) ? ` ${first}` : "";
  throw new UsageError(`unknown ledger command${named}; assistant.ts ledger ORG -h lists them`);
}

function ledger(org: string, words: string[], options: Record<string, unknown>, now: Date): string {
  const { name, command, args } = ledgerCommand(words);
  if (args.length !== command.args.length) {
    const wants = command.args.map((arg) => `<${arg}>`).join(" ") || "no arguments";
    throw new UsageError(`ledger ${name} takes ${wants}`);
  }
  const zone = loadProfile(org).timezone;
  const folder = stateDir(org);
  const file = join(folder, "ledger.json");
  const execute = () => {
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
  };
  // Every write replaces the file whole, so a command that only reads needs no lock; one that writes
  // reads the ledger and writes it back, so two at once would lose one's change.
  if (!command.writes) return execute();
  const done = withLock(join(folder, ".ledger.lock"), execute);
  if (done === "busy") throw new FileError(file, "another ledger command holds it; run this again");
  return done;
}

/**
 * The one organisation this assistant thread serves, by its id or else by the title's `name`; one
 * whose profile then fails to load fails, naming its file.
 */
function findOrg(name: string | null): string {
  const thread = process.env.T3CODE_THREAD_ID || null;
  const { matches, by, unreadable } = matchOrgs({ thread, name });
  const [org, ...more] = matches;
  if (org !== undefined && more.length === 0) return loadProfile(org).org;
  if (org !== undefined) {
    const field = by === "thread" ? "this thread's id" : `the name ${name}`;
    throw new LookupError(`${matches.length} profiles match ${field}: ${matches.join(", ")}`);
  }
  const tried = [thread && "this thread's id", name && `the name ${name}`].filter(Boolean);
  const broken =
    unreadable.length > 0 ? `; can't read the profiles of ${unreadable.join(", ")}` : "";
  throw new LookupError(
    `no profile matches ${tried.join(" or ") || "anything: give --name"}${broken}`,
  );
}

/** The batch to post: the one named `id`, or else the sent batch, or else the inline one. */
function batch(org: string, id: string | null, now: Date): string {
  const sources = loadProfile(org).sources;
  const folder = stateDir(org);
  const pending = readJson(join(folder, "pending.json"), pendingParser);
  const book = readJson(join(folder, "ledger.json"), ledgerParser) ?? EMPTY_LEDGER;
  const frozen = [pending?.sent, pending?.inline].flatMap((entry) => entry ?? []);
  const chosen = id === null ? frozen[0] : frozen.find((entry) => entry.id === id);
  if (chosen === undefined) {
    if (id === null) return "No batch waits to be posted.";
    throw new LookupError(`no batch ${id} waits to be posted: it went out already, or never froze`);
  }
  const delivered = book.delivered.some((entry) => entry.batch === chosen.id);
  return renderBatch(chosen, { now, sources, delivered });
}

/**
 * Scans each organisation in a process of its own, so one that crashes or can't write its state
 * fails only itself; the exit code is the worst of theirs.
 */
function scanEach(orgs: string[], flags: string[]): number {
  const script = fileURLToPath(import.meta.url);
  const codes = orgs.map(
    (org) =>
      spawnSync(process.execPath, [script, "scan", org, ...flags], { stdio: "inherit" }).status ??
      1,
  );
  return Math.max(0, ...codes);
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
  org: { name: { type: "string" } },
  status: NOW,
  batch: NOW,
  ledger: {
    ...NOW,
    until: { type: "string" },
    ticket: { type: "string" },
    remove: { type: "boolean" },
    help: { type: "boolean", short: "h" },
  },
} as const;

const parse = <O extends (typeof OPTIONS)[keyof typeof OPTIONS]>(args: string[], options: O) =>
  parseArgs({ args, options, allowPositionals: true, strict: true, tokens: true });

function run(command: string | undefined, args: string[]): number {
  if (command === "scan") {
    const { values, positionals, tokens } = parse(args, OPTIONS.scan);
    if (values["dry-run"] && values.inline)
      throw new UsageError("a scan is --dry-run or --inline, not both");
    if (values.inline && positionals.length !== 1)
      throw new UsageError("--inline scans exactly one organisation");
    const mode: Mode = values["dry-run"] ? "dry" : values.inline ? "inline" : "timer";
    const options = { mode, since: values.since === undefined ? null : duration(values.since) };
    const at = instant(values.now);
    const [org] = positionals;
    if (org !== undefined && positionals.length === 1) return scanOrg(org, at, options);
    const named = new Set(
      tokens.flatMap((token) => (token.kind === "positional" ? token.index : [])),
    );
    const flags = args.filter((_, index) => !named.has(index));
    return scanEach(positionals.length > 0 ? positionals : orgs(), flags);
  }
  if (command === "org") {
    const { values, positionals } = parse(args, OPTIONS.org);
    if (positionals.length > 0) throw new UsageError("org takes no organisation, only --name");
    process.stdout.write(`${findOrg(values.name ?? null)}\n`);
    return 0;
  }
  if (command === "status") {
    const { values, positionals } = parse(args, OPTIONS.status);
    const [org, ...more] = positionals;
    if (org === undefined || more.length > 0) throw new UsageError("status takes one organisation");
    process.stdout.write(`${status(org, instant(values.now))}\n`);
    return 0;
  }
  if (command === "batch") {
    const { values, positionals } = parse(args, OPTIONS.batch);
    const [org, id = null, ...more] = positionals;
    if (org === undefined || more.length > 0)
      throw new UsageError("batch takes one organisation and, optionally, a batch id");
    process.stdout.write(`${batch(org, id, instant(values.now))}\n`);
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
    if (
      error instanceof FileError ||
      error instanceof LedgerError ||
      error instanceof LookupError
    ) {
      process.stderr.write(`assistant.ts: ${error.message}\n`);
      return 1;
    }
    throw error;
  }
}

if (import.meta.main) process.exitCode = main(process.argv.slice(2));
