/**
 * Computes /usage-review's fixed metrics from extract.ts output, and classifies each shipped
 * change's follow-up rate against the baseline frozen when it shipped.
 *
 * Usage: metrics.ts --in <messages.jsonl> --out <metrics.json> [--shipped <shipped.json>]
 *        metrics.ts --in <messages.jsonl> --freeze <new-contracts.json>
 * `--freeze` prints the contracts with each one's baseline rate on these messages, ready to
 * append to shipped.json.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { parseArgs } from "node:util";

import type { OwnerMessage } from "./extract.ts";

/** Case-insensitive substrings; every given field must hold. */
export interface Predicate {
  /** An option on the answered menu contains it. */
  readonly offered?: string;
  /** The option the owner picked contains it. */
  readonly picked?: string;
  /** The owner's message contains it. */
  readonly text?: string;
}

export interface Rate {
  readonly numerator: number;
  readonly opportunities: number;
}

export interface Contract {
  readonly rule: string;
  readonly pr?: number;
  readonly opportunity: Predicate;
  readonly success: Predicate;
  readonly direction: "up" | "down";
  /** Raised to 20 when lower. */
  readonly minExposure?: number;
  /** The rate on the messages of the run that shipped the change. */
  readonly baseline?: Rate;
  /** When installed copies first held the merged change; only messages from then on count. */
  readonly measureFrom?: string;
}

export type FollowUp = "moved" | "unchanged" | "wrong-way" | "insufficient-exposure";

const MIN_EXPOSURE = 20;
const THRESHOLD_POINTS = 5;

/** The letter a reply picks: a bare letter, a letter and a tweak, or "option a" phrasing. */
export function pickedLetter(reply: string): string | null {
  const text = reply.trim();
  const lead = text.match(/^([a-d])(?:$|[,.:!)]|\s+(?:then|but|and|with|plus)\b)/i);
  if (lead) return lead[1].toLowerCase();
  // "do a review" is an article, so a letter after a verb counts only when nothing follows it.
  const named =
    text.match(/\boption\s+([a-d])\b/i) ??
    text.match(/\b(?:do|go with|implement)\s+([a-d])(?=$|[,.:;!)]|\s+(?:then|and|but)\b)/i);
  return named?.[1].toLowerCase() ?? null;
}

const menuOf = (row: OwnerMessage) => (row.ending?.kind === "options" ? row.ending.options : []);

function holds(predicate: Predicate, row: OwnerMessage): boolean {
  const has = (haystack: string, needle: string) =>
    haystack.toLowerCase().includes(needle.toLowerCase());
  const options = menuOf(row);
  if (predicate.offered && !options.some((o) => has(o.text, predicate.offered!))) return false;
  if (predicate.picked) {
    const picked = options.find((o) => o.letter === pickedLetter(row.text));
    if (!picked || !has(picked.text, predicate.picked)) return false;
  }
  return !predicate.text || has(row.text, predicate.text);
}

export function rateOf(contract: Contract, rows: readonly OwnerMessage[]): Rate {
  const eligible = rows.filter((row) => holds(contract.opportunity, row));
  return {
    numerator: eligible.filter((row) => holds(contract.success, row)).length,
    opportunities: eligible.length,
  };
}

/** Moved means at least five points in the preferred direction, at the minimum exposure. */
export function classify(contract: Contract, current: Rate, baseline: Rate): FollowUp {
  const min = Math.max(MIN_EXPOSURE, contract.minExposure ?? 0);
  if (current.opportunities < min || baseline.opportunities < min) return "insufficient-exposure";
  // Cross-multiplied, so an exact five-point change isn't lost to rounding.
  const scaled =
    100 * (current.numerator * baseline.opportunities - baseline.numerator * current.opportunities);
  const threshold = THRESHOLD_POINTS * current.opportunities * baseline.opportunities;
  const signed = contract.direction === "up" ? scaled : -scaled;
  if (signed >= threshold) return "moved";
  if (signed <= -threshold) return "wrong-way";
  return "unchanged";
}

/** A change is measured only once it is live and has a frozen baseline. */
export function followUp(contract: Contract, rows: readonly OwnerMessage[]): FollowUp {
  if (!contract.baseline || !contract.measureFrom) return "insufficient-exposure";
  const live = rows.filter((row) => row.at >= contract.measureFrom!);
  return classify(contract, rateOf(contract, live), contract.baseline);
}

const STOPWORDS = new Set(
  "a an and are as at be but by can do for from has have i if in into is it its me my not of on or so that the then this to was we what when with you your".split(
    " ",
  ),
);

