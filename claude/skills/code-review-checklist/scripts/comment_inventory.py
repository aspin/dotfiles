"""Inventory every comment/docstring line ADDED by a diff range.

Used by the code-review-checklist skill (workflow step 5) to build the
mechanical, provably-complete inventory of added comments and docstrings.

Usage:
    python3 comment_inventory.py --repo /path/to/worktree \
        --range origin/main...HEAD [--exclude generated/]

Output: one block per item (a contiguous run of added comment lines, or one
docstring), with repo-relative file:line headers, followed by a total count.

Method: the added-line numbers come from `git diff --unified=0`; the
classification comes from tokenizing the post-image file (COMMENT tokens via
`tokenize`, docstring line ranges via `ast`), so multi-line strings and
tricky quoting are handled by the real Python parser rather than regexes.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import sys
import tokenize

HUNK_RE = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@")

DEFAULT_EXCLUDES: list[str] = []


def added_lines_by_file(repo: str, diff_range: str) -> dict[str, set[int]]:
    """Map repo-relative .py path -> set of post-image line numbers added."""
    out = subprocess.run(
        ["git", "-C", repo, "diff", "--unified=0", diff_range, "--", "*.py"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    result: dict[str, set[int]] = {}
    current: set[int] | None = None
    lineno = 0
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            current = result.setdefault(line[6:], set())
        elif line.startswith("+++ /dev/null"):
            current = None
        elif m := HUNK_RE.match(line):
            lineno = int(m.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            if current is not None:
                current.add(lineno)
            lineno += 1
    return result


def comment_and_docstring_lines(
    source: str,
) -> tuple[set[int], list[tuple[int, int]]]:
    """(comment line numbers, docstring (start, end) line ranges)."""
    comment_lines: set[int] = set()
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            comment_lines.add(tok.start[0])

    docstring_ranges: list[tuple[int, int]] = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
        ):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            doc = body[0]
            end = doc.end_lineno if doc.end_lineno is not None else doc.lineno
            docstring_ranges.append((doc.lineno, end))
    return comment_lines, docstring_ranges


def file_post_image(repo: str, diff_range: str, path: str) -> str | None:
    """Post-image content of path at the range's right-hand commit."""
    head = diff_range.split("...")[-1].split("..")[-1] or "HEAD"
    proc = subprocess.run(
        ["git", "-C", repo, "show", f"{head}:{path}"],
        capture_output=True,
        text=True,
    )
    return proc.stdout if proc.returncode == 0 else None


def collect_items(
    repo: str, diff_range: str, excludes: list[str]
) -> list[dict[str, object]]:
    """Every added comment/docstring as an ordered list of item dicts.

    Each item: {id, file, line, span, kind, text}. ``id`` is a stable 1-based
    index over the same file-then-line order the human output prints, so a
    verdicts file keyed by these ids lines up with a fresh --json run.
    """
    collected: list[dict[str, object]] = []
    for path, added in sorted(added_lines_by_file(repo, diff_range).items()):
        if any(path.startswith(prefix) for prefix in excludes):
            continue
        source = file_post_image(repo, diff_range, path)
        if source is None:
            continue
        try:
            comment_lines, docstring_ranges = comment_and_docstring_lines(
                source
            )
        except SyntaxError as e:
            print(f"WARNING: could not parse {path}: {e}", file=sys.stderr)
            continue
        lines = source.splitlines()

        items: list[tuple[int, list[str], str]] = []
        # Docstrings: one item per docstring with >=1 added line.
        for start, end in docstring_ranges:
            if any(n in added for n in range(start, end + 1)):
                items.append((start, lines[start - 1 : end], "docstring"))
        # Comments: contiguous runs of added comment lines = one item.
        run: list[int] = []
        for n in sorted(comment_lines & added):
            if run and n == run[-1] + 1:
                run.append(n)
            else:
                if run:
                    items.append(
                        (run[0], [lines[i - 1] for i in run], "comment")
                    )
                run = [n]
        if run:
            items.append((run[0], [lines[i - 1] for i in run], "comment"))

        for start, text, kind in sorted(items):
            collected.append(
                {
                    "file": path,
                    "line": start,
                    "span": len(text),
                    "kind": kind,
                    "text": "\n".join(text),
                }
            )
    for index, item in enumerate(collected, 1):
        item["id"] = index
    return collected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--range", dest="diff_range", required=True)
    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="path prefixes to skip, e.g. generated code (default: none)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the inventory as a JSON list (id/file/line/span/kind/text)"
        " for render_review_page.py instead of the human report",
    )
    args = parser.parse_args()
    excludes = args.exclude if args.exclude is not None else DEFAULT_EXCLUDES
    items = collect_items(args.repo, args.diff_range, excludes)

    if args.json:
        print(json.dumps(items, indent=2))
        return 0

    for item in items:
        print(f"=== {item['file']}:{item['line']} [{item['kind']}]")
        for text_line in str(item["text"]).split("\n"):
            print(f"    {text_line}")
    print(f"\nTOTAL ITEMS: {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
