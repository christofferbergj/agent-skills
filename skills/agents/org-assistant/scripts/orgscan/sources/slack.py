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
PAUSE = float(os.environ.get("ORG_ASSISTANT_SLACK_PAUSE", "30"))  # seconds before the one retry
SPACING = float(os.environ.get("ORG_ASSISTANT_SLACK_SPACING", "3.5"))  # seconds between searches: ≤ 17 a minute


def _messages(result) -> tuple[list[dict], str | None]:
    """A search page as (messages, next cursor). Only ids are kept from it."""
    if not isinstance(result, dict) or not isinstance(result.get("results"), str):
        raise SourceError("Slack search returned no results text")
    text = result["results"]
    numbers = [(int(n), int(of)) for n, of in RESULT.findall(text)]
    # Real records number on without a gap under one "of"; a message body that copies the
    # heading breaks that, and the page is refused rather than read wrong.
    if any(b[0] != a[0] + 1 for a, b in zip(numbers, numbers[1:])) or len({of for _, of in numbers}) > 1:
        raise SourceError("Slack search returned a page whose records can't be told apart")
    found = []
    for block in RESULT.split(text)[3::3]:
        block = block.split("\nText:", 1)[0]  # the record's fields come before its text, which can hold anything
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


def _search(executor, args: dict) -> tuple[list[dict], bool]:
    """Every message a search finds, oldest first, across up to PAGES pages, and whether it
    read them all: a page shorter than the limit, or one with no next cursor, is the last.
    Oldest first means a cut-off search misses only the newest messages, which the next scan
    reads from where this one stopped."""
    args = {**args, "sort": "timestamp", "sort_dir": "asc"}
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
    # One cursor per search. A cut-off search resumes exactly where it stopped; the others
    # reach back OVERLAP for messages Slack indexed late, which their ids keep from counting twice.
    cursors = {name: prev.get("cursors", {}).get(name) or {"at": start} for name in SEARCHES}
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
        after = cursor["at"] if cursor.get("resume") else cursor["at"] - OVERLAP
        found[name], whole = _search(executor, {**COMMON, **filters[name], "after": str(int(after))})
        last = found[name][-1]["ts"] if found[name] else None
        cursors[name] = {"at": now} if whole or not last else {"at": float(last), "resume": True}
    oldest = min([float(w["ts"]) for w in waiting] + [now - OVERLAP])
    mine, _ = _search(executor, {**COMMON, "filters": f"from:<@{me}>", "after": str(int(oldest))})
    changes: list[dict] = []
    known = {(w["channel"], w["ts"]) for w in waiting}
    for message in found["dm"] + found["mention"]:
        if message["from"] in (me, *BOTS) or (message["channel"], message["ts"]) in known:
            continue
        known.add((message["channel"], message["ts"]))
        # The sender's id is needed only for the check above, so it stays out of the snapshot.
        waiting.append({**{k: v for k, v in message.items() if k != "from"}, "woke": False})
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
