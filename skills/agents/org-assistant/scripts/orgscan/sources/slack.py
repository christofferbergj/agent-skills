"""Slack: direct messages and mentions the user hasn't answered, and a message count for
each confirmed channel. The waiting list is kept apart from the search cursor, so a message
stays on it across scans until the user answers or it has woken the thread once. Keeps
channel, message, and staff user ids only: the search text is parsed for them and dropped."""
from __future__ import annotations

import os
import re
import time
from datetime import timedelta

from ..calls import LIMITED, SourceError
from ..changes import change
from ..times import from_ts, iso

TOOL = "tools.slack.mcp.slack_search_public_and_private"
TOOLS = (TOOL,)
PAGES = 10  # 20 messages a page
FORGET = timedelta(days=3)  # a waiting message older than this leaves the list
SEARCHES = ("dm", "mention", "channels")
COMMON = {"response_format": "detailed", "include_context": False, "limit": 20}
OVERLAP = 600  # seconds each search reaches back before the cursor, for messages Slack indexed late
RESULT = re.compile(r"^### Result (\d+) of (\d+)\s*$", re.M)
CHANNEL = re.compile(r"^Channel: (.*?)\s*\(ID: ([A-Z0-9]+)\)", re.M)
FROM = re.compile(r"^From: .*\(ID: ([A-Z0-9]+)\)", re.M)
TS = re.compile(r"^Message_ts: ([0-9]+\.[0-9]+)", re.M)
THREAD = re.compile(r"[?&]thread_ts=([0-9]+\.[0-9]+)")
CURSOR = re.compile(r"`([A-Za-z0-9+/=_-]{8,})`")
BOTS = {"U00", "USLACKBOT"}
PAUSE = float(os.environ.get("ORG_ASSISTANT_SLACK_PAUSE", "60"))  # seconds before the one retry
SPACING = float(os.environ.get("ORG_ASSISTANT_SLACK_SPACING", "6"))  # seconds between searches: ≤ 10 a minute


def _records(text: str) -> list[str]:
    """Each record's field lines: from its `### Result N of M` heading up to its `Text:` line.
    A heading counts only when it numbers on from the one before under the page's own total,
    so a message body that copies a heading stays part of that message, and is never read."""
    headings, expected, total = [], None, None
    for match in RESULT.finditer(text):
        number, of = int(match.group(1)), int(match.group(2))
        if (expected is None or (number == expected and of == total)) and number <= of:
            headings.append(match)
            expected, total = number + 1, of
    ends = [h.start() for h in headings[1:]] + [len(text)]
    return [text[h.end():end].split("\nText:", 1)[0] for h, end in zip(headings, ends)]


def _messages(result) -> tuple[list[dict], str | None]:
    """A search page as (messages, next cursor). Only ids are kept from it."""
    if not isinstance(result, dict) or not isinstance(result.get("results"), str):
        raise SourceError("Slack search returned no results text")
    found = []
    for block in _records(result["results"]):
        channel, sender, ts = CHANNEL.search(block), FROM.search(block), TS.search(block)
        if not (channel and ts):
            continue
        thread = THREAD.search(block)
        label = channel.group(1)
        found.append({"channel": channel.group(2), "ts": ts.group(1), "from": sender.group(1) if sender else "",
                      "thread": thread.group(1) if thread and thread.group(1) != ts.group(1) else None,
                      "dm": label.startswith("DM") or label.startswith("Group DM")})
    cursor = CURSOR.search(str(result.get("pagination_info") or ""))
    return found, cursor.group(1) if cursor else None


def _call(executor, args: dict):
    """One search call. Slack limits search bursts, so searches go one at a time, and a
    rate-limited call waits and tries once more before it fails the source."""
    time.sleep(SPACING)
    try:
        return executor.call([(TOOL, args)])[0]
    except SourceError as error:
        if not LIMITED.search(str(error)):
            raise
        time.sleep(PAUSE)
        return executor.call([(TOOL, args)])[0]


def _search(executor, args: dict, order: str = "asc") -> tuple[list[dict], bool]:
    """Every message a search finds, oldest first, across up to PAGES pages, and whether it
    read them all: a page shorter than the limit, or one with no next cursor, is the last.
    Oldest first means a cut-off search misses only the newest messages, which the next scan
    reads from where this one stopped."""
    args = {**args, "sort": "timestamp", "sort_dir": order}
    found, cursor = [], None
    for _ in range(PAGES):
        page, cursor = _messages(_call(executor, {**args, **({"cursor": cursor} if cursor else {})}))
        found.extend(page)
        if not cursor or len(page) < args.get("limit", 20):
            return found, True
    return found, False


