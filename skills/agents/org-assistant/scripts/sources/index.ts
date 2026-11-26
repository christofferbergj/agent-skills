/**
 * One adapter per kind of source. Each reads its source, compares what it finds with its section of
 * the last snapshot, and returns its new section and its changes. A new kind, such as
 * `azure-boards`, is a module here with the same shape, a case in `scanSource`, and its kinds in
 * KINDS; until it exists, a profile that names it fails that source on every scan, so the gap
 * shows in the health line instead of passing silently.
 */
import { SourceError, read } from "../calls.ts";
import type { Change, ChangeFields, ChangeKind, ChangeOf } from "../changes.ts";
import type { Ledger } from "../ledger.ts";
import type { Parser } from "../parse.ts";
import type { Schedule, Source } from "../profile.ts";
import { github } from "./github.ts";
import { linear } from "./linear.ts";
import { slack } from "./slack.ts";
import { t3 } from "./t3.ts";

/**
 * Where a source's scan starts. `resume` compares with the source's last section; a source with no
 * section yet records a `baseline` on the organisation's first scan and returns no changes, or
 * counts changes `since` a time: its first attempt, or an earlier start `--since` gave it.
 */
export type Window<S> =
  | { kind: "resume"; prev: S }
  | { kind: "since"; since: Date }
  | { kind: "baseline" };
export type Fresh = Exclude<Window<never>, { kind: "resume" }>;

export type Context = {
  now: Date;
  zone: string;
  schedule: Schedule;
  ledger: Ledger;
  /** The assistant thread, which the T3 source leaves out. */
  thread: string | null;
  /** A change found by this source. */
  change<K extends ChangeKind>(kind: K, fields: ChangeFields<K>): ChangeOf<K>;
};

export type Result<S> = {
  section: S;
  changes: Change[];
  /** Whether a change this source found earlier, still gathered, is still true. */
  still?: (item: Change) => boolean;
};

export type Adapter<Src, S> = {
  /** Reads the source's section of the snapshot, as this adapter last wrote it. */
  section: Parser<S>;
  scan(source: Src, window: Window<S>, ctx: Context): Result<S>;
};

const PLANNED: Record<string, string> = {
  "azure-boards": "the Azure Boards adapter is not built yet; see references/scan.md",
};

/** Where a source's scan starts: its last section, `prev`, or `fresh` when it has none yet. */
export type Start = { prev: unknown; fresh: Fresh; ctx: Context };

/**
 * Runs `adapter` from where `scan` says. Any error but a SourceError, such as a value no parser
 * caught, fails the source too, named by the error's type alone, since its message can quote what
 * the adapter read; the other sources still scan.
 */
export function scanWith<Src, S>(
  scan: Start & { adapter: Adapter<Src, S>; source: Src },
): Result<unknown> {
  const { adapter, source, prev, fresh, ctx } = scan;
  const window: Window<S> =
    prev === undefined
      ? fresh
      : { kind: "resume", prev: read(adapter.section, prev, "its snapshot section") };
  try {
    return adapter.scan(source, window, ctx);
  } catch (error) {
    if (error instanceof SourceError) throw error;
    const type = error instanceof Error ? error.name : typeof error;
    throw new SourceError(`failed unexpectedly (${type})`, { cause: error });
  }
}

/** Scans one source from where `start` says. */
export function scanSource(source: Source, start: Start): Result<unknown> {
  switch (source.kind) {
    case "linear":
      return scanWith({ ...start, adapter: linear, source });
    case "slack":
      return scanWith({ ...start, adapter: slack, source });
    case "github":
      return scanWith({ ...start, adapter: github, source });
    case "t3":
      return scanWith({ ...start, adapter: t3, source });
    case "unbuilt":
      throw new SourceError(PLANNED[source.wanted] ?? `no adapter for kind ${source.wanted}`);
    default: {
      const unhandled: never = source;
      return unhandled;
    }
  }
}
