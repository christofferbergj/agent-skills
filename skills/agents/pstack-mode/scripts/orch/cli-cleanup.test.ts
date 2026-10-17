import { afterEach, describe, expect, it } from "bun:test";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { openStore } from "./store.ts";

const FIXTURE = join(import.meta.dir, "cli-cleanup.test-helper.ts");
const CLI = join(import.meta.dir, "orch.ts");
const directories: string[] = [];
const FIRST_ORDER = "Never repeat a completed write to retry cleanup.";

async function directory(): Promise<string> {
  const path = await mkdtemp(join(tmpdir(), "orch-cli-cleanup-"));
  directories.push(path);
  const store = openStore(path);
  try {
    await store.init();
    await store.units.add({ id: "existing", track: "build" });
  } finally {
    await store.close();
  }
  return path;
}

async function run(script: string, args: readonly string[]) {
  const child = Bun.spawn([process.execPath, script, ...args], {
    env: { ...process.env, PSTACK_TOOL_RUNTIME: dirname(import.meta.dir) },
    stdout: "pipe",
    stderr: "pipe",
  });
  const timeout = setTimeout(() => child.kill(), 3_000);
  try {
    const [code, stdout, stderr] = await Promise.all([
      child.exited,
      new Response(child.stdout).text(),
      new Response(child.stderr).text(),
    ]);
    return { code, stdout, stderr };
  } finally {
    clearTimeout(timeout);
  }
}

afterEach(async () => {
  await Promise.all(
    directories.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

describe("orch CLI cleanup outcomes", () => {
  it("preserves a completed write and exit zero when lock cleanup fails", async () => {
    const path = await directory();
    const result = await run(FIXTURE, [path, "standing", "add", FIRST_ORDER]);
    expect(await readFile(join(path, "preferences.md"), "utf8")).toBe(`1. ${FIRST_ORDER}\n`);
    expect(JSON.parse(result.stdout)).toEqual({ number: 1, line: FIRST_ORDER });
    expect(result.code).toBe(0);
    expect(result.stderr).toContain("warning:");
    expect(result.stderr).toContain("store lock maintenance held by pid");

    // The failed cleanup leaves a dead process's lease. A subsequent distinct
    // write reclaims it without replaying the completed standing-order append.
    const next = await run(CLI, ["--store", path, "standing", "add", "A different order."]);
    expect(next.code).toBe(0);
    expect(next.stderr).toContain("replacing stale store lock");
    expect(await readFile(join(path, "preferences.md"), "utf8")).toBe(
      `1. ${FIRST_ORDER}\n2. A different order.\n`,
    );
  });

  it("preserves the original not-found outcome and data when operation and cleanup fail", async () => {
    const path = await directory();
    const before = await readFile(join(path, "units.tsv"), "utf8");
    const result = await run(FIXTURE, [path, "unit", "set", "missing", "--state", "done"]);
    expect(await readFile(join(path, "units.tsv"), "utf8")).toBe(before);
    expect(result.code).toBe(2);
    expect(result.stdout).toBe("");
    expect(result.stderr).toContain("warning:");
    expect(result.stderr).toContain("store lock maintenance held by pid");
    expect(result.stderr).toContain("error: unit missing not found");
    const observer = openStore(path);
    try {
      expect(await observer.units.get("existing")).toMatchObject({
        id: "existing",
        state: "pending",
      });
    } finally {
      await observer.close();
    }
  });
});
