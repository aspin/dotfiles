---
name: pr-quick
description: Use when asked for a quick look/orientation on an open PR in the current repo — invoked as /pr-quick <PR number or URL>. Checks out the PR and explains it in plain language so the user can ask questions. NOT a full review — use pr-review for verdicts and the report page.
---

# PR Quick Look

Fast orientation on an open PR in the current repo: check out the code,
read the diff, explain what the PR does in plain language, then stand by
for questions. **This is not a review** — no verdicts, no comment audit,
no `review.html`, no subagents, and never post anything to the PR.

## Workflow

### 1. Resolve the PR

Accept a bare number or any GitHub PR URL (including `/changes` or
`/files` suffixes) — extract the number.

```bash
gh pr view <N> --json number,title,headRefName,baseRefName,author,body,state,isDraft
```

### 2. Check out the PR head in a worktree

Never check out an external branch in the main checkout. Find it with
`git rev-parse --show-toplevel`; below, `<checkout>` is that path and
`<base>` is the PR's `baseRefName` (usually `main`).

```bash
git -C <checkout> fetch origin <base> <headRefName>
```

```bash
git -C <checkout> worktree add <worktree-root>/<repo>/quick-pr-<N> origin/<headRefName> --detach
```

If the worktree path already exists (a previous quick look at this PR),
don't re-add — refresh it instead:

```bash
git -C <worktree-root>/<repo>/quick-pr-<N> checkout --detach origin/<headRefName>
```

Diff range inside the worktree: `origin/<base>...HEAD`.

### 3. Read enough to orient

In the worktree: `git diff origin/<base>...HEAD --stat`, then the full
diff, plus the PR body. Open touched files only where the diff alone is
unclear. Read directly — no subagents; the whole point is a fast turn.

### 4. Report (final message)

Short and plain-language, in this shape:

- `## What This PR Does` — 3–6 simple sentences, derived from the diff
  (the PR body may be stale or aspirational).
- `## Key Files` — up to ~6 bullets: file → one-line role in the change.
- `## Worth Knowing` — only if something stands out: big churn, a risky
  spot, migrations, TODOs, test gaps. Omit the section if nothing does.

End by naming the worktree path and saying you're ready for questions.

### 5. Stand by for questions

Follow-up questions arrive as chat turns in this same session. Answer
from the worktree — read whatever code is needed. The no-posting rule
holds in chat too: no `gh pr comment`/`gh pr review` writes unless the
user explicitly asks for a post in that turn.

## Common mistakes

- Doing a full review anyway (subagents, verdicts, rendering a report
  page) — that is `/pr-review`'s job; this skill is orientation.
- Checking out the PR branch in the main checkout.
- Summarizing from the PR description instead of the diff.

## Local overrides

If `~/.claude/skills-work/pr-quick.md` exists, read it and apply it as additional rules for this skill; where it conflicts with the text above, it wins.
