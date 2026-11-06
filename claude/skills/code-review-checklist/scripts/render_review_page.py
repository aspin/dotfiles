"""Render a self-contained comment-review webpage from a diff + verdicts.

Turns a code-review-checklist comment/docstring pass into an interactive local
HTML page: the diff rendered GitHub-style (Python-highlighted), each analyzed
comment's verdict/reasoning/suggested-rewrite shown inline beneath the line it
annotates, a sticky file+comment navigator, per-comment feedback controls
(agree / disagree / adjust, override verdict, free-text note) that persist to
localStorage, and an "Export feedback" button that emits a markdown blob to
paste back for re-review.

Cheap-by-design inputs (the verbatim comment text and the diff come free from
tooling, so the model only produces the small verdicts file):

    # 1. structured inventory (verbatim text + line spans + stable ids)
    python3 comment_inventory.py --repo <worktree> --range origin/main...HEAD \
        --json > inventory.json

    # 2. the model writes verdicts.json keyed by those ids (see shape below)

    # 3. render
    python3 render_review_page.py --repo <worktree> --range origin/main...HEAD \
        --inventory inventory.json --verdicts verdicts.json --out review.html

verdicts.json shape (ids match the inventory produced in the SAME run):

    {
      "pr": "123",                           # optional; --pr overrides
      "title": "Add endpoint",               # optional; --title overrides
      "verdicts": {
        "1": {"verdict": "COMPACT",
              "reasoning": "one-line why",
              "suggestion": "final rewrite text"},
        "5": {"verdict": "DELETE", "reasoning": "restates the signature"},
        ...
      }
    }

Any verdict string is allowed; KEEP / DELETE / COMPACT / "... extract ..." get
coloured badges, anything else renders neutral. Items with no verdict entry
render with a "—" badge so the page is still complete.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import subprocess
import sys

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PR #__PR__ — comment review</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
  :root {
    --bg:#0d1117; --panel:#161b22; --border:#30363d; --fg:#e6edf3;
    --muted:#8b949e; --add:#1a3326; --addline:#2ea04326; --del:#3d1b1f;
    --delline:#f8514926; --accent:#2f81f7; --keep:#3fb950; --del2:#f85149;
    --compact:#d29922; --extract:#a371f7;
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
  code, pre, .code { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
  header.top { position:sticky; top:0; z-index:20; background:var(--panel);
    border-bottom:1px solid var(--border); padding:12px 20px; display:flex;
    align-items:center; gap:16px; flex-wrap:wrap; }
  header.top h1 { font-size:15px; margin:0; font-weight:600; }
  header.top .sub { color:var(--muted); font-size:12px; }
  .spacer { flex:1; }
  button { background:var(--accent); color:#fff; border:0; border-radius:6px;
    padding:7px 14px; font-size:13px; font-weight:600; cursor:pointer; }
  button.secondary { background:#21262d; border:1px solid var(--border); color:var(--fg); }
  button:hover { filter:brightness(1.1); }
  .counts { display:flex; gap:10px; font-size:12px; }
  .counts span { color:var(--muted); }
  .counts b { color:var(--fg); }
  .layout { display:flex; align-items:flex-start; gap:16px; max-width:1240px;
    margin:0 auto; padding:16px; }
  .sidebar { position:sticky; top:60px; flex:0 0 232px; width:232px;
    max-height:calc(100vh - 76px); overflow:auto; border:1px solid var(--border);
    border-radius:8px; background:var(--panel); padding:6px; font-size:12px; }
  .nav-file { margin-bottom:4px; }
  .nav-fname { display:flex; align-items:center; gap:6px; padding:5px 7px;
    color:var(--fg); text-decoration:none; border-radius:5px; font-weight:600;
    word-break:break-all; }
  .nav-fname:hover { background:#21262d; }
  .nav-count { margin-left:auto; color:var(--muted); font-weight:400; }
  .nav-item { display:flex; align-items:center; gap:7px; padding:3px 7px 3px 16px;
    color:var(--muted); text-decoration:none; border-radius:5px; cursor:pointer; }
  .nav-item:hover { background:#21262d; color:var(--fg); }
  .nav-item.touched { color:var(--fg); }
  .dot { display:inline-block; width:8px; height:8px; border-radius:50%; flex:0 0 auto; }
  main { flex:1 1 auto; min-width:0; }
  .file { border:1px solid var(--border); border-radius:8px; margin-bottom:14px; overflow:hidden;
    scroll-margin-top:64px; }
  tr.skip td { background:#0d1117; color:#6e7681; text-align:center; font-size:11px;
    padding:2px; border-top:1px solid var(--border); border-bottom:1px solid var(--border);
    user-select:none; }
  table.diff td.code { line-height:1.4; }
  .file > .fname { background:var(--panel); padding:9px 14px; font-size:12.5px;
    border-bottom:1px solid var(--border); word-break:break-all; }
  table.diff { width:100%; border-collapse:collapse; table-layout:fixed; }
  col.c-ln { width:52px; }
  table.diff td { padding:0 8px; vertical-align:top; white-space:pre-wrap;
    word-break:break-word; overflow-wrap:anywhere; }
  td.ln { width:1%; min-width:46px; text-align:right; color:var(--muted); user-select:none;
    padding:0 10px; font-size:12px; border-right:1px solid var(--border);
    white-space:nowrap; word-break:keep-all; }
  tr.add td.code { background:var(--addline); }
  tr.add td.code::before { content:"+"; color:var(--keep); }
  tr.del td.code { background:var(--delline); }
  tr.del td.code::before { content:"-"; color:var(--del2); }
  tr.ctx td.code::before { content:" "; }
  td.code { font-size:12.5px; }
  td.code code { background:transparent!important; padding:0; font-size:inherit;
    white-space:inherit; overflow-wrap:inherit; word-break:inherit; }
  td.code code.hljs { color:inherit; }
  tr.hunk td { background:#161b2299; color:var(--muted); font-size:12px; padding:3px 8px; }
  tr.flagged td.code { box-shadow:inset 2px 0 0 var(--accent); }
  tr.analysis > td { padding:0; }
  .card { margin:0; border-top:1px solid var(--border);
    border-bottom:1px solid var(--border); background:#0b1a2e; padding:8px 14px;
    display:flex; flex-direction:column; gap:6px; line-height:1.35; }
  .card .hd { display:flex; align-items:center; gap:10px; margin:0; }
  .badge { font-size:11px; font-weight:700; padding:3px 8px; border-radius:20px;
    background:#30363d; color:var(--fg); }
  .b-KEEP { background:var(--keep); color:#04260f; }
  .b-DELETE { background:var(--del2); color:#2b0405; }
  .b-COMPACT { background:var(--compact); color:#2a1e00; }
  .b-EXTRACT { background:var(--extract); color:#1c0838; }
  .card .why { color:#c9d1d9; margin:0; }
  .card pre.sugg { background:#0d1117; border:1px solid var(--border);
    border-radius:6px; padding:7px 10px; margin:0; font-size:12px;
    color:#7ee787; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere; }
  .sugg-label { font-size:11px; color:var(--muted); margin:0; text-transform:uppercase;
    letter-spacing:.04em; }
  .fb { margin:0; border-top:1px dashed var(--border); padding-top:6px;
    display:flex; flex-direction:column; gap:6px; }
  .fb .row { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin:0; }
  .fb label.seg { font-size:12px; color:var(--muted); }
  .stance { display:inline-flex; border:1px solid var(--border); border-radius:6px; overflow:hidden; }
  .stance button { background:#161b22; color:var(--muted); border:0; border-right:1px solid var(--border);
    padding:5px 12px; font-weight:600; font-size:12px; border-radius:0; }
  .stance button:last-child { border-right:0; }
  .stance button.on-agree { background:var(--keep); color:#04260f; }
  .stance button.on-disagree { background:var(--del2); color:#2b0405; }
  .stance button.on-adjust { background:var(--compact); color:#2a1e00; }
  select { background:#161b22; color:var(--fg); border:1px solid var(--border);
    border-radius:6px; padding:5px 8px; font-size:12px; }
  textarea { width:100%; min-height:42px; background:#0d1117; color:var(--fg);
    border:1px solid var(--border); border-radius:6px; padding:9px; font-size:13px;
    font-family:inherit; resize:vertical; }
  textarea:focus, select:focus { outline:1px solid var(--accent); }
  .touched { box-shadow:inset 3px 0 0 var(--accent); }
  @keyframes flash { 0% { outline:2px solid var(--accent); outline-offset:-2px; }
                     100% { outline:2px solid transparent; outline-offset:-2px; } }
  .card.flash { animation:flash 1.1s ease-out; }
  dialog { background:var(--panel); color:var(--fg); border:1px solid var(--border);
    border-radius:10px; max-width:820px; width:92%; padding:0; }
  dialog .dhd { padding:12px 16px; border-bottom:1px solid var(--border); display:flex; gap:12px; align-items:center; }
  dialog textarea { min-height:340px; border-radius:0; border:0; }
  dialog .dft { padding:10px 16px; display:flex; gap:10px; justify-content:flex-end; border-top:1px solid var(--border); }
  .pill { font-size:11px; color:var(--muted); }
</style>
</head>
<body>
<header class="top">
  <h1>PR #__PR__ · comment review</h1>
  <span class="sub">__TITLE__</span>
  <div class="counts" id="counts"></div>
  <div class="spacer"></div>
  <button class="secondary" id="btn-prev" title="Previous comment (p)">&uarr; Prev</button>
  <button class="secondary" id="btn-next" title="Next comment (n)">&darr; Next</button>
  <button class="secondary" id="btn-clear">Clear feedback</button>
  <button id="btn-export">Export feedback →</button>
</header>
<div class="layout">
  <aside class="sidebar" id="sidebar"></aside>
  <main id="main"></main>
</div>

<dialog id="export-dialog">
  <div class="dhd"><b>Feedback to paste back into Claude</b>
    <span class="pill">copied to clipboard &amp; downloaded as feedback.md</span></div>
  <textarea id="export-text" readonly></textarea>
  <div class="dft">
    <button class="secondary" id="btn-copy">Copy again</button>
    <button id="btn-close">Close</button>
  </div>
</dialog>

<script>
const DIFF = __DIFF__;
const ANALYSIS = __ANALYSIS__;
const LSKEY = "comment-review-" + ANALYSIS.pr;
let store = JSON.parse(localStorage.getItem(LSKEY) || "{}");

// Override-verdict choices: the standard set plus any verdict actually used.
const OVERRIDE_OPTIONS = ["", ...new Set(
  ["KEEP", "DELETE", "COMPACT", ...ANALYSIS.items.map(i => i.verdict)]
    .filter(v => v && v !== "—"))];

function save() { localStorage.setItem(LSKEY, JSON.stringify(store)); renderCounts(); }

// ---- parse unified diff into { file, rows:[{type,oldNo,newNo,text}] } ----
function parseDiff(text) {
  const files = []; let cur = null;
  const lines = text.split("\n");
  let oldNo = 0, newNo = 0;
  for (const ln of lines) {
    if (ln.startsWith("diff --git")) { cur = { file:null, rows:[] }; files.push(cur); continue; }
    if (ln.startsWith("+++ ")) { if (cur) cur.file = ln.slice(4).replace(/^b\//, ""); continue; }
    if (ln.startsWith("--- ")) continue;
    if (ln.startsWith("index ") || ln.startsWith("new file") || ln.startsWith("deleted file")
        || ln.startsWith("rename ") || ln.startsWith("similarity ")) continue;
    if (ln.startsWith("@@")) {
      const m = ln.match(/@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
      if (m) { oldNo = +m[1]; newNo = +m[2]; }
      if (cur) cur.rows.push({ type:"hunk", text: m ? m[0] : ln });
      continue;
    }
    if (!cur) continue;
    const c = ln[0];
    if (c === "+") { cur.rows.push({ type:"add", newNo, text:ln.slice(1) }); newNo++; }
    else if (c === "-") { cur.rows.push({ type:"del", oldNo, text:ln.slice(1) }); oldNo++; }
    else { cur.rows.push({ type:"ctx", oldNo, newNo, text:ln.slice(1) }); oldNo++; newNo++; }
  }
  return files;
}

// item lookup: file -> line -> item ; flagged lines = the span of each item
const itemAt = {}, flagged = {};
for (const it of ANALYSIS.items) {
  (itemAt[it.file] = itemAt[it.file] || {})[it.line] = it;
  for (let i = 0; i < it.span; i++) (flagged[it.file] = flagged[it.file] || new Set()).add(it.line + i);
}

const vClass = v => (v || "").toLowerCase().includes("extract") ? "EXTRACT"
  : (v || "").split(" ")[0].toUpperCase();

function esc(s){ return (s || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

function cardHTML(it) {
  const st = store[it.id] || {};
  const sugg = it.suggestion
    ? `<div class="sugg-label">Suggested</div><pre class="sugg">${esc(it.suggestion)}</pre>` : "";
  const stance = st.stance || "";
  return `<div class="card">
    <div class="hd">
      <span class="badge b-${vClass(it.verdict)}">${esc(it.verdict)}</span>
      <span class="pill">${esc(it.file.split("/").pop())}:${it.line} · ${it.kind}</span>
    </div>
    <div class="why">${esc(it.reasoning)}</div>
    ${sugg}
    <div class="fb">
      <div class="row">
        <label class="seg">Your call:</label>
        <span class="stance" data-id="${it.id}">
          <button data-s="agree" class="${stance==='agree'?'on-agree':''}">Agree</button>
          <button data-s="disagree" class="${stance==='disagree'?'on-disagree':''}">Disagree</button>
          <button data-s="adjust" class="${stance==='adjust'?'on-adjust':''}">Adjust</button>
        </span>
        <label class="seg">Override verdict:</label>
        <select data-ov="${it.id}">
          ${OVERRIDE_OPTIONS.map(o =>
            `<option value="${esc(o)}" ${st.override===o?"selected":""}>${o?esc(o):"— none —"}</option>`).join("")}
        </select>
      </div>
      <textarea data-fb="${it.id}" placeholder="Feedback for re-review (why you disagree, better wording, a rule to add)...">${esc(st.note||"")}</textarea>
    </div>
  </div>`;
}

function renderRows(f) {
  const flags = flagged[f.file] || new Set();
  const items = itemAt[f.file] || {};
  let html = "";
  for (const r of f.rows) {
    if (r.type === "hunk") { html += `<tr class="hunk"><td colspan="3">${esc(r.text)}</td></tr>`; continue; }
    const on = (r.newNo && flags.has(r.newNo)) ? " flagged" : "";
    html += `<tr class="${r.type}${on}"><td class="ln">${r.oldNo||""}</td><td class="ln">${r.newNo||""}</td>`
          + `<td class="code"><code class="language-python">${esc(r.text)}</code></td></tr>`;
    if (r.newNo && items[r.newNo]) {
      html += `<tr class="analysis" id="item-${items[r.newNo].id}"><td colspan="3">${cardHTML(items[r.newNo])}</td></tr>`;
    }
  }
  return html;
}

const slug = s => s.replace(/[^a-zA-Z0-9]/g, "-");

function renderSidebar(files) {
  const sb = document.getElementById("sidebar");
  sb.innerHTML = files.map(f => {
    const its = ANALYSIS.items.filter(i => i.file === f.file);
    const name = f.file.split("/").pop();
    return `<div class="nav-file">`
      + `<a class="nav-fname" href="#file-${slug(f.file)}">${esc(name)}`
      + `<span class="nav-count">${its.length}</span></a>`
      + its.map(i => `<a class="nav-item" data-jump="${i.id}">`
          + `<span class="dot b-${vClass(i.verdict)}"></span>:${i.line} `
          + `<span class="nav-count">${esc(i.verdict.split(" ")[0])}</span></a>`).join("")
      + `</div>`;
  }).join("");
  sb.querySelectorAll("[data-jump]").forEach(a => a.addEventListener("click", () =>
    jumpToId(+a.dataset.jump)));
}

function render() {
  const files = parseDiff(DIFF).filter(f => f.file && itemAt[f.file]);
  const main = document.getElementById("main");
  main.innerHTML = files.map(f =>
    `<div class="file" id="file-${slug(f.file)}"><div class="fname">${esc(f.file)}</div>`
    + `<table class="diff"><colgroup><col class="c-ln"><col class="c-ln"><col></colgroup>`
    + `<tbody>${renderRows(f)}</tbody></table></div>`).join("");
  if (window.hljs) {
    document.querySelectorAll("td.code > code.language-python").forEach(el => {
      if (el.textContent.trim()) hljs.highlightElement(el);
    });
  }
  renderSidebar(files);
  wire();
  renderCounts();
}

function wire() {
  document.querySelectorAll(".stance").forEach(el => el.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    const id = el.dataset.id; store[id] = store[id] || {};
    store[id].stance = b.dataset.s; save();
    el.querySelectorAll("button").forEach(x => x.className = "");
    b.className = "on-" + b.dataset.s;
    markTouched(id);
  }));
  document.querySelectorAll("[data-fb]").forEach(t => t.addEventListener("input", e => {
    const id = e.target.dataset.fb; store[id] = store[id] || {};
    store[id].note = e.target.value; save(); markTouched(id);
  }));
  document.querySelectorAll("[data-ov]").forEach(s => s.addEventListener("change", e => {
    const id = e.target.dataset.ov; store[id] = store[id] || {};
    store[id].override = e.target.value; save(); markTouched(id);
  }));
  ANALYSIS.items.forEach(it => markTouched(it.id));
}

function markTouched(id) {
  const st = store[id] || {};
  const touched = !!(st.stance || st.note || st.override);
  document.querySelectorAll(`[data-fb="${id}"]`).forEach(t =>
    t.closest(".card").classList.toggle("touched", touched));
  document.querySelectorAll(`.nav-item[data-jump="${id}"]`).forEach(a =>
    a.classList.toggle("touched", touched));
}

function renderCounts() {
  const total = ANALYSIS.items.length;
  let done = 0, dis = 0;
  ANALYSIS.items.forEach(it => {
    const st = store[it.id] || {};
    if (st.stance || st.note || st.override) done++;
    if (st.stance === "disagree" || st.stance === "adjust" || (st.override && st.override !== it.verdict)) dis++;
  });
  document.getElementById("counts").innerHTML =
    `<span>reviewed <b>${done}</b>/${total}</span><span>flagged for re-review <b>${dis}</b></span>`;
}

function exportText() {
  const lines = [`# Feedback on comment review — PR #${ANALYSIS.pr}`, ""];
  ANALYSIS.items.forEach(it => {
    const st = store[it.id] || {};
    if (!(st.stance || st.note || st.override)) return;
    lines.push(`## ${it.file.split("/").pop()}:${it.line} (item ${it.id})`);
    lines.push(`- my verdict: ${it.verdict}`);
    if (st.stance) lines.push(`- your stance: ${st.stance.toUpperCase()}`);
    if (st.override) lines.push(`- override verdict: ${st.override}`);
    if (st.note) lines.push(`- note: ${st.note.replace(/\n/g, " ")}`);
    lines.push("");
  });
  if (lines.length === 2) lines.push("_(no feedback entered)_");
  return lines.join("\n");
}

document.getElementById("btn-export").addEventListener("click", async () => {
  const txt = exportText();
  document.getElementById("export-text").value = txt;
  document.getElementById("export-dialog").showModal();
  try { await navigator.clipboard.writeText(txt); } catch(e) {}
  const blob = new Blob([txt], {type:"text/markdown"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = "feedback.md"; a.click();
});
document.getElementById("btn-copy").addEventListener("click", () =>
  navigator.clipboard.writeText(document.getElementById("export-text").value));
document.getElementById("btn-close").addEventListener("click", () =>
  document.getElementById("export-dialog").close());
document.getElementById("btn-clear").addEventListener("click", () => {
  if (confirm("Clear all feedback for this PR?")) { store = {}; save(); render(); }
});

// ---- jump between comments ----
let navIdx = -1;
function flashCard(card) {
  card.scrollIntoView({ behavior:"smooth", block:"center" });
  card.classList.remove("flash"); void card.offsetWidth; card.classList.add("flash");
}
function jump(dir) {
  const cards = [...document.querySelectorAll("tr.analysis .card")];
  if (!cards.length) return;
  navIdx = (navIdx + dir + cards.length) % cards.length;
  flashCard(cards[navIdx]);
}
function jumpToId(id) {
  const rows = [...document.querySelectorAll("tr.analysis")];
  const idx = rows.findIndex(r => r.id === "item-" + id);
  if (idx < 0) return;
  navIdx = idx;
  flashCard(rows[idx].querySelector(".card"));
}
document.getElementById("btn-next").addEventListener("click", () => jump(1));
document.getElementById("btn-prev").addEventListener("click", () => jump(-1));
document.addEventListener("keydown", e => {
  if (e.target.matches("textarea, select, input")) return;
  if (e.key === "n") jump(1);
  else if (e.key === "p") jump(-1);
});

render();
</script>
</body>
</html>
"""


