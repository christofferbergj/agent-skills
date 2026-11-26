/** Danish wall-clock times through both daylight-saving changes, with no timezone library. */
import assert from "node:assert/strict";
import { test } from "node:test";

import { parse } from "../parse.ts";
import { calendarDate, localIso, local, midnight, parseTime, shortTime } from "../time.ts";
import { Org } from "./helpers.ts";

const ZONE = "Europe/Copenhagen";

const at = (instant: string) => {
  const moment = local(new Date(instant), ZONE);
  return `${moment.date} ${moment.clock} +${moment.offset}`;
};
const utcOf = (written: string) => parseTime(written, ZONE)?.toISOString();

test("summer time starts on the last Sunday of March, when 02:00 becomes 03:00", () => {
  assert.equal(at("2026-03-29T00:59:00Z"), "2026-03-29 01:59 +60");
  assert.equal(at("2026-03-29T01:00:00Z"), "2026-03-29 03:00 +120");
  assert.equal(utcOf("2026-03-29T01:30"), "2026-03-29T00:30:00.000Z");
  // 02:30 never happens that day; it reads with the offset from before the change, as 03:30.
  assert.equal(utcOf("2026-03-29T02:30"), "2026-03-29T01:30:00.000Z");
  assert.equal(utcOf("2026-03-29T03:30"), "2026-03-29T01:30:00.000Z");
  assert.equal(
    midnight(parse(calendarDate, "2026-03-29"), ZONE, 1).toISOString(),
    "2026-03-29T22:00:00.000Z",
  );
});

test("summer time ends on the last Sunday of October, when 03:00 becomes 02:00", () => {
  assert.equal(at("2026-10-25T00:30:00Z"), "2026-10-25 02:30 +120");
  assert.equal(at("2026-10-25T01:30:00Z"), "2026-10-25 02:30 +60");
  // 02:30 happens twice that day; a time written without an offset is the first of the two.
  assert.equal(utcOf("2026-10-25T02:30"), "2026-10-25T00:30:00.000Z");
  assert.equal(utcOf("2026-10-25T03:30"), "2026-10-25T02:30:00.000Z");
  assert.equal(
    midnight(parse(calendarDate, "2026-10-25"), ZONE, 1).toISOString(),
    "2026-10-25T23:00:00.000Z",
  );
});

test("a time written with an offset keeps it, and one that isn't a time is null", () => {
  assert.equal(utcOf("2026-11-26T14:00+01:00"), "2026-11-26T13:00:00.000Z");
  assert.equal(utcOf("2026-11-26T14:00:00.250Z"), "2026-11-26T14:00:00.250Z");
  assert.equal(parseTime("26/11/2026 14:00"), null);
  assert.equal(parseTime("2026-13-01T00:00"), null);
});

test("a time that doesn't exist is null, never another time it rolls over to", () => {
  for (const text of [
    "2026-02-30T14:00", // 30 February
    "2026-02-29", // 2026 is no leap year
    "2026-04-31T09:00",
    "2026-11-26T14:99",
    "2026-11-26T14:60",
    "2026-11-26T24:00",
    "2026-11-26T14:00:61Z",
    "2026-11-26T14:00+25:00",
    "2026-11-26T14:00+01:75",
    "0099-01-01T00:00Z", // Date.UTC reads a year under 100 as 19xx
  ]) {
    assert.equal(parseTime(text, ZONE), null, text);
  }
  assert.equal(utcOf("2028-02-29T12:00"), "2028-02-29T11:00:00.000Z");
  assert.equal(utcOf("2026-11-26T14:00-11:30"), "2026-11-27T01:30:00.000Z");
});

test("times read as the user sees them, in summer and in winter", () => {
  const summer = local(new Date("2026-06-01T07:05:00Z"), ZONE);
  assert.equal(localIso(summer), "2026-06-01T09:05+02:00");
  assert.equal(summer.isWeekday, true);
  assert.equal(shortTime(new Date("2026-11-28T13:00:00Z"), ZONE), "Sat 28 Nov 14:00");
  assert.equal(local(new Date("2026-11-28T13:00:00Z"), ZONE).isWeekday, false);
});

test("the overview goes out at 09:05 Danish time on the Mondays after both changes", (t) => {
  for (const [baseline, overview] of [
    ["2026-03-30T06:30:00Z", "2026-03-30T07:05:00Z"],
    ["2026-10-26T07:30:00Z", "2026-10-26T08:05:00Z"],
  ] as const) {
    const org = new Org(t);
    assert.equal(org.cli(["scan", "acme"], baseline).code, 0);
    const early = JSON.parse(
      org.cli(["scan", "acme"], new Date(Date.parse(overview) - 10 * 60_000).toISOString()).stdout,
    );
    assert.equal(early.reason, "outside the scan window");
    const done = org.cli(["scan", "acme"], overview);
    assert.equal(JSON.parse(done.stdout).wake, "overview", done.stderr);
  }
});
