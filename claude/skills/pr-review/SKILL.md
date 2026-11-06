---
name: pr-review
description: Use when reviewing someone else's open PR in the current repo — invoked as /pr-review <PR number or URL>, or when asked to review a colleague's pull request, or to check/validate your own pending (draft) or submitted review comments on a PR.
---

# PR Review

Full review of an open PR in the current repo, built on `/code-review-checklist`, plus a correctness analysis of your own review comments on that PR — **all of them**: pending drafts, every previously submitted review round, inline thread replies, and conversation-tab comments.

Two deliverables:
1. The complete `code-review-checklist` structured report, run against the PR's branch.
2. A per-comment verdict on every comment you have ever written on the PR — are the claims correct, are questions answerable from the code, is anything stale?

**This skill never posts anything to the PR by default.** The output is a local report for you to act on manually. Posting is a rare, explicitly-requested exception — see "Posting comments" below.

## Execution model

Same as `code-review-checklist`: the review itself always runs in a fresh subagent (the main conversation may be biased; a fresh-context reviewer judges the diff the way an external reviewer will). The main session does the setup (worktree, comment fetching) and relays the subagent's report **as-is** — no pre-filtering or softening.

## Workflow (main session)

### 1. Resolve the PR

Accept a bare number or any GitHub PR URL (including `/changes` or `/files` suffixes) — extract the number.

```bash
gh pr view <N> --json number,title,headRefName,baseRefName,author,body,state,isDraft
```

### 2. Check out the PR head in a worktree

Never review an external branch from the main checkout — it pollutes the working copy and breaks if local state differs from the PR head. Find the checkout with `git rev-parse --show-toplevel`; below, `<checkout>` is that path and `<base>` is the PR's `baseRefName` (usually `main`). Detached checkout at the PR head:

```bash
git -C <checkout> fetch origin <base> <headRefName>
```

```bash
git -C <checkout> worktree add <worktree-root>/<repo>/review-pr-<N> origin/<headRefName> --detach
```

Diff range inside the worktree: `origin/<base>...HEAD`.

### 3. Fetch your own comments on the PR

The authenticated user is you. Get the login first and use it as `<login>` below:

```bash
gh api user --jq .login
```

Three sources, all mandatory — previous rounds count as much as pending drafts:

**a. All submitted inline comments (every past review round + thread replies), in one call:**

```bash
gh api repos/{owner}/{repo}/pulls/<N>/comments --paginate --jq '[.[] | select(.user.login == "<login>") | {id, path, line, original_line, side, in_reply_to_id, body, diff_hunk}]'
```

**b. Pending (draft) review comments** — these do NOT appear in `/pulls/<N>/comments`; they surface only via the reviews endpoint, as `state: PENDING`, and only to their author (which is why this runs as you in the main session):

```bash
gh api repos/{owner}/{repo}/pulls/<N>/reviews --paginate --jq '[.[] | select(.user.login == "<login>" and .state == "PENDING") | {id, state, body}]'
```

```bash
gh api repos/{owner}/{repo}/pulls/<N>/reviews/<review_id>/comments --jq '[.[] | {id, path, line, original_line, side, in_reply_to_id, body, diff_hunk}]'
```

- `line` is **null** when the comment anchors to an outdated diff — fall back to `original_line` + `diff_hunk` to locate the code.
- For a reply (`in_reply_to_id` set), fetch enough of the parent thread that the subagent can judge the reply in context.
- Also collect your conversation-tab comments (they sometimes contain review claims worth checking):

```bash
gh api repos/{owner}/{repo}/issues/<N>/comments --jq '[.[] | select(.user.login == "<login>") | {id, body}]'
```

If there are no comments of yours anywhere, note that and skip the comment-analysis pass — the run degrades to a plain `code-review-checklist` of the PR branch.

### 4. Read the code-review-checklist skill fresh

Read `~/.claude/skills/code-review-checklist/SKILL.md` in full at run time — it evolves; never reproduce its instructions from memory.

### 5. Dispatch one fresh subagent

