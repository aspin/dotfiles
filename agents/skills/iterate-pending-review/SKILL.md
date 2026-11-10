---
name: iterate-pending-review
description: Pull your PENDING (unsubmitted) self-review comments from one of your draft PRs in the current repo and address each one — invoked as /iterate-pending-review <N>, or as a pass inside a PR-monitoring loop. Implements or answers each pending comment, then deletes the pending review so other reviewers never see the self-review churn. Pushed-back comments are kept pending and surfaced in the report.
---

# Iterate on a Draft PR from Your Pending Self-Review Comments

You self-review your draft PRs by leaving comments in a **pending review**
(GitHub's "start a review" flow, never submitted). Pending comments are
visible only to their author — and the gh token authenticates as you, so
this skill can read them. The loop: read the pending comments, act on each,
then **delete them** so the PR stays clean for other reviewers. Nothing from
the self-review round should remain visible on the PR — no resolved threads,
no reactions, no replies.

Only pending comments are in scope. Submitted comments, bot threads, and
other humans' comments are out of scope for this pass.

If run inside a PR-monitoring loop, this pass runs **before** any
bot-comment pass: your pending comments are handled and deleted first, then
bot threads. Your directives supersede (and can moot) bot suggestions, and
the agent never posts general (conversation-tab) comments on the PR.

## Step 1: Fetch the pending review

A user has at most one pending review per PR. Get the repo coordinates with
`gh repo view --json owner,name`, then fetch the review with its body and
comments (REST cannot see pending comments reliably; use GraphQL):

```bash
gh api graphql -f query='
query {
  repository(owner: "<owner>", name: "<name>") {
    pullRequest(number: <N>) {
      reviews(states: PENDING, first: 5) {
        nodes {
          id
          databaseId
          author { login }
          body
          comments(first: 100) {
            nodes { id databaseId path line originalLine body diffHunk }
          }
        }
      }
    }
  }
}'
```

Confirm the pending review's author is the PR author. If there is no pending
review, report "no pending self-review comments" in one line and stop the
pass. The review **body** (if non-empty) is an action item too, not just the
inline comments.

## Step 2: Address each comment

- **Directive** (change request): implement it. Follow the repo gates —
  tests for the touched code, then the repo's test, lint and type-check
  gates per its AGENTS.md or CLAUDE.md.
- **Question**: answer it in the session report. Do not reply on the PR —
  the whole point is that this round leaves no trace there.
- **Disagree**: push back in the session report with reasoning. Keep that
  comment pending (do not delete it) — you decide.

## Step 3: Commit

Before committing: every change must meet the code-review-checklist
standards, and if this pass added or modified comments, docstrings, or
non-trivial code, run the code-review-checklist pass on the introduced diff
first and apply its delete/compact verdicts — iteration rounds accrete
narration comments otherwise.

Pending comments are unsubmitted and invisible to everyone else — they never
count as external review. Run three fresh human-activity checks, each
counting items by anyone other than the PR author (bots excluded):

```bash
gh api repos/{owner}/{repo}/pulls/<N>/comments --paginate --jq '[.[] | select(.user.login != "<author>" and .user.type != "Bot")] | length'
```

```bash
gh api repos/{owner}/{repo}/pulls/<N>/reviews --paginate --jq '[.[] | select(.user.login != "<author>" and .user.type != "Bot")] | length'
```

```bash
gh api repos/{owner}/{repo}/issues/<N>/comments --paginate --jq '[.[] | select(.user.login != "<author>" and .user.type != "Bot")] | length'
```

- Commit the round as a **separate commit** with a descriptive message and
  a plain `git push` — never amend immediately. The revision commit is what
  you review next.
- Squash into the base commit only when you ask or at the final pre-merge
  squash, keeping ONE commit per round of external activity. Re-run the
  three checks in the same batch as the `--force-with-lease`; any nonzero
  (including a lone approval) means the squash waits for your go-ahead.

## Step 4: Delete the addressed pending comments — one by one, never the whole review

**Never use the whole-review DELETE endpoint**
(`DELETE /pulls/<N>/reviews/<review_databaseId>`). You may add comments to
the pending review while the pass is running; a review-level delete based on
a stale fetch destroys comments written after Step 1 fetched.

Instead, after the fixes are pushed, delete **each handled comment
individually** by its GraphQL node id:

```bash
gh api graphql -f query='mutation { deletePullRequestReviewComment(input: {id: "<comment node id>"}) { pullRequestReview { id } } }'
```

- **Re-fetch the pending review immediately before deleting** and delete only
  node ids that (a) appeared in the fetch you worked from AND (b) you actually
  handled. Any comment in the fresh fetch you haven't handled is new — leave
  it pending and handle it (this pass or the next).
- Pushed-back comments stay pending as before.
- Deleting the last comment leaves an empty pending review shell; that's
  harmless — do not delete the review object itself unless a fresh fetch shows
  it empty of comments AND its body is empty/handled.

Never submit the pending review — submitting publishes it, which is exactly
the noise this flow avoids.

## Step 5: Report

One line per pending comment: location, your ask (one sentence), and the
action — `implemented in <sha>, deleted` / `answered: <answer>, deleted` /
`pushed back: <reason>, kept pending`. Lead with pushed-back items. Include
answers to questions in full — the comment is deleted, so the report is the
only record.

## Gotchas

- **The report is the only record.** Deleted pending comments are gone;
  quote each comment's ask in the report before deleting so you can audit
  the round.
- If you submit the pending review mid-run, the comments become public
  submitted threads — stop deleting, handle them as ordinary review
  feedback (new commits, no amend), and say so.
- PR body edits (if any) follow the repo's PR body rules if it has them and
  preserve any live checkbox state.

## Local overrides

If `~/.agents/skills-work/iterate-pending-review.md` exists, read it and apply it as additional rules for this skill; where it conflicts with the text above, it wins.
