/**
 * `assistant.ts status`: the health line, a warning for each sign that the scan or the thread is
 * broken, the batches in flight, and the holds. The warnings' times come from the profile's
 * schedule: the stamp counts as old from shortly after the window opens, and the overview as
 * missing when the scan froze none today by half an hour after it is due. An overview frozen but
 * not yet posted shows on the "In flight" line instead, since the run posting it reads this first;
 * the scan's give-up fails its unit when a thread never posts it.
 */
import { join } from "node:path";

import { EMPTY_LEDGER, ledgerParser } from "./ledger.ts";
import { pendingParser } from "./pending.ts";
import { holds, overviewOwed } from "./policy.ts";
import { loadProfile } from "./profile.ts";
import { healthLine, snapshotParser } from "./snapshot.ts";
import { readJson, readText, stateDir } from "./store.ts";
import { MINUTE, addMinutes, local, parseTime, shortTime } from "./time.ts";

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
    const age =
      stamp === null
        ? "never"
        : `${Math.floor((now.getTime() - stamp.getTime()) / MINUTE)} min ago`;
    lines.push(`⚠️ The last scan ran ${age}: the timer may be stopped.`);
  }

  const delivered = new Set(ledger.delivered.map((entry) => entry.batch));
  const frozen = pending?.meta.overview_on === at.date;
  const due = addMinutes(profile.schedule.overview, OVERVIEW_GRACE);
  if (!frozen && overviewOwed(at, profile.schedule, holds(ledger, now), due)) {
    lines.push(`⚠️ No overview sent today by ${due}: the scan or the thread may be broken.`);
  }

  for (const [name, state] of Object.entries(snapshot?.health ?? {}).sort(([a], [b]) =>
    a < b ? -1 : 1,
  )) {
    if (!state.ok) lines.push(`⚠️ ${name}: ${state.message}`);
  }
  if (pending?.sent) {
    const done = delivered.has(pending.sent.id) ? ", already marked delivered" : "";
    const { id, kind, items, tries } = pending.sent;
    lines.push(
      `In flight: batch ${id} (${kind}, ${items.length} items, ${tries.length} wakes${done})`,
    );
  }
  if (pending?.inline) {
    const done = delivered.has(pending.inline.id) ? ", already marked delivered" : "";
    lines.push(
      `Inline, not yet delivered: batch ${pending.inline.id} (${pending.inline.items.length} items${done})`,
    );
  }
  lines.push(`Gathered since: ${pending?.gathered.length ?? 0} changes`);
  const hold = holds(ledger, now);
  if (hold.quiet !== null) lines.push(`Quiet until ${shortTime(new Date(hold.quiet), zone)}`);
  if (hold.paused !== null) lines.push(`Paused until ${shortTime(new Date(hold.paused), zone)}`);
  return lines.join("\n");
}
