---
name: pstack-make-bot-ui
description: Build a local control UI for an existing agent webhook receiver, optionally exposed on Tailscale.
disable-model-invocation: true
---

# Make a webhook control UI

1. Identify an existing receiver and read its documented request, authentication, and success contracts. Confirm which event starts agent work and how delivery can be observed. If no receiver exists, report that prerequisite and stop this integration path. Complete when the endpoint contract is known without inventing a Codex or Claude webhook service.
2. Define the UI's small action schema and the receiver's allowed operations. Treat request bodies as untrusted data. Obtain credentials through the environment's existing secure mechanism and keep them server-side. Do not put the credential in the browser, in chat, or in this skill. Do not print the value. Do not log the value. Complete when input validation, authorization, and credential storage are concrete.
3. Build a UI and local server-side proxy using the repository's stack. Bind to localhost by default. Follow the receiver's actual headers, timeout, idempotency, and retry contract; never treat an arbitrary HTTP 200 as proof that work started. Do not send media bytes on the webhook. Complete when browser requests reach only the local proxy and the proxy follows the documented receiver protocol.
4. Verify with a harmless supported event or a contract fixture, then inspect the corresponding delivery or execution evidence. Preserve failures visibly; a durable retry queue is appropriate only when the receiver can actually drain or acknowledge it. Complete when the claimed delivery behavior has evidence and any real-service gap is stated.
5. Expose the UI through Tailscale only when requested. Reuse an existing node, inspect the available CLI, and follow current documented setup if a node is needed. Do not create a second hostname on a node that is already online. Bind the server to `0.0.0.0:<port>`, not `127.0.0.1`, for this exposure. Tailscale peers cannot reach a localhost-only bind. When setup prints a login URL, send that URL to the user. The user approves the machine in the browser. Do not ask for Tailscale credentials. Do not type them. If the login URL expires, run `tailscale up` again and send the new URL. Give the user both `http://<hostname>.<tailnet>.ts.net:<port>` and `http://<100.x.x.x>:<port>`. Use HTTP. Do not add HTTPS unless the user asks. Complete when the requested URL is reachable from the intended network and its access boundary is clear.

Return local URLs, the action contract, delivery evidence, and remaining prerequisites. Provide additional network URLs only for exposure the user requested.
