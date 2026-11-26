"""When the gathered changes wake the thread, as pure functions of the time, the schedule,
what today already sent, the ledger, and the changes themselves."""
from __future__ import annotations

from datetime import datetime

from .changes import NOW, PULSE, tier, urgent
from .times import parse


def _before(value: str | None, now: datetime) -> bool:
    """Whether a ledger hold such as `quiet_until` is still ahead of now."""
    if not value:
        return False
    try:
        return parse(value) > now
    except ValueError:
        return False


def held(now: datetime, ledger: dict, kind: str) -> bool:
    """A pause holds every wake; quiet holds deltas and lets the overview through."""
    return _before(ledger.get("paused_until"), now) or (kind != "overview" and _before(ledger.get("quiet_until"), now))


def overview_due(now: datetime, schedule: dict, meta: dict, ledger: dict) -> bool:
    """A weekday in the window, past the overview's time, with no overview frozen today."""
    clock = now.strftime("%H:%M")
    first, last = schedule["window"]
    return (now.weekday() < 5 and first <= clock <= last and clock >= schedule["overview"]
            and meta.get("overview_on") != now.date().isoformat() and not held(now, ledger, "overview"))


def decide(now: datetime, schedule: dict, meta: dict, ledger: dict, gathered: list[dict]):
    """(kind, items, reason): kind is "overview", "delta", or None for no wake; items are the
    changes the wake carries, which leave the gathered list once it is frozen."""
    today, clock = now.date().isoformat(), now.strftime("%H:%M")
    if held(now, ledger, "overview"):
        return None, [], f"paused until {ledger['paused_until']}"
    first, last = schedule["window"]
    if not first <= clock <= last:
        return None, [], "outside the scan window"
    weekday = now.weekday() < 5
    if overview_due(now, schedule, meta, ledger):
        return "overview", list(gathered), "the weekday overview"
    if held(now, ledger, "delta"):
        return None, [], f"quiet until {ledger['quiet_until']}"
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
