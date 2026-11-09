#!/usr/bin/env python3
"""Checks a reply card against ui/catalog.schema.json, the catalog reply.js draws.

Reads a JSON payload ({"ui": [...]}) or an HTML page holding it in
<script type="application/json" id="ui">, from a file or stdin. Prints each problem as
`<path>: <message>` and exits 1 when there is one, else prints `ok: N blocks` and exits 0.

Only the JSON Schema keywords the catalog uses are supported, and an unknown one is an
error, so the schema can't quietly grow a rule this check skips.

With --hook it's a PreToolUse hook on html_render (the kit's hooks/reply-card.py runs it):
it reads the call from stdin and denies a page that loads reply.js from any URL but
ui/renderer.url's, or whose card is missing or invalid, naming the fix. A page that
doesn't load reply.js passes.

Usage: validate-card.py [payload.json | page.html | -]
       validate-card.py --hook < pretooluse.json
"""

import json
import math
import pathlib
import re
import sys
from html.parser import HTMLParser

SCHEMA = pathlib.Path(__file__).resolve().parent.parent / "ui" / "catalog.schema.json"
ANNOTATIONS = {"$schema", "$id", "$defs", "title", "description"}
KEYWORDS = {"$ref", "oneOf", "type", "enum", "required", "additionalProperties", "properties",
            "items", "prefixItems", "minItems", "maxItems", "minLength", "maxLength", "pattern",
            "minimum", "maximum"} | ANNOTATIONS
RENDERER = SCHEMA.with_name("renderer.url")
# A script src that loads the renderer, from any host or version.
RENDERER_SRC = re.compile(r"reply-ui|/reply\.js(?:[?#]|$)", re.I)


def is_type(value, name):
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "null":
        return value is None
    raise ValueError(f"unsupported type {name!r}")


class Validator:
    def __init__(self, schema):
        self.root = schema

    def resolve(self, ref):
        if not ref.startswith("#/"):
            raise ValueError(f"unsupported $ref {ref!r}")
        node = self.root
        for part in ref[2:].split("/"):
            node = node[part]
        return node

    def errors(self, value, schema, path="$"):
        unknown = set(schema) - KEYWORDS
        if unknown:
            raise ValueError(f"unsupported schema keyword {sorted(unknown)[0]!r} at {path}")
        if "$ref" in schema:
            return self.errors(value, self.resolve(schema["$ref"]), path)
        if "oneOf" in schema:
            return self.one_of(value, schema["oneOf"], path)
        found = []
        if "type" in schema:
            names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
            if not any(is_type(value, n) for n in names):
                return [f"{path}: expected {' or '.join(names)}, got {json.dumps(value)[:40]}"]
        if "enum" in schema and value not in schema["enum"]:
            found.append(f"{path}: {json.dumps(value)} is not one of {', '.join(map(str, schema['enum']))}")
        if isinstance(value, str):
            if len(value) < schema.get("minLength", 0):
                found.append(f"{path}: shorter than {schema['minLength']} characters")
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                found.append(f"{path}: longer than {schema['maxLength']} characters")
            # ECMA-262's `$`, which JSON Schema patterns use, ends the string; Python's also
            # matches before a final newline, so it becomes `\Z`.
            if "pattern" in schema and not re.search(re.sub(r"(?<!\\)\$", r"\\Z", schema["pattern"]), value):
                found.append(f"{path}: {json.dumps(value)} doesn't match {schema['pattern']}")
        if is_type(value, "number"):
            if "minimum" in schema and value < schema["minimum"]:
                found.append(f"{path}: below {schema['minimum']}")
            if "maximum" in schema and value > schema["maximum"]:
                found.append(f"{path}: above {schema['maximum']}")
        if isinstance(value, dict):
            props = schema.get("properties", {})
            found += [f"{path}: missing {key!r}" for key in schema.get("required", []) if key not in value]
            for key, item in value.items():
                if key in props:
                    found += self.errors(item, props[key], f"{path}.{key}")
                elif schema.get("additionalProperties", True) is False:
                    found.append(f"{path}: unknown field {key!r}")
        if isinstance(value, list):
            if len(value) < schema.get("minItems", 0):
                found.append(f"{path}: fewer than {schema['minItems']} items")
            if "maxItems" in schema and len(value) > schema["maxItems"]:
                found.append(f"{path}: more than {schema['maxItems']} items")
            prefix = schema.get("prefixItems", [])
            for i, item in enumerate(value):
                sub = prefix[i] if i < len(prefix) else schema.get("items")
                if sub is not None:
                    found += self.errors(item, sub, f"{path}[{i}]")
        return found

    def one_of(self, value, branches, path):
        """Exactly one branch must match. A miss reports the branch whose required keys the
        value has, such as the block type it names, or else lists what each branch needs."""
        results = [self.errors(value, b, path) for b in branches]
        passed = [r for r in results if not r]
        if len(passed) == 1:
            return []
        if len(passed) > 1:
            return [f"{path}: matches {len(passed)} block types, expected one"]
        needs = [self.resolve(b["$ref"]) if "$ref" in b else b for b in branches]
        for branch, result in zip(needs, results):
            required = branch.get("required", [])
            if isinstance(value, dict) and required and all(k in value for k in required):
                return result
        names = [k for b in needs for k in b.get("required", [])]
        keys = ", ".join(map(repr, value)) if isinstance(value, dict) else json.dumps(value)[:40]
        return [f"{path}: unknown block {keys}; a block has one key of {', '.join(names)}"]


