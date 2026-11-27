/**
 * Times, written UTC with a `Z` in every file and read in the profile's timezone for the wake rules
 * and on screen. Wall-clock times go through `Intl.DateTimeFormat`, so both daylight-saving changes
 * follow the timezone's own rules with no library.
 */
import { ShapeError, refine, string } from "./parse.ts";

/** A wall-clock time of day, `HH:MM`, which compares in order as a string. */
export type Clock = string & { readonly __brand: "Clock" };

export function isClock(value: string): value is Clock {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(value);
}

export const clock = refine(string, isClock, "expected a time of day such as 09:00");

export function isZone(name: string): boolean {
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: name });
    return true;
  } catch {
    return false;
  }
}

/** A moment as the profile's timezone reads it. */
export type Local = {
  instant: Date;
  zone: string;
  /** `YYYY-MM-DD`. */
  date: string;
  clock: Clock;
  /** Monday to Friday. */
  isWeekday: boolean;
  /** Minutes ahead of UTC. */
  offset: number;
};

type Wall = {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
};

const formats = new Map<string, Intl.DateTimeFormat>();

function wallAt(instant: Date, zone: string): Wall {
  let format = formats.get(zone);
  if (format === undefined) {
    format = new Intl.DateTimeFormat("en-US", {
      timeZone: zone,
      hourCycle: "h23",
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
    });
    formats.set(zone, format);
  }
  const parts = new Map(format.formatToParts(instant).map((part) => [part.type, part.value]));
  const read = (type: Intl.DateTimeFormatPartTypes) => Number(parts.get(type));
  return {
    year: read("year"),
    month: read("month"),
    day: read("day"),
    hour: read("hour"),
    minute: read("minute"),
    second: read("second"),
  };
}

const wallMs = (wall: Wall) =>
  Date.UTC(wall.year, wall.month - 1, wall.day, wall.hour, wall.minute, wall.second);

/** The zone's offset from UTC at `instant`, in milliseconds. */
function offsetAt(ms: number, zone: string): number {
  const whole = Math.floor(ms / 1000) * 1000;
  return wallMs(wallAt(new Date(whole), zone)) - whole;
}

const pad = (value: number, width = 2) => String(value).padStart(width, "0");

export function local(instant: Date, zone: string): Local {
  const wall = wallAt(instant, zone);
  const weekday = new Date(Date.UTC(wall.year, wall.month - 1, wall.day)).getUTCDay();
  const clockText = `${pad(wall.hour)}:${pad(wall.minute)}`;
  if (!isClock(clockText)) throw new Error(`the timezone ${zone} gave the time ${clockText}`);
  return {
    instant,
    zone,
    date: `${pad(wall.year, 4)}-${pad(wall.month)}-${pad(wall.day)}`,
    clock: clockText,
    isWeekday: weekday >= 1 && weekday <= 5,
    offset: Math.round(offsetAt(instant.getTime(), zone) / 60_000),
  };
}

/**
 * The instant a wall-clock time names in `zone`. A time that occurs twice, when the clocks go back,
 * is the first of the two; a time the clocks skip, when they go forward, reads with the offset from
 * before the change, so 02:30 on the day summer time starts is 03:30 summer time.
 */
function fromWall(wall: Wall, zone: string): Date {
  const naive = wallMs(wall);
  const before = naive - offsetAt(naive - 12 * 3_600_000, zone);
  const after = naive - offsetAt(naive + 12 * 3_600_000, zone);
  const valid = [before, after].filter((ms) => ms + offsetAt(ms, zone) === naive);
  return new Date(valid.length > 0 ? Math.min(...valid) : before);
}

const ISO =
  /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?)?(Z|[+-]\d{2}:?\d{2})?$/;

/**
 * An ISO time as written, before a timezone reads it: its wall clock, and its offset if it names
 * one.
 */
export type WrittenTime = { wall: Wall; ms: number; offset: number | null };

/**
 * Whether a wall clock names a moment that exists: a day its month has, and an hour, minute, and
 * second in range. `Date.UTC` rolls anything else over, so 30 February reads back as March.
 */
function exists(wall: Wall): boolean {
  const back = new Date(wallMs(wall));
  return (
    back.getUTCFullYear() === wall.year &&
    back.getUTCMonth() + 1 === wall.month &&
    back.getUTCDate() === wall.day &&
    back.getUTCHours() === wall.hour &&
    back.getUTCMinutes() === wall.minute &&
    back.getUTCSeconds() === wall.second
  );
}

/**
 * The parts of an ISO time such as `2026-11-26T14:00` or `2026-11-26T09:05:00Z`, or null when it
 * isn't one or names a time that doesn't exist, such as `2026-02-30T14:99`.
 */
export function readTime(text: string): WrittenTime | null {
  const match = ISO.exec(text.trim());
  if (match === null) return null;
  const [, year, month, day, hour = "0", minute = "0", second = "0", fraction = "", offset] = match;
  const wall = {
    year: Number(year),
    month: Number(month),
    day: Number(day),
    hour: Number(hour),
    minute: Number(minute),
    second: Number(second),
  };
  if (!exists(wall)) return null;
  const ms = Number(fraction.padEnd(3, "0").slice(0, 3));
  if (offset === undefined) return { wall, ms, offset: null };
  if (offset === "Z") return { wall, ms, offset: 0 };
  const digits = offset.replace(/[^0-9]/g, "");
  const hours = Number(digits.slice(0, 2));
  const minutes = Number(digits.slice(2));
  if (hours > 23 || minutes > 59) return null;
  return { wall, ms, offset: (offset.startsWith("-") ? -1 : 1) * (hours * 60 + minutes) };
}

