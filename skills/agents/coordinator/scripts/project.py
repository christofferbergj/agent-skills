#!/usr/bin/env python3
"""Edits a coordinator project's project.md (references/project.md says what each
section holds), so the coordinator writes by hand only the Goal section and the close's
Result. Every edit leaves the rest of the file byte for byte and replaces the file atomically.

  project.py DIR init --project P --coordinator LINK --checkout PATH --goal G --proof P
  project.py DIR decide TEXT        add `- <date> · TEXT` under Decisions
  project.py DIR learn TEXT         add `- <date> · TEXT` under Learnings
  project.py DIR worker SLUG [--proof P] [--thread T] [--pr B] [--state S] [--waits W] [--last L]
                                    set a Workers row's columns, adding the row if it's new
  project.py DIR listen KEY VALUE   set `- KEY: VALUE` under Listening
  project.py DIR phase SLUG --result R (--goal G --proof P | --park REASON)
                                    end the running phase: save project.md to
                                    phases/<NN>-SLUG.md, add its line under Phases, reset
                                    the phase's sections, then start the next or park
  project.py DIR start --goal G --proof P
                                    start the next phase on a parked project
  project.py DIR tick [--send]      print what changed since the last tick that T3 doesn't
                                    report; --send messages it to the coordinator's thread
                                    and saves DIR/tick.json, while Heartbeat is `tick`

TEXT or VALUE `-` reads standard input. A row's Worker cell is SLUG, or SLUG followed by ` (`
and a label. State starts with one of STATES; detail may follow, as in
`done: #12 MERGED`. Exits 2 on a usage error and 1 on a file it can't edit."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime
from pathlib import Path

STATES = ("queued", "overdue", "unknown", "running", "waiting", "stuck", "done", "dropped",
          "replaced by <worker>", "absorbed into <worker>")
STATE = re.compile(r"(queued|overdue|unknown|running|waiting|stuck|done|dropped)\b|(replaced by|absorbed into) \S")
COLUMNS = {"proof": "Proof", "thread": "Thread", "pr": "Branch or PR", "state": "State", "waits": "Waits on",
           "last": "Last side effect"}
CELL = re.compile(r"(?<!\\)\|")

SKELETON = """# ◆ {project}

Coordinator: {coordinator} · Checkout: {checkout}

## Goal

{goal}
Proof: {proof}
Follow-ups: none

## Decisions

## Workers

| Worker | Proof | Thread | Branch or PR | State | Waits on | Last side effect |
|---|---|---|---|---|---|---|

## Learnings

## Listening

