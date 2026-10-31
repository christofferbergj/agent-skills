# Explorer model bakeoff, 2026-10-31

Historical evaluation record. Models, plan limits, and timings describe this snapshot; current routing lives in /swarm's [execution contract](../../skills/agents/swarm/references/execution.md).

The owner asked whether Pstack's fast roles should stay on Sonnet in Claude Code. Over the previous 14 days, about 70% of read-only subagents that matched a fast role had run on the session's Opus model anyway, because ad-hoc spawns named no role. Most of them were architecture scans and research, not plain lookups.

## Method

Three real read-only briefs from those sessions were rerun unchanged against the same commits:

| Brief             | Repository and scope                                           |
| ----------------- | -------------------------------------------------------------- |
| Architecture scan | andel-energi monorepo, deepening candidates across portals     |
| Module deep-dive  | fysioscout-web Dashboard `program-templates` slice             |
| Dependency sweep  | adapt-care monorepo, upstream release notes for 11 bump groups |

Each brief ran once on Sonnet 5.5 and Opus 5.5 as Claude Code subagents and once on GPT-6.1 Sol as a read-only T3 Code child task, all at `xhigh`. The reports were relabeled at random. For each brief, one Opus judge and one GPT judge read all three blind, verified every disputed claim and at least five more per report against the code and upstream sources, and ranked them. An earlier round had three Opus judges compare Sonnet and Opus only.

## Results

| Model       | Ranks from Opus judges | Ranks from GPT judges | Accuracy / coverage / judgment, mean of 6 | Mean minutes           |
| ----------- | ---------------------- | --------------------- | ----------------------------------------- | ---------------------- |
| Opus 5.5    | 1, 1, 1                | 2, 2, 2               | 7.7 / 8.3 / 7.3                           | 6.6                    |
| GPT-6.1 Sol | 2, 2, 2                | 1, 1, 1               | 8.8 / 7.8 / 7.8                           | 3.6 fast, 4.5 standard |
| Sonnet 5.5  | 3, 3, 3                | 3, 3, 3               | 6.7 / 6.8 / 6.0                           | 4.2                    |

- Sonnet ranked last in all nine verdicts across both rounds. Its errors were unverified claims, such as a missing `next.config` that exists and a `projection_pending` bug that the code already handles.
- Each judge family ranked its own model first, so the Opus and GPT order is a tie. Scored only by the other family's judges, GPT led on accuracy (9.0 against 7.7) and Opus on coverage (8.0 against 7.0).
- Each model found real defects the others missed, so a union of Opus and GPT findings beats either alone.
- Sonnet made about 25 tool calls per read-only task against Opus's 39 over the 14 days, at the same seconds per call: its speed came from checking less.
- T3 dispatch added about one second. Standard speed ran about 25% slower than fast mode.

## Codex usage

Nine GPT runs moved the Codex weekly window from 41% to 43% used, and the three standard-speed runs did not move it a whole point. That puts one run at roughly 0.15–0.35% of the week. The owner's read-only spawns average about 130 a week, and the plan had changed to Pro Lite five days earlier, with the week on track for about 85% before any explorers. Moving every explorer would risk the reviews' Codex budget, which led to the pace rule.

## Limits

One run per brief per model, three briefs. Judges could likely tell vendors apart by style. Opus was tested at `xhigh`; the native fallback that routing uses is Opus at `high`. GPT at lower effort was not tested.
