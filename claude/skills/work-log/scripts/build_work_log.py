"""Build your yearly work log from git history and Jira.

Sources:
  - merged commits authored by you in the repo for the year
  - Jira tickets assigned to you created in the year (catches
    investigations and tickets with no PR)
  - per-ticket Jira lookups (summary, status, parent epic, created) via
    acli, cached on disk so re-runs only fetch new keys

Output: a markdown file with a hand-maintained header above a marker and a
generated "By epic" section below it. Everything above the marker is
preserved verbatim on re-runs.
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

MARKER = "<!-- generated below: do not edit by hand -->"
DEFAULT_KEY_PATTERN = r"[A-Z][A-Z0-9]+-\d+"
KEY_RE = re.compile(rf"\b({DEFAULT_KEY_PATTERN})\b")
PR_RE = re.compile(r"\(#(\d+)\)\s*$")


def run(cmd, timeout=60):
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=False
    )


def git_commits(repo, author, year, ref):
    since = f"{year}-01-01"
    until = f"{year + 1}-01-01"
    res = run(
        [
            "git",
            "-C",
            repo,
            "log",
            "--author",
            author,
            "--since",
            since,
            "--until",
            until,
            "--date=short",
            "--format=%ad\t%s",
            "--no-merges",
            ref,
        ],
        timeout=120,
    )
    if res.returncode != 0:
        sys.exit(f"git log failed: {res.stderr.strip()}")
    commits = []
    for line in res.stdout.splitlines():
        date, _, subject = line.partition("\t")
        keys = KEY_RE.findall(subject)
        pr = PR_RE.search(subject)
        commits.append(
            {
                "date": date,
                "subject": subject,
                "key": keys[0] if keys else None,
                "pr": int(pr.group(1)) if pr else None,
            }
        )
    return commits


def assigned_keys(year):
    jql = (
        f'assignee = currentUser() AND created >= "{year}-01-01" '
        f'AND created < "{year + 1}-01-01" ORDER BY created DESC'
    )
    res = run(
        [
            "acli",
            "jira",
            "workitem",
            "search",
            "-j",
            jql,
            "-l",
            "500",
            "--paginate",
            "--json",
        ],
        timeout=300,
    )
    if res.returncode != 0:
        print(f"warning: acli search failed: {res.stderr.strip()}")
        return []
    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError:
        print("warning: acli search returned non-JSON output")
        return []
    return [item["key"] for item in data]


def load_cache(path):
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    return {}


def save_cache(path, cache):
    with open(path, "w") as fh:
        json.dump(cache, fh, indent=1, sort_keys=True)


def fetch_ticket(key):
    res = run(
        [
            "acli",
            "jira",
            "workitem",
            "view",
            key,
            "-f",
            "summary,status,parent,created",
            "--json",
        ]
    )
    if res.returncode != 0:
        return {"summary": "", "status": "", "epic": None, "epic_summary": "",
                "created": "", "missing": True}
    fields = json.loads(res.stdout).get("fields", {})
    parent = fields.get("parent") or {}
    return {
        "summary": fields.get("summary", ""),
        "status": (fields.get("status") or {}).get("name", ""),
        "epic": parent.get("key"),
        "epic_summary": (parent.get("fields") or {}).get("summary", ""),
        "created": (fields.get("created") or "")[:10],
        "missing": False,
    }


def ensure_tickets(keys, cache, refresh_open):
    todo = []
    for key in sorted(keys):
        entry = cache.get(key)
        if entry is None:
            todo.append(key)
        elif refresh_open and entry.get("status") not in ("Done", "Abandoned"):
            todo.append(key)
    for i, key in enumerate(todo, 1):
        print(f"  jira {i}/{len(todo)} {key}", flush=True)
        cache[key] = fetch_ticket(key)
    return cache


def render(year, commits, assigned, cache):
    by_key = defaultdict(list)
    for c in commits:
        by_key[c["key"] or "(no ticket)"].append(c)
    all_keys = set(by_key) | set(assigned)
    all_keys.discard("(no ticket)")

    by_epic = defaultdict(list)
    for key in all_keys:
        t = cache.get(key) or {}
        epic = (t.get("epic") or "(no epic)", t.get("epic_summary") or "")
        by_epic[epic].append(key)

    def epic_sort(item):
        (_, _), keys = item
        return -sum(len(by_key.get(k, [])) for k in keys)

    out = []
    out.append(f"## By epic ({year})")
    out.append("")
    total_prs = sum(1 for c in commits if c["pr"])
    out.append(f"Merged PRs: {total_prs}. Tickets: {len(all_keys)}.")
    out.append("")
    for (epic, epic_summary), keys in sorted(by_epic.items(), key=epic_sort):
        prs = sum(len(by_key.get(k, [])) for k in keys)
        title = f"{epic} {epic_summary}".strip()
        out.append(f"### {title} ({prs} PRs, {len(keys)} tickets)")
        out.append("")

        def key_sort(k):
            dates = [c["date"] for c in by_key.get(k, [])]
            return min(dates) if dates else (cache.get(k) or {}).get("created", "9999")

        for key in sorted(keys, key=key_sort):
            t = cache.get(key) or {}
            status = t.get("status") or "?"
            summary = t.get("summary") or "(ticket not found)"
            out.append(f"- **{key}** [{status}] {summary}")
            for c in sorted(by_key.get(key, []), key=lambda c: c["date"]):
                subject = c["subject"]
                subject = PR_RE.sub("", subject).strip()
                subject = re.sub(r"^\[?" + re.escape(key) + r"\]?:?\s*", "", subject)
                pr = f" #{c['pr']}" if c["pr"] else ""
                out.append(f"  - {c['date']} {subject}{pr}")
        out.append("")

    untracked = by_key.get("(no ticket)", [])
    if untracked:
        out.append("### Commits without a ticket key")
        out.append("")
        for c in sorted(untracked, key=lambda c: c["date"]):
            out.append(f"- {c['date']} {c['subject']}")
        out.append("")
    return "\n".join(out)


def write_output(path, year, generated):
    header = ""
    if os.path.exists(path):
        with open(path) as fh:
            existing = fh.read()
        if MARKER in existing:
            header = existing.split(MARKER)[0]
    if not header:
        header = (
            f"# Work log {year}\n\n"
            "## Areas\n\n"
            "(narrative summary by area, maintained by /work-log)\n\n"
        )
    today = dt.date.today().isoformat()
    body = f"{header.rstrip()}\n\n{MARKER}\n\nGenerated {today} by /work-log.\n\n{generated}"
    with open(path, "w") as fh:
        fh.write(body)


def git_output(args, cwd="."):
    res = run(["git", "-C", cwd, *args], timeout=30)
    if res.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout.strip()


def main():
    global KEY_RE
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=dt.date.today().year)
    ap.add_argument(
        "--repo",
        default=None,
        help="repo checkout (default: git toplevel of the current directory)",
    )
    ap.add_argument(
        "--author",
        default=None,
        help="git author (default: git config user.name in the repo)",
    )
    ap.add_argument(
        "--ref", default="origin/main", help="branch to read merged commits from"
    )
    ap.add_argument(
        "--key-pattern",
        default=DEFAULT_KEY_PATTERN,
        help="regex for ticket keys in commit subjects",
    )
    ap.add_argument("--out", default=None)
    ap.add_argument(
        "--refresh-open",
        action="store_true",
        help="re-fetch tickets whose cached status is not Done/Abandoned",
    )
    ap.add_argument("--skip-jira-search", action="store_true")
    args = ap.parse_args()

    repo = args.repo or git_output(["rev-parse", "--show-toplevel"])
    author = args.author or git_output(["config", "user.name"], cwd=repo)
    KEY_RE = re.compile(rf"\b({args.key_pattern})\b")

    notes = os.path.expanduser("~/notes")
    out = os.path.expanduser(args.out) if args.out else os.path.join(
        notes, f"work-log-{args.year}.md"
    )
    cache_path = os.path.join(notes, ".work-log-jira-cache.json")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    os.makedirs(notes, exist_ok=True)

    print(f"git log ({author} in {repo}) ...", flush=True)
    commits = git_commits(repo, author, args.year, args.ref)
    print(f"  {len(commits)} commits", flush=True)

    assigned = []
    if not args.skip_jira_search:
        print("jira search (assigned) ...", flush=True)
        assigned = assigned_keys(args.year)
        print(f"  {len(assigned)} tickets", flush=True)

    keys = {c["key"] for c in commits if c["key"]} | set(assigned)
    cache = load_cache(cache_path)
    print(f"jira lookups for {len(keys)} keys ...", flush=True)
    cache = ensure_tickets(keys, cache, args.refresh_open)
    save_cache(cache_path, cache)

    generated = render(args.year, commits, assigned, cache)
    write_output(out, args.year, generated)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