Pick a scratchpad dir for this run (the session scratchpad) and pass its absolute path to the subagent. Give it, in one prompt:
- The worktree path and diff range (`origin/<base>...HEAD`), with the standing subagent constraints: absolute paths everywhere, `git -C <worktree>` for every git command, no `cd &&` compounds, no `$VAR` expansion.
- The PR number/title/author, and the instruction to run the code-review-checklist PR Body pass against PR <N>.
- The **full** code-review-checklist workflow, review areas, and output format (from step 4), minus Module Layout: that area is house style for your own branches, not review feedback for colleagues' PRs — instruct the subagent to skip it and write "Skipped (pr-review)." in its output section.
- The **PR summary and review guide** contract below — the report must OPEN with `## What This PR Does` followed by `## How to Review This`, before every code-review-checklist section.
- The **comment correctness pass** below, with the collected comments inlined as JSON (the subagent should not re-fetch them).
- The **review-page artifacts** instruction (so step 6 is cheap): as part of the Comments/Docstrings pass, the subagent must (a) run `comment_inventory.py --json` and save the result to `<scratchpad>/inventory.json`, and (b) write `<scratchpad>/verdicts.json` — the small `{pr, title, verdicts: {<id>: {verdict, reasoning, suggestion}}}` object keyed by the inventory ids (verdict is the KEEP/DELETE/COMPACT/… string, reasoning is the one-liner, suggestion is the post-round-3 rewrite for COMPACT/extract, empty otherwise). This is a Write-tool file, NOT part of the returned report, so the verbatim comment text and diff never re-enter the token stream.
- **Comments/Docstrings section is summary-only in the report** (override of the code-review-checklist output format for this skill): the per-item verdict entries live in `verdicts.json` and render on the review page, so the returned `## Comments and Docstrings` section must contain ONLY the total item count, a verdict tally (e.g. "19 KEEP, 1 DELETE, 5 COMPACT"), and the 2-3 sentence whole-PR verbosity assessment — no per-item entries, no verbatim quotes. A comment whose *content* is factually wrong still gets a full finding in Correctness/Terminology (those sections are unaffected).

### 6. Build the interactive review page

The comment/docstring pass is far easier to triage in the HTML review viewer than in prose. Once the subagent has written `inventory.json` and `verdicts.json`, render and open the page (the diff comes free from git; nothing to hand-assemble):

```bash
python3 ~/.claude/skills/code-review-checklist/scripts/render_review_page.py --repo <worktree-root>/<repo>/review-pr-<N> --range origin/<base>...HEAD --inventory <scratchpad>/inventory.json --verdicts <scratchpad>/verdicts.json --out <scratchpad>/review.html
```

```bash
open <scratchpad>/review.html
```

The page renders the diff GitHub-style (Python-highlighted) with each verdict + reasoning + suggested rewrite inline beneath the comment it annotates, a sticky file/comment navigator, and per-comment feedback controls (agree/disagree/adjust, override verdict, note) that persist to `localStorage`. You triage inline and click **Export feedback** to get a markdown blob to paste back; take that and re-run the affected verdicts. If the subagent didn't emit the artifacts, generate them from the main session (run `comment_inventory.py --json` yourself and write `verdicts.json` from the returned report) rather than skipping the page.

### 7. Relay and clean up

Present the subagent's report as-is, and tell the user the review page is open (path from step 6). Leave the worktree in place while the review is being iterated on; once the user is done with the PR, remove it:

```bash
git -C <checkout> worktree remove <worktree-root>/<repo>/review-pr-<N>
```

## PR summary and review guide (subagent instructions)

The report OPENS with these two sections, in this order, before any
review findings. They are written for a reader who has NOT read the PR
body and does not want to — readers find PR descriptions too dense to
parse.

### `## What This PR Does`

4–8 sentences in plain language, then one worked example. Contract:

