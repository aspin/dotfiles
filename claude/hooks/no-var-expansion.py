#!/usr/bin/env python3
"""Block Bash commands that use shell variable expansion ($VAR, ${VAR}).

Single-quoted strings and single-quoted heredoc bodies (<<'EOF' ... EOF)
are stripped before checking, since shell expansion is suppressed there.
"""

import json
import re
import sys


def main() -> int:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Bash":
        return 0
    command = payload.get("tool_input", {}).get("command", "") or ""

    sanitized = re.sub(
        r"<<-?'(\w+)'.*?\n\1\b", "", command, flags=re.DOTALL
    )
    sanitized = re.sub(r"'[^']*'", "", sanitized)

    match = re.search(
        r"\$[A-Za-z_][A-Za-z0-9_]*|\$\{[^}]+\}", sanitized
    )
    if match:
        print(
            f"shell variable expansion {match.group(0)!r} is banned — "
            "write the literal value directly instead of capturing into "
            "a shell variable",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
