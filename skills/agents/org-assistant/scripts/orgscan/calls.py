"""The scan's only ways out: Executor tool calls through `probe.ts`, and the `gh` and `t3`
CLIs. Every Executor call must name a tool the profile's source lists under `tools` and
must not look like a write, so a profile typo can't make the scan change a source."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

WRITE = re.compile(r"(^|[._])(mark|save|create|update|delete|archive|retire|restore|send|draft|schedule|post|"
                   r"add|remove|set|invite|upload|complete|react)[_a-z]*$")
LIMITED = re.compile(r"\b429\b|limiting requests|rate.?limit", re.I)
HTTP = re.compile(r"\bHTTP (\d{3})\b")
AUTH = re.compile(r"unauthori[sz]ed|reauth|re-auth|sign[ -]?in|log[ -]?in again|expired|invalid_auth|"
                  r"not_authed|token_revoked|\b401\b|connect(ion)? link", re.I)
TIMEOUT = 300


class SourceError(Exception):
    """A source that could not be read this scan; `auth` when its sign-in looks expired."""

    def __init__(self, message: str, auth: bool = False):
        super().__init__(message)
        self.auth = auth


def failure(what: str, text) -> SourceError:
    """A failed call or command, named by what failed and a category read from its error text:
    sign-in, rate limit, or HTTP status. The text itself is dropped, since a tool's error can
    quote the ticket or message it was reading."""
    text = text if isinstance(text, str) else json.dumps(text) if text is not None else ""
    if AUTH.search(text):
        return SourceError(f"{what}: sign-in expired", auth=True)
    if LIMITED.search(text):
        return SourceError(f"{what}: rate limited")
    status = HTTP.search(text)
    return SourceError(f"{what}: failed" + (f" (HTTP {status.group(1)})" if status else ""))


def run(args: list[str], cwd: str | None = None, stdin: str | None = None) -> tuple[int, str, str]:
    try:
        done = subprocess.run(args, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as error:
        return 127, "", str(error)
    return done.returncode, done.stdout, done.stderr


def run_json(args: list[str], what: str, cwd: str | None = None):
    code, out, err = run(args, cwd=cwd)
    if code != 0:
        raise failure(f"{what} (exit {code})", err or out)
    # A CLI can log a warning ahead of its JSON, so parse from the first line that opens it.
    for match in re.finditer(r"^[\[{]", out, re.M):
        try:
            return json.JSONDecoder().raw_decode(out, match.start())[0]
        except ValueError:
            continue
    raise SourceError(f"{what}: no JSON in its output")


class Executor:
    """Calls Executor tools for one source, from the repository its profile names."""

    def __init__(self, command: list[str], source: dict):
        self.command, self.source = command, source
        self.allowed = set(source["tools"])

    def call(self, calls: list[tuple[str, dict]], partial: bool = False) -> list:
        """Each call's parsed result, in order. Any refused, failed, or unreadable call fails
        the whole source for this scan, so its snapshot keeps the last good state; with
        `partial`, a call that failed for any reason but sign-in is None instead."""
        if not calls:
            return []
        for path, _ in calls:
            name = path.rsplit(".", 1)[-1]
            if path not in self.allowed:
                raise SourceError(f"{path} is not in this source's tools")
            if WRITE.search(name):
                raise SourceError(f"{path} looks like a write, and the scan only reads")
        account = self.source.get("account", "")
        body = {"calls": [{"path": path, "input": {"accountId": account, "input": args}} for path, args in calls]}
        cwd = self.source.get("repo") or None
        if cwd and not Path(cwd).is_dir():
            raise SourceError(f"its repository {cwd} is missing")
        code, out, err = run([*self.command, "call", json.dumps(body)], cwd=cwd)
        if code != 0:
            raise failure(f"Executor (exit {code})", err or out)
        execution = None
        for line in out.splitlines():
            if not line.startswith("{"):
                continue
            try:
                execution = json.loads(line)["result"]["structuredContent"]["execution"]
            except (ValueError, KeyError, TypeError):
                continue
        if execution is None:
            raise SourceError("Executor printed no result")
        if "value" not in execution:
            raise failure("Executor call", execution.get("error"))
        values = execution["value"] if isinstance(execution["value"], list) else [execution["value"]]
        if not isinstance(values, list) or len(values) != len(calls):
            raise SourceError("Executor returned a different number of results than calls")
        results = []
        for (path, _), value in zip(calls, values):
            try:
                results.append(self._result(path, value))
            except SourceError as error:
                if not partial or error.auth:
                    raise
                results.append(None)
        return results

    @staticmethod
    def _result(path: str, value):
        if not isinstance(value, dict) or not value.get("ok", False):
            raise failure(path, value.get("error") if isinstance(value, dict) else None)
        inner = value.get("value", value)
        if isinstance(inner, dict) and inner.get("isError"):
            raise failure(path, "".join(part.get("text", "") for part in inner.get("content", [])
                                        if isinstance(part, dict)))
        if isinstance(inner, dict) and isinstance(inner.get("structuredContent"), dict) and inner["structuredContent"]:
            return inner["structuredContent"]
        if isinstance(inner, dict) and inner.get("content"):
            text = "".join(part.get("text", "") for part in inner["content"] if isinstance(part, dict))
            try:
                return json.loads(text)
            except ValueError:
                return text
        return inner
