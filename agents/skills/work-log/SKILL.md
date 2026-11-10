---
name: work-log
description: Rebuild your yearly work log (merged PRs and Jira tickets grouped by epic, plus a short narrative by area) into ~/notes/work-log-<year>.md — invoked as /work-log [year]. Use for end-of-year reviews, onsite or deck prep ("what have I worked on"), or whenever an up-to-date list of your work is needed.
---

# Work Log

One file per year at `~/notes/work-log-<year>.md`. Two parts:

- **Above the marker:** a hand-maintained `## Areas` narrative. Short
  paragraphs or bullets per work area, each naming the epics and the date
  span. This is the part a human reads first.
- **Below the marker** (`<!-- generated below: do not edit by hand -->`):
  a generated `## By epic` section listing every ticket with its status and
  every merged PR under it. Regenerated on each run; never edit by hand.

Requires the `acli` CLI (Atlassian) for Jira lookups.

## Step 1: Regenerate the generated section

Run `scripts/build_work_log.py` from the `scripts/` folder next to this
SKILL.md:

```bash
python3 <skill-dir>/scripts/build_work_log.py --year 2026 --repo <repo-checkout>
```

- Sources: `git log --author <author>` on `origin/main` (`--ref` to change)
  of the repo for the year, Jira tickets assigned to you created in the
  year, and one `acli jira workitem view` per ticket key for summary,
  status, parent epic and created date.
- Defaults: `--repo` is the git toplevel of the current directory;
  `--author` is `git config user.name` in that repo; `--key-pattern` (the
  regex for ticket keys in commit subjects) is `[A-Z][A-Z0-9]+-\d+`.
- Ticket lookups are cached in `~/notes/.work-log-jira-cache.json`.
  Only new keys are fetched, so re-runs are fast. Pass `--refresh-open` to
  re-fetch tickets whose cached status is not Done or Abandoned (use this at
  review time so statuses are current).
- The first run of a year fetches every key and takes a few minutes. Run it
  in the background and keep working.
- Run `git -C <repo-checkout> fetch origin` first so `origin/main` is
  current.
- The script calls `acli` and `git` itself. Nothing in the Bash call needs a
  pipe, redirect, or `>=`, so it auto-approves under the shell hooks.

## Step 2: Refresh the Areas narrative

Read the generated section and update `## Areas` above the marker so it
matches. Rules:

- One bullet or short paragraph per area. Name the epics, the date span, and
  what the work amounted to in business terms. No PR lists here; those live
  below the marker.
- Keep existing area wording unless the generated section contradicts it.
  Add new areas at the bottom. Drop an area only if it has no tickets left.
- Order areas by volume of work, largest first.
- Plain sentences, no invented terminology, no acronyms that are not already
  in the codebase or Jira.
- Edit the file in place. Do not rewrite the generated section.

## Step 3: Report

Report the file path, the number of PRs and tickets, and which areas
changed since the last run (compare against the previous Areas text).

## Notes

- Commits whose subject has no ticket key land in a "Commits without a
  ticket key" list at the end of the generated section.
- Tickets with no merged PR (investigations, open work) still appear under
  their epic with their status.
- A ticket the Jira lookup cannot find is listed as "(ticket not found)";
  delete its cache entry to retry.

## Local overrides

If `~/.agents/skills-work/work-log.md` exists, read it and apply it as additional rules for this skill; where it conflicts with the text above, it wins.
