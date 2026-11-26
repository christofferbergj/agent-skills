"""One adapter per kind of source. Each module's `scan(source, prev, ctx)` returns the
source's new snapshot section and its changes; `prev` is None on the first scan, which
records a baseline and returns no changes unless the run passes --since.

A new kind, such as `azure-boards` for Adapt's client trackers, is a module here with the
same `scan` and an entry in ADAPTERS. Until it exists, a profile that names it fails that
source on every scan, so the gap shows in the health line instead of passing silently."""
from __future__ import annotations

from . import github, linear, slack, t3

ADAPTERS = {"linear": linear.scan, "slack": slack.scan, "github": github.scan, "t3": t3.scan}
# still(section, change): whether a gathered change is still true after the source's latest scan.
STILL = {"slack": slack.still_waiting}
PLANNED = {"azure-boards": "the Azure Boards adapter is not built yet; see references/scan.md"}