- Heartbeat: none
- Startup: none
- Watches: none
"""


class ProjectError(Exception):
    pass


def _section(lines: list[str], name: str) -> tuple[int, int]:
    """The index of `## name` and the index where its section ends."""
    try:
        start = lines.index(f"## {name}")
    except ValueError:
        raise ProjectError(f"no `## {name}` section")
    return start, _end(lines, start)


def _end(lines: list[str], start: int) -> int:
    return next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))


def _insert(lines: list[str], name: str, line: str) -> None:
    """Puts `line` after the section's last non-blank line, keeping a blank line before
    the next heading."""
    start, end = _section(lines, name)
    at = next(i for i in range(end - 1, start - 1, -1) if lines[i].strip()) + 1
    added = [line] if at > start + 1 else ["", line]
    if at < len(lines) and lines[at].startswith("## "):
        added.append("")
    lines[at:at] = added


def _bullet(text: str) -> str:
    return "- " + text.strip().replace("\n", "\n  ")


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in CELL.split(row.strip())[1:-1]]


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _dated(text: str) -> str:
    if not text.strip():
        raise ProjectError("empty text")
    return _bullet(f"{date.today().isoformat()} · {text.strip()}")


def decide(lines: list[str], text: str) -> None:
    _insert(lines, "Decisions", _dated(text))


def learn(lines: list[str], text: str) -> None:
    _insert(lines, "Learnings", _dated(text))


def worker(lines: list[str], slug: str, **columns: str | None) -> None:
    state = columns.get("state")
    if state is not None and not STATE.match(state):
        raise ProjectError(f"state {state!r} doesn't start with one of: {', '.join(STATES)}")
    if "|" in slug:  # a column value escapes it, but the lookup matches the Worker cell as written
        raise ProjectError(f"a worker name holds no |: {slug!r}")
    for value in [slug, *(v for v in columns.values() if v is not None)]:
        if "\n" in value or not value.strip():
            raise ProjectError(f"a cell is one non-empty line: {value!r}")
    start, end = _section(lines, "Workers")
    table = [i for i in range(start + 1, end) if lines[i].startswith("|")]
    if len(table) < 2:
        raise ProjectError("no Workers table")
    header = _cells(lines[table[0]])
    rows = [i for i in table[2:] if (first := _cells(lines[i])[0]) == slug or first.startswith(f"{slug} (")]
    if len(rows) > 1:
        raise ProjectError(f"{len(rows)} Workers rows match {slug!r}")
    if not rows and state is None:  # most likely a mistyped slug
        raise ProjectError(f"no Workers row matches {slug!r}: a new row needs --state")
    cells = _cells(lines[rows[0]]) if rows else [slug] + ["—"] * (len(header) - 1)
    if len(cells) != len(header):  # a hand edit dropped or split a cell: which one is a guess
        raise ProjectError(f"the {slug!r} row has {len(cells)} cells and the header {len(header)}: fix it by hand")
    for key, value in columns.items():
        if value is not None:
            if COLUMNS[key] not in header:
                raise ProjectError(f"the Workers table has no {COLUMNS[key]!r} column")
            cells[header.index(COLUMNS[key])] = value.strip().replace("|", "\\|")
    if rows:
        lines[rows[0]] = _row(cells)
    else:
        lines.insert(table[-1] + 1, _row(cells))


def listen(lines: list[str], key: str, value: str) -> None:
    start, end = _section(lines, "Listening")
    if not key.strip() or ":" in key or not value.strip() or "\n" in value.strip():
        raise ProjectError("listen takes a KEY without a colon and a one-line VALUE")
    line = _bullet(f"{key}: {value.strip()}")
    found = [i for i in range(start + 1, end) if lines[i].startswith(f"- {key}:")]
    if found:
        lines[found[0]] = line
    else:
        _insert(lines, "Listening", line)


FINAL = re.compile(r"(done|dropped)\b|(replaced by|absorbed into) \S")  # the end states in STATE
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PARKED = "Parked "  # a parked Goal's first line: `Parked <date>: <reason>`


def phase(lines: list[str], archive: str, result: str, *,
          goal: str | None = None, proof: str | None = None, park: str | None = None) -> list[str]:
    """Ends the running phase whose snapshot is at `archive` (`phases/<NN>-<slug>.md`): adds
    `- <date> · <NN-slug>: RESULT · ARCHIVE` under Phases, creating it after Goal; empties
    Decisions and Learnings; removes each Result section; drops Workers rows in a FINAL
    state; then writes Goal as GOAL and `Proof: PROOF`, or as `Parked <date>: PARK`, keeping
    its Delivery line and Follow-ups. Refuses a parked project, a rerun of the phase end
    just recorded, and anything but goal and proof, or park alone. Returns the Worker cells
    of the rows `_drop_final` kept unread."""
    if _parked(lines):
        raise ProjectError("the project is parked: start its next phase with start")
    if (goal is None or proof is None) == (park is None):
        raise ProjectError("a phase ends with a goal and a proof, or with park alone")
    slug = Path(archive).stem.split("-", 1)[1]
    if goal is not None and _rerun(lines, slug, goal, proof):
        raise ProjectError(f"phase {slug!r} already ended with this goal and proof, and nothing is recorded since: the project is in its next phase; to end a new phase like it, give it another slug")
    today = date.today().isoformat()
    body = [f"{PARKED}{today}: {_line('park', park)}"] if park is not None else _next(goal, proof)
    line = f"- {today} · {Path(archive).stem}: {_line('result', result)} · {archive}"
    while (heading := next((i for i, text in enumerate(lines)
                            if text == "## Result" or text.startswith("## Result (")), None)) is not None:
        del lines[heading:_end(lines, heading)]
    for name in ("Decisions", "Learnings"):
        if f"## {name}" in lines:
            start_at, end = _section(lines, name)
            lines[start_at + 1:end] = [""]
    unread = _drop_final(lines)
    _goal(lines, body)
    if "## Phases" in lines:
        _insert(lines, "Phases", line)
    else:
        at = _section(lines, "Goal")[1]
        lines[at:at] = ["## Phases", "", line, ""]
    return unread


def _rerun(lines: list[str], slug: str, goal: str, proof: str) -> bool:
    """The phase end just recorded: the newest Phases line ended `slug`, Goal already opens
    with `goal` and `proof`, and Decisions and Learnings are still as `phase` left them, empty.
    Content can't tell such a retry from a new phase with the same slug, goal, and proof and
    nothing recorded, so the refusal names the way out: another slug."""
    if "## Phases" not in lines:
        return False
    start_at, end = _section(lines, "Phases")
    entries = [text for text in lines[start_at + 1:end] if text.startswith("- ")]
    goal_at, goal_end = _section(lines, "Goal")
    current = [text.strip() for text in lines[goal_at + 1:goal_end] if text.strip()][:2]
    untouched = all(not any(text.strip() for text in lines[a + 1:b])
                    for a, b in (_section(lines, name) for name in ("Decisions", "Learnings")
                                 if f"## {name}" in lines))
    return (bool(entries) and re.search(rf" · \d+-{re.escape(slug)}: ", entries[-1]) is not None
            and current == _next(goal, proof) and untouched)


def start(lines: list[str], goal: str, proof: str) -> None:
    """Starts the next phase on a parked project: Goal becomes GOAL and `Proof: PROOF`,
    keeping its Delivery line and Follow-ups. Refuses a project whose phase is running."""
    if not _parked(lines):
        raise ProjectError("the project's phase is running: end it with phase")
    _goal(lines, _next(goal, proof))


def _line(name: str, value: str) -> str:
    if not value.strip() or "\n" in value.strip() or "\r" in value:
        raise ProjectError(f"--{name} takes one non-empty line")
    return value.strip()


def _next(goal: str, proof: str) -> list[str]:
    return [_line("goal", goal), f"Proof: {_line('proof', proof)}"]


def _parked(lines: list[str]) -> bool:
    """Goal opens with `phase`'s parked line, `Parked <date>: `, and has no `Proof:` above its
    Follow-ups, so a running goal that happens to start with the word stays running."""
    start_at, end = _section(lines, "Goal")
    body = lines[start_at + 1:end]
    body = body[:next((i for i, text in enumerate(body) if text.startswith("Follow-ups:")), len(body))]
    first = next((text for text in body if text.strip()), "")
    return (re.match(rf"{PARKED}\d{{4}}-\d\d-\d\d: ", first) is not None
            and not any(text.startswith("Proof:") for text in body))


def _goal(lines: list[str], body: list[str]) -> None:
    """Replaces Goal's body with `body`, any `Delivery:` line above its Follow-ups, since an
    open PR keeps its delivery's rules, and its Follow-ups: the `Follow-ups:` line and the
    lines after it up to Goal's next `###` subheading or its end, or `Follow-ups: none`."""
    start_at, end = _section(lines, "Goal")
    at = next((i for i in range(start_at + 1, end) if lines[i].startswith("Follow-ups:")), None)
    delivery = [text for text in lines[start_at + 1:end if at is None else at] if text.startswith("Delivery:")]
    follow_ups = ["Follow-ups: none"]
    if at is not None:
        stop = next((i for i in range(at + 1, end) if lines[i].startswith("### ")), end)
        while not lines[stop - 1].strip():
            stop -= 1
        follow_ups = lines[at:stop]
    lines[start_at + 1:end] = ["", *body, *delivery, *follow_ups, ""]


