/**
 * An organisation's profile, `~/.config/org-assistant/<org>/profile.json`, parsed and checked when
 * it loads, so a broken profile fails only its own organisation and nothing past this file
 * re-checks it. `references/state.md` shows a whole profile.
 */
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

import {
  type Infer,
  ShapeError,
  array,
  boolean,
  count,
  isRecord,
  literal,
  map,
  object,
  optional,
  refine,
  string,
  withDefault,
} from "./parse.ts";
import { FileError, configRoot, expandHome, readJson } from "./store.ts";
import { type Clock, clock, isZone } from "./time.ts";

/** Every organisation with a profile, by folder name. */
export function orgs(): string[] {
  const root = configRoot();
  if (!existsSync(root)) return [];
  return readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && existsSync(join(root, entry.name, "profile.json")))
    .map((entry) => entry.name)
    .sort();
}

/** A path, with `~` read as the home folder so the profile stays machine-neutral. */
const path = map(string, expandHome);
const strict = { strict: true };
const names = withDefault(array(string), []);
const flag = withDefault(boolean, false);

const window = refine(
  array(clock),
  (value): value is [Clock, Clock] => {
    const [first, last] = value;
    return value.length === 2 && first !== undefined && last !== undefined && first <= last;
  },
  'expected a start and an end time within one day, such as ["09:00", "23:59"]',
);

export const scheduleParser = object(
  {
    window: withDefault(window, ["09:00", "23:59"]),
    overview: withDefault(clock, "09:00"),
    batch_slots: withDefault(array(clock), ["13:00", "17:00"]),
    daily_deltas: withDefault(count, 6),
    slack_wait_minutes: withDefault(count, 30),
    /** Resends of an undelivered batch before the unit fails. */
    retries: withDefault(count, 1),
    /** Failed scans in a row before the unit fails. */
    source_failures: withDefault(count, 3),
  },
  strict,
);
export type Schedule = Infer<typeof scheduleParser>;

const name = refine(string, (value): value is string => value.length > 0, "expected a name");

const linear = object(
  {
    name,
    kind: literal("linear"),
    /** Executor is called from this repository. */
    repo: optional(path),
    account: string,
    teams: names,
    tools: names,
  },
  strict,
);

const slack = object(
  {
    name,
    kind: literal("slack"),
    repo: optional(path),
    account: string,
    /** The user's Slack id. */
    me: string,
    tools: names,
    channels: withDefault(array(object({ id: string, name: optional(string) }, strict)), []),
  },
  strict,
);

const github = object(
  {
    name,
    kind: literal("github"),
    /** The user's GitHub login. */
    me: string,
    repos: array(
      object(
        {
          repo: string,
          mine: flag,
          review_requests: flag,
          issues: flag,
          open_prs: flag,
          releases: flag,
        },
        strict,
      ),
    ),
  },
  strict,
);

const t3 = object(
  {
    name,
    kind: literal("t3"),
    projects: array(
      object(
        {
          path,
          /** The seat and coding model a thread launched in this project runs on. */
          provider: optional(string),
          model: optional(string),
          options: names,
        },
        strict,
      ),
    ),
  },
  strict,
);

/** How Linear and Slack reach Executor: the profile's command, which every such source shares. */
type ViaExecutor = { command: string[] };
export type LinearSource = Infer<typeof linear> & ViaExecutor;
export type SlackSource = Infer<typeof slack> & ViaExecutor;
export type GithubSource = Infer<typeof github>;
export type T3Source = Infer<typeof t3>;
/** A kind with no adapter yet: it fails every scan, so the gap shows in the health line. */
export type UnbuiltSource = { kind: "unbuilt"; name: string; wanted: string };
export type Source = LinearSource | SlackSource | GithubSource | T3Source | UnbuiltSource;

/** Each kind of source an adapter reads, by the parser for its profile entry. */
const SOURCE_KINDS = { linear, slack, github, t3 };
/** A source as the profile writes it, before the Executor command is attached. */
type ProfileSource = Infer<(typeof SOURCE_KINDS)[keyof typeof SOURCE_KINDS]> | UnbuiltSource;

function isSourceKind(kind: unknown): kind is keyof typeof SOURCE_KINDS {
  return typeof kind === "string" && Object.hasOwn(SOURCE_KINDS, kind);
}

const source = (value: unknown, at: string): ProfileSource => {
  if (!isRecord(value)) throw new ShapeError(at, "expected an object");
  if (isSourceKind(value.kind)) return SOURCE_KINDS[value.kind](value, at);
  return {
    kind: "unbuilt",
    name: name(value.name, `${at}.name`),
    wanted: string(value.kind, `${at}.kind`),
  };
};

const zone = refine(string, (value): value is string => isZone(value), "unknown timezone");

const profile = object(
  {
    /** The folder's name. */
    org: optional(string),
    /** The thread's title is `✦ <name> assistant`. */
    name,
    timezone: withDefault(zone, "Europe/Copenhagen"),
    /** Empty until go-live: the scan then sends nothing. */
    thread: withDefault(string, ""),
    executor: optional(object({ command: array(path) }, strict)),
    schedule: withDefault(scheduleParser, {}),
    sources: refine(
      array(source),
      (value): value is [ProfileSource, ...ProfileSource[]] => value.length > 0,
      "expected at least one source",
    ),
    people: optional(object({ file: path }, strict)),
    privacy: optional(object({ rules: array(string) }, strict)),
  },
  strict,
);

export type Profile = Omit<Infer<typeof profile>, "org" | "thread" | "executor" | "sources"> & {
  org: string;
  /** The assistant thread's id, or null before go-live. */
  thread: string | null;
  sources: [Source, ...Source[]];
};

export function profilePath(org: string): string {
  return join(configRoot(), org, "profile.json");
}

export function loadProfile(org: string): Profile {
  const file = profilePath(org);
  const read = readJson(file, profile);
  if (read === null) throw new FileError(file, "missing");
  if (read.org !== undefined && read.org !== org) {
    throw new FileError(file, `org is ${read.org}, but its folder is ${org}`);
  }
  const seen = new Set<string>();
  for (const entry of read.sources) {
    if (seen.has(entry.name)) throw new FileError(file, `two sources are named ${entry.name}`);
    seen.add(entry.name);
  }
  const { executor, sources, ...rest } = read;
  const withCommand = (entry: ProfileSource): Source => {
    if (entry.kind !== "linear" && entry.kind !== "slack") return entry;
    if (executor === undefined)
      throw new FileError(file, `the ${entry.name} source needs the executor command`);
    return { ...entry, command: executor.command };
  };
  const [head, ...tail] = sources;
  return {
    ...rest,
    org,
    thread: read.thread === "" ? null : read.thread,
    sources: [withCommand(head), ...tail.map(withCommand)],
  };
}
