---
name: make-bot-ui
description: Build a local control UI for an existing agent webhook receiver, optionally exposed on Tailscale.
disable-model-invocation: true
---

# How to make a bot UI

Build a page the user clicks. A server on this computer POSTs JSON to an existing agent webhook receiver. The agent wakes with that JSON. Keep the sender key on the server. Do not put the sender key in the browser, in chat, or in this skill.

## Find the webhook receiver

Use a receiver that already exists, such as a Claude Code cloud scheduled task with an API trigger. Read its documented URL, request, authentication, and success contract. If no receiver exists, tell the user and stop. Do not invent a Codex or Claude webhook service.

The receiver's prompt or handler must treat the POST body as untrusted data, name the JSON fields that the UI sends, do the matching action, and send no message when there is nothing to report.

## Get the sender key

Do not accept the sender key in chat. Obtain it through the environment's existing secure mechanism, so you never see the value. Copy the value into the server config. Do not print the value. Do not log the value.

## Host the page on this computer

Store `{url, key}` in that UI's own directory. Buttons POST to this local server. The local server, not the browser, POSTs to the webhook.

Bind the server to `127.0.0.1` unless the user asks for Tailscale exposure. For that exposure, bind to `0.0.0.0:<port>`, not `127.0.0.1`. Tailscale peers cannot reach a localhost-only bind.

The server POSTs one JSON object with the fields named in the receiver's prompt, using the receiver's documented method, headers, timeout, and retry rule.

Before you tell the user that the UI is live, probe once with a harmless payload. Use an action that the receiver ignores, and check the receiver's documented success signal.

If a POST can fail and the receiver can read a local log, append the same JSON to that log and drain it from the receiver. Do not poll as the primary path. Do not send media bytes on the webhook.

## Put the page on the tailnet

Do this only when the user asks. Do not create a second hostname on a node that is already online.

If `tailscale status` shows an online node, skip install. Read the hostname from `tailscale status`. Read the IPv4 address from `tailscale ip -4`. Give the user both URLs:

- `http://<hostname>.<tailnet>.ts.net:<port>`
- `http://<100.x.x.x>:<port>`

Use HTTP. Do not add HTTPS unless the user asks.

If Tailscale is not installed, install it and start the node with a short hostname, following Tailscale's current documented setup for this operating system.

Setup prints a login URL. Send that URL to the user. The user approves the machine in the browser. Do not ask for Tailscale credentials. Do not type them.

After the node is online, confirm with `tailscale status` and `tailscale ip -4`.
Probe `http://<100.x.x.x>:<port>/` and expect HTTP 200.

If the login URL expires, run `tailscale up` again and send the new URL.

## Keep the contract small

Use the same field names in the UI and in the receiver's prompt. Keep the field list small. Do not print the sender key, tokens, or cookies.