def still_waiting(section: dict, item: dict) -> bool:
    """A gathered `slack.waiting` stays only while its message is still unanswered."""
    if item["kind"] != "slack.waiting":
        return True
    return item["ref"] in {f"slack:{w['channel']}:{w['ts']}" for w in section.get("waiting", [])}


def _answered(item: dict, mine: list[dict]) -> bool:
    """The user wrote after it in the same DM, or in the same channel thread."""
    for reply in mine:
        if reply["channel"] != item["channel"] or float(reply["ts"]) <= float(item["ts"]):
            continue
        if item["dm"] or (reply["thread"] or reply["ts"]) == (item["thread"] or item["ts"]) or \
                reply["thread"] == item["ts"]:
            return True
    return False


def scan(source: dict, prev: dict | None, ctx) -> tuple[dict, list[dict]]:
    executor = ctx.executor(source, TOOLS)
    me = source.get("me")
    if not me:
        raise SourceError("the profile's slack source has no `me` user id")
    now = ctx.now.timestamp()
    baseline = prev is None and ctx.since is None
    prev = prev or {}
    start = ctx.since.timestamp() if ctx.since else now
    # One cursor per search. `reach` says where the next search starts: OVERLAP back from `at`,
    # for messages Slack indexed late, or exactly at it when a cut-off search made no progress
    # past its cursor, so a burst can't replay forever.
    cursors = {name: prev.get("cursors", {}).get(name) or {"at": start, "reach": "overlap"} for name in SEARCHES}
    wait = ctx.schedule["slack_wait_minutes"] * 60
    waiting = [w for w in prev.get("waiting", []) if now - float(w["ts"]) < FORGET.total_seconds()]
    if baseline:
        return {"cursors": cursors, "waiting": waiting}, []
    entries = [e if isinstance(e, dict) else {"id": e} for e in source.get("channels", [])]
    filters = {"dm": {"filters": "to:me", "channel_types": "im,mpim"}, "mention": {"keywords": [f"<@{me}>"]},
               "channels": {"filters": " ".join(f"in:<#{e['id']}>" for e in entries)}}
    found = {}
    for name in SEARCHES:
        if name == "channels" and not entries:
            found[name] = []
            continue
        cursor = cursors[name]
        after = cursor["at"] if cursor.get("reach") == "exact" else cursor["at"] - OVERLAP
        found[name], whole = _search(executor, {**COMMON, **filters[name], "after": str(int(after))})
        last = float(found[name][-1]["ts"]) if found[name] else None
        if whole or last is None:
            cursors[name] = {"at": now, "reach": "overlap"}
        else:
            stuck = cursor.get("reach") in ("resume", "exact") and last <= cursor["at"]
            cursors[name] = {"at": max(last, cursor["at"]), "reach": "exact" if stuck else "resume"}
    changes: list[dict] = []
    known = {(w["channel"], w["ts"]) for w in waiting}
    for message in found["dm"] + found["mention"]:
        if message["from"] in (me, *BOTS) or (message["channel"], message["ts"]) in known:
            continue
        known.add((message["channel"], message["ts"]))
        # The sender's id is needed only for the check above, so it stays out of the snapshot.
        waiting.append({**{k: v for k, v in message.items() if k != "from"}, "woke": False})
    # The user's own messages since the oldest one still waiting, newest first: a cut-off read
    # then misses only the oldest replies, never the reply to a message that just arrived.
    oldest = min([float(w["ts"]) for w in waiting] + [now - OVERLAP])
    mine, _ = _search(executor, {**COMMON, "filters": f"from:<@{me}>", "after": str(int(oldest))}, order="desc")
    kept = []
    for item in waiting:
        if _answered(item, mine):
            continue
        age = now - float(item["ts"])
        if age >= wait and not item["woke"]:
            item = {**item, "woke": True}
            changes.append(change("slack.waiting", f"slack:{item['channel']}:{item['ts']}", iso(from_ts(item["ts"])),
                                  key="waiting", scope=f"slack:{item['channel']}",
                                  via="dm" if item["dm"] else "mention", channel=item["channel"],
                                  minutes=int(age // 60)))
        kept.append(item)
    names = {e["id"]: e.get("name", e["id"]) for e in entries}
    for message in found["channels"]:
        if message["channel"] in names and message["from"] != me:
            changes.append(change("slack.channel", message["channel"], iso(from_ts(message["ts"])), key=message["ts"],
                                  scope=f"slack:{message['channel']}", name=names[message["channel"]]))
    return {"cursors": cursors, "waiting": kept}, changes
