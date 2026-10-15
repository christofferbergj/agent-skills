---
name: pstack-make-bot-ui
description: "Use when building a Pstack control UI for an existing agent webhook receiver or explicitly exposing it on Tailscale."
---

# Make a webhook control UI

1. Identify an existing receiver and read its documented request, authentication, and success contracts. Confirm which event starts agent work and how delivery can be observed. If no receiver exists, report that prerequisite and stop this integration path. Complete when the endpoint contract is known without inventing a Codex or Claude webhook service.
2. Define the UI's small action schema and the receiver's allowed operations. Treat request bodies as untrusted data. Obtain credentials through the environment's existing secure mechanism and keep them server-side. Complete when input validation, authorization, and credential storage are concrete.
3. Build a UI and local server-side proxy using the repository's stack. Bind to localhost by default. Follow the receiver's actual headers, timeout, idempotency, and retry contract; never treat an arbitrary HTTP 200 as proof that work started. Complete when browser requests reach only the local proxy and the proxy follows the documented receiver protocol.
4. Verify with a harmless supported event or a contract fixture, then inspect the corresponding delivery or execution evidence. Preserve failures visibly; a durable retry queue is appropriate only when the receiver can actually drain or acknowledge it. Complete when the claimed delivery behavior has evidence and any real-service gap is stated.
5. Expose the UI through Tailscale only when requested. Reuse an existing node, inspect the available CLI, and follow current documented setup if a node is needed. Complete when the requested URL is reachable from the intended network and its access boundary is clear.

Return local URLs, the action contract, delivery evidence, and remaining prerequisites. Provide additional network URLs only for exposure the user requested.