def _drop_final(lines: list[str]) -> list[str]:
    """Drops Workers rows whose State is FINAL. A row whose cells don't match the header
    stays, since its State is a guess, and its Worker cell is returned."""
    if "## Workers" not in lines:
        return []
    start_at, end = _section(lines, "Workers")
    table = [i for i in range(start_at + 1, end) if lines[i].startswith("|")]
    header = _cells(lines[table[0]]) if table else []
    if len(table) < 2 or COLUMNS["state"] not in header:
        return []
    state = header.index(COLUMNS["state"])
    unread = []
    for i in reversed(table[2:]):
        cells = _cells(lines[i])
        if len(cells) != len(header):
            unread.insert(0, cells[0] if cells else lines[i])
        elif FINAL.match(cells[state]):
            del lines[i]
    return unread


def _archive_name(folder: Path, snapshot: bytes, slug: str) -> str:
    """The archive path from `folder` for `snapshot`: `phases/<NN>-<slug>.md`, NN one past
    the highest there, from 01, or a file there that already holds these bytes, left by a
    run whose project.md write failed."""
    phases = folder / "phases"
    numbered = [(m, p) for p in phases.iterdir() if (m := re.match(r"(\d+)-(.+)\.md\Z", p.name))] \
        if phases.is_dir() else []
    for match, path in numbered:
        if match.group(2) == slug and path.read_bytes() == snapshot:
            return f"phases/{path.name}"
    return f"phases/{max((int(m.group(1)) for m, _ in numbered), default=0) + 1:02d}-{slug}.md"


