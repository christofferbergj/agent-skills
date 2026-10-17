import { mock } from "bun:test";
import * as fs from "node:fs/promises";
import { basename, join } from "node:path";

const [scenario, directory] = process.argv.slice(2);
if (!scenario || !directory) throw new Error("expected scenario and store directory");
const lockPath = join(directory, ".orch.lock");
const realUnlink = fs.unlink;
const realReadFile = fs.readFile;
const realSymlink = fs.symlink;
const realLink = fs.link;

function signal() {
  let resolve!: () => void;
  return {
    promise: new Promise<void>((done) => {
      resolve = done;
    }),
    resolve: () => resolve(),
  };
}
const entered = signal();
const proceed = signal();
const successorEntered = signal();
const guardContended = signal();
const firstAcquired = signal();
let deletions = 0;
let interceptRead = false;
const closeScenario = scenario === "close-retry" || scenario === "close-concurrent";

mock.module("node:fs/promises", () => ({
  ...fs,
  unlink: async (path: Parameters<typeof realUnlink>[0]) => {
    if (String(path) === lockPath) {
      if (scenario === "stale-race") {
        const deletion = ++deletions;
        if (deletion === 1) {
          entered.resolve();
          await proceed.promise;
        }
        if (deletion === 2) {
          successorEntered.resolve();
          await firstAcquired.promise;
        }
      }
    }
    await realUnlink(path);
    if (scenario === "crash-after-unlink" && String(path) === lockPath) process.exit(0);
  },
  readFile: async (...args: Parameters<typeof realReadFile>) => {
    const contents = await realReadFile(...args);
    if (
      (scenario === "release-race" || closeScenario) &&
      interceptRead &&
      String(args[0]) === lockPath
    ) {
      interceptRead = false;
      entered.resolve();
      await proceed.promise;
    }
    return contents;
  },
  symlink: async (...args: Parameters<typeof realSymlink>) => {
    try {
      await realSymlink(...args);
    } catch (error) {
      if (
        String(args[1]) === join(directory, ".orch.lock.guard") &&
        (error as NodeJS.ErrnoException).code === "EEXIST"
      ) {
        guardContended.resolve();
      }
      throw error;
    }
    const name = basename(String(args[1]));
    if (scenario === "crash-guard" && name === ".orch.lock.guard") process.exit(0);
    if (scenario === "crash-recovery" && name.startsWith(".orch.lock.guard.")) process.exit(0);
  },
  link: async (...args: Parameters<typeof realLink>) => {
    if (scenario === "crash-before-link" && String(args[1]) === lockPath) process.exit(0);
    await realLink(...args);
    if (scenario === "crash-after-link" && String(args[1]) === lockPath) process.exit(0);
  },
}));

const { openStore } = await import("./store.ts");
const first = openStore(directory);
if (closeScenario) {
  await first.init();
  interceptRead = true;
  const competing = openStore(directory);
  const competingInit = competing.init().then(
    () => "acquired",
    (error) => String(error),
  );
  await entered.promise;
  const requests =
    scenario === "close-concurrent" ? [first.close(), first.close()] : [first.close()];
  const closing = Promise.allSettled(requests);
  const blockedDuringClose = await first.units.add({ id: "closing", track: "build" }).then(
    () => "written",
    (error) => String(error),
  );
  const failures = await closing;
  const blockedWrite = await first.units.add({ id: "closed", track: "build" }).then(
    () => "written",
    (error) => String(error),
  );
  proceed.resolve();
  const competitor = await competingInit;
  const retryClose = await first.close().then(
    () => "closed",
    (error) => String(error),
  );
  const third = openStore(directory);
  const thirdOpen = await third.init().then(
    () => "acquired",
    (error) => String(error),
  );
  console.log(
    JSON.stringify({
      failures: failures.map((result) =>
        result.status === "rejected" ? String(result.reason) : "closed",
      ),
      blockedDuringClose,
      blockedWrite,
      competitor,
      retryClose,
      thirdOpen,
    }),
  );
  await first.close();
  await competing.close();
  await third.close();
} else if (scenario === "hold") {
  try {
    await first.init();
    console.log("acquired");
    setInterval(() => {}, 1_000);
  } catch (error) {
    console.log(
      error instanceof Error && error.message.includes("store lock held")
        ? "blocked"
        : String(error),
    );
    process.exit(0);
  }
} else if (scenario.startsWith("crash-")) {
  await first.init();
  throw new Error("expected process to exit at crash boundary");
} else {
  const second = openStore(directory, scenario === "release-race" ? { force: true } : {});
  let results: PromiseSettledResult<unknown>[];
  if (scenario === "stale-race") {
    const firstInit = first.init().then((value) => {
      firstAcquired.resolve();
      return value;
    });
    await entered.promise;
    const secondInit = second.init();
    // Resume only once the competitor reaches its deletion or waits on the
    // mutation guard. The final assertion concerns store ownership in either case.
    await Promise.race([successorEntered.promise, guardContended.promise]);
    proceed.resolve();
    results = await Promise.allSettled([firstInit, secondInit]);
  } else if (scenario === "release-race") {
    await first.init();
    interceptRead = true;
    const closing = first.close();
    await entered.promise;
    const forced = second.init();
    await Promise.race([forced.then(() => {}), guardContended.promise]);
    proceed.resolve();
    await closing;
    await forced;
    const third = openStore(directory);
    results = await Promise.allSettled([third.init()]);
    await third.close();
  } else {
    throw new Error(`unknown scenario ${scenario}`);
  }
  const fulfilled = results.filter((result) => result.status === "fulfilled").length;
  console.log(
    JSON.stringify({
      scenario,
      fulfilled,
      errors: results.map((result) =>
        result.status === "rejected" ? String(result.reason) : null,
      ),
    }),
  );
  await first.close();
  await second.close();
}
