#!/usr/bin/env python3
"""PreToolUse(Bash) hook: reject compound/complex commands so every Bash call is
a single simple command that permission rules can auto-approve (no prompts).

Blocks, at shell level and quote-aware:
  - pipes             |
  - chaining          && || ; &
  - redirects         > >> < << 2> &> ...  (including 2>/dev/null)
  - substitution      $(...)  `...`
  - subshell/group    (...)

Operators INSIDE quotes are ignored (grep 'a|b', grep "x>y" are fine), and
escaped operators (echo a\\>b) are ignored. Substitutions that are still active
inside double quotes ("$(cmd)", "`cmd`") ARE caught. Env-var prefixes
(PYTHONPATH=... cmd) and ordinary flags are fine.

Split compound work into separate Bash calls; use the Read/Write/Edit tools for
file I/O instead of redirects; for large output just run the command plainly
(the harness saves big output to a file you can Read).

User preference — added via the update-config skill. To relax, remove this hook
from ~/.claude/settings.json (PreToolUse, matcher "Bash").
"""
import json
import sys


def _strip(s, keep_dquotes):
    """Remove escaped chars and single-quoted spans. Double-quoted spans are
    removed when keep_dquotes is False, kept (with quotes) when True."""
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2  # skip the escaped char
            continue
        if c == "'":
            j = s.find("'", i + 1)
            if j == -1:
                break  # unbalanced quote: stop scanning
            i = j + 1
            continue
        if c == '"':
            j = i + 1
            while j < n:
                if s[j] == "\\":
                    j += 2
                    continue
                if s[j] == '"':
                    break
                j += 1
            if keep_dquotes:
                out.append(s[i : j + 1])
            i = j + 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def offending(cmd):
    structural = _strip(cmd, keep_dquotes=False)  # | & ; < > ( ) only real here
    subst = _strip(cmd, keep_dquotes=True)  # $( and ` active inside "..." too
    found = []
    if "|" in structural:
        found.append("pipe (|)")
    if "&" in structural:
        found.append("chaining/background (&& / ||-tail / &)")
    if ";" in structural:
        found.append("command sequencing (;)")
    if ">" in structural:
        found.append("output redirection (> / >> / 2>)")
    if "<" in structural:
        found.append("input redirection (< / <<)")
    if "(" in structural or ")" in structural or "$(" in subst:
        found.append("subshell / command substitution")
    if "`" in subst:
        found.append("backtick substitution")
    return list(dict.fromkeys(found))


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not isinstance(cmd, str) or not cmd.strip():
        sys.exit(0)

    ops = offending(cmd)
    if ops:
        sys.stderr.write(
            "Command blocked (user preference: single simple commands only). "
            f"Found: {', '.join(ops)}. Split this into separate Bash calls — no "
            "pipes, no chaining (&& / || / ;), no redirects (including "
            "2>/dev/null), no substitution ($(...) / backticks), no subshells. "
            "Use the Read/Write/Edit tools for file I/O instead of redirects; "
            "for large output just run the command plainly (the harness saves "
            "big output to a file you can Read). If a compound command is truly "
            "unavoidable, put the logic in a script file and run that as one "
            "command, or ask the user to relax the deny-complex-commands hook.\n"
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
