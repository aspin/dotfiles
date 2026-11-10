# Claude Code hooks

`hooks/`: PreToolUse guards for Bash calls that keep commands simple enough to auto-approve.
Each blocked call explains why on stderr.

- `no-var-expansion.py`: rejects `$VAR` / `${VAR}` expansion
- `deny-text-tools.py`: rejects sed/awk/cat/head/tail/... in favour of grep and the Read/Edit tools
- `deny-complex-commands.py`: rejects pipes, chaining, redirects, substitution and subshells
- `deny-venv-bin.py`: rejects running tools via `.venv/bin/...` paths

`../agents/install.zsh` symlinks the hooks into `~/.claude/hooks`. It also copies
`settings.json`, which wires them up, but only when `~/.claude/settings.json` doesn't exist
yet. Otherwise it prints a reminder to merge the hooks block by hand.