def _archive(folder: Path, snapshot: bytes, archive: str) -> None:
    """Writes `snapshot` to `archive` under `folder`, never overwriting, and no wider than
    project.md; an archive already there, which `_archive_name` found holds these bytes,
    only narrows."""
    path, mode = folder / archive, (folder / "project.md").stat().st_mode
    if path.exists():
        os.chmod(path, path.stat().st_mode & mode)
        return
    path.parent.mkdir(exist_ok=True)
    handle, tmp = tempfile.mkstemp(dir=path.parent, prefix=".phase.")
    try:
        with os.fdopen(handle, "wb") as f:
            f.write(snapshot)
        os.chmod(tmp, mode)  # no wider than its source
        os.link(tmp, path)  # fails if the name exists, where os.replace would overwrite it
    finally:
        os.unlink(tmp)


# The tick: the machine's timer runs `tick --send` every 10 minutes (references/tick.md), so
# the coordinator's model wakes only for news T3 doesn't deliver. A heartbeat that woke it
# hourly took no action on 91% of its turns.
ACTIVE = {"preparing", "queued", "starting", "running", "waiting"}  # T3's run statuses still under way
THREAD_ROW = re.compile(r"(running|overdue|unknown)\b")  # a row whose thread should be running
PR_ROW = re.compile(r"(running|overdue|unknown|waiting|stuck)\b")  # a row whose PR is still open work
LINK = re.compile(r"t3-thread://v2/([^/>\s)]+)/([^>\s)]+)")  # bare, in <…>, or a Markdown link's (…)
# A PR as its URL, owner/repo#N, repo#N (the checkout's owner), or #N (the checkout's repo).
PR_REF = re.compile(r"github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)|(?<![\w/.-])([\w.-]*\w(?:/[\w.-]+)?)#(\d+)\b"
                    r"|(?<![\w/#])#(\d+)\b")
