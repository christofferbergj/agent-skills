import { afterEach, describe, expect, it } from "bun:test";
import { mkdir, mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { openStore, type Store } from "./store.ts";

const directories: string[] = [];
const stores: Store[] = [];

async function fixture(initialize = true): Promise<{ directory: string; store: Store }> {
  const directory = await mkdtemp(join(tmpdir(), "orch-concurrency-test-"));
  directories.push(directory);
  const store = useStore(directory);
  if (initialize) await store.init();
  return { directory, store };
}

function useStore(directory: string): Store {
  const store = openStore(directory);
  stores.push(store);
  return store;
}

afterEach(async () => {
  await Promise.all(stores.splice(0).map((store) => store.close()));
  await Promise.all(
    directories.splice(0).map((directory) => rm(directory, { recursive: true, force: true })),
  );
});

describe("orch same-handle operation ordering", () => {
  it("persists every successful overlapping unit addition", async () => {
    const { directory, store } = await fixture();
    const accepted = await Promise.all([
      store.units.add({ id: "one", track: "build" }),
      store.units.add({ id: "two", track: "build" }),
    ]);
    await store.close();
    const observer = useStore(directory);
    expect(await observer.units.list()).toEqual(accepted);
    const disk = await readFile(join(directory, "units.tsv"), "utf8");
    expect(disk).toContain("one\tbuild\tpending");
    expect(disk).toContain("two\tbuild\tpending");
  });

  it("admits one addition when concurrent callers use the same id", async () => {
    const { store } = await fixture();
    const results = await Promise.allSettled([
      store.units.add({ id: "same", track: "first" }),
      store.units.add({ id: "same", track: "second" }),
    ]);
    expect(results.map((result) => result.status)).toEqual(["fulfilled", "rejected"]);
    expect(await store.units.get("same")).toMatchObject({ track: "first" });
  });

  it("preserves different fields when queued changes update the same unit", async () => {
    const { store } = await fixture();
    await store.units.add({ id: "one", track: "build" });
    await Promise.all([
      store.units.set({ id: "one", state: "building", branch: "feature/one" }),
      store.units.set({ id: "one", state: "verified", sha: "verified-sha" }),
    ]);
    expect(await store.units.get("one")).toMatchObject({
      state: "verified",
      branch: "feature/one",
      sha: "verified-sha",
    });
  });

  it("keeps distinct ledger entries and orders updates to one entry", async () => {
    const { store } = await fixture();
    const record = (pr: number, evidence: string) =>
      store.ledger.record({ pr, sha: "head", verdict: "unit-test-verified", evidence });
    await Promise.all([record(1, "first"), record(2, "second"), record(1, "latest")]);
    expect(await store.ledger.summary()).toEqual({ "unit-test-verified": 2 });
    expect(await store.ledger.check({ pr: 1, sha: "head" })).toMatchObject({ evidence: "latest" });
    expect(await store.ledger.check({ pr: 2, sha: "head" })).toMatchObject({ evidence: "second" });
  });

  it("preserves gate additions and resolves a gate parked earlier in the queue", async () => {
    const { store } = await fixture();
    const park = (id: string) =>
      store.gates.park({ id, question: `Choose ${id}`, options: "a|b", defaultAnswer: "a" });
    await Promise.all([park("one"), park("two"), store.gates.resolve({ id: "one", answer: "b" })]);
    expect((await store.gates.list()).map((gate) => gate.id)).toEqual(["two"]);
    const status = await store.status.render();
    expect(status.gates).toContainEqual(expect.objectContaining({ id: "one", answer: "b" }));
  });

  it("assigns successive standing-order numbers without losing lines", async () => {
    const { store } = await fixture();
    const accepted = await Promise.all([
      store.standing.add({ line: "first" }),
      store.standing.add({ line: "second" }),
    ]);
    expect(accepted).toEqual([
      { number: 1, line: "first" },
      { number: 2, line: "second" },
    ]);
    expect(await store.standing.show()).toEqual(accepted);
  });

  it("increments the frontier for each admitted update", async () => {
    const { directory, store } = await fixture();
    const repo = join(directory, "repo");
    await mkdir(repo);
    const git = Bun.spawnSync(["git", "init", "--initial-branch=main", repo]);
    expect(git.exitCode).toBe(0);
    const updates = await Promise.all([
      store.frontier.set({ repo, trunk: "main" }),
      store.frontier.set({ repo, trunk: "main" }),
    ]);
    expect(updates.map((frontier) => frontier.generation)).toEqual([1, 2]);
    expect(await store.frontier.show()).toMatchObject({ generation: 2 });
  });

  it("drains earlier inbox pushes and retains later pushes", async () => {
    const { store } = await fixture();
    const push = (unit: string) => store.inbox.push({ agent: "worker", unit, status: "done" });
    const results = await Promise.allSettled([push("first"), store.inbox.drain(), push("second")]);
    expect(results.map((result) => result.status)).toEqual(["fulfilled", "fulfilled", "fulfilled"]);
    const drained = results[1];
    expect(drained?.status === "fulfilled" ? drained.value : null).toEqual([
      expect.objectContaining({ unit: "first" }),
    ]);
    expect((await store.inbox.peek()).map((pointer) => pointer.unit)).toEqual(["second"]);
    expect(await store.inbox.count()).toBe(1);
  });

  it("reads and renders the writes called before them", async () => {
    const { store } = await fixture();
    const adding = store.units.add({ id: "one", track: "build" });
    const getting = store.units.get("one");
    const listing = store.units.list();
    const counting = store.units.counts();
    const rendering = store.status.render();
    const results = await Promise.allSettled([adding, getting, listing, counting, rendering]);
    expect(results.map((result) => result.status)).toEqual(Array(5).fill("fulfilled"));
    expect(await getting).toMatchObject({ id: "one" });
    expect(await listing).toHaveLength(1);
    expect(await counting).toEqual({ pending: 1 });
    expect((await rendering).units).toHaveLength(1);
  });

  it("continues queued operations after a rejected operation", async () => {
    const { store } = await fixture();
    const results = await Promise.allSettled([
      store.units.add({ id: "", track: "build" }),
      store.units.add({ id: "valid", track: "build" }),
      store.units.get("valid"),
    ]);
    expect(results.map((result) => result.status)).toEqual(["rejected", "fulfilled", "fulfilled"]);
    expect(await store.units.list()).toHaveLength(1);
  });

  it("finishes admitted writes before close and rejects later operations", async () => {
    const { directory, store } = await fixture();
    const writes = [
      store.units.add({ id: "one", track: "build" }),
      store.units.add({ id: "two", track: "build" }),
    ];
    const closed = store.close();
    const late = store.units.add({ id: "late", track: "build" });
    const lateRead = store.units.list();
    const results = await Promise.allSettled([...writes, closed, late, lateRead]);
    expect(results.map((result) => result.status)).toEqual([
      "fulfilled",
      "fulfilled",
      "fulfilled",
      "rejected",
      "rejected",
    ]);
    const successor = useStore(directory);
    await successor.init();
    expect((await successor.units.list()).map((unit) => unit.id)).toEqual(["one", "two"]);
  });

  it("waits for admitted initialization before releasing its lease", async () => {
    const { directory, store } = await fixture(false);
    const initializing = store.init();
    const closed = store.close();
    const results = await Promise.allSettled([initializing, closed]);
    expect(results.map((result) => result.status)).toEqual(["fulfilled", "fulfilled"]);
    const successor = useStore(directory);
    await successor.init();
    await expect(successor.units.add({ id: "successor", track: "build" })).resolves.toMatchObject({
      id: "successor",
    });
  });
});
