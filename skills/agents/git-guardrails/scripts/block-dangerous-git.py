#!/usr/bin/env python3
"""Deny configured literal Git operations from a Bash PreToolUse event."""

import json
from pathlib import PurePath
import re
import shlex
import sys

VALUE_OPTIONS = {'-C', '-c', '--git-dir', '--work-tree', '--namespace', '--config-env', '--super-prefix'}
WRAPPER_VALUE_OPTIONS = {'env': {'-u', '--unset', '-C', '--chdir'}, 'exec': {'-a'}}


def without_comments(command):
    """Preserve shell word boundaries while removing literal comments."""
    result = []
    quote = None
    word_start = True
    index = 0
    while index < len(command):
        character = command[index]
        if character == '\\' and quote != "'" and index + 1 < len(command):
            following = command[index + 1]
            if following != '\n':
                result.extend([character, following])
                word_start = False
            index += 2
            continue
        if quote:
            result.append(character)
            if character == quote:
                quote = None
        elif character in ["'", '"']:
            quote = character
            word_start = False
            result.append(character)
        elif character == '#' and word_start:
            while index < len(command) and command[index] != '\n':
                index += 1
            continue
        else:
            result.append(character)
            word_start = character in ' \t\r\n;&|()<>'
        index += 1
    return ''.join(result)


def segments(command):
    lexer = shlex.shlex(without_comments(command), posix=True, punctuation_chars=';&|()\n')
    lexer.whitespace = ' \t\r'
    lexer.whitespace_split = True
    lexer.commenters = ''
    current = []
    for token in lexer:
        if re.fullmatch(r'[;&|()\n]+', token):
            if current:
                yield current
                current = []
        else:
            current.append(token)
    if current:
        yield current


def operation(words):
    words = list(words)
    while words and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*=.*', words[0], re.DOTALL):
        words.pop(0)
    while words and words[0] in ['command', 'builtin', 'exec', 'env']:
        wrapper = words.pop(0)
        while words and words[0].startswith('-'):
            flag = words.pop(0)
            if flag in WRAPPER_VALUE_OPTIONS.get(wrapper, set()) and words:
                words.pop(0)
        while words and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*=.*', words[0], re.DOTALL):
            words.pop(0)
    if not words:
        return None
    executable = PurePath(words[0]).name
    if executable in ['bash', 'sh', 'zsh']:
        for index, word in enumerate(words[1:], 1):
            if re.fullmatch(r'-[A-Za-z]*c[A-Za-z]*', word):
                return denied(words[index + 1]) if index + 1 < len(words) else 'unrecognized shell command'
    if executable != 'git':
        return None
    index = 1
    while index < len(words) and words[index].startswith('-'):
        flag = words[index]
        if flag == '--':
            index += 1
            break
        index += 2 if flag in VALUE_OPTIONS else 1
    if index >= len(words):
        return None
    verb, arguments = words[index], words[index + 1:]
    if verb == 'push':
        return 'git push'
    if verb == 'reset' and '--hard' in arguments:
        return 'git reset --hard'
    if verb == 'clean' and any(flag == '--force' or (flag.startswith('-') and not flag.startswith('--') and 'f' in flag[1:]) for flag in arguments):
        return 'forced git clean'
    if verb == 'branch':
        short = ''.join(flag[1:] for flag in arguments if flag.startswith('-') and not flag.startswith('--'))
        deleting = 'd' in short or '--delete' in arguments
        forced = 'f' in short or '--force' in arguments
        if 'D' in short or (deleting and forced):
            return 'forced branch deletion'
    if verb in ['checkout', 'restore']:
        paths = arguments[arguments.index('--') + 1:] if '--' in arguments else arguments
        if any(path in ['.', ':/'] or path.startswith('./') for path in paths):
            return 'bulk working-tree restore'
    return None


def denied(command):
    for words in segments(command):
        reason = operation(words)
        if reason:
            return reason
    return None


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict) or not isinstance(event.get('tool_input'), dict):
            raise ValueError('Unrecognized hook event')
        command = event['tool_input'].get('command')
        if not isinstance(command, str):
            raise ValueError('Hook command is not a string')
        reason = denied(command)
    except (ValueError, TypeError):
        reason = 'Git guardrail could not inspect this hook input'
    if reason:
        message = 'BLOCKED by configured guardrail: ' + reason + '. The user has prevented you from doing this.'
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': message}}))
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
