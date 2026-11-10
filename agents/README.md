# Agent skills

General-purpose skills for Claude Code and Codex.

- `skills/`: mostly adapted from [obra/superpowers](https://github.com/obra/superpowers) v7.0.2
  (MIT, see `skills/LICENSE-superpowers`), plus the review and PR skills, `reviewing-code` and
  `solid`. Vendored copies differ from upstream only in dropping the `superpowers:` prefix, the
  "Local overrides" section in `using-git-worktrees`, and a customized `writing-plans`.
  Skills use Claude Code's tool vocabulary; `using-superpowers/references/<harness>-tools.md`
  maps it for other harnesses.
- Review and PR skills (`code-review-checklist`, `pr-review`, `pr-quick`, `pr-feedback-check`,
  `iterate-pending-review`, `doc-review`, `work-log`) end with a "Local overrides" hook:
  if `~/.agents/skills-work/<name>.md` exists, its rules apply on top. Keep repo- or
  employer-specific rules there, outside this repo.

## Install

`setup.zsh` runs `install.zsh`, which symlinks the skills into `~/.claude/skills` (Claude Code)
and `~/.agents/skills` (Codex), and the Claude Code hooks from `../claude` (see its README).
