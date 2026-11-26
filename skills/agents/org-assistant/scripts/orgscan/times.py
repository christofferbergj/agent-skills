"""The one place timestamps are written and read: UTC with a `Z` in every file."""
from __future__ import annotations

from datetime import datetime, timezone


def iso(moment: datetime, ms: bool = False) -> str:
    """UTC, as `2026-11-26T09:05:00Z`, or with milliseconds as Linear writes its times, so the
    two compare as strings."""
    return moment.astimezone(timezone.utc).isoformat(timespec="milliseconds" if ms else "seconds") \
        .replace("+00:00", "Z")


def parse(text: str) -> datetime:
    moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def from_ts(ts) -> datetime:
    """A Slack message timestamp, such as `1795683600.000100`."""
    return datetime.fromtimestamp(float(ts), timezone.utc)