export interface Candidate {
  readonly phrase: string;
  readonly messages: number;
  readonly threads: number;
  readonly messageIds: readonly string[];
}

/**
 * Recurring 2–4-word phrases in the owner's messages, counted once per message. A phrase must
 * reach `minMessages` across `minThreads`; a shorter phrase that always occurs inside a longer
 * qualifying one is dropped. These are candidates for the agent to validate, not findings.
 */
export function phraseCandidates(
  rows: readonly OwnerMessage[],
  minMessages = 10,
  minThreads = 5,
): Candidate[] {
  const seen = new Map<string, { ids: Set<string>; threads: Set<string> }>();
  for (const row of rows) {
    const words = row.text.toLowerCase().match(/\p{L}[\p{L}\p{N}'’-]*/gu) ?? [];
    const phrases = new Set<string>();
    for (let n = 2; n <= 4; n++)
      for (let i = 0; i + n <= words.length; i++) {
        const gram = words.slice(i, i + n);
        if (STOPWORDS.has(gram[0]) || STOPWORDS.has(gram[n - 1])) continue;
        phrases.add(gram.join(" "));
      }
    for (const phrase of phrases) {
      const entry = seen.get(phrase) ?? { ids: new Set(), threads: new Set() };
      entry.ids.add(row.messageId);
      entry.threads.add(row.threadId);
      seen.set(phrase, entry);
    }
  }
  const qualifying = [...seen]
    .filter(([, e]) => e.ids.size >= minMessages && e.threads.size >= minThreads)
    .map(([phrase, e]) => ({
      phrase,
      messages: e.ids.size,
      threads: e.threads.size,
      messageIds: [...e.ids],
    }));
  return qualifying
    .filter(
      (c) =>
        !qualifying.some(
          (longer) =>
            longer.phrase !== c.phrase &&
            ` ${longer.phrase} `.includes(` ${c.phrase} `) &&
            longer.messages === c.messages,
        ),
    )
    .sort((a, b) => b.messages - a.messages || b.threads - a.threads);
}

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = values.toSorted((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

export function metrics(rows: readonly OwnerMessage[], contracts: readonly Contract[] = []) {
  const answers = rows.filter((row) => row.interaction === "answer");
  const menus = answers.filter((row) => menuOf(row).length > 0);
  const answerKind = (row: OwnerMessage) =>
    /^[a-d][.!]?$/i.test(row.text.trim())
      ? "letter"
      : pickedLetter(row.text)
        ? "letterAndWords"
        : "ownWords";
  const picksBySize: Record<string, Record<string, number>> = {};
  for (const row of menus) {
    const size = String(menuOf(row).length);
    const pick = pickedLetter(row.text) ?? "ownWords";
    picksBySize[size] ??= {};
    picksBySize[size][pick] = (picksBySize[size][pick] ?? 0) + 1;
  }
  return {
    messages: rows.length,
    threads: new Set(rows.map((row) => row.threadId)).size,
    interactions: Object.fromEntries(
      Object.entries(Object.groupBy(rows, (row) => row.interaction)).map(([k, v]) => [
        k,
        v!.length,
      ]),
    ),
    menuAnswers: Object.fromEntries(
      Object.entries(Object.groupBy(menus, answerKind)).map(([k, v]) => [k, v!.length]),
    ),
    picksByMenuSize: picksBySize,
    medianAssistantWords: median(answers.map((row) => row.assistantWords ?? 0)),
    followUps: Object.fromEntries(contracts.map((c) => [c.rule, followUp(c, rows)])),
    candidates: phraseCandidates(rows).slice(0, 40),
  };
}

if (import.meta.main) {
  const { values } = parseArgs({
    options: {
      in: { type: "string" },
      out: { type: "string" },
      shipped: { type: "string" },
      freeze: { type: "string" },
    },
  });
  if (!values.in || !(values.out || values.freeze))
    throw new Error("metrics.ts needs --in and --out or --freeze; see the usage in its header");
  const rows = readFileSync(values.in, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line) as OwnerMessage);
  const load = (path: string) => JSON.parse(readFileSync(path, "utf8")) as Contract[];
  if (values.freeze) {
    const frozen = load(values.freeze).map((c) => ({ ...c, baseline: rateOf(c, rows) }));
    console.log(JSON.stringify(frozen, null, 2));
  } else {
    const result = metrics(rows, values.shipped ? load(values.shipped) : []);
    writeFileSync(values.out!, JSON.stringify(result, null, 2) + "\n");
    const { candidates, ...summary } = result;
    console.log(JSON.stringify({ ...summary, candidates: candidates.length }));
  }
}
