#!/usr/bin/env python3
"""PreToolUse(Bash) hook: block direct execution of venv-bin paths
(.venv/bin/python, .venv/bin/pytest, any <something>venv/bin/<tool>).

Rationale: venv-path invocations bypass the environment the session was
launched with and don't match any Bash(...) allow rule, causing prompts
and wrong-interpreter confusion. The sanctioned path is the bare command
(pytest, python, uvicorn, ...) resolved by the active pyenv env — launch
the session from the repo whose env you need. If the wrong env is
active, say so instead of routing around it with venv paths.

User preference — added via the update-config skill. To relax, remove
this hook from ~/.claude/settings.json (PreToolUse, matcher "Bash").
"""
import json
import re
import sys

# A path component ending in "venv/bin/" used anywhere in the command:
# covers .venv/bin/..., venv/bin/..., /abs/path/.venv/bin/..., and
# quoted or assigned forms (VAR=.venv/bin/python).
VENV_BIN = re.compile(r'(^|[\s"\'=:|;&(])(\S*/)?\.?[A-Za-z0-9_.-]*venv/bin/')


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unparseable input: do not block
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not isinstance(cmd, str) or not cmd.strip():
        sys.exit(0)
    if VENV_BIN.search(cmd):
        sys.stderr.write(
            "venv-bin paths (.venv/bin/..., venv/bin/...) are disabled by "
            "user preference. Run the bare command instead (pytest, python, "
            "black, uvicorn, ...) — the repo's pyenv env supplies it when "
            "the session is launched from that repo. If the wrong "
            "environment is active, tell the user rather than bypassing it "
            "via venv paths.\n"
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
