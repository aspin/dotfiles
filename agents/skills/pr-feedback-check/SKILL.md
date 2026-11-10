---
name: pr-feedback-check
description: Use when asked how well your review feedback was addressed on a PR in the current repo — invoked as /pr-feedback-check <PR number or URL>. Checks the current code against every review comment you submitted and issues per-comment verdicts (addressed / partially / unaddressed / moot).
---

# PR Feedback Check

Audit of a PR in the current repo: for every review comment you have
**submitted** on it, judge whether the author's subsequent changes (or
replies) actually addressed it. Output is a verdict table in plain
language, then stand by for questions. **Never post anything to the
PR.** No subagents — read the code directly.

## Workflow

### 1. Resolve the PR

Accept a bare number or any GitHub PR URL — extract the number.

```bash
gh pr view <N> --json number,title,headRefName,baseRefName,author,state,isDraft
```

### 2. Check out the current PR head in a worktree

Never check out an external branch in the main checkout. Find it with
`git rev-parse --show-toplevel`; below, `<checkout>` is that path and
`<base>` is the PR's `baseRefName` (usually `main`).

```bash
git -C <checkout> fetch origin <base> <headRefName>
```

```bash
git -C <checkout> worktree add <worktree-root>/<repo>/feedback-pr-<N> origin/<headRefName> --detach
```

If the worktree path already exists, refresh it instead:

```bash
git -C <worktree-root>/<repo>/feedback-pr-<N> checkout --detach origin/<headRefName>
```

### 3. Fetch your feedback with full thread context

Get your login and the repo coordinates first:

```bash
gh api user --jq .login
```

```bash
gh repo view --json owner,name
```

One GraphQL call gets every review thread with resolution state,
every comment's author/body/timestamps, and file/line anchors:

```bash
gh api graphql -f query='query { repository(owner: "<owner>", name: "<name>") { pullRequest(number: <N>) { reviewThreads(first: 100) { nodes { isResolved isOutdated path line originalLine comments(first: 30) { nodes { author { login } body createdAt } } } } reviews(first: 30) { nodes { author { login } state submittedAt body } } } } }'
```

Keep only threads containing a comment by your login, and your
submitted review bodies (`state != PENDING`) when they carry
substantive asks. Pending drafts are NOT feedback the author ever
saw — exclude them.

Also fetch the commits pushed after your earliest comment, for the
evidence column:

```bash
git -C <worktree> log --oneline --since=<earliest comment timestamp> origin/<base>..HEAD
```

### 4. Judge each comment against the CURRENT code

For every one of your threads, in the worktree:

- Read the file at/around the anchored line (use `originalLine` when
  `line` is null — the code may have moved).
- Decide the verdict from the code first, replies second:
  - **addressed** — the concern is fixed in the current code.
  - **partially** — some of the ask landed, part remains (say which).
  - **unaddressed** — code unchanged, no fix; note if the author
    replied with pushback (quote the gist).
  - **moot** — the commented code was deleted/rewritten so the
    comment no longer applies, or it was a question that got a
    complete answer in replies.
- Thread resolution state is a signal, not a verdict: authors
  resolve threads without fixing things. If a thread is resolved but
  the code still has the problem, say so plainly — that is the whole
  point of this check.

### 5. Report (final message)

- `## Feedback Scorecard` — one line: N comments — X addressed, Y
  partially, Z unaddressed, W moot.
- A table: file:line · the comment's gist (≤10 words) · verdict ·
  evidence (≤15 words: what the code/replies show now).
- `## Needs Another Look` — only unaddressed/partial rows, each with
  1-2 sentences of detail and what to re-check or re-raise.
- End by naming the worktree path and saying you're ready for
  questions.

### 6. Stand by for questions

Follow-ups arrive as chat turns in this session. Answer from the
worktree. The no-posting rule holds in chat too — no `gh pr comment`
or `gh pr review` writes unless the user explicitly asks in that turn.

## Common mistakes

- Trusting thread resolution instead of reading the current code.
- Including your PENDING draft comments (the author never saw
  them; they can't have been addressed).
- Judging against the diff at review time instead of the current
  head — later force-pushes may have changed everything.
- Checking out the PR branch in the main checkout.

## Local overrides

If `~/.agents/skills-work/pr-feedback-check.md` exists, read it and apply it as additional rules for this skill; where it conflicts with the text above, it wins.
