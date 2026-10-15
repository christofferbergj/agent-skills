import { createHash } from "node:crypto";
import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { join, relative, resolve } from "node:path";

const scriptsDirectory = import.meta.dir;

function fingerprint(directory: string): string {
  const hash = createHash("sha256");
  function walk(current: string): void {
    for (const item of readdirSync(current, { withFileTypes: true }).sort((a, b) =>
      a.name.localeCompare(b.name),
    )) {
      if (["node_modules", "__pycache__"].includes(item.name) || item.name.startsWith(".pstack-"))
        continue;
      const path = join(current, item.name);
      if (item.isDirectory()) walk(path);
      else if (item.isFile())
        hash.update(relative(directory, path)).update("\0").update(readFileSync(path)).update("\0");
    }
  }
  walk(directory);
  return hash.digest("hex");
}

export function prepareRuntime(): string {
  if (
    process.env.PSTACK_TOOL_RUNTIME === scriptsDirectory &&
    existsSync(join(scriptsDirectory, "node_modules/commander/package.json"))
  )
    return scriptsDirectory;
  const key = fingerprint(scriptsDirectory);
  const base = resolve(
    process.env.PSTACK_CACHE_DIR ||
      join(process.env.XDG_CACHE_HOME || join(homedir(), ".cache"), "pstack", "tools"),
  );
  if (base === scriptsDirectory || base.startsWith(scriptsDirectory + "/"))
    throw new Error("Pstack runtime cache must be outside installed scripts");
  mkdirSync(base, { recursive: true });
  const destination = join(base, key);
  const marker = join(destination, ".pstack-install-key");
  const installed = () =>
    existsSync(join(destination, "node_modules/commander/package.json")) &&
    existsSync(marker) &&
    readFileSync(marker, "utf8").trim() === key;
  if (installed()) return destination;
  const staging = mkdtempSync(join(base, ".pstack-prepare-"));
  try {
    cpSync(scriptsDirectory, staging, {
      recursive: true,
      filter: (source) => !source.split(/[\\/]/).includes("node_modules"),
    });
    const result = Bun.spawnSync([process.execPath, "install", "--frozen-lockfile"], {
      cwd: staging,
    });
    if (result.exitCode !== 0 || !existsSync(join(staging, "node_modules/commander/package.json")))
      throw new Error(`Pstack dependency installation failed with status ${result.exitCode}`);
    writeFileSync(join(staging, ".pstack-install-key"), `${key}\n`);
    try {
      renameSync(staging, destination);
    } catch (error) {
      if (!installed()) throw error;
    }
  } finally {
    if (existsSync(staging)) rmSync(staging, { recursive: true, force: true });
  }
  return destination;
}

export function ensureDependenciesInstalled(): void {
  const runtime = prepareRuntime();
  if (runtime === scriptsDirectory) return;
  const entry = relative(scriptsDirectory, resolve(process.argv[1]));
  if (entry.startsWith("..") || !existsSync(join(runtime, entry)))
    throw new Error("Pstack entrypoint is outside its runtime package");
  const result = Bun.spawnSync([process.execPath, join(runtime, entry), ...process.argv.slice(2)], {
    cwd: process.cwd(),
    env: { ...process.env, PSTACK_TOOL_RUNTIME: runtime },
    stdin: "inherit",
    stdout: "inherit",
    stderr: "inherit",
  });
  process.exit(result.exitCode ?? 1);
}

if (import.meta.main) {
  if (process.argv[2] !== "--print-runtime")
    throw new Error("Usage: bun bootstrap.ts --print-runtime");
  console.log(prepareRuntime());
}