REMOTE = re.compile(r"github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?$")
STALL = 3600  # seconds with no new thread item before a running worker counts as stalled
REPEAT = 3600  # a finding still true this long after it was sent is sent again
TIMER_STAMP = ".tick"  # touched in the coordinator folder by scripts/tick.sh on each run


def _run(args: list[str], cwd: Path | None = None, stdin: str | None = None) -> tuple[int, str]:
    try:
        done = subprocess.run(args, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        return 127, str(error)
    return done.returncode, done.stdout if done.returncode == 0 else done.stderr


def show_thread(thread: str) -> dict | None:
    """The thread's state from `t3 thread show`, or None when it can't be read."""
    code, out = _run(["t3", "thread", "show", thread, "--json", "--messages", "0", "--log-level", "error"])
    if code != 0:
        return None
    # A t3 CLI older than the server can still log a multi-line warning to stdout ahead of
    # the JSON, so parse from the first line that opens an object holding the thread.
    for start in re.finditer(r"^\{", out, re.M):
        try:
            return json.JSONDecoder().raw_decode(out, start.start())[0]["thread"]
        except (ValueError, KeyError, TypeError):
            continue
    return None


def view_pr(ref: str) -> list | None:
    """[state, isDraft] of `owner/repo#N`; None when unread."""
    repo, number = ref.split("#")
    code, out = _run(["gh", "pr", "view", number, "-R", repo, "--json", "state,isDraft"])
    try:
        pr = json.loads(out) if code == 0 else None
        return [pr["state"], pr["isDraft"]] if pr else None
    except (ValueError, KeyError, TypeError):
        return None


def _header(lines: list[str], field: str) -> str:
    """A `Field: value` from the line under the title, up to the next ` · `."""
    line = next((text for text in lines if text.startswith("Coordinator:")), "")
    match = re.search(rf"(?:^| · ){field}: (.*?)(?= · |$)", line)
    return match.group(1).strip() if match else ""


def _workers(lines: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    """The Workers rows as {column: cell}, and the rows whose cells don't match the header."""
    start, end = _section(lines, "Workers")
    table = [i for i in range(start + 1, end) if lines[i].startswith("|")]
    if len(table) < 2:
        return [], []
    header, rows, odd = _cells(lines[table[0]]), [], []
    for i in table[2:]:
        cells = _cells(lines[i])
        if len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
        else:
            odd.append(lines[i])
    return rows, odd


def _listened(lines: list[str], key: str) -> str:
    start, end = _section(lines, "Listening")
    return next((lines[i][len(f"- {key}:"):].strip() for i in range(start + 1, end)
                 if lines[i].startswith(f"- {key}:")), "")


def _pr_refs(text: str, origin: str, refs: set[str]) -> None:
    """Adds each PR the text names to refs as `owner/repo#N`: `#N` and `repo#N` resolve
    against the checkout's origin, `owner/repo`, and a range `#20–#22` names each PR in
    it (`#20–22` too, but `#20 - 22` stays one PR, since 22 may count something else). Without an origin, `#N` becomes `?#N` and `repo#N` `?/repo#N`, which tick reports. A `none` Watches value names none."""
    if text.startswith("none"):
        return
    text = re.sub(r"(?<![\w/#])#(\d+)(?:\s*[–-]\s*#|–)(\d+)\b", lambda m: " ".join(
        f"#{n}" for n in range(int(m[1]), int(m[2]) + 1)) if 0 < int(m[2]) - int(m[1]) <= 20 else m[0], text)
    owner = origin.split("/")[0] if origin else "?"
    for url_repo, url_n, repo, n, local in PR_REF.findall(text):
        repo = url_repo or (repo if not repo or "/" in repo else f"{owner}/{repo}") or origin or "?"
        refs.add(f"{repo}#{url_n or n or local}")


def _origin(checkout: Path | None) -> str:
    """`owner/repo` of the checkout's GitHub origin, or ""."""
    code, out = _run(["git", "-C", str(checkout), "remote", "get-url", "origin"]) if checkout else (1, "")
    match = REMOTE.search(out) if code == 0 else None
    return match.group(1).removesuffix(".git") if match else ""


def _when(stamp: str | None) -> float | None:
    """Seconds since the epoch for T3's ISO time, or None."""
    try:
        return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp() if stamp else None
    except ValueError:
        return None


def tick(lines: list[str], state: dict, now: float, show=show_thread, view=view_pr,
         hold: bool = True) -> tuple[list[tuple[str, str]], dict] | None:
    """What changed since the last tick that T3 doesn't tell the coordinator, as (key, line)
    pairs due to send, and the state to save once they're sent; None when the coordinator's
    thread can't be read or is archived. While it runs, threads are still read, so a stop or
    a stall is timed from when it happened, but nothing is due and PRs wait, so its own turn
    settles first; hold=False, for a dry run, checks as if it were idle. A read that fails
    is named on stderr, which the timer logs. A row's thread is news when
    it stopped, or has a question, through two ticks while its row says running, since a
    completion T3 delivers gets its row fixed by then; when it runs with no new item for
    STALL since its `updatedAt`; or when it's on another machine, which `t3 thread show` can't read. Each of
    these repeats every REPEAT until its row changes. A PR on an open row or under Watches
    is news once when it merges, closes, reopens, or turns ready or draft against what the
    tick last saw, and a merged or closed PR still under Watches repeats like a row: T3's watch sends
    checks, comments, reviews, and conflicts, not those."""
    coordinator = LINK.search(_header(lines, "Coordinator"))
    lead = coordinator and show(coordinator.group(2))
    if not lead or lead.get("archived"):
        print(f"tick: can't read the coordinator's thread, or it's archived: {_header(lines, 'Coordinator')}", file=sys.stderr)
        return None
    busy = hold and lead.get("status") in ACTIVE
    place = _header(lines, "Checkout").split(" (")[0].strip()
    checkout = Path(place).expanduser() if place else None
    origin = _origin(checkout)
    seen, threads, prs, found = state.get("threads", {}), {}, {}, []
    watched: set[str] = set()
    _pr_refs(_listened(lines, "Watches"), origin, watched)
    refs = set(watched)
    rows, odd = _workers(lines)
    for line in odd:
        if any(PR_ROW.match(cell) for cell in _cells(line)):  # a cell that opens with a state
            first = (_cells(line) or ["?"])[0]
            found.append((f"odd:{first}", f"{first}: its row's cells don't match the Workers header, so the tick "
                                          "can't read it"))
    for row in rows:
        slug, row_state = row.get("Worker", "?"), row.get(COLUMNS["state"], "")
        if PR_ROW.match(row_state):
            _pr_refs(row.get(COLUMNS["pr"], ""), origin, refs)
        link = LINK.search(row.get(COLUMNS["thread"], ""))
        if not THREAD_ROW.match(row_state):
            continue
        if not link:
            found.append((f"unlinked:{slug}", f"{slug}: its row says {row_state} but has no thread link to check"))
            continue
        place, thread = link.groups()
        if place != coordinator.group(1):
            found.append((f"remote:{thread}", f"{slug}: its thread is on another machine, so read its status with "
                                              f"`t3_thread_read` and environmentId {place}"))
            continue
        now_seen = show(thread)
        if now_seen is None:
            print(f"tick: can't read thread {thread}", file=sys.stderr)
            if thread in seen:
                threads[thread] = seen[thread]  # keep its last look, so a stall stays timed
            found.append((f"unread:{thread}", f"{slug}: `t3 thread show` can't read its thread"))
            continue
        before = seen.get(thread, {})
        status, runs, items = now_seen.get("status"), now_seen.get("runCount"), now_seen.get("itemCount")
        asked = now_seen.get("pendingRequestCount") or 0
        # The item count dates activity; updatedAt, which metadata such as a title also moves,
        # dates only a new count or the first look.
        since = before["since"] if before.get("items") == items and "since" in before else (
            _when(now_seen.get("updatedAt")) or now)
        threads[thread] = {"status": status, "runs": runs, "items": items, "asked": asked, "since": since}
        held = before.get("status") == status and before.get("runs") == runs  # the same for a whole tick
        if status not in ACTIVE and held:
            found.append((f"ended:{thread}:{runs}", f"{slug}: its thread stopped ({status}) while its row says {row_state}"))
        elif asked and held and before.get("asked") == asked:
            found.append((f"asked:{thread}:{asked}", f"{slug}: its thread waits on {asked} question(s) its row doesn't show"))
        elif status == "running" and now - since >= STALL:
            found.append((f"stalled:{thread}:{items}", f"{slug}: no new thread item in {int((now - since) // 60)} min"))
    for ref in sorted(ref for ref in refs if ref.startswith("?")):
        refs.discard(ref)
        found.append((f"owner:{ref}", f"{ref.lstrip('?/')}: the tick can't tell its repo from the checkout's origin, so "
                                      "write it as owner/repo#N"))
    if busy:
        return [], {**state, "threads": threads}
    events = []
    for ref in sorted(refs):
        known = state.get("prs", {}).get(ref)
        prs[ref] = view(ref) or known
        if prs[ref] is known:
            print(f"tick: can't read PR {ref}", file=sys.stderr)
        if ref in watched and prs[ref] and prs[ref][0] != "OPEN":  # a watch left on a finished PR
            found.append((f"watch:{ref}", f"{ref}: {prs[ref][0].lower()}, and still under Watches"))
        elif known and prs[ref] != known:
            change = ({"OPEN": "reopened"}.get(prs[ref][0], prs[ref][0].lower()) if prs[ref][0] != known[0]
                      else "turned draft" if prs[ref][1] else "marked ready")
            events.append((f"pr:{ref}", f"{ref}: {change}"))
    sent = {key: at for key, at in state.get("sent", {}).items() if key in {k for k, _ in found}}
    due = [(key, line) for key, line in found if now - sent.get(key, 0) >= REPEAT] + events
    sent.update({key: now for key, _ in due if not key.startswith("pr:")})
    kept = {**state.get("prs", {}), **{k: v for k, v in prs.items() if v}}  # a PR that leaves and returns isn't new
    return due, {"threads": threads, "prs": kept, "sent": sent}


def tick_message(lines: list[str], due: list[tuple[str, str]], path: Path) -> str:
    project = lines[0].removeprefix("# ◆").strip() if lines else "?"
    return "\n".join([f'<coordinator-tick project="{project}">', *(f"- {line}" for _, line in due),
                      "</coordinator-tick>",
                      f"Read {path} and handle each line with step 4 of the coordinator skill, loading it only "
                      "if it isn't in your context. Fix the line's row in project.md, or the tick repeats it hourly."])


def _write(path: Path, text: str) -> None:
    handle, tmp = tempfile.mkstemp(dir=path.parent, prefix=".project.md.")
    with os.fdopen(handle, "w") as f:
        f.write(text)
    os.chmod(tmp, path.stat().st_mode if path.exists() else 0o644)  # mkstemp makes it 0600
    os.replace(tmp, path)


def _tick(folder: Path, lines: list[str], send: bool) -> int:
    """Runs tick: with --send only while Listening's Heartbeat is `tick`, saving the state
    only after the message went out, so a failed send is retried next tick."""
    if send and _listened(lines, "Heartbeat") != "tick":
        return 0
    store = folder / "tick.json"
    try:
        state = json.loads(store.read_text()) if store.exists() else {}
    except ValueError:
        state = {}
    if not send:
        stamp = folder.parent / TIMER_STAMP
        if not stamp.exists() or time.time() - stamp.stat().st_mtime > 1200:
            print("the tick timer hasn't run in 20 minutes: install it as references/tick.md says")
    result = tick(lines, state, time.time(), hold=send)
    if result is None:
        return 1
    due, after = result
    if not send:
        print("\n".join(f"- {line}" for _, line in due) or "nothing new")
        return 0
    if due:
        code, out = _run(["t3", "thread", "send", LINK.search(_header(lines, "Coordinator")).group(2), "-"],
                         stdin=tick_message(lines, due, folder / "project.md"))
        if code:
            raise ProjectError(f"t3 thread send failed: {out.strip()[:300]}")
    _write(store, json.dumps(after, indent=1) + "\n")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="project.py", description=__doc__, allow_abbrev=False,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dir", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", allow_abbrev=False)
    for name in ("project", "coordinator", "checkout", "goal", "proof"):
        init.add_argument(f"--{name}", required=True)
    for name in ("decide", "learn"):
        commands.add_parser(name).add_argument("text")
    row = commands.add_parser("worker", allow_abbrev=False)
    row.add_argument("slug")
    for name in COLUMNS:
        row.add_argument(f"--{name}")
    listening = commands.add_parser("listen")
    listening.add_argument("key")
    listening.add_argument("value")
    ending = commands.add_parser("phase", allow_abbrev=False)
    ending.add_argument("slug")
    ending.add_argument("--result", required=True)
    ending.add_argument("--proof")
    next_or_park = ending.add_mutually_exclusive_group(required=True)
    next_or_park.add_argument("--goal")
    next_or_park.add_argument("--park")
    starting = commands.add_parser("start", allow_abbrev=False)
    starting.add_argument("--goal", required=True)
    starting.add_argument("--proof", required=True)
    commands.add_parser("tick", allow_abbrev=False).add_argument("--send", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "phase" and (args.goal is None) != (args.proof is None):
        ending.error("--goal needs --proof, and --park takes neither")
    path = args.dir / "project.md"
    try:
        if args.command == "init":
            if path.exists():
                raise ProjectError(f"{path} exists")
            args.dir.mkdir(parents=True, exist_ok=True)
            _write(path, SKELETON.format(**{k: v for k, v in vars(args).items() if k not in ("dir", "command")}))
            print(path)
            return 0
        if not path.is_file():
            raise ProjectError(f"no {path}: run init first")
        if args.command == "phase":
            snapshot = path.read_bytes()
            lines = snapshot.decode().replace("\r\n", "\n").replace("\r", "\n").split("\n")  # as read_text does
            if not SLUG.match(args.slug):
                raise ProjectError(f"slug {args.slug!r} isn't lowercase words joined by hyphens")
            archive = _archive_name(args.dir, snapshot, args.slug)
            unread = phase(lines, archive, args.result, goal=args.goal, proof=args.proof, park=args.park)
            _archive(args.dir, snapshot, archive)  # after every refusal
            _write(path, "\n".join(lines))
            if unread:
                print(f"kept {len(unread)} Workers rows whose cells don't match the header, so their"
                      f" State is unread: {', '.join(unread)}. Fix or delete each by hand.", file=sys.stderr)
            print(args.dir / archive)
            print(path)
            return 0
        lines = path.read_text().split("\n")
        if args.command == "tick":
            return _tick(args.dir, lines, args.send)
        if args.command in ("decide", "learn"):
            body = sys.stdin.read() if args.text == "-" else args.text
            (decide if args.command == "decide" else learn)(lines, body)
        elif args.command == "start":
            start(lines, args.goal, args.proof)
        elif args.command == "worker":
            worker(lines, args.slug, **{key: getattr(args, key) for key in COLUMNS})
        else:
            listen(lines, args.key, sys.stdin.read() if args.value == "-" else args.value)
        _write(path, "\n".join(lines))
    except ProjectError as error:
        print(error, file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
