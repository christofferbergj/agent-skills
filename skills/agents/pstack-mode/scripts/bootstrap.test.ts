import { expect, test } from "bun:test";
import { createHash } from "node:crypto";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

test("bootstrap prepares an external runtime idempotently without editing source", async () => {
  const cache = mkdtempSync(join(tmpdir(), "pstack-runtime-test-"));
  const entry = join(import.meta.dir, "bootstrap.ts");
  const digest = () =>
    createHash("sha256")
      .update(readFileSync(entry))
      .update(readFileSync(join(import.meta.dir, "package.json")))
      .update(readFileSync(join(import.meta.dir, "bun.lock")))
      .digest("hex");
  const before = digest();
  try {
    const invoke = async () => {
      const child = Bun.spawn([process.execPath, entry, "--print-runtime"], {
        env: { ...process.env, PSTACK_CACHE_DIR: cache, PSTACK_TOOL_RUNTIME: "" },
        stdout: "pipe",
        stderr: "pipe",
      });
      const output = (await new Response(child.stdout).text()).trim();
      expect(await child.exited).toBe(0);
      expect(output.startsWith(cache + "/")).toBe(true);
      expect(existsSync(join(output, "node_modules/commander/package.json"))).toBe(true);
      return output;
    };
    const [first, concurrent] = await Promise.all([invoke(), invoke()]);
    expect(first).toBe(concurrent);
    expect(await invoke()).toBe(first);
    expect(digest()).toBe(before);
  } finally {
    rmSync(cache, { recursive: true, force: true });
  }
}, 30000);
