"""Reads the TOML subset a profile uses, since Python 3.9 has no `tomllib`: tables,
arrays of tables, bare or quoted keys, dotted header names, basic and literal strings,
integers, floats, booleans, arrays across lines, and inline tables. Dates and multi-line
strings raise TomlError, so a profile never parses into something other than it says."""
from __future__ import annotations

import re

NUMBER = re.compile(r"[+-]?\d[\d_]*(\.\d[\d_]*)?")
BARE = re.compile(r"[A-Za-z0-9_-]+")
ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}


class TomlError(ValueError):
    pass


class _Parser:
    def __init__(self, text: str):
        self.text, self.pos = text, 0

    def fail(self, message: str):
        line = self.text.count("\n", 0, self.pos) + 1
        raise TomlError(f"line {line}: {message}")

    def peek(self, n: int = 1) -> str:
        return self.text[self.pos:self.pos + n]

    def spaces(self):
        while self.peek() in (" ", "\t"):
            self.pos += 1

    def gap(self):
        """Spaces, newlines, and comments, as allowed inside arrays and between lines."""
        while True:
            self.spaces()
            if self.peek() == "#":
                while self.peek() not in ("\n", ""):
                    self.pos += 1
            if self.peek() in ("\n", "\r"):
                self.pos += 1
                continue
            return

    def end_of_line(self):
        self.spaces()
        if self.peek() == "#":
            while self.peek() not in ("\n", ""):
                self.pos += 1
        if self.peek() == "\r":
            self.pos += 1
        if self.peek() not in ("\n", ""):
            self.fail("expected the end of the line")

    def key(self) -> list[str]:
        parts = []
        while True:
            self.spaces()
            if self.peek() in ('"', "'"):
                parts.append(self.string())
            else:
                match = BARE.match(self.text, self.pos)
                if not match:
                    self.fail("expected a key")
                parts.append(match.group())
                self.pos = match.end()
            self.spaces()
            if self.peek() != ".":
                return parts
            self.pos += 1

    def string(self) -> str:
        quote = self.peek()
        if self.peek(3) == quote * 3:
            self.fail("multi-line strings are not supported")
        self.pos += 1
        out = []
        while True:
            char = self.peek()
            if char in ("", "\n"):
                self.fail("unterminated string")
            self.pos += 1
            if char == quote:
                return "".join(out)
            if char == "\\" and quote == '"':
                code = self.peek()
                if code == "u" or code == "U":
                    width = 4 if code == "u" else 8
                    digits = self.text[self.pos + 1:self.pos + 1 + width]
                    try:
                        out.append(chr(int(digits, 16)))
                    except ValueError:
                        self.fail("bad unicode escape")
                    self.pos += 1 + width
                    continue
                if code not in ESCAPES:
                    self.fail(f"unknown escape \\{code}")
                out.append(ESCAPES[code])
                self.pos += 1
                continue
            out.append(char)

    def value(self):
        char = self.peek()
        if char in ('"', "'"):
            return self.string()
        if char == "[":
            self.pos += 1
            items = []
            while True:
                self.gap()
                if self.peek() == "]":
                    self.pos += 1
                    return items
                items.append(self.value())
                self.gap()
                if self.peek() == ",":
                    self.pos += 1
                elif self.peek() != "]":
                    self.fail("expected , or ] in an array")
        if char == "{":
            self.pos += 1
            table: dict = {}
            self.spaces()
            if self.peek() == "}":
                self.pos += 1
                return table
            while True:
                path = self.key()
                if self.peek() != "=":
                    self.fail("expected = in an inline table")
                self.pos += 1
                self.spaces()
                _assign(table, path, self.value(), self)
                self.spaces()
                if self.peek() == "}":
                    self.pos += 1
                    return table
                if self.peek() != ",":
                    self.fail("expected , or } in an inline table")
                self.pos += 1
        for word, result in (("true", True), ("false", False)):
            if self.text.startswith(word, self.pos):
                self.pos += len(word)
                return result
        match = NUMBER.match(self.text, self.pos)
        if match:
            end = match.end()
            if self.text[end:end + 1] in ("-", ":", "T"):
                self.fail("dates and times are not supported; write them as strings")
            self.pos = end
            raw = match.group().replace("_", "")
            return float(raw) if match.group(1) else int(raw)
        self.fail("expected a value")

    def document(self) -> dict:
        root: dict = {}
        current = root
        while True:
            self.gap()
            if self.peek() == "":
                return root
            if self.peek(2) == "[[":
                self.pos += 2
                path = self.key()
                if self.peek(2) != "]]":
                    self.fail("expected ]]")
                self.pos += 2
                parent = _table(root, path[:-1], self)
                array = parent.setdefault(path[-1], [])
                if not isinstance(array, list):
                    self.fail(f"{'.'.join(path)} is not an array of tables")
                current = {}
                array.append(current)
            elif self.peek() == "[":
                self.pos += 1
                path = self.key()
                if self.peek() != "]":
                    self.fail("expected ]")
                self.pos += 1
                current = _table(root, path, self)
            else:
                path = self.key()
                if self.peek() != "=":
                    self.fail("expected =")
                self.pos += 1
                self.spaces()
                _assign(current, path, self.value(), self)
            self.end_of_line()


def _table(root: dict, path: list[str], parser: _Parser) -> dict:
    node = root
    for part in path:
        node = node.setdefault(part, {})
        if isinstance(node, list):
            node = node[-1]
        if not isinstance(node, dict):
            parser.fail(f"{'.'.join(path)} is not a table")
    return node


def _assign(table: dict, path: list[str], value, parser: _Parser):
    node = _table(table, path[:-1], parser)
    if path[-1] in node:
        parser.fail(f"{'.'.join(path)} is set twice")
    node[path[-1]] = value


def loads(text: str) -> dict:
    return _Parser(text).document()
