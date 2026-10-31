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

TEXT or VALUE `-` reads standard input. A row's Worker cell is SLUG, or SLUG followed by ` (`
and a label. State starts with one of STATES; detail may follow, as in
`done: #12 MERGED`. Exits 2 on a usage error and 1 on a file it can't edit."""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from datetime import date
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
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


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


def _write(path: Path, text: str) -> None:
    handle, tmp = tempfile.mkstemp(dir=path.parent, prefix=".project.md.")
    with os.fdopen(handle, "w") as f:
        f.write(text)
    os.chmod(tmp, path.stat().st_mode if path.exists() else 0o644)  # mkstemp makes it 0600
    os.replace(tmp, path)


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
    args = parser.parse_args(argv)
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
        text = path.read_text()
        lines = text.split("\n")
        if args.command in ("decide", "learn"):
            body = sys.stdin.read() if args.text == "-" else args.text
            (decide if args.command == "decide" else learn)(lines, body)
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