/** The instant a written time names; one without an offset is a wall-clock time in `zone`. */
export function instantOf(written: WrittenTime, zone: string): Date {
  const { wall, ms, offset } = written;
  if (offset === null) return new Date(fromWall(wall, zone).getTime() + ms);
  return new Date(wallMs(wall) + ms - offset * 60_000);
}

/**
 * An ISO time, such as `2026-11-26T09:05:00Z`; one without an offset is a wall-clock time in
 * `zone`.
 */
export function parseTime(text: string, zone = "UTC"): Date | null {
  const written = readTime(text);
  return written === null ? null : instantOf(written, zone);
}

/** A time the user writes, read once a timezone is known, as a parser. */
export const written = (value: unknown, path: string): WrittenTime => {
  const read = readTime(string(value, path));
  if (read === null) throw new ShapeError(path, "expected a time such as 2026-11-26T14:00");
  return read;
};

/** A time read from a file the scan wrote, or one a source sent, as a parser. */
export const time = (value: unknown, path: string): Date => {
  const parsed = parseTime(string(value, path));
  if (parsed === null) throw new ShapeError(path, "expected an ISO time");
  return parsed;
};

/** UTC to the second, as `2026-11-26T09:05:00Z`, the form every file holds. */
export function iso(instant: Date): string {
  return instant.toISOString().replace(/\.\d{3}Z$/, "Z");
}

/** A calendar date, `YYYY-MM-DD`, that exists. */
export type CalendarDate = string & { readonly __brand: "CalendarDate" };

export function isCalendarDate(text: string): text is CalendarDate {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(text)) return false;
  const [year = 0, month = 0, day = 0] = text.split("-").map(Number);
  return exists({ year, month, day, hour: 0, minute: 0, second: 0 });
}

export const calendarDate = refine(string, isCalendarDate, "expected a date such as 2026-11-26");

/** A time the scan wrote with `iso`, such as `2026-11-26T09:05:00Z`. */
export const instant = refine(
  string,
  (text): text is string => {
    const ms = Date.parse(text);
    return !Number.isNaN(ms) && iso(new Date(ms)) === text;
  },
  "expected a time such as 2026-11-26T09:05:00Z",
);

/** The local midnight that starts `date` plus `days`, in `zone`. */
export function midnight(date: CalendarDate, zone: string, days = 0): Date {
  const [year = 0, month = 1, day = 1] = date.split("-").map(Number);
  const shifted = new Date(Date.UTC(year, month - 1, day + days));
  return fromWall(
    {
      year: shifted.getUTCFullYear(),
      month: shifted.getUTCMonth() + 1,
      day: shifted.getUTCDate(),
      hour: 0,
      minute: 0,
      second: 0,
    },
    zone,
  );
}

/** A clock time shifted by whole minutes within its day, kept between 00:00 and 23:59. */
export function addMinutes(at: Clock, minutes: number): Clock {
  const [hour = 0, minute = 0] = at.split(":").map(Number);
  const total = Math.min(23 * 60 + 59, Math.max(0, hour * 60 + minute + minutes));
  const text = `${pad(Math.floor(total / 60))}:${pad(total % 60)}`;
  if (!isClock(text)) throw new Error(`no clock time ${text}`);
  return text;
}

/** `2026-11-26T10:05+01:00`: the scan's time in its report. */
export function localIso(moment: Local): string {
  const sign = moment.offset < 0 ? "-" : "+";
  const offset = Math.abs(moment.offset);
  return `${moment.date}T${moment.clock}${sign}${pad(Math.floor(offset / 60))}:${pad(offset % 60)}`;
}

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** `Thu 26 Nov 14:00`: a time as the user reads it. */
export function shortTime(instant: Date, zone: string): string {
  const wall = wallAt(instant, zone);
  const weekday = new Date(Date.UTC(wall.year, wall.month - 1, wall.day)).getUTCDay();
  return `${DAYS[weekday]} ${pad(wall.day)} ${MONTHS[wall.month - 1]} ${pad(wall.hour)}:${pad(wall.minute)}`;
}

/** A Slack message timestamp, such as `1795683600.000100`, that names a time a Date can hold. */
export type SlackTs = string & { readonly __brand: "SlackTs" };

export function isSlackTs(text: string): text is SlackTs {
  return /^\d+\.\d+$/.test(text) && !Number.isNaN(new Date(Number(text) * 1000).getTime());
}

export const slackTs = refine(string, isSlackTs, "expected a Slack message timestamp");

export function fromSlackTs(ts: SlackTs): Date {
  return new Date(Math.floor(Number(ts) * 1000));
}

/** Blocks the process for `ms`; the scan runs one step at a time, so nothing else waits on it. */
export function sleep(ms: number): void {
  if (ms > 0) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

export const MINUTE = 60_000;
export const HOUR = 60 * MINUTE;
export const DAY = 24 * HOUR;
