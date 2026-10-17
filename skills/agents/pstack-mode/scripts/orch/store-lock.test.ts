import { afterEach, describe, expect, it } from "bun:test";
import { mkdtemp, readdir, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { openStore, type Store } from "./store.ts";

const FIXTURE = join(import.meta.dir, "lock.test-helper.ts");
const directories: string[] = [];
const stores: Store[] = [];

async function makeDirectory(): Promise<string> {
  const directory = await mkdtemp(join(tmpdir(), "orch-lock-test-"));
  directories.push(directory);
  return directory;
}
function useStore(directory: string, force = false): Store {
  const store = openStore(directory, { force });
  stores.push(store);
  return store;
}
async function deadPid(): Promise<number> {
  const child = Bun.spawn(["true"]);
  await child.exited;
  return child.pid;
}
async function fixture(scenario: string, directory: string) {
  const child = Bun.spawn([process.execPath, FIXTURE, scenario, directory], {
    stdout: "pipe",
    stderr: "pipe",
  });
  const timeout = setTimeout(() => child.kill(), 3_000);
  try {
    const [stdout, stderr, code] = await Promise.all([
      new Response(child.stdout).text(),
      new Response(child.stderr).text(),
      child.exited,
    ]);
    expect({ code, stderr }).toEqual({ code: 0, stderr: "" });
    return stdout;
  } finally {
    clearTimeout(timeout);
  }
}

afterEach(async () => {
  await Promise.all(stores.splice(0).map((store) => store.close()));
  await Promise.all(
    directories.splice(0).map((directory) => rm(directory, { force: true, recursive: true })),
  );
});

describe("orch store lock ownership", () => {
  it("retries a failed close without reopening writes", async () => {
    const directory = await makeDirectory();
    const result = JSON.parse(await fixture("close-retry", directory));
    expect(result.failures).toHaveLength(1);
    expect(result.failures[0]).toContain("store lock maintenance held by pid");
    expect(result.blockedDuringClose).toContain("store is closed");
    expect(result.blockedWrite).toContain("store is closed");
    expect(result.competitor).toContain("store lock held by pid");
    expect(result.retryClose).toBe("closed");
    expect(result.thirdOpen).toBe("acquired");
  });

  it("shares concurrent close failures and retries the retained release", async () => {
    const directory = await makeDirectory();
    const result = JSON.parse(await fixture("close-concurrent", directory));
    expect(result.failures).toHaveLength(2);
    for (const failure of result.failures) {
      expect(failure).toContain("store lock maintenance held by pid");
    }
    expect(result.blockedDuringClose).toContain("store is closed");
    expect(result.blockedWrite).toContain("store is closed");
    expect(result.retryClose).toBe("closed");
    expect(result.thirdOpen).toBe("acquired");
  });

  it("admits only one of two contenders recovering the same stale lock", async () => {
    const directory = await makeDirectory();
    await writeFile(join(directory, ".orch.lock"), `${await deadPid()}\n`);
    const result = JSON.parse(await fixture("stale-race", directory));
    expect(result.fulfilled).toBe(1);
    expect(result.errors.filter((error: unknown) => error !== null)).toHaveLength(1);
  });

  it("keeps a forced successor locked when the earlier handle closes in the same process", async () => {
    const directory = await makeDirectory();
    const first = useStore(directory);
    await first.init();
    const forced = useStore(directory, true);
    await forced.init();
    await first.close();
    const third = useStore(directory);
    await expect(third.init()).rejects.toThrow("store lock held by pid");
    await forced.close();
    await expect(third.init()).resolves.toEqual({ store: directory });
  });

  it("keeps a successor locked when force races an earlier handle's release", async () => {
    const directory = await makeDirectory();
    const result = JSON.parse(await fixture("release-race", directory));
    expect(result.fulfilled).toBe(0);
    expect(result.errors[0]).toContain("store lock held by pid");
  });

  for (const boundary of ["guard", "recovery", "before-link", "after-link", "after-unlink"]) {
    it(`automatically recovers after a process dies at ${boundary}`, async () => {
      const directory = await makeDirectory();
      if (boundary === "recovery") {
        const pid = await deadPid();
        await symlink(`${pid}:previous-recovery`, join(directory, ".orch.lock.guard"));
      }
      if (boundary === "after-unlink") {
        await writeFile(join(directory, ".orch.lock"), `${await deadPid()}\n`);
      }
      await fixture(`crash-${boundary}`, directory);
      const recovered = useStore(directory);
      await recovered.init();
      expect(await recovered.units.add({ id: "recovered", track: "build" })).toMatchObject({
        id: "recovered",
      });
      await recovered.close();
      expect(await readdir(directory)).not.toContain(".orch.lock");
      expect(await readdir(directory)).not.toContain(".orch.lock.guard");
    });
  }

  it("admits only one live process after recovering a crashed writer", async () => {
    const directory = await makeDirectory();
    await fixture("crash-after-link", directory);
    const children = Array.from({ length: 4 }, () =>
      Bun.spawn([process.execPath, FIXTURE, "hold", directory], { stdout: "pipe", stderr: "pipe" }),
    );
    try {
      const results = await Promise.all(
        children.map(async (child) => {
          const reader = child.stdout.getReader();
          const first = await reader.read();
          reader.releaseLock();
          return new TextDecoder().decode(first.value).trim();
        }),
      );
      expect(results.sort()).toEqual(["acquired", "blocked", "blocked", "blocked"]);
    } finally {
      for (const child of children) child.kill();
      await Promise.all(children.map((child) => child.exited));
    }
  });
});
