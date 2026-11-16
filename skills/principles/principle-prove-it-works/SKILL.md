---
name: principle-prove-it-works
description: "Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'"
---

# Prove It Works

Verify every output by checking the real thing directly: run the feature, read the actual value, inspect the diff. Proxies (file mtimes, self-reports, cached output, "it compiles") do not count. When a check fails, suspect the observation method before the system.

For changed runtime behavior, drive the real user or caller path through the project's verification skill or available browser, Computer Use, CLI, or service tools. A Claude session without a Computer Use tool hands a check that needs one to Codex through /swarm's Computer Use route. Inspect promised durable effects as well as the response. Tests provide supporting evidence; report a blocked real-path check as a gap rather than treating a unit-test pass as its substitute. For planning or review phases, the real artifact is the spec, graph, or reviewed diff; this principle does not start implementation.

Script the check when you can. A deterministic script that reruns the comparison beats a one-time look. Keep its output where the human can see it, and commit it only when the trail must be auditable later.
