import { createHash, randomUUID } from "node:crypto";
import { link, readFile, readlink, rm, symlink, unlink, writeFile } from "node:fs/promises";
import { basename, join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";

const LOCK_FILE = ".orch.lock";
const GUARD_FILE = `${LOCK_FILE}.guard`;

export interface OpenStoreOptions {
  readonly force?: boolean;
  readonly onLockStolen?: (holder: string) => void;
  readonly onStaleLock?: (holder: string) => void;
}

export class LockError extends Error {}

function errorCode(error: unknown): string | null {
  return error !== null &&
    typeof error === "object" &&
    "code" in error &&
    typeof error.code === "string"
    ? error.code
    : null;
}

function holderIsDead(holder: string): boolean {
  const pid = Number.parseInt(holder, 10);
  if (!Number.isSafeInteger(pid) || pid <= 0 || String(pid) !== holder) return false;
  try {
    process.kill(pid, 0);
    return false;
  } catch (error) {
    return errorCode(error) === "ESRCH";
  }
}

async function guardToken(path: string): Promise<string | null> {
  try {
    return await readlink(path);
  } catch (error) {
    if (errorCode(error) === "ENOENT") return null;
    if (errorCode(error) === "EINVAL")
      throw new LockError("store lock maintenance has an unknown owner");
    throw error;
  }
}

// A symlink publishes its owner atomically. Live guards are never stolen, even
// with --force. Every deletion of a dead guard holds the guard for that exact
// token, so a delayed reclaimer cannot delete a successor. Recovery uses the
// same protocol if a process dies while holding a recovery guard.
async function withGuard<T>(store: string, name: string, operation: () => Promise<T>): Promise<T> {
  const path = join(store, name);
  const token = `${process.pid}:${randomUUID()}`;
  for (let attempts = 0; ; attempts += 1) {
    try {
      await symlink(token, path);
      break;
    } catch (error) {
      if (errorCode(error) !== "EEXIST") throw error;
    }
    const observed = await guardToken(path);
    if (observed === null) continue;
    const holder = observed.split(":")[0] ?? "unknown";
    if (holderIsDead(holder)) {
      const recovery = createHash("sha256")
        .update(basename(path))
        .update("\0")
        .update(observed)
        .digest("hex");
      await withGuard(store, `${GUARD_FILE}.${recovery}`, async () => {
        if ((await guardToken(path)) === observed) await unlink(path);
      });
    } else {
      if (attempts >= 100)
        throw new LockError(`store lock maintenance held by pid ${holder}; retry`);
      await delay(10);
    }
  }
  try {
    return await operation();
  } finally {
    // Only this live owner can remove this guard.
    await unlink(path);
  }
}

async function lockContents(path: string): Promise<string | null> {
  try {
    return await readFile(path, "utf8");
  } catch (error) {
    if (errorCode(error) === "ENOENT") return null;
    throw error;
  }
}

export async function acquireLock(
  store: string,
  options: OpenStoreOptions,
): Promise<() => Promise<void>> {
  const path = join(store, LOCK_FILE);
  const lease = `${process.pid}\n${randomUUID()}\n`;
  await withGuard(store, GUARD_FILE, async () => {
    const current = await lockContents(path);
    if (current !== null) {
      // Legacy locks contain only the PID; new leases add an instance identity.
      const holder = current.split("\n")[0]?.trim() || "unknown";
      if (holderIsDead(holder)) options.onStaleLock?.(holder);
      else if (options.force) options.onLockStolen?.(holder);
      else throw new LockError(`store lock held by pid ${holder}`);
      await unlink(path);
    }
    // Publish only a complete lease. A crash leaves either no main lock or a
    // complete PID that the next process can automatically reclaim.
    const temporary = join(store, `${LOCK_FILE}.${process.pid}.${randomUUID()}.tmp`);
    try {
      await writeFile(temporary, lease, { flag: "wx" });
      await link(temporary, path);
    } finally {
      await rm(temporary, { force: true });
    }
  });
  return async () => {
    await withGuard(store, GUARD_FILE, async () => {
      if ((await lockContents(path)) === lease) await unlink(path);
    });
  };
}
