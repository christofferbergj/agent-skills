# Runtime forensics

Own a diagnosis from live instrumentation. A diagnosis request does not authorize a fix.

1. Define the symptom, affected process, version, workload, and observable predicate. Establish a reproducible baseline and process ownership before instrumentation. Complete when the capture targets the actual failing path.
2. Choose the least intrusive applicable instrument: CPU profiler, allocation or heap capture, task/thread state, event-loop tracing, network timing, or syscall/process sampling. Use available native tools and repository diagnostics. Record overhead and missing access. Complete when a representative capture and its conditions are saved.
3. Follow causal evidence through stacks, lifetimes, queues, locks, or I/O. Distinguish observation from inference, and use /pstack-how or /pstack-why where code or historical rationale matters. Complete when the explanation predicts a discriminating probe.
4. Run that probe without changing production behavior and compare the signal. Invoke /pstack-benchmark-checklist for measured claims. Complete when the diagnosis is supported or competing hypotheses remain explicitly unresolved.
5. Stop only instrumentation and processes this run owns, retaining evidence. Complete when the report can be audited and the user's environment is left in its prior state.

Return diagnosis, capture paths, causal chain, confidence, alternatives, and the next justified action.
