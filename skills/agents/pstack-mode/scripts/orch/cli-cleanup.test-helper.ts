import { mock } from "bun:test";
import * as fs from "node:fs/promises";
import { join } from "node:path";
import type { Store } from "./store.ts";

const [directory, ...args] = process.argv.slice(2);
if (!directory) throw new Error("expected store directory and CLI arguments");
const lockPath = join(directory, ".orch.lock");
const guardPath = join(directory, ".orch.lock.guard");
const realSymlink = fs.symlink;
const realReadFile = fs.readFile;
let guardAttempts = 0;
let pauseRead = false;
let entered!: () => void;
let proceed!: () => void;
const competingRead = new Promise<void>((resolve) => {
  entered = resolve;
});
const resumeCompeting = new Promise<void>((resolve) => {
  proceed = resolve;
});
let competing: Store | null = null;
let competingResult: Promise<void> | null = null;

mock.module("node:fs/promises", () => ({
  ...fs,
  symlink: async (...params: Parameters<typeof realSymlink>) => {
    if (String(params[1]) === guardPath && ++guardAttempts === 2) {
      // The operation acquired the first guard. Hold a competing store's guard
      // before the CLI's cleanup begins, until main has returned its result.
      pauseRead = true;
      competing = openStore(directory);
      competingResult = competing.init().then(
        () => {
          throw new Error("competing store unexpectedly acquired the lease");
        },
        (error) => {
          if (!(error instanceof Error) || !error.message.includes("store lock held by pid"))
            throw error;
        },
      );
      await competingRead;
    }
    await realSymlink(...params);
  },
  readFile: async (...params: Parameters<typeof realReadFile>) => {
    const contents = await realReadFile(...params);
    if (pauseRead && String(params[0]) === lockPath) {
      pauseRead = false;
      entered();
      await resumeCompeting;
    }
    return contents;
  },
}));

const { openStore } = await import("./store.ts");
const { main } = await import("./orch.ts");
const code = await main(["--store", directory, "--json", ...args]);
proceed();
if (competingResult === null || competing === null)
  throw new Error("cleanup contention was not exercised");
await competingResult;
await (competing as Store).close();
process.exitCode = code;
