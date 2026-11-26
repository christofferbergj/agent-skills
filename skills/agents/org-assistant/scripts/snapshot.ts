/**
 * snapshot.json: each source's section, its cursors and fingerprints, which only its adapter reads;
 * each source's health; where a source not yet read starts counting, its first attempt or an
 * earlier start `--since` gave; and the last scan's time.
 */
import {
  type Infer,
  count,
  literal,
  nullable,
  object,
  oneOf,
  record,
  string,
  unknown,
  withDefault,
} from "./parse.ts";
import { shortTime } from "./time.ts";

/** The health entry for reading the assistant thread itself, beside the sources'. */
export const THREAD = "assistant thread";

const health = oneOf(
  object({ ok: literal(true), at: string }),
  object({
    ok: literal(false),
    /** When it last succeeded. */
    at: nullable(string),
    failures: count,
    error: literal("auth", "failed"),
    /**
     * What failed and its category, such as `Executor call: sign-in expired`, never a tool's text.
     */
    message: string,
  }),
);
export type Health = Infer<typeof health>;

export const snapshotParser = object({
  sources: withDefault(record(unknown), {}),
  health: withDefault(record(health), {}),
  starts: withDefault(record(string), {}),
  last_scan: nullable(string),
});
export type Snapshot = Infer<typeof snapshotParser>;

export const EMPTY_SNAPSHOT: Snapshot = { sources: {}, health: {}, starts: {}, last_scan: null };

/** `linear ok · slack sign-in expired ×2 · scanned Thu 26 Nov 10:05`. */
export function healthLine(snapshot: Snapshot, zone: string): string {
  const parts = Object.entries(snapshot.health)
    .sort(([a], [b]) => (a < b ? -1 : 1))
    .map(([name, state]) =>
      state.ok
        ? `${name} ok`
        : `${name} ${state.error === "auth" ? "sign-in expired" : "failing"} ×${state.failures}`,
    );
  const scanned =
    snapshot.last_scan === null ? "never" : shortTime(new Date(snapshot.last_scan), zone);
  return [...parts, `scanned ${scanned}`].join(" · ");
}
