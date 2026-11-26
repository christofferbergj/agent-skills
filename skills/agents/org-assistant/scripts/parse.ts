/**
 * Parsers for everything that crosses into the scan: the profile, the state files, and each
 * source's responses. A parser returns the typed value or throws a ShapeError that names where the
 * shape broke by its field path only, never by the value, since a value can quote what a source was
 * reading. Each type that crosses a boundary is derived from its parser with `Infer`.
 */

export class ShapeError extends Error {
  readonly path: string;

  constructor(path: string, problem: string) {
    super(`${path || "the value"}: ${problem}`);
    this.path = path;
  }
}

export type Parser<T> = (value: unknown, path: string) => T;
export type Infer<P> = P extends Parser<infer T> ? T : never;

type Shape = Record<string, Parser<unknown>>;
type OptionalKeys<S extends Shape> = {
  [K in keyof S]: undefined extends Infer<S[K]> ? K : never;
}[keyof S];
type Simplify<T> = { [K in keyof T]: T[K] } & {};
export type ObjectOf<S extends Shape> = Simplify<
  { [K in Exclude<keyof S, OptionalKeys<S>>]: Infer<S[K]> } & {
    [K in OptionalKeys<S>]?: Infer<S[K]>;
  }
>;

const at = (path: string, key: string | number) =>
  typeof key === "number" ? `${path}[${key}]` : path ? `${path}.${key}` : key;

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Runs a parser on a whole value, from the top of its path. */
export function parse<T>(parser: Parser<T>, value: unknown): T {
  return parser(value, "");
}

export const string: Parser<string> = (value, path) => {
  if (typeof value !== "string") throw new ShapeError(path, "expected a string");
  return value;
};

export const number: Parser<number> = (value, path) => {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new ShapeError(path, "expected a number");
  }
  return value;
};

/** A whole number of zero or more, such as a count or a number of minutes. */
export const count: Parser<number> = (value, path) => {
  const parsed = number(value, path);
  if (!Number.isInteger(parsed) || parsed < 0) {
    throw new ShapeError(path, "expected a whole number of zero or more");
  }
  return parsed;
};

export const boolean: Parser<boolean> = (value, path) => {
  if (typeof value !== "boolean") throw new ShapeError(path, "expected true or false");
  return value;
};

export const unknown: Parser<unknown> = (value) => value;

export function literal<const L extends readonly (string | boolean)[]>(
  ...values: L
): Parser<L[number]> {
  return (value, path) => {
    const found = values.find((option) => option === value);
    if (found === undefined) throw new ShapeError(path, `expected ${values.join(" or ")}`);
    return found;
  };
}

/** A value that may be absent or null, read as null. */
export function nullable<T>(parser: Parser<T>): Parser<T | null> {
  return (value, path) => (value === undefined || value === null ? null : parser(value, path));
}

/** A field that may be absent. */
export function optional<T>(parser: Parser<T>): Parser<T | undefined> {
  return (value, path) => (value === undefined ? undefined : parser(value, path));
}

/** A field that reads as `fallback`, parsed like any value, when it is absent. */
export function withDefault<T>(parser: Parser<T>, fallback: unknown): Parser<T> {
  return (value, path) => parser(value === undefined ? structuredClone(fallback) : value, path);
}

export function array<T>(item: Parser<T>): Parser<T[]> {
  return (value, path) => {
    if (!Array.isArray(value)) throw new ShapeError(path, "expected a list");
    return value.map((entry, index) => item(entry, at(path, index)));
  };
}

export function record<T>(item: Parser<T>): Parser<Record<string, T>> {
  return (value, path) => {
    if (!isRecord(value)) throw new ShapeError(path, "expected an object");
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [key, item(entry, at(path, key))]),
    );
  };
}

/**
 * An object with the fields `shape` names. Other fields are ignored, as a source's response may grow
 * them, unless `strict`, as for the profile, where an unknown field is most often a typo.
 */
export function object<S extends Shape>(
  shape: S,
  options: { strict?: boolean } = {},
): Parser<ObjectOf<S>> {
  return (value, path) => {
    if (!isRecord(value)) throw new ShapeError(path, "expected an object");
    if (options.strict) {
      const extra = Object.keys(value).find((key) => !Object.hasOwn(shape, key));
      if (extra !== undefined) throw new ShapeError(at(path, extra), "is not a field it knows");
    }
    const out: Record<string, unknown> = {};
    for (const [key, parser] of Object.entries(shape)) {
      const parsed = parser(value[key], at(path, key));
      if (parsed !== undefined) out[key] = parsed;
    }
    // Every field of the shape was parsed above, so `out` holds exactly the shape's type.
    return out as ObjectOf<S>;
  };
}

/** The first of `parsers` that reads the value; strict object parsers keep them apart. */
export function oneOf<P extends Parser<unknown>[]>(...parsers: P): Parser<Infer<P[number]>> {
  return (value, path) => {
    for (const parser of parsers) {
      try {
        return parser(value, path) as Infer<P[number]>;
      } catch (error) {
        if (!(error instanceof ShapeError)) throw error;
      }
    }
    throw new ShapeError(path, "matches none of the shapes it may take");
  };
}

/** A parsed value that must also pass `check`, such as a string in a format; it may brand it. */
export function refine<T, U extends T>(
  parser: Parser<T>,
  check: (value: T) => value is U,
  problem: string,
): Parser<U> {
  return (value, path) => {
    const parsed = parser(value, path);
    if (!check(parsed)) throw new ShapeError(path, problem);
    return parsed;
  };
}

export function map<T, U>(parser: Parser<T>, convert: (value: T) => U): Parser<U> {
  return (value, path) => convert(parser(value, path));
}