- Say what the system does differently after this PR merges —
  behavior, not implementation ("the /orders endpoint returns one row
  per order instead of one per shipment", not "refactors the listing
  builder").
- Use the simplest words that stay precise. One idea per sentence. A
  term of art may appear only if the diff itself uses it, and gets a
  half-sentence gloss on first use.
- End with **Example:** — pick one real workflow this PR touches and
  trace it before vs after in 2–4 sentences ("Today, when a customer
  places an order that ships in two parts, the listing shows ...; after
  this PR, the same order shows ...").
- Derive everything from the diff, not the PR body. If the body and
  the diff disagree, the diff wins (that contradiction belongs in the
  PR Body section, not here).

### `## How to Review This`

3–6 numbered recommendations for reviewing this specific PR, most
useful first, each naming concrete files/functions from the diff:

1. Where to start reading, and why that entry point orients the rest.
2. Which file(s) carry the design decision — the part worth real
   scrutiny.
3. Which changes are mechanical churn (renames, regenerated files,
   repeated test scaffolding) that can be skimmed once the pattern is
   spot-checked.
4. The riskiest assumption or edge case to verify, and how to verify
   it (a test to read, an invariant to trace, a query to run).

Scale to the diff: a 50-line PR gets 3 short entries, not padding.

## Comment correctness pass (subagent instructions)

For **every** comment of yours collected in step 3 (an omitted comment is a defect in the review itself):

1. Locate the code it refers to in the worktree (path + `line`, falling back to `original_line`/`diff_hunk` matching when `line` is null).
2. Evaluate the comment against the actual code and issue one verdict:
   - **CORRECT** — the claim/request stands as written; one line of confirming evidence.
   - **INCORRECT** — the claim is wrong; explain why with `file:line` evidence. Do not soften: a wrong comment posted under your name is exactly what this pass exists to catch.
   - **NEEDS REWORDING** — right idea, but the wording is ambiguous, overstated, or targets the wrong line; give the suggested replacement text.
   - **STALE** — the code changed since the comment was written (outdated anchor) and the point no longer applies.
   - **ANSWERED** — the comment is a question; answer it definitively from the code, with evidence.
3. Cross-check against the fresh review's own findings: note where one of your comments and a review finding coincide (mutual confirmation), and where the review contradicts a comment (call that out explicitly — it's the highest-value output of this pass).

Add this section to the code-review-checklist output format, directly before `## Risk Summary`:

```
## Your Review Comments
<count, split pending vs submitted>
- <path>:<line> [pending|submitted] — "<comment excerpt>" — CORRECT | INCORRECT | NEEDS REWORDING | STALE | ANSWERED — <evidence / answer / suggested rewording>
```

## Posting comments (rare — off by default)

The default is **never post**. Reasons to make an exception (each requires the user explicitly asking in this session): batching validated findings into a draft review for the user to edit and submit themselves, or replying to a thread with a factual answer already approved in conversation.

When posting is explicitly requested:

- Include an AI-generated disclaimer on every posted body (follow the repo's rules for it if it has them — read those first).
- **Never submit or approve a review.** Creating a *pending* review is acceptable (the user edits and submits it manually); POSTing with an `event` field, or `gh pr review --approve/--request-changes/--comment`, is not.
- Single inline comment on the current head commit:

```bash
gh api repos/{owner}/{repo}/pulls/<N>/comments -f body='<text>' -f commit_id='<head sha>' -f path='<file>' -F line=<n> -f side=RIGHT
```

- Reply to an existing inline thread:

```bash
gh api repos/{owner}/{repo}/pulls/<N>/comments/<comment_id>/replies -f body='<text>'
```

- Batch comments into a **pending** review (stays draft because no `event` is sent): write the JSON payload to the scratchpad, then

```bash
gh api repos/{owner}/{repo}/pulls/<N>/reviews --input <scratchpad>/pending_review.json
```

with payload shape `{"commit_id": "<head sha>", "comments": [{"path": "...", "line": <n>, "side": "RIGHT", "body": "..."}]}`.

## Common mistakes

- A report that opens with setup notes or findings instead of `## What This PR Does` — the summary and review guide come first, always.
- Reviewing from the main checkout instead of a worktree — pollutes the working copy and breaks if local state differs from the PR head.
- Assuming pending comments are invisible or unfetchable — they're in `/pulls/<N>/reviews` with `state: PENDING`, for the author only.
- Trusting `line` on fetched comments — null means outdated anchor; use `original_line` + `diff_hunk`.
- Softening an INCORRECT verdict on your own comment — catching those before a human sees them is the point.
- Printing per-item comment/docstring verdicts in the relayed report — they belong only in `verdicts.json` / the review page; the report carries just the count, tally, and verbosity assessment.
- Posting anything (even "harmless" replies) without an explicit request in this session.

## Local overrides

If `~/.claude/skills-work/pr-review.md` exists, read it and apply it as additional rules for this skill; where it conflicts with the text above, it wins.
