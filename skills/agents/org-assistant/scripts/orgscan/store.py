"""Where an organisation's profile and state live, and how they are read and written.
Each file has one writer: the scan writes snapshot.json, pending.json, and scan.stamp; the
model writes ledger.json through `assistant.py ledger`. Every write replaces its file
atomically, and a lock keeps a timer scan and an inline scan from running at once."""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import tempfile
import time
from pathlib import Path

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import toml

SOURCE_FIELDS = {"name", "kind"}


class ProfileError(ValueError):
    pass


def config_root() -> Path:
    return Path(os.environ.get("ORG_ASSISTANT_CONFIG", "~/.config/org-assistant")).expanduser()


def state_root() -> Path:
    return Path(os.environ.get("ORG_ASSISTANT_STATE", "~/.local/state/org-assistant")).expanduser()


def orgs() -> list[str]:
    root = config_root()
    return sorted(p.parent.name for p in root.glob("*/profile.toml")) if root.is_dir() else []


def expand(value):
    """~ in every string of a profile value, so the profile can stay machine-neutral."""
    if isinstance(value, str):
        return os.path.expanduser(value) if value.startswith("~") else value
    if isinstance(value, list):
        return [expand(v) for v in value]
    if isinstance(value, dict):
        return {k: expand(v) for k, v in value.items()}
    return value


def load_profile(org: str) -> dict:
    path = config_root() / org / "profile.toml"
    try:
        profile = expand(toml.loads(path.read_text()))
    except OSError as error:
        raise ProfileError(f"{path}: {error.strerror}")
    except toml.TomlError as error:
        raise ProfileError(f"{path}: {error}")
    if not isinstance(profile, dict):
        raise ProfileError(f"{path}: not a table")
    profile.setdefault("org", org)
    if profile["org"] != org:
        raise ProfileError(f"{path}: org is {profile['org']!r}, but its folder is {org!r}")
    sources = profile.get("sources")
    if not isinstance(sources, list) or not sources or not all(isinstance(s, dict) for s in sources):
        raise ProfileError(f"{path}: no [[sources]] tables")
    names = set()
    for source in sources:
        missing = SOURCE_FIELDS - set(source)
        if missing:
            raise ProfileError(f"{path}: a source lacks {', '.join(sorted(missing))}")
        if source["name"] in names:
            raise ProfileError(f"{path}: two sources are named {source['name']}")
        names.add(source["name"])
    profile.setdefault("timezone", "Europe/Copenhagen")
    try:
        ZoneInfo(str(profile["timezone"]))
    except (ValueError, ZoneInfoNotFoundError):
        raise ProfileError(f"{path}: unknown timezone {profile['timezone']!r}")
    profile.setdefault("thread", "")
    schedule = profile.setdefault("schedule", {})
    if not isinstance(schedule, dict) or not isinstance(profile["thread"], str):
        raise ProfileError(f"{path}: [schedule] must be a table and thread a string")
    schedule.setdefault("window", ["09:00", "23:59"])
    schedule.setdefault("overview", "09:00")
    schedule.setdefault("batch_slots", ["13:00", "17:00"])
    schedule.setdefault("daily_deltas", 6)
    schedule.setdefault("slack_wait_minutes", 30)
    schedule.setdefault("retries", 1)
    schedule.setdefault("source_failures", 3)
    return profile


def state_dir(org: str) -> Path:
    return state_root() / org


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(fd, "w") as out:
        json.dump(value, out, indent=1, sort_keys=True)
        out.write("\n")
    os.replace(tmp, path)


@contextlib.contextmanager
def locked(folder: Path, wait: float = 60):
    """Holds folder/.lock, waiting up to `wait` seconds; yields False when it stays taken."""
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / ".lock", "w") as handle:
        deadline = time.monotonic() + wait
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    yield False
                    return
                time.sleep(0.5)
        try:
            yield True
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
