---
name: pstack-setup
description: "Use when configuring Pstack model roles, effort budgets, optional review providers, or source locations."
---

# Set up Pstack

1. Inspect installed skills, the current host's exposed model choices, optional other CLI availability, and existing configuration. Honor the host's schema and current defaults; `auto` and `inherit-parent` omit overrides. Complete when capabilities and unavailable integrations are explicit.
2. Load `~/.config/pstack/config.json`, or the explicit `PSTACK_CONFIG` path, if present. Keep Codex and Claude Code role settings in separate sections of this one personal file. Read repository overrides only when explicitly configured. Complete when current choices are known without altering global host settings.
3. Ask only for missing preferences: task budget, role choices the user wants to override, optional cross-vendor reviews, and the source repository for learning-driven changes. Offer inherited models as the default. Map effort through actual supported options rather than editing model-slug strings. Complete when every explicit override is available and within the user's choices.
4. Write the agreed personal configuration atomically outside installed instructions. Include a schema version, host role sections, optional review timeout, and source location. Keep credentials in the providers' existing stores, not this file. Complete when the file can be read back and matches the agreed choices.
5. Summarize the location, overrides, prerequisite gaps, and how to return a role to inherited defaults. Offer /pstack-create-verification-skill when the repository lacks a way to prove behavior. When consequential properties need checks beyond ordinary test coverage and no formal verification skill exists, offer the user the explicit /pstack-create-formal-verification-skill entrypoint. Complete when setup status is verifiable without claiming that installation activated the mode.
