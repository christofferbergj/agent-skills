"""T3 Code: threads in the organisation's projects that wait on the user, and threads the
assistant started, through `t3 thread list`. Keeps thread ids and statuses, never titles."""
from __future__ import annotations

from datetime import timezone

from ..calls import SourceError, run_json
from ..changes import change

DONE = {"completed", "failed", "cancelled", "interrupted", "stopped"}
WAITS = "waiting"


def scan(source: dict, prev: dict | None, ctx) -> tuple[dict, list[dict]]:
    baseline = prev is None and ctx.since is None
    prev = prev or {}
    now = ctx.now.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    started = {entry.get("thread"): entry for entry in ctx.ledger.get("started", [])}
    seen = prev.get("threads", {})
    threads: dict = {}
    changes: list[dict] = []
    for project in source.get("projects", []):
        listed = run_json(["t3", "thread", "list", "--project", project["path"], "--json", "--log-level", "error"],
                          f"T3 threads in {project['path']}")
        for thread in listed if isinstance(listed, list) else []:
            ident = thread.get("threadId")
            if not ident or ident == ctx.thread or thread.get("archived"):
                continue
            status = thread.get("status") or ""
            if thread.get("settled") and ident not in started:
                continue
            threads[ident] = status
            was = seen.get(ident)
            if baseline or was == status:
                continue
            ref = f"t3:{ident}"
            if ident in started:
                ticket = started[ident].get("ticket", "")
                if status in DONE:
                    changes.append(change("thread.finished", ref, now, key=f"{status}:{thread.get('updatedAt')}",
                                          status=status, ticket=ticket, link=thread.get("link", "")))
                elif status == WAITS:
                    changes.append(change("thread.waiting", ref, now, key=f"waiting:{thread.get('updatedAt')}",
                                          ticket=ticket, link=thread.get("link", "")))
            elif status == WAITS:
                changes.append(change("thread.waits_on_you", ref, now, key=f"waiting:{thread.get('updatedAt')}",
                                      link=thread.get("link", "")))
    return {"threads": threads}, changes


def show(thread: str) -> dict | None:
    """The assistant thread's state and its last message, or None when it can't be read."""
    try:
        shown = run_json(["t3", "thread", "show", thread, "--json", "--messages", "1", "--log-level", "error"],
                         "the assistant thread")
    except SourceError:
        return None
    if not isinstance(shown, dict) or not isinstance(shown.get("thread"), dict):
        return None
    last = (shown.get("messages") or [{}])[-1]
    return {**shown["thread"], "lastText": last.get("text", "") if last.get("role") == "assistant" else ""}