class Scripts(HTMLParser):
    """A page's script srcs, every element whose id is exactly "ui" in document order (the
    first is the one getElementById gives the renderer), and the text of each such script,
    parsed as the browser does: a repeated attribute keeps its first value, spacing and
    quotes vary, and script text is never markup."""

    def __init__(self, html):
        super().__init__()
        self.srcs, self.ui_tags, self.payloads, self._open = [], [], [], None
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        first = {}
        for name, value in attrs:
            first.setdefault(name, value)
        if first.get("id") == "ui":
            self.ui_tags.append(tag)
        if tag == "script":
            if first.get("src"):
                self.srcs.append(first["src"].strip())
            self._open = [] if first.get("id") == "ui" else None

    def handle_data(self, data):
        if self._open is not None:
            self._open.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._open is not None:
            self.payloads.append("".join(self._open))
            self._open = None


def _no_constant(name):
    raise ValueError(f"{name} isn't JSON")


def _safe_int(text):
    if abs(int(text)) > 2 ** 53 - 1:
        raise ValueError(f"{text} loses precision in JavaScript; write it as a string")
    return int(text)


def _finite(text):
    if not math.isfinite(float(text)):
        raise ValueError(f"{text} isn't a finite JavaScript number; write it as a string")
    return float(text)


def parse(text):
    """JSON as the renderer gets it from JSON.parse: NaN and Infinity fail, and so does a
    number JavaScript can't hold exactly, or nesting too deep to check."""
    try:
        return json.loads(text, parse_constant=_no_constant, parse_int=_safe_int, parse_float=_finite)
    except RecursionError:
        raise ValueError("nested too deep") from None


def load(text):
    """The payload: the first <script id="ui"> of a page, the one the renderer reads, or the
    whole text as JSON."""
    found = Scripts(text).payloads
    return parse(found[0] if found else text)


def references(payload, skip=()):
    """Problems the schema can't express, in each block the schema passed (not in skip): an
    index past its list, and decision keys or picks that clash."""
    found = []
    blocks = payload.get("ui") if isinstance(payload, dict) else None
    for i, block in enumerate(blocks if isinstance(blocks, list) else []):
        if i in skip or not isinstance(block, dict) or len(block) != 1:
            continue
        (kind, body), = block.items()
        path = f"$.ui[{i}].{kind}"
        if kind == "table" and body.get("pick", 0) >= len(body["rows"]):
            found.append(f"{path}.pick: no row {body['pick']}; rows count from 0")
        if kind == "flow" and body.get("mark", 0) >= len(body["steps"]):
            found.append(f"{path}.mark: no step {body['mark']}; steps count from 0")
        if kind == "decision":
            keys = [o["key"] for o in body["options"]]
            if len(set(keys)) < len(keys):
                found.append(f"{path}.options: each key once, got {', '.join(keys)}")
            if sum(1 for o in body["options"] if o.get("rec")) > 1:
                found.append(f"{path}.options: at most one rec")
    return found


def check(payload, schema=None):
    """The problems in payload, as `<path>: <message>` lines; none when it's valid."""
    schema = schema or json.loads(SCHEMA.read_text())
    try:
        errors = Validator(schema).errors(payload, schema)
    except RecursionError:
        return ["$: nested too deep"]
    broken = {int(m.group(1)) for m in map(re.compile(r"\$\.ui\[(\d+)\]").match, errors) if m}
    return errors + references(payload, broken)


def pinned():
    """The one URL a card may load reply.js from."""
    return RENDERER.read_text().strip()


def refusal(html):
    """Why html_render should refuse this page, with the fix, or None when it passes."""
    page = Scripts(html)
    sources = [src for src in page.srcs if RENDERER_SRC.search(src)]
    if not sources:
        return None
    url = pinned()
    wrong = [src for src in sources if src != url]
    if wrong:
        return f"Reply card loads {wrong[0]}; load exactly {url} (reply-shape's ui/renderer.url)."
    if len(page.ui_tags) > 1:
        return 'Reply card has more than one element with id="ui"; keep only the card\'s script, since the renderer reads the first.'
    if not page.payloads:
        return 'Reply card has no payload; add <script type="application/json" id="ui">{"ui":[...]}</script> after reply.js.'
    try:
        problems = check(parse(page.payloads[0]))
    except ValueError as error:
        problems = [f"$: not JSON: {error}"]
    if not problems:
        return None
    more = f" (and {len(problems) - 1} more)" if len(problems) > 1 else ""
    return (f"Reply card is invalid: {problems[0]}{more}. Fix the payload to match reply-shape's "
            "ui/catalog.schema.json; scripts/validate-card.py page.html lists every problem.")


def hook(stdin):
    """The PreToolUse output for one html_render call, or "" when it passes."""
    try:
        tool_input = json.load(stdin).get("tool_input") or {}
        html = tool_input.get("html")
        if not isinstance(html, str) and isinstance(tool_input.get("path"), str):
            html = pathlib.Path(tool_input["path"]).read_text()
    except (OSError, ValueError, AttributeError):
        return ""
    reason = refusal(html) if isinstance(html, str) else None
    if not reason:
        return ""
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                              "permissionDecisionReason": reason}})


def main(argv):
    if argv[1:] == ["--hook"]:
        out = hook(sys.stdin)
        if out:
            print(out)
        return 0
    source = argv[1] if len(argv) > 1 else "-"
    text = sys.stdin.read() if source == "-" else pathlib.Path(source).read_text()
    try:
        payload = load(text)
    except ValueError as error:
        print(f"$: not JSON: {error}")
        return 1
    problems = check(payload)
    for line in problems:
        print(line)
    if problems:
        return 1
    print(f"ok: {len(payload['ui'])} blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
