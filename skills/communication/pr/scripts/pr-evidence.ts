#!/usr/bin/env node
/**
 * Uploads a PR's screenshots to an images-only branch and prints its Evidence Markdown: a
 * Before | After table per view, a table of the states the base branch never reaches, and the
 * views that are new. Run it from the PR branch's checkout; `--dry-run` checks names and pushes
 * nothing.
 *
 * usage: node pr-evidence.ts [--dry-run] <png or directory>...
 *
 * Names: <view>-before.png and <view>-after.png for a pair, <view>-after.png alone for a new view,
 * and <view>--<state>.png for a state the base branch never reaches. A leading `NN-` is ignored.
 */
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { parseArgs } from "node:util";

type Side = "before" | "after";

interface Screenshot {
  /** File name in the images commit, and so in the image URL. */
  name: string;
  view: string;
  portrait: boolean;
}

interface View {
  before?: Screenshot;
  after?: Screenshot;
  /** States that `main` never reaches, by state name, in input order. */
  states: Map<string, Screenshot>;
}

export interface ScreenshotFile {
  file: string;
  width: number;
  height: number;
}

// A leading `NN-` is the capture order that verification skills add, so it is not part of the view.
const PAIR_NAME = /^(?:\d+-)?(?<view>[a-z0-9]+(?:-[a-z0-9]+)*)-(?<side>before|after)\.png$/;
const STATE_NAME =
  /^(?:\d+-)?(?<view>[a-z0-9]+(?:-[a-z0-9]+)*)--(?<state>[a-z0-9]+(?:-[a-z0-9]+)*)\.png$/;
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function label(name: string): string {
  const words = name.replaceAll("-", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function table(headings: string[], rows: string[][]): string {
  const line = (cells: string[]) =>
    `| ${headings.map((_, column) => cells[column] ?? " ").join(" | ")} |`;
  return [line(headings), line(headings.map(() => "---")), ...rows.map(line)].join("\n");
}

/**
 * Screenshots without a pair share one table, so every image in it gets the same width: three to
 * a row when every one is portrait, as phone screenshots are, and two otherwise. Each image's
 * heading sits in the cell above it.
 */
function gallery(cells: { heading: string; image: string; shot: Screenshot }[]): string {
  const columns = Math.min(cells.every(({ shot }) => shot.portrait) ? 3 : 2, cells.length);
  const rows: string[][] = [];
  for (let start = 0; start < cells.length; start += columns) {
    const row = cells.slice(start, start + columns);
    if (start > 0) {
      rows.push(row.map(({ heading }) => `**${heading}**`));
    }
    rows.push(row.map(({ image }) => image));
  }
  return table(
    cells.slice(0, columns).map(({ heading }) => heading),
    rows,
  );
}

/** Groups the screenshots by view, or throws naming every file that breaks the pattern. */
function groupByView(files: ScreenshotFile[]): Map<string, View> {
  const problems: string[] = [];
  const views = new Map<string, View>();

  for (const { file, width, height } of files) {
    const name = path.basename(file);
    const groups = STATE_NAME.exec(name)?.groups ?? PAIR_NAME.exec(name)?.groups;
    if (!groups?.view) {
      problems.push(
        `${name}: name it <view>-before.png, <view>-after.png or <view>--<state>.png, in kebab case`,
      );
      continue;
    }
    const view = views.get(groups.view) ?? { states: new Map<string, Screenshot>() };
    views.set(groups.view, view);
    const { state } = groups;
    const side = groups.side as Side;
    const existing = state ? view.states.get(state) : view[side];
    if (existing) {
      const slot = state ? `${state} state` : side;
      problems.push(`${existing.name} and ${name} are both the ${slot} of ${groups.view}`);
      continue;
    }
    const shot = { name, view: groups.view, portrait: height > width };
    if (state) {
      view.states.set(state, shot);
    } else {
      view[side] = shot;
    }
  }

  for (const [name, { before, after }] of views) {
    if (before && !after) {
      problems.push(`${before.name} has no ${name}-after.png`);
    }
  }
  if (problems.length > 0) {
    throw new Error(problems.join("\n"));
  }
  return views;
}

/**
 * The PR body's screenshot evidence, in input order: per view, a Before | After table when `main`
 * has the same state, and a table of the states `main` never reaches. Views that only have an
 * after, because they are new, follow together at the end.
 */
export function renderEvidence(files: ScreenshotFile[], imageBaseUrl: string): string {
  const views = groupByView(files);
  const image = (alt: string, shot: Screenshot) =>
    `![${alt}](${imageBaseUrl}/${shot.name}?raw=true)`;
  const blocks: string[] = [];
  const afterOnly: Screenshot[] = [];

  for (const [name, { before, after, states }] of views) {
    const tables: string[] = [];
    if (before && after) {
      tables.push(
        table(
          ["Before", "After"],
          [[image(`${label(name)} before`, before), image(`${label(name)} after`, after)]],
        ),
      );
    } else if (after) {
      afterOnly.push(after);
    }
    if (states.size > 0) {
      tables.push(
        gallery(
          [...states].map(([state, shot]) => ({
            heading: label(state),
            image: image(`${label(name)}, ${state.replaceAll("-", " ")}`, shot),
            shot,
          })),
        ),
      );
    }
    if (tables.length > 0) {
      blocks.push([`**${label(name)}**`, ...tables].join("\n\n"));
    }
  }

  if (afterOnly.length > 0) {
    const cells = afterOnly.map((shot) => ({
      heading: label(shot.view),
      image: image(label(shot.view), shot),
      shot,
    }));
    blocks.push(`**After only**\n\n${gallery(cells)}`);
  }

  return `${blocks.join("\n\n")}\n`;
}

/** `owner/name` of a GitHub remote URL, over HTTPS or SSH. */
export function githubRepository(remoteUrl: string): string {
  const repository = /github\.com[:/](?<repository>[^/]+\/[^/]+?)(?:\.git)?\/?$/.exec(remoteUrl)
    ?.groups?.repository;
  if (!repository) {
    throw new Error(`The remote is not a GitHub repository: ${remoteUrl}`);
  }
  return repository;
}

/**
 * Commits the files as the only content of an images-only branch and pushes it. Each upload's
 * parent is the branch's previous tip, so the push fast-forwards and image URLs in earlier PR body
 * revisions keep resolving. Uploading the same files again returns the existing commit.
 */
export function uploadImages(options: {
  cwd: string;
  remote: string;
  branch: string;
  files: string[];
  message: string;
}): string {
  const git = (args: string[], input?: string) =>
    execFileSync("git", args, { cwd: options.cwd, encoding: "utf-8", input }).trim();

  const entries = options.files.map(
    (file) => `100644 blob ${git(["hash-object", "-w", "--", file])}\t${path.basename(file)}\n`,
  );
  const tree = git(["mktree"], entries.join(""));
  const ref = `refs/heads/${options.branch}`;
  const [tip] = git(["ls-remote", options.remote, ref]).split("\t");

  if (tip) {
    git(["fetch", "--quiet", "--no-tags", options.remote, ref]);
    if (git(["rev-parse", `${tip}^{tree}`]) === tree) {
      return tip;
    }
  }
  const commit = git(["commit-tree", tree, ...(tip ? ["-p", tip] : []), "-m", options.message]);
  git(["push", "--quiet", options.remote, `${commit}:${ref}`]);
  return commit;
}

function readScreenshot(file: string): ScreenshotFile {
  const header = readFileSync(file).subarray(0, 24);
  if (header.length < 24 || !header.subarray(0, 8).equals(PNG_SIGNATURE)) {
    throw new Error(`${file} is not a PNG`);
  }
  return { file, width: header.readUInt32BE(16), height: header.readUInt32BE(20) };
}

function listScreenshots(inputs: string[]): string[] {
  return inputs.flatMap((input) =>
    statSync(input).isDirectory()
      ? readdirSync(input)
          .filter((name) => name.endsWith(".png"))
          .toSorted()
          .map((name) => path.resolve(input, name))
      : [path.resolve(input)],
  );
}

function main() {
  const { values, positionals } = parseArgs({
    allowPositionals: true,
    options: { "dry-run": { type: "boolean", default: false } },
  });
  if (positionals.length === 0) {
    throw new Error("Usage: node pr-evidence.ts [--dry-run] <png or directory>...");
  }

  const cwd = process.cwd();
  const git = (args: string[]) => execFileSync("git", args, { cwd, encoding: "utf-8" }).trim();
  const branch = git(["branch", "--show-current"]);
  if (!branch || branch === "main") {
    throw new Error("Check out the PR branch first; its name sets the images branch.");
  }

  const screenshots = listScreenshots(positionals).map(readScreenshot);
  const repository = githubRepository(git(["remote", "get-url", "origin"]));
  // Without the `agent/` or other prefix, as the images branches already on the remote are named.
  const imagesBranch = `pr-images/${branch.replace(/^[^/]+\//, "")}`;
  // Lay out first, so a naming problem stops the run before anything is pushed.
  renderEvidence(screenshots, "");

  let commit = "DRY-RUN";
  if (values["dry-run"]) {
    console.error(`Dry run: would push ${screenshots.length} images to ${imagesBranch}`);
  } else {
    commit = uploadImages({
      cwd,
      remote: "origin",
      branch: imagesBranch,
      files: screenshots.map((screenshot) => screenshot.file),
      message: `PR images for ${branch} (images only, never merge)`,
    });
    console.error(`Pushed ${screenshots.length} images to ${imagesBranch} at ${commit}`);
  }
  process.stdout.write(
    renderEvidence(screenshots, `https://github.com/${repository}/blob/${commit}`),
  );
}

if (process.argv[1] === import.meta.filename) {
  try {
    main();
  } catch (error) {
    console.error((error as Error).message);
    process.exit(1);
  }
}
