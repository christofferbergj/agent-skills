#!/usr/bin/env python3
"""Read or upsert a literal dotenv value without shell evaluation."""

import argparse
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

KEY = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')
ASSIGNMENT = re.compile(r'^[ \t]*(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)[ \t]*=[ \t]*')


def encode(value):
    if '\0' in value or '\r' in value:
        raise ValueError('Unsupported NUL or carriage return in dotenv value')
    for quote in ["'", '`']:
        if quote not in value:
            return quote + value + quote
    if '"' not in value and '\\n' not in value and '\\r' not in value:
        return '"' + value + '"'
    if '\n' not in value and '#' not in value and value == value.strip() and value[:1] not in ["'", '"', '`']:
        return value
    raise ValueError('This value needs the consuming application\'s dotenv serializer')


def records(text):
    lines = text.splitlines(keepends=True)
    index = 0
    while index < len(lines):
        start = index
        match = ASSIGNMENT.match(lines[index])
        if not match:
            yield None, lines[index], None
            index += 1
            continue
        raw = lines[index][match.end():]
        key = match[1]
        if raw[:1] in ["'", '"', '`']:
            quote = raw[0]
            content = raw[1:]
            while True:
                closing = content.find(quote)
                if closing >= 0:
                    tail = content[closing + 1:].strip()
                    if tail and not tail.startswith('#'):
                        raise ValueError('Unsupported existing dotenv quoting')
                    value = content[:closing]
                    if quote == '"':
                        value = value.replace('\\n', '\n').replace('\\r', '\r')
                    break
                index += 1
                if index >= len(lines):
                    raise ValueError('Unterminated existing dotenv value')
                content += lines[index]
        else:
            value = raw.split('#', 1)[0].strip()
        yield key, ''.join(lines[start:index + 1]), value
        index += 1


def upsert(path, key, value):
    if not KEY.fullmatch(key):
        raise ValueError('Invalid environment variable name')
    encoded = encode(value)
    target = path.resolve()
    text = target.read_text() if target.exists() else ''
    existing = list(records(text))
    kept = ''.join(raw for name, raw, _ in existing if name != key)
    if kept and not kept.endswith('\n'):
        kept += '\n'
    content = kept + key + '=' + encoded + '\n'
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o600
    descriptor, temporary = tempfile.mkstemp(prefix='.wizard-env-', dir=target.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(content)
        os.chmod(temporary, mode)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['read', 'write'])
    parser.add_argument('path', type=Path)
    parser.add_argument('key')
    arguments = parser.parse_args()
    try:
        if not KEY.fullmatch(arguments.key):
            raise ValueError('Invalid environment variable name')
        if arguments.operation == 'write':
            upsert(arguments.path, arguments.key, sys.stdin.read())
        else:
            values = [value for name, _, value in records(arguments.path.read_text()) if name == arguments.key]
            if not values:
                return 1
            print(values[-1], end='')
        return 0
    except (OSError, ValueError) as error:
        print('Wizard dotenv operation failed: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
