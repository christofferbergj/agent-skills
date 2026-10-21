# pstack-make-bot-ui: source and local adaptations

## Source and credit

- Original author: Lauren Tan, known as Poteto.
- Canonical source: [cursor/plugins, Pstack](https://github.com/cursor/plugins/tree/main/pstack).
- Original skill: [`pstack/skills/make-bot-ui/SKILL.md`](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/make-bot-ui/SKILL.md), including its skill-local resources.
- Tracking policy: upstream `main`, scoped to `pstack/`.
- Imported from commit: `e5136d82418d2db3165ea1050d17577cd618cc05`.
- Reviewed through commit: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Fidelity checked through: `190d28736eff128ec94f502a22c7fe0c4b56cd37`.
- Last upstream review: 2026-10-21.
- License: [MIT, copyright 2026 Lauren Tan](LICENSE). Retain this notice with derived material.

## Local adaptations to preserve

- The [library-wide adaptations](../../agents/maintain-skills/references/ADAPTATION.md#library-wide-adaptations) apply; this list holds only this skill's own divergences.
- Model-invoked, where upstream is user-invoked: a Pstack helper whose description scopes triggering to Pstack tasks.
- Works against an existing receiver's documented contract and stops when none exists. Upstream's Cursor routine creation (`update_state`), routine-panel URL and sender-key steps, `SendToUser` secret request, and `[routine]` wake format have no Codex or Claude Code equivalent, so the skill does not invent a webhook service; generic sender-key wording becomes the credential.
- Replaces upstream's fixed request (Bearer and `X-Automation-Key` headers, 8-second timeout, one try, HTTP 200 means the routine woke) with the receiver's documented headers, timeout, idempotency, and retry contract, and requires delivery evidence beyond a 200.
- Binds to localhost by default and binds to `0.0.0.0` only for a requested Tailscale exposure; upstream always binds `0.0.0.0`. A credential-holding proxy stays off other networks unless the user asks.
- Keeps a durable retry queue only when the receiver can drain or acknowledge it, instead of upstream's log drained by the Cursor routine and its no-polling rule.
- Follows current documented Tailscale setup for the host instead of upstream's Linux `install.sh` and fixed `tailscale up` flags, and drops upstream's statement that agents on this computer share one node, which describes Cursor's machine.
- Each step ends with a completion criterion, per the repository's skill rules.

## Maintenance

Invoke `/maintain-skills` for repository-wide upkeep, including this suite's supporting files and shared consumers. Reinstalling from this repository refreshes the adaptation; it does not merge Cursor's originals.

Keep the original import fixed. Advance the reviewed-through baseline only after the relevant delta is fully resolved and checks pass. Record adopted, adapted, and excluded changes and their reasons.

| Review date | Candidate revision                         | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-15  | `e5136d82418d2db3165ea1050d17577cd618cc05` | Imported and adapted the complete pinned skill and required resources for the agreed portable suite. Retained original intent; replaced host-specific integration and policy where necessary.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2026-10-18  | `0b8e952052d482ee6de06deebf14d590d77b1b34` | Reviewed the upstream lowercase frontmatter-name repair. The local pstack-make-bot-ui name and metadata already satisfy the same requirement; retained the portable existing-webhook contract, credential handling, delivery proof, and requested-only Tailscale exposure. Repository gates and independent native review pass; no service behavior changed.                                                                                                                                                                                                                                                                                                                                                           |
| 2026-10-21  | `190d28736eff128ec94f502a22c7fe0c4b56cd37` | No upstream change in `pstack/skills/make-bot-ui/` since `0b8e952`. First fidelity check: restored dropped host-neutral rules (keep the credential out of the browser, chat, and skill and never print or log it; no media bytes on the webhook; no second hostname on an online node; bind `0.0.0.0` for tailnet exposure because peers cannot reach a localhost bind; the user approves the login URL, a fresh one after expiry, and the agent never handles Tailscale credentials; give both tailnet URLs; HTTP unless asked) and recorded the receiver-contract, localhost-default, retry, setup, and invocation divergences. Tailscale 1.102.2 `up --help` still lists `--hostname`, `--accept-dns`, and `--ssh`. |