def git_diff(repo: str, diff_range: str, files: list[str], context: int) -> str:
    return subprocess.run(
        ["git", "-C", repo, "diff", diff_range, f"-U{context}", "--", *files],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--range", dest="diff_range", default="origin/main...HEAD")
    parser.add_argument(
        "--inventory", required=True, help="comment_inventory.py --json output"
    )
    parser.add_argument(
        "--verdicts", required=True, help="verdicts JSON (see module docstring)"
    )
    parser.add_argument("--out", required=True)
    parser.add_argument("--pr", default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--context", type=int, default=8)
    args = parser.parse_args()

    inventory = json.loads(pathlib.Path(args.inventory).read_text())
    raw = json.loads(pathlib.Path(args.verdicts).read_text())
    verdicts = raw.get("verdicts", raw)  # allow bare {id: {...}} too
    verdicts = {str(k): v for k, v in verdicts.items()}

    pr = str(args.pr or raw.get("pr", "?"))
    title = args.title or raw.get("title", "")

    items = []
    for inv in inventory:
        v = verdicts.get(str(inv["id"]), {})
        items.append(
            {
                "id": inv["id"],
                "file": inv["file"],
                "line": inv["line"],
                "span": inv["span"],
                "kind": inv["kind"],
                "text": inv["text"],
                "verdict": v.get("verdict", "—"),
                "reasoning": v.get("reasoning", ""),
                "suggestion": v.get("suggestion", ""),
            }
        )
    if not items:
        print("no inventory items — nothing to render", file=sys.stderr)
        return 1

    files = sorted({it["file"] for it in items})
    diff = git_diff(args.repo, args.diff_range, files, args.context)

    analysis = {"pr": pr, "title": title, "items": items}
    # json.dumps then neutralise any </script> that could close the inline block.
    diff_js = json.dumps(diff).replace("</", "<\\/")
    analysis_js = json.dumps(analysis).replace("</", "<\\/")

    out_html = (
        TEMPLATE.replace("__PR__", html.escape(pr))
        .replace("__TITLE__", html.escape(title))
        .replace("__DIFF__", diff_js)
        .replace("__ANALYSIS__", analysis_js)
    )
    out_path = pathlib.Path(args.out)
    out_path.write_text(out_html)
    print(f"wrote {out_path} ({len(items)} items, {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
