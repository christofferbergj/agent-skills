/**
 * `assistant.ts status`: the health line, a warning for each sign that the scan or the thread is
 * broken, the batches in flight, and the holds. The warnings' times come from the profile's
 * schedule: the stamp counts as old from shortly after the window opens, and the overview as
 * missing when the scan froze none today by half an hour after it is due. An overview frozen but
 * not yet posted shows on the "In flight" line instead, since the run posting it reads this first.
 * The scan gives up on it, failing its unit, only on an idle thread, so while the thread stays busy
 * that line is the only sign.
 */
import { join } from "node:path";

import { EMPTY_LEDGER, deliveredNote, ledgerParser } from "./ledger.ts";
import { EMPTY_PENDING, pendingParser } from "./pending.ts";
import { holds, overviewDue } from "./policy.ts";
import { loadProfile } from "./profile.ts";
import { healthLine, snapshotParser } from "./snapshot.ts";
import { readJson, readText, stateDir } from "./store.ts";
import { MINUTE, addMinutes, local, minutesAgo, parseTime, shortTime } from "./time.ts";

/** A stamp older than this, inside the window, means the timer may have stopped. */
const STALE = 90 * MINUTE;
/** How long after the window opens the first scan of the day has had to run. */
const FIRST_SCAN = 15;
/** How long after the overview is due it should have been delivered. */
const OVERVIEW_GRACE = 30;

export function status(org: string, now: Date): string {
  const profile = loadProfile(org);
  const zone = profile.timezone;
  const folder = stateDir(org);
  const snapshot = readJson(join(folder, "snapshot.json"), snapshotParser);
  const pending = readJson(join(folder, "pending.json"), pendingParser);
  const ledger = readJson(join(folder, "ledger.json"), ledgerParser) ?? EMPTY_LEDGER;
  const at = local(now, zone);
  const [opens, closes] = profile.schedule.window;
  const lines = [
    snapshot === null ? "Health: no scan has run yet" : `Health: ${healthLine(snapshot, zone)}`,
  ];

  const stamp = parseTime(readText(join(folder, "scan.stamp")) ?? "");
  const inWindow = addMinutes(opens, FIRST_SCAN) <= at.clock && at.clock <= closes;
  if (stamp === null || (inWindow && now.getTime() - stamp.getTime() > STALE)) {
    const age = stamp === null ? "never" : `${minutesAgo(stamp, now)} min ago`;
    lines.push(`⚠️ The last scan ran ${age}: the timer may be stopped.`);
  }

  const hold = holds(ledger, now);
  const due = addMinutes(profile.schedule.overview, OVERVIEW_GRACE);
  const situation = { at, schedule: profile.schedule, hold, pending: pending ?? EMPTY_PENDING };
  if (overviewDue(situation, due)) {
    lines.push(`⚠️ No overview sent today by ${due}: the scan or the thread may be broken.`);
  }

  for (const [name, state] of Object.entries(snapshot?.health ?? {}).sort(([a], [b]) =>
    a < b ? -1 : 1,
  )) {
    if (!state.ok) lines.push(`⚠️ ${name}: ${state.message}`);
  }
  if (pending?.sent) {
    const { id, kind, items, tries } = pending.sent;
    const done = deliveredNote(ledger, id);
    lines.push(
      `In flight: batch ${id} (${kind}, ${items.length} items, ${tries.length} wakes${done})`,
    );
  }
  if (pending?.inline) {
    const done = deliveredNote(ledger, pending.inline.id);
    lines.push(
      `Inline, not yet delivered: batch ${pending.inline.id} (${pending.inline.items.length} items${done})`,
    );
  }
  lines.push(`Gathered since: ${pending?.gathered.length ?? 0} changes`);
  if (hold.quiet !== null) lines.push(`Quiet until ${shortTime(new Date(hold.quiet), zone)}`);
  if (hold.paused !== null) lines.push(`Paused until ${shortTime(new Date(hold.paused), zone)}`);
  return lines.join("\n");
}
