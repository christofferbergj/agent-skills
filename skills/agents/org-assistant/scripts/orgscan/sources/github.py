"""GitHub, through the `gh` CLI: the user's open PRs with reviews and checks, review
requests, issues, other people's open PRs, and releases, per repository as the profile
sets them. Reads only. Keeps numbers, states, and tags, never titles or bodies."""
from __future__ import annotations

from datetime import timezone

from ..calls import run_json
from ..changes import change

RED = {"FAILURE", "ERROR", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}
WAITING = {"PENDING", "EXPECTED", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}


def _ci(rollup: list[dict]) -> str:
    """failing, pending, or passing, from a PR's statusCheckRollup."""
    states = [(c.get("conclusion") or c.get("state") or "", c.get("status") or "") for c in rollup or []]
    if any(conclusion in RED for conclusion, _ in states):
        return "failing"
    if any(status in WAITING or conclusion in WAITING or (status and status != "COMPLETED" and not conclusion)
           for conclusion, status in states):
        return "pending"
    return "passing"


def _new(before, key: str, created: str | None, since: str | None) -> bool:
    """Whether key is new since the last scan; on a first scan with --since, whether it was
    created after that."""
    if before is not None:
        return key not in before
    return bool(since and (created or "") >= since)


def _gh(args: list[str], what: str):
    return run_json(["gh", *args], what)


def scan(source: dict, prev: dict | None, ctx) -> tuple[dict, list[dict]]:
    baseline = prev is None and ctx.since is None
    prev = prev or {}
    now = ctx.now.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    since = ctx.since.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if ctx.since else None
    me = source.get("me", "")
    waits = {}
    for wait in ctx.ledger.get("waits", []):
        waits.setdefault(wait.get("on"), []).append(wait.get("pr"))
    state: dict = {}
    changes: list[dict] = []
    for entry in source.get("repos", []):
        repo = entry["repo"]
        old = prev.get(repo, {})
        new: dict = {}
        if entry.get("mine"):
            prs = _gh(["pr", "list", "-R", repo, "--author", "@me", "--state", "open", "--limit", "100", "--json",
                       "number,isDraft,reviewDecision,statusCheckRollup,updatedAt"], f"{repo} PRs")
            new["mine"] = {}
            for pr in prs:
                ref = f"{repo}#{pr['number']}"
                seen = {"ci": _ci(pr.get("statusCheckRollup")), "review": pr.get("reviewDecision") or "",
                        "draft": pr.get("isDraft", False)}
                new["mine"][str(pr["number"])] = seen
                was = old.get("mine", {}).get(str(pr["number"]))
                if baseline or (was is None and since is None):
                    continue
                was = was or {"ci": "", "review": ""}
                at = pr.get("updatedAt") or now
                if seen["ci"] == "failing" and was["ci"] != "failing":
                    changes.append(change("pr.ci_failed", ref, at, key=at))
                if seen["review"] != was["review"] and seen["review"] == "CHANGES_REQUESTED":
                    changes.append(change("pr.changes_requested", ref, at, key=at))
                elif seen["review"] != was["review"] and seen["review"] == "APPROVED":
                    changes.append(change("pr.approved", ref, at, key=at))
        if entry.get("review_requests"):
            asked = _gh(["pr", "list", "-R", repo, "--search", "review-requested:@me", "--state", "open", "--limit",
                         "100", "--json", "number,updatedAt"], f"{repo} review requests")
            new["requested"] = sorted(str(pr["number"]) for pr in asked)
            for pr in asked:
                if not baseline and str(pr["number"]) not in old.get("requested", []):
                    changes.append(change("pr.review_requested", f"{repo}#{pr['number']}", pr.get("updatedAt") or now,
                                          key=pr.get("updatedAt") or now))
        if entry.get("issues"):
            issues = _gh(["issue", "list", "-R", repo, "--state", "open", "--limit", "200", "--json",
                          "number,assignees,createdAt"], f"{repo} issues")
            before = old.get("issues")
            new["issues"] = {}
            for issue in issues:
                number, ref = str(issue["number"]), f"{repo}#{issue['number']}"
                mine = any(a.get("login") == me for a in issue.get("assignees") or [])
                new["issues"][number] = mine
                fresh = _new(before, number, issue.get("createdAt"), since)
                if baseline:
                    continue
                if mine and (fresh or (before is not None and number in before and not before[number])):
                    changes.append(change("issue.assigned", ref, issue.get("createdAt") or now, key="assigned"))
                elif fresh:
                    changes.append(change("issue.new", ref, issue.get("createdAt") or now, key="new"))
        if entry.get("open_prs"):
            prs = _gh(["pr", "list", "-R", repo, "--state", "open", "--limit", "200", "--json", "number,createdAt"],
                      f"{repo} open PRs")
            before = old.get("open")
            new["open"] = sorted(str(pr["number"]) for pr in prs)
            if not baseline:
                for pr in prs:
                    if _new(before, str(pr["number"]), pr.get("createdAt"), since):
                        changes.append(change("pr.opened", f"{repo}#{pr['number']}", pr.get("createdAt") or now,
                                              key="open"))
                for number in sorted(set(before or []) - set(new["open"])):
                    changes.append(change("pr.closed", f"{repo}#{number}", now, key="closed"))
        if entry.get("releases"):
            releases = _gh(["release", "list", "-R", repo, "--limit", "10", "--json", "tagName,publishedAt,isDraft"],
                           f"{repo} releases")
            before = old.get("releases")
            new["releases"] = [r["tagName"] for r in releases if not r.get("isDraft")]
            for release in releases:
                tag = release["tagName"]
                if baseline or release.get("isDraft") or not _new(before, tag, release.get("publishedAt"), since):
                    continue
                kind = "release.awaited" if repo in waits else "release.new"
                changes.append(change(kind, f"{repo}@{tag}", release.get("publishedAt") or now, key=tag,
                                      prs=waits.get(repo, [])))
        state[repo] = new
    return state, changes
