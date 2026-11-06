# Claude Code

General-purpose skills and safety hooks.

- `skills/`: mostly adapted from [obra/superpowers](https://github.com/obra/superpowers)
  (MIT, see `skills/LICENSE-superpowers`), plus `reviewing-code` and `solid`.
- Review and PR skills (`code-review-checklist`, `pr-review`, `pr-quick`, `pr-feedback-check`,
  `iterate-pending-review`, `doc-review`, `work-log`) end with a "Local overrides" hook:
  if `~/.claude/skills-work/<name>.md` exists, its rules apply on top. Keep repo- or
  employer-specific rules there, outside this repo.
- `hooks/`: PreToolUse guards for Bash calls that keep commands simple enough
  to auto-approve. Each blocked call explains why on stderr.
  - `no-var-expansion.py`: rejects `$VAR` / `${VAR}` expansion
  - `deny-text-tools.py`: rejects sed/awk/cat/head/tail/... in favour of grep and the Read/Edit tools
  - `deny-complex-commands.py`: rejects pipes, chaining, redirects, substitution and subshells
  - `deny-venv-bin.py`: rejects running tools via `.venv/bin/...` paths

## Install

`setup.zsh` runs `install.zsh`, which symlinks the skills and hooks into `~/.claude`.
It also copies `settings.json`, which wires up the hooks, but only when `~/.claude/settings.json`
doesn't exist yet. Otherwise it prints a reminder to merge the hooks block by hand.
