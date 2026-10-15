# Trace forensics

Own a diagnosis from the supplied capture, with its limits intact.

1. Identify the artifact format, process/build, time range, workload, sampling method, and known symptom. Preserve the original file. Complete when what the capture can and cannot measure is explicit.
2. Parse with the format's supported tooling. Inspect dominant stacks, timing, allocations, waits, errors, and relevant outliers rather than one attractive frame. Complete when findings cite positions in the artifact and corresponding source where available.
3. Build competing causal explanations and test them against the capture. Use /pstack-how or /pstack-why for code and rationale. Complete when the supported inference and unresolved gaps are distinct.
4. Explain what additional live capture or discriminating probe would settle remaining uncertainty. A capture-only request stays read-only. Complete when the user has a useful diagnosis without an invented runtime result.

Return the finding, artifact evidence, confidence, competing explanations, and next probe.
