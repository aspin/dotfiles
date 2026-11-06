#!/usr/bin/env python3
"""PreToolUse(Bash) hook: block text/search shell utilities so Claude uses the
native Read / Grep / Glob / Edit tools instead.

Blocks the utility whether it is the leading command, piped, inside process
substitution, prefixed by env assignments / sudo / xargs, or aliased with a
leading backslash. Non-matching commands pass through untouched (exit 0).

User preference — added via the update-config skill. To relax, remove this
hook from ~/.claude/settings.json (PreToolUse, matcher "Bash") or trim BANNED.
"""
import json
import re
import sys

# NOTE: `grep` intentionally NOT banned. On native macOS/Linux Claude Code
# builds (>=2.1.117) the built-in Grep tool was removed and `grep` is aliased to
# the embedded `ugrep` — so bash `grep` is the sanctioned search path, with no
# native Grep tool to fall back to. rg/egrep/fgrep stay blocked: plain `grep`
# (with -E/-F) covers their use and they are not the embedded-alias path.
BANNED = {
    "egrep", "fgrep", "rg",
    "sed", "awk", "gawk",
    "cut", "tr", "head", "tail", "cat",
}

MODIFIERS = {"sudo", "command", "builtin", "nohup", "time", "xargs", "then", "do", "else"}


def leading_executable(segment: str) -> str:
    s = segment.strip()
    # strip leading VAR=value assignments (possibly several)
    while True:
        m = re.match(r'^[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|\'[^\']*\'|\S*)\s+', s)
        if not m:
            break
        s = s[m.end():]
    # strip leading command modifiers (sudo, xargs, time, ...)
    tokens = s.split()
    while tokens and tokens[0].lstrip('\\').rsplit('/', 1)[-1] in MODIFIERS:
        tokens = tokens[1:]
    if not tokens:
        return ""
    tok = tokens[0].lstrip('\\')
    return tok.rsplit('/', 1)[-1]


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unparseable input: do not block
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not isinstance(cmd, str) or not cmd.strip():
        sys.exit(0)

    # break into command contexts on shell control operators
    for segment in re.split(r'\|\||&&|[|;&\n(){}]', cmd):
        base = leading_executable(segment)
        if base in BANNED:
            sys.stderr.write(
                f"'{base}' is disabled by user preference. Use instead: bash `grep` "
                "(allowed — the sanctioned search path on this build) for "
                "rg/egrep/fgrep; the Read tool with offset/limit for cat/head/tail "
                "file slices; the Edit tool for sed edits. Rebuild as a `grep` or "
                "native-tool call. If this utility is genuinely required, ask the "
                "user to relax the deny-text-tools hook.\n"
            )
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
