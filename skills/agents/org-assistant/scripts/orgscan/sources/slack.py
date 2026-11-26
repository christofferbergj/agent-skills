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
OVERLAP = 600  # seconds each search reaches back before the cursor, for messages Slack indexed late
CHANNEL = re.compile(r"^Channel: (.*?)\s*\(ID: ([A-Z0-9]+)\)", re.M)
FROM = re.compile(r"^From: .*\(ID: ([A-Z0-9]+)\)", re.M)
TS = re.compile(r"^Message_ts: ([0-9]+\.[0-9]+)", re.M)
THREAD = re.compile(r"[?&]thread_ts=([0-9]+\.[0-9]+)")
COUNT = re.compile(r"\((\d+) results?\)")
CURSOR = re.compile(r"`([A-Za-z0-9+/=_-]{8,})`")
BOTS = {"U00", "USLACKBOT"}
PAUSE = float(os.environ.get("ORG_ASSISTANT_SLACK_PAUSE", "30"))  # seconds before the one retry
SPACING = float(os.environ.get("ORG_ASSISTANT_SLACK_SPACING", "3.5"))  # seconds between searches: ≤ 17 a minute


def _messages(result) -> tuple[list[dict], int, str | None]:
    """A search page as (messages, total, next cursor). Only ids are kept from it."""
    if not isinstance(result, dict) or not isinstance(result.get("results"), str):
        raise SourceError("Slack search returned no results text")
    text = result["results"]
    total = COUNT.search(text)
    found = []
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        channel, sender, ts = CHANNEL.search(block), FROM.search(block), TS.search(block)
        if not (channel and ts):
            continue
        thread = THREAD.search(block)
        label = channel.group(1)
        found.append({"channel": channel.group(2), "ts": ts.group(1), "from": sender.group(1) if sender else "",
                      "thread": thread.group(1) if thread and thread.group(1) != ts.group(1) else None,
                      "dm": label.startswith("DM") or label.startswith("Group DM")})
    cursor = CURSOR.search(str(result.get("pagination_info") or ""))
    return found, int(total.group(1)) if total else len(found), cursor.group(1) if cursor else None


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
    read them all. Oldest first means a cut-off search misses only the newest messages, which
    the next scan reads from where this one stopped."""
    found, total, cursor = _messages(_call(executor, {**args, "sort": "timestamp", "sort_dir": "asc"}))
    for _ in range(PAGES - 1):
        if not cursor or len(found) >= total:
            break
        more, _, cursor = _messages(_call(executor, {**args, "sort": "timestamp", "sort_dir": "asc", "cursor": cursor}))
        if not more:
            break
        found.extend(more)
    return found, len(found) >= total


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
    after = prev.get("at") or (ctx.since.timestamp() if ctx.since else now)
    wait = ctx.schedule["slack_wait_minutes"] * 60
    common = {"response_format": "detailed", "include_context": False, "limit": 20}
    waiting = [w for w in prev.get("waiting", []) if now - float(w["ts"]) < FORGET.total_seconds()]
    if baseline:
        return {"at": now, "waiting": waiting}, []
    changes: list[dict] = []
    entries = [e if isinstance(e, dict) else {"id": e} for e in source.get("channels", [])]
    reach = int(after - OVERLAP)
    oldest = int(min([float(w["ts"]) for w in waiting] + [reach]))
    direct, whole_direct = _search(executor, {**common, "filters": "to:me", "channel_types": "im,mpim",
                                              "after": str(reach)})
    mentions, whole_mentions = _search(executor, {**common, "keywords": [f"<@{me}>"], "after": str(reach)})
    mine, _ = _search(executor, {**common, "filters": f"from:<@{me}>", "after": str(oldest)})
    # One search covers every confirmed channel: Slack ORs a repeated in: filter.
    listened, _ = _search(executor, {**common, "after": str(int(after)),
                                     "filters": " ".join(f"in:<#{e['id']}>" for e in entries)}) if entries else ([], True)
    known = {(w["channel"], w["ts"]) for w in waiting}
    for message in direct + mentions:
        if message["from"] in (me, *BOTS) or (message["channel"], message["ts"]) in known:
            continue
        known.add((message["channel"], message["ts"]))
        waiting.append({**message, "woke": False})
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
                                  sender=item["from"], minutes=int(age // 60)))
        kept.append(item)
    window = iso(from_ts(after))
    for entry in entries:
        count = sum(1 for m in listened if m["channel"] == entry["id"] and m["from"] != me)
        if count:
            changes.append(change("slack.channel", entry["id"], iso(from_ts(now)), key=window,
                                  scope=f"slack:{entry['id']}", name=entry.get("name", entry["id"]), messages=count))
    # A cut-off search resumes after the newest message it read; the rest start from now.
    cut = [found[-1]["ts"] for found, whole in ((direct, whole_direct), (mentions, whole_mentions))
           if not whole and found]
    return {"at": min([now] + [float(ts) for ts in cut]), "waiting": kept}, changes
