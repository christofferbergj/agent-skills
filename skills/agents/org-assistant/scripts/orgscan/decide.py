"""When the gathered changes wake the thread, as one pure function of the time, the
schedule, what the scan already sent today, the ledger, and the changes themselves."""
from __future__ import annotations

from datetime import datetime

from .changes import NOW, PULSE, tier, urgent


def _until(value: str | None, now: datetime) -> bool:
    if not value:
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")) > now
    except ValueError:
        return False


def decide(now: datetime, schedule: dict, meta: dict, ledger: dict, gathered: list[dict]):
    """(kind, items, reason): kind is "overview", "delta", or None for no wake; items are the
    changes the wake carries, which leave the gathered list once it is frozen."""
    today, clock = now.date().isoformat(), now.strftime("%H:%M")
    if _until(ledger.get("paused_until"), now):
        return None, [], f"paused until {ledger['paused_until']}"
    first, last = schedule["window"]
    if not first <= clock <= last:
        return None, [], "outside the scan window"
    if _until(ledger.get("quiet_until"), now):
        return None, [], f"quiet until {ledger['quiet_until']}"
    weekday = now.weekday() < 5
    if weekday and meta.get("overview_on") != today and clock >= schedule["overview"]:
        return "overview", list(gathered), "the weekday overview"
    worth = [item for item in gathered if tier(item) != PULSE]
    capped = meta.get("deltas", {}).get(today, 0) >= schedule["daily_deltas"]
    if not weekday or capped:
        wake = [item for item in worth if urgent(item)]
        why = "weekend" if not weekday else f"past {schedule['daily_deltas']} deltas today"
        if wake:
            return "delta", wake, f"{why}: someone waits on you, a new assignment, or a deadline within 24 hours"
        return None, [], f"{why}: nothing urgent"
    if any(tier(item) == NOW for item in worth):
        return "delta", list(gathered), "a change worth a wake"
    flushed = meta.get("slots", {}).get(today, [])
    if worth and any(slot <= clock and slot not in flushed for slot in schedule["batch_slots"]):
        return "delta", list(gathered), "a batch slot"
    return None, [], "nothing worth a wake yet"
