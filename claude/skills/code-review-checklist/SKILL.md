---
name: code-review-checklist
description: Manually invoked pre-PR code review checklist for changes on the current git branch. Use when asked to review code before sending a PR for external review, or when invoked as /code-review-checklist. Always runs in a separate subagent. Covers comment and docstring quality (bias hard toward conciseness), terminology/vocabulary validation (no invented terms), correctness/bugs, rollout risk, type annotation quality, exception precision, architecture & code quality (SOLID), DRY/best-practice alignment, test coverage, and module layout (newspaper order; skipped under /pr-review). Always invoke this skill before creating or marking a PR ready for review.
---

# Code Review Checklist

A structured pre-PR review for changes on the current branch. Run this before marking a branch ready for external review. Covers comments and docstrings, terminology and naming, correctness, riskiness, typing, exception precision, architecture & code quality, best practices/DRY, test coverage, and module layout (newspaper order — own-branch reviews only).

## Execution: always in a separate subagent

Never perform this review inline in the main conversation. Dispatch the entire review to a fresh subagent via the Agent tool and relay its report:

- The implementing conversation is biased — terminology and design invented during the session look natural to the author. A fresh-context reviewer judges the diff the way an external reviewer will.
- Give the subagent: the repo/worktree path, the branch or commit range, and the full instructions of this skill (workflow, all review areas, output format). The subagent performs the workflow below and returns the structured review.
- Present the subagent's review to the user as-is — do not pre-filter or soften findings.

## Setup

`git diff` works from any subdirectory of the repo — no `cd` needed. If a worktree branch is specified, use `git -C <worktree-root>/<repo>/<branch>` to target it without changing the shell CWD.

## Workflow

1. Run `git diff main...HEAD --stat` to see which files changed.
2. Run `git diff main...HEAD` to read the full diff.
3. For anything that looks like it might duplicate existing utilities, use Grep to search the broader codebase for similar patterns.
4. Load the `solid` skill for design principles to apply during the Architecture review.
5. **Exhaustive comment/docstring inventory pass (mandatory, per-item verdicts):** spot-checking is not acceptable — the pass must provably cover 100% of added comments and docstrings. Build the mechanical inventory with the skill's helper script in the `scripts/` folder next to this SKILL.md (never an ad-hoc `python3 -c` pipeline — those match no permission rule and prompt every time):

   ```bash
   python3 <skill-dir>/scripts/comment_inventory.py --repo <worktree> --range origin/main...HEAD
   ```

   It prints every added comment block and docstring (classified by tokenizing the post-image files, so multi-line docstrings are exact) with `file:line` headers and a total item count; pass `--exclude <prefix>` (repeatable) to skip generated code. Group contiguous lines into items (one comment block or one docstring = one item) and state the total item count in the review. Then, for EVERY item — including ones being kept — emit one verdict entry in the Comments and Docstrings section: a `file:line — KEEP | DELETE | COMPACT` header, the item's **verbatim text quoted in a fenced code block** (so the reader sees exactly what the verdict is about without opening the file), and the one-line reason (plus the final suggested text for COMPACT). Quoting the text is mandatory, not optional — a bare `file:line` row is a defect. Apply the two-question test in §1 and the **iterative compaction rule**: be brutal — run at least 3 compaction rounds on every surviving item. Round 1: delete everything reconstructible from the code. Round 2: take the survivor and compact it again — drop qualifiers, merge clauses, cut examples and restated context. Round 3: ask once more "can this be shorter or gone entirely?" — only what survives all three rounds is the verdict. A KEEP verdict on a multi-line item must state why round-3 compaction failed. For COMPACT verdicts, include the final (post-round-3) suggested text. An omitted item is a defect in the review itself. Close the section with a 2-3 sentence whole-PR verbosity assessment (roughly what fraction of the added comment/docstring mass should go, and the worst-offender files).

   **Layout pass (mandatory, after compaction):** for EVERY item whose verdict is KEEP or COMPACT, apply the §1 "Layout: one idea per line" triggers to the surviving text. A hit changes the verdict to RESTRUCTURE (or keeps COMPACT with the suggested text re-laid-out). State in each entry's reason line that the layout triggers were checked, so a reader can tell the pass ran. The equation-in-a-sentence trigger is the one most often missed: a docstring that reads as one wrapped sentence usually hides a formula, a definition and a qualifier.

   **Optional interactive review page.** The same inventory feeds an HTML viewer that renders the diff GitHub-style with each verdict + reasoning + suggested rewrite inline, a sticky navigator, and per-comment feedback controls that export a markdown blob to paste back for re-review. It's cheap because the verbatim text and diff come from tooling, not the token stream: run `comment_inventory.py --json` to `inventory.json`, write a small `verdicts.json` (`{pr, title, verdicts: {<id>: {verdict, reasoning, suggestion}}}` keyed by the inventory ids), then `python3 <skill-dir>/scripts/render_review_page.py --repo <worktree> --range <range> --inventory inventory.json --verdicts verdicts.json --out review.html` and `open` it. `/pr-review` generates this automatically; for a plain `/code-review-checklist` produce it when asked or when the comment pass is large.
6. **Terminology pass (mandatory):** for every term of art in added comments, docstrings, and identifiers, apply the vocabulary test in §2. Do not skip this pass.
7. **PR body pass (only if a PR exists for this branch):** run `gh pr view --json number,body --jq '.body'` for the current branch. If a PR exists, apply the §11 review to its body. If no PR exists yet, skip this pass and write "No PR open yet — skipped." in the PR Body output section.
8. **Module layout pass:** for each new or substantially reworked module in the diff, apply §10 (skipped entirely under `/pr-review`).
9. **Parametrization pass (mandatory):** list every test function added by the diff, grouped by file, and check each group against §9's Parametrization bullet — two or more added tests sharing a skeleton and differing only in input/expected values must be flagged for `@pytest.mark.parametrize`. Small new test files are the classic miss (a 3-test truth table reads as too little to bother with — it isn't). State the added-test count per file in the review so the pass is provably exhaustive.
10. Write a structured review covering all areas below.

## Review Areas

### 1. Comments and Docstrings

The same bar applies to both. Explain *why*, not *what*. If removing the comment or docstring wouldn't confuse a future reader, it should be deleted — not reworded. **Bias hard toward conciseness; useless prose is a defect, not a neutral choice.**

**Required pass:** for every comment and docstring touched by the diff, run this two-question test and flag anything that fails either:

1. Could a competent reader of the surrounding code (signatures, types, names, **and the language constructs in view — `Protocol`, `async`, `@dataclass`, `frozen=`, `Enum`, `Final`, …**) reconstruct this in their head without the comment? If yes → **delete it**, don't reword. A comment that explains a keyword by restating what the keyword *definitionally does* is circular and always fails this test.
2. Is the explanation grounded in something durable (an invariant, an external constraint, a rejected alternative, a ticket) — or is it a transient pointer to current implementation details that will drift the moment the body changes? If it's the latter → **delete it**, the code already says this and the comment will start lying.

**Passing Q2 does not rescue a comment that fails Q1 — the two are AND, not OR.** The most common miss is a comment with a genuine, durable *why* (so it passes Q2) that is nonetheless reconstructible because that same *why* is **already stated at a higher level or enforced elsewhere**: declared in the module/class docstring the reader has already seen, or pinned by a named test that fails the moment someone violates it. A local restatement of an already-stated invariant fails Q1 — prefer **DELETE** and let the higher-level statement or the test carry it. Example: a `raise`-not-skip rationale on a parse-error branch (*"skipping would drop their orders silently"*) whose importer module docstring already declares "an order must never be silently dropped" AND is pinned by a `test_unparseable_line_fails_alone` — the rationale is real but stated twice; delete the local copy. When you KEEP a comment on durable-rationale grounds, first confirm the rationale is not already carried by a docstring in view or a named test.

Default action on a flagged comment is **deletion**. Only suggest a reword when there's a genuine kernel that survives the two-question test and the existing wording obscures it.

For each surviving comment or docstring, apply the iterative compaction rule: ask "can this be compacted?" at least 3 times, compacting the result each round — delete the reconstructible, then drop qualifiers/examples/restated context, then ask once more whether the remainder can shrink or go entirely. Only the round-3 survivor is acceptable; anything longer is a finding. Long docstrings are almost always a sign the function is doing too much or the explanation belongs in a design doc. **A 3+ line comment block that justifies a single guard should be one short line; if it can't fit in a line, it should fit in a per-field comment inside the data structure itself.**

**Structure: bullets for conditions and steps.** A surviving docstring that enumerates multiple conditions, branches, or sequential steps must present them as a bullet list — one bullet per condition/step — not as chained prose sentences. Dense multi-sentence prose is a finding even when every sentence individually survives compaction; verdict is COMPACT with the bulleted rewrite as the suggested text. A one- or two-sentence docstring stays prose — don't bullet a single fact.

**Layout: one idea per line.** Compaction decides how many words survive; layout decides how they sit on the lines. A short comment can still be hard to read when several ideas share one wrapped sentence. For every surviving item, check these observable triggers:

- an equation or identity (`==`, `=`, `+`, `-` between named quantities) sits inside a prose sentence
- a `where` / `with` / `i.e.` clause defines a term used earlier in the same sentence
- two or more cases, conditions or steps are joined inline with commas, `and`, `or`, colons or semicolons
- a statement and its reason share one sentence (`X: because Y`, `X, so Y`)

Any hit is a **RESTRUCTURE** verdict: same words or fewer, laid out one idea per line — the formula on its own line, each definition on its own line below it, cases as bullets, the reason on the line after the statement. Multi-line never means longer: the word count must stay flat or drop. Example:

```
"""Per invoice, in cents: total == subtotal + tax - discount, where
discount = sum of applied coupon amounts."""
```

Restructured:

```
"""Per invoice, in cents:

    total == subtotal + tax - discount

discount = sum of applied coupon amounts"""
```

A COMPACT verdict's suggested text must already be laid out this way; compaction must never fold two ideas back into one sentence to save a line.

Flag any of these with a `file:line` reference and a one-line note.

**Useless content to flag (always delete, don't reword):**
- **Narrating what the code does** when names and types already say it (`# increment counter` above `counter += 1`; `"""Returns the value."""` above `def get_value() -> int`).
- **Workflow narration in tests**: `# First run — collect events.` / `# Simulate what the entrypoint would do: persist them.` / `# Second run — should find identical rows, no errors.` The next 1-2 lines of code already say this.
- **Restating an assertion in prose**: `# A's events are dropped; B's events remain.` directly above `assert kept == [b1, b2]`. The assertion is the statement.
- **Restating the function signature** in the docstring without adding semantics ("Takes a list of foos and returns the bar.").
- **"This function does X" / "This class represents Y" boilerplate** where X/Y is the function or class name in different words.
- **Circular explanations of a language construct** — a comment that justifies a keyword by restating what the keyword definitionally does. `# A Protocol, not a base class, so callers can supply their own shape without inheriting` (structural conformance without inheritance *is* what `Protocol` means); `# frozen so instances are immutable`; `# async so it can be awaited`; `# an Enum, so the values are distinct`. The construct already tells the reader this — the comment adds nothing. Delete it. The only comment that earns its place next to a construct is one that says something the construct *can't*: a non-obvious constraint, an invariant, or why the obvious alternative was rejected (e.g. `# Protocol not ABC because the CSV rows are pydantic and can't add a second base` — but only if that tension is real and non-obvious).
- **Argument-by-argument `:param x:` blocks** that repeat the parameter name and type and add nothing else.
- **reST / Sphinx docstring markup** — when the repo runs no doc generator (no Sphinx), reST field lists and interpreted-text roles render to nothing and are pure syntactic noise: `:param:` / `:returns:` / `:raises:` / `:type:` / `:rtype:` field blocks, double-backtick inline literals (```` ``candidates`` ````), and cross-reference roles (`:class:`, `:meth:`, `:func:`, `:mod:`, `:attr:`, e.g. ``:meth:`~Decompressor.expand` ``). Unlike the other items here this is a **strip-the-markup** action, not delete-the-whole-thing: drop the field blocks entirely (a `:param x:` that just repeats the name/type adds nothing per the item above; anything one genuinely says folds into a plain sentence), and downgrade ```` ``x`` ````/``:class:`X` `` to plain `x` in prose. Flag every reST construct in an added docstring, quoting it, with the de-marked-up rewrite as the suggestion.
- **Storytelling about how the code came to be**: "originally we tried X", "we used to do Y", "TODO: refactor later" (with no actionable ticket).
- **Implementation chatter**: describing which other functions the body calls, or how callers downstream will consume the output. Example: `# Set on both lines so the resulting OrderShipped rows (buyer side and seller side, both populated from these fields by the mapper) carry the promotion_id in their event_properties.` The caller cares about the contract (inputs, output, side effects, errors), not the mapper's internal choices — those will drift, and the comment will silently lie.
- **Section banners**: `# --- Helper functions ---` between groups of helper functions.
- **Type narrations in docstrings** when the annotation already covers it ("foo: int — the foo as an integer").
- **Redundant module docstrings** that just name what's in the module ("This module contains the Foo class.").
- **Multi-line rationale for a single-element set/list**: a 5-line block explaining why one field is ignored should be a per-field comment inside the data structure (`frozenset({"updated_at"})` becomes a `frozenset({"updated_at",  # rerun must not flag prior imports})`).
- **Narrating external API mechanics the code already exercises**: `# The endpoint pages at 50 rows by default; request a size comfortably above any customer's order count so a single page usually returns them all. Some customers exceed that in practice, so follow next_page...` above a pagination loop. The loop IS the statement that pagination must be followed; the default page size and the sizing rationale are trivia. Delete the whole block. This includes **API error behavior the guards already handle**: `# delete_object on a missing key is a silent no-op` above explicit missing/dir guards — the guards' existence already implies the API won't raise for you, and when the error contract is test-enforced, stripping a guard fails a named test that explains itself better than the comment. Delete.
- **Justifying a script's existence or audience in its module docstring**: "This script exists so <team> operators can run it themselves; it also serves as the executable record of ..." — who runs it and why it was written belong in the PR body/runbook, not the module. Same for "may not be merged" style notes. Delete.
- **Out-of-scope enumerations**: "X is deliberately absent — the split does not cover Y", "the EU region is out of scope". Scope decisions live in the ticket/PR body; in code they read as mystery trivia and drift when scope changes. The data structure's contents already show what's in scope. Delete.
- **Cross-file sibling narration**: "consumed by the export/config scripts", "not part of the export mapping — the export script handles those", "created so <other script> has somewhere to put X". Comments describing what OTHER files do with this data drift silently and force the reader to cross-reference. The import graph already expresses consumption. Delete.
- **Stating a count or shape the literal shows**: "(one per region)" above a 4-element tuple with one entry per region. Delete.
- **Re-teaching domain structure the reader already carries**: a comment that explains what an entity *is* — its parts, composition, or how it's assembled — at a site that merely uses it. `# An order books shipment lines alongside the payment lines; a shipment line moves the item itself, so its entity is its own sku_id` above a line-partitioning filter. A competent reader of the module already knows an order's line composition; narrating it at every partition site is storytelling about the domain, and it drifts when the model changes. Delete the structural narration. The domain fact does NOT justify the comment — see the next item for where it should live instead.
- **Re-teaching a general principle the reader already carries**: comments that state general engineering knowledge or platform conventions — `# staging data should mirror prod`, `# The OAuth token must come from the same environment as the API it calls`, `# The aiohttp session must be created inside the running event loop`. These are things any competent engineer on the platform already knows (or the runtime enforces loudly on its own). A comment earns its place only when the code *diverges* from the convention — then state the divergence and its trigger tersely (`# Staging calls the production geocoder: the sandbox returns fixed coordinates.`) without re-deriving why the convention exists. Delete the principle, keep only the divergence.
- **Precedent citations / unnecessary references to other files**: "(like the payments client)", "matches the billing/payments token-fetch precedent", "same pattern as <other integration>". A reference to another file or integration is only worth writing when the linkage must be *maintained* — when a change here requires a change there. A historical "we copied this shape from X" is storytelling: it drifts when X changes, sends the reader on a cross-file detour that teaches nothing, and implies a coupling that doesn't exist. Delete the citation; if the shared shape is a real constraint, encode it (shared helper, test) instead of naming the sibling. **This includes "source of truth" pointers to other functions/modules** — `— the shape catalog.products.sku_ensurer provisions` next to a `"USD"` currency constant. Naming the module that produces the convention does not rescue the reference: state the assumption plainly ("Assume all prices are in USD") and stop. Do not reference another function or module in a comment unless there is a really good reason — a maintained, bidirectional coupling that cannot be encoded; when in doubt, delete.
- **A comment standing in for a name (extract a predicate/helper instead)**: when the thing that's actually opaque is an *expression* — `if line.entity != line_sku_id(line)`, a bare arithmetic guard, a magic-number compare — the fix is to name it, not to annotate it. Extract a predicate or helper (a sibling to the module's existing accessors, e.g. `is_shipment_line(line)`), so the call site reads `if not is_shipment_line(line)` and the one durable fact lives *once*, at the definition, encoded rather than narrated. A multi-line comment explaining a one-line expression is almost always a missing name. Flag as DELETE + "extract predicate", and note it in Best Practices / DRY too — inline domain logic that belongs beside the module's other accessors is a DRY finding, not just a comment one.

- **Trailing period on a simple comment** — a single-line comment that is a fragment or one terse statement (`# Fallback path.`, `# created_at is the row's unique id.`) must not end with a period; strip it. Multi-sentence or multi-line explanatory comments keep normal sentence punctuation. (Flag as COMPACT with the period removed.)
- **A constraint the type-checker or linter already enforces** — a comment explaining why the code is written a certain way to satisfy the type checker or linter (`# Use the underlying field names, not the aliases, so the type checker resolves the constructor`) is redundant: violating it fails the check immediately with a clear message, so the comment guards nothing the tooling doesn't already say at the moment you'd break it. Delete it.
- **Design / architecture / grouping justification in code** — a comment explaining *why* code is structured or grouped a particular way (`# The billing poller hits a REST API, so it runs as its own service rather than with the batch-file sources`) is a design decision that belongs in the PR body or ticket, not the code. The structure itself (the group, key, or module) shows *what*; the *why* drifts and the reader can't act on it. Delete it.

**Content worth keeping (and what makes it worth keeping):**
- A hidden constraint or invariant the type system can't express.
- A workaround for a specific bug or external limitation (link the issue if there is one).
- Why an obvious approach was rejected (a "the alternative is wrong because" line).
- Pre/post conditions or side effects callers must respect.
- References to specs, RFCs, or external docs that explain the *why* of a design choice.

**Required shape for modal-behavior comments (feature flags, config switches, enabled/disabled modes):** a state table, not a narrative. One title line, then one bulleted block per state, one behavior per bullet, parentheticals for exceptions. Colon-chained prose describing flag states ("when enabled X; reads instead Y: because Z") is a COMPACT finding — restructure it into this shape:

```
New orders table

When enabled:
 - writes go to the v2 orders table
 - reads select both, preferring v2 when possible
   (not possible for guest orders)

When disabled:
 - writes go to the v1 orders table
 - reads select the v1 orders table
```

When a docstring is genuinely warranted, keep it to one or two sentences. Long docstrings are almost always a sign the function is doing too much or the explanation belongs in a design doc.

### 2. Terminology and Naming

Every term of art in added comments, docstrings, and identifiers must be real vocabulary, not coinage invented during development. The author can't see this themselves — invented terms look natural after hours in the design conversation — which is one reason this review runs in a fresh subagent.

**Required pass:** for each domain-sounding term introduced by the diff (hyphenated compounds, codename/letter labels, abbreviations, single-letter tags), classify it:
- **Established in the codebase** — grep for it outside the diff; if it appears in pre-existing code, it's fine.
- **Standard domain vocabulary** — a term a new engineer could look up (e.g. "refund", "idempotency key", "outbox").
- Otherwise it is **invented** — flag it and propose spelled-out phrasing (e.g. "null-pool" → "orders with no invoice id"; "topology B" → "billing address == shipping address with payer separate").

Red flags:
- Shorthand only meaningful to someone who was in the design conversation ("topology B/C/D", "null-pool", "event-pool", a bare "X" tag).
- Names or comments that describe the change rather than the code ("new defaults", "the new resolver", "older design", "legacy path") — the code has no history; the PR description does.
- Truncations that are ambiguous because the codebase has several unrelated concepts of the same shape (a bare "event id" / `event_id` where several kinds of event id exist): flag and spell out the specific one.

**Banned: "operator" / "operator-run"**: AI-slop phrasing, and doubly confusing because "operator" falsely implies a dedicated ops team. Say "manually run" / "run manually" or "engineer-run" / "an engineer runs" instead. Flag every instance in added comments, docstrings, PR bodies, and identifiers (pre-existing occurrences in untouched code are out of scope).

**No generic collection names — name the item and the key**: "group"/"groups" (and equally generic "items", "data", "key" as a bare loop variable) hide what a collection holds. Name what it's a group OF: a dict is `<items>_by_<key>` with both halves concrete (`orders_by_customer_and_region`, never `orders_by_group` — "it's like saying `items_by_key`"); a composite dict key is a NamedTuple whose class name states its fields (`_CustomerAndRegion`, not `_GroupKey`), and loop code destructures it (`for (customer, region), orders in ...`) instead of dereferencing `key.field`. Flag every "group"-family identifier and every `<x>_by_<y>` name where either half is generic. Same bar for near-miss names that under-describe their shape: a dict named like a list/set (`sku_keys` holding key→sku) is a finding — rename to say the mapping.

**Error messages use the code's own field vocabulary and never teach domain structure**: a validation/rejection message names the violated field using its code name ("the ship date {date}") and states the concrete fix — nothing else. Flag messages that re-derive the domain inside the string ("the express shipment, which leaves same-day on order_date {date}"): the reader needs which check failed and how to fix it, not why the date is what it is. If a term in the message doesn't correspond to a field or established vocabulary the reader can see, rename it.

### 3. Correctness

Look for actual behavioral bugs — cases where the code does the wrong thing or produces incorrect results:

- **Logic errors**: Conditions that are inverted, transformations that don't match intent, incorrect operator precedence, or off-by-one errors.
- **Silent failures**: Functions that silently produce wrong output when given unexpected input (e.g., `str.removeprefix` returns the original string unchanged when the prefix isn't present — if all callers assume the prefix exists, you get a wrong URL with no error). Swallowed exceptions or `None` returns that callers don't check.
- **Incorrect assumptions about data or APIs**: The code assumes something about data shape, API response format, or external system state that isn't guaranteed. When the assumption breaks, what happens — clean error, or wrong behavior?
- **Edge cases**: What happens with empty collections, null/None values, missing dict keys, duplicate entries, or boundary conditions? Does the code handle these correctly or produce wrong output?
- **Concurrency and ordering**: For async code or multi-step operations, are there race conditions, TOCTOU (check-then-act) issues, or incorrect assumptions about execution order?

Flag each bug with a `file:line` reference, explain the wrong behavior concretely, and suggest the fix.

### 4. Riskiness

Assess whether these changes are safe to deploy:
- **Backward compatibility**: Do any changes to function signatures, database schemas, API contracts, or serialised data formats risk breaking existing callers or stored data?
- **Rollout safety**: Can this be deployed incrementally, or does it require coordinated cutover? Scripts that write to production databases or external services are higher risk than additive library changes.
- **Data integrity**: If the change touches migrations, stored records, or external API calls, what happens to existing data? Is there a risk of silent corruption or double-writes?

Assign an overall risk rating: **Low / Medium / High**, and explain what specifically drives it.

### 5. Typing

Never suppress type errors (`# type: ignore`, `# pyre-fixme`, and the like) — always find the correct annotation instead. Look for:
- **Missing annotations**: Any unannotated parameters or return types?
- **Overly complex annotations**: Long `tuple[A, B, C, D, ...]` that would read better as a `NamedTuple`. Many `str` parameters that would be clearer as `NewType` aliases (e.g. `CustomerName = NewType("CustomerName", str)`).
- **Imprecise types**: `Any`, `object`, or overly broad types where a narrower type would document intent better.
- **Annotation/reality mismatches**: Does the annotation match what the function actually accepts and returns?

### 6. Exception Precision

Exception types are part of the public contract of a function. Review both what is raised and what is caught:

- **Overly generic raises**: `ValueError`, `RuntimeError`, and `Exception` obscure intent. Flag any case where a more descriptive domain exception would make the error's meaning self-evident to callers (e.g. `InvalidTransitionError`, `ConcurrentModificationError`). Generic built-ins are acceptable only for truly general-purpose errors (e.g. `TypeError` for wrong argument type at the boundary of a utility function).
- **Overly broad catches**: `except Exception`, `except (ValueError, SomeOtherError)` — verify that every type in the tuple can actually be raised by the code inside the `try` block. A catch clause that includes exception types the code never raises is dead code and misleads readers.
- **HTTP status code correctness**: When exceptions map to HTTP responses, verify the code matches the error's semantics:
  - 409 Conflict — two requests are in conflict with each other (concurrent writes, optimistic locking)
  - 422 Unprocessable Entity — the request itself is semantically invalid given the resource's current state (invalid state-machine transition, operation disallowed in terminal state)
  - 400 Bad Request — the request is malformed or violates a documented constraint
  - Don't use 409 for validation errors or 422 for concurrency conflicts.
- **Exception hierarchy**: If multiple domain exceptions share a common supertype, consider whether callers should catch the supertype or specific subtypes. Flag cases where callers catch a broad type when they should be handling subtypes differently.

### 7. Architecture & Code Quality

Assess whether the overall design of new or modified code makes sense. Apply the SOLID principles from the `solid` skill:
- **Single responsibility**: Do classes and functions have a clear, singular purpose? Flag god classes or methods that do too many things.
- **Appropriate abstractions**: Is the code structured at the right level? Are there missing abstractions (repeated patterns that should be unified) or premature abstractions (over-engineered for one use case)?
- **Coupling and cohesion**: Is the code appropriately decoupled? Flag tight dependencies between unrelated modules or components that know too much about each other's internals.
- **Is this the best approach?** Given the existing codebase patterns and the problem being solved, is the chosen design the right one? Note alternatives worth considering and the tradeoffs.

**Do not suggest rewrites for their own sake.** Focus on issues that would meaningfully affect maintainability, extensibility, or correctness going forward.

- **Validators: one violated check → one independent error; no message-precedence logic**: flag error-collection code that decides which of several applicable messages "wins" or suppresses one check's error because another check also fired — the `continue`-chain gymnastics are harder to follow than just emitting both errors. Each check gets its own error stating its own field and fix; if a remedy could mislead when errors combine, fix the message wording ("... or backdate updated_at"), never the control flow. A comment narrating message precedence ("its message wins", "suppressed when X is also violated") is the tell. This also applies when a review bot suggests adding suppression — push back with this rule.
- **Review every default argument value; convenience is not a justification**: for each parameter added or changed in the diff that carries a default, demand a positive justification. The ONLY acceptable one is rarely-tweaked configuration — a knob virtually every caller wants at the same value and only unusual sites override. Backward compatibility with existing call sites and shrinking the diff are NOT justifications: a default that exists so old call sites compile unchanged lets a production call site silently omit an argument it should be making an explicit choice about (e.g. `stale_order_cutoff: datetime | None = None` where every production caller must derive the cutoff from config + a CLI flag — defaulting to None invites a silent safety-check bypass at future call sites). Tests having to pass `param=None` explicitly everywhere is a small price. Verdict for an unjustified default: remove it and update the call sites.

### 8. Best Practices / DRY

Search the codebase for similar patterns to what's been added. Consider:
- Is there an existing utility that does the same thing, which the new code duplicates?
- Is a pattern repeated across the diff that suggests an abstraction would help?
- Do neighboring files establish conventions (naming, error handling, logging) that the new code diverges from without a clear reason?
- **Redundant named parameters**: Flag any `foo(bar=bar)` where the kwarg name mirrors the variable name
- **`dict()` constructors**: Flag any `dict(...)` used to construct a literal — always `{}` instead; `dict()` is slower and never clearer. Named params are only justified when passing a literal (e.g. `retries=3`) or when the call would otherwise be ambiguous.
- **`setdefault` where `defaultdict` fits**: flag `d.setdefault(k, <mutable default>)` accumulation loops — build with `collections.defaultdict(list|set|dict)` instead. `setdefault` constructs the default argument on every call even when the key exists, and reads worse. When the dict is returned or otherwise escapes, convert at the boundary (`return dict(grouped)`) so callers don't inherit defaultdict's insert-on-read behavior. Legitimate `setdefault` uses — don't flag these: (a) a one-off insert-if-absent on a plain dict you didn't build and won't convert; (b) per-key heterogeneous defaults (defaultdict has one factory); (c) insert-and-use in one expression on a dict whose type must stay plain `dict` end to end (e.g. it's read with `d[k]` by code that must KeyError on missing keys).

**Do not suggest automatic refactors.** Note the opportunity and explain the tradeoff — over-applying DRY can create tight coupling that makes future changes harder.

### 9. Test Coverage

Review both quantity and quality of tests:
- **Coverage**: Do the tests exercise the meaningful behaviors of the changed code? Flag logic paths (especially error paths, edge cases, and branching conditions) that have no test coverage.
- **Test value**: For each test, ask whether it's actually testing something useful. A test that only asserts on mock call counts without verifying real behavior can pass even when the implementation is broken. These are worth flagging.
- **Absence-pin tests — flag, and never recommend adding one**: a test asserting behavior is *independent* of a field or input (e.g. "applies with coupon_code=None" when nothing in the path reads coupon_code) pins a non-dependency, not a behavior. Like a mirror test, it can only fail when someone deliberately re-introduces the dependency — and that change would delete the test alongside it — so it catches no realistic regression. The meaningful pin is the positive assertion on what the code DOES use (e.g. ship date equals order_date, with fixture values that discriminate). When reviewing coverage of a removed dependency, check the positive assertions exist; do not ask for an absence test.
- **State vs. mocks**: Prefer tests that set up concrete, reusable state (e.g. a shared fixture or `InMemoryFoo`) over single-use mocked objects. A test built on well-defined state is easier to read, easier to extend, and more likely to catch real regressions. Flag tests where heavy mocking obscures what's actually being verified.
- **Missing edge cases**: Are there inputs or conditions the tests don't cover that a reviewer might reasonably ask about?
- **Parametrization**: Look for groups of tests that share the same structure but differ only in input/expected-output values — these are candidates for `@pytest.mark.parametrize`. Flag them when collapsing would meaningfully reduce duplication without losing per-case clarity. Conversely, flag tests that *are* parametrized but probably shouldn't be: if the cases exercise meaningfully different code paths, separate named tests are clearer and easier to debug when one fails. The bar is whether a future reader can understand the failing case from the parametrize ID alone.

### 10. Module Layout (skip under /pr-review)

**Scope:** house style for your own branches. When this review runs inside `/pr-review` (a colleague's PR), skip this area entirely and write "Skipped (pr-review)." Apply it to new modules and modules the diff substantially reworks — don't flag layout on files the diff barely touches.

Procedural modules read in newspaper order — the public entry points are the headline, the machinery follows:

1. Module docstring, imports, constants.
2. Public result types — only because signature annotations evaluate at def time and need them.
3. Public entry-point functions.
4. Private helpers, each near its callers (a private type used only in one helper's signature sits just above that helper).
5. Large config literals / data tables as a bottom appendix.

Python only forces ordering at def time (signature annotations, decorators, base classes, module-level executed code); body references resolve at call time, so helpers and config dicts can — and should — live below the functions that use them.

**Flag:** a wall of NamedTuples/dataclasses and private helpers before the first public function (the reader has to wade through types and internals to find what the module does). **Exempt:** data-model modules (`models.py`, schema/type modules) where the types are the point, and files following an established local layout — consistency within a package outranks the rule.

### 11. PR Body (only if a PR exists)

Re-read the open PR's body (`gh pr view --json body`) and check it against two things:

- **Conciseness.** Each template section should be as short as it can be while still letting a reviewer replicate the work without guessing. Flag padding, restated diff, hedging, and prose that narrates the obvious. The bar is the same as for comments in §1: if removing a sentence wouldn't cost the reviewer anything, cut it.
- **Structural before/after narrated in prose or bullets.** When the body describes re-parenting, re-referencing, or topology changes as sentences ("X gains the Y reference, and two relations are created — A → B…"), flag it: that belongs in a fenced diagram — one tree per stage, identifiers spelled out entirely (no `…` truncation), `<- NEW` / `(end-dated)` annotations on changed lines. Bullets are for independent facts, not structure.
- **References to uncommitted files.** Flag every reference to a file that is not committed and pushed — in particular temporary local spec files (e.g. paths under `tmp/`, `tmp/docs/specs/`, or any absolute local path). Reviewers can't open these, so the link is confusing and useless. The fix is to describe the design inline, or link a committed file / ticket / published doc instead. To check, list the paths the body references and confirm each is tracked: `git ls-files --error-unmatch <path>` (or that it's a URL, not a local path).

Quote the offending text with a one-line note for each finding.

## Output Format

Use these exact section headers. If a section has no findings, write "Nothing flagged." — completeness signals the area was checked, not skipped.

```
## Comments and Docstrings
<total item count from the workflow-step-5 inventory>

**N. file.py:LINE [comment|docstring] — KEEP | DELETE | COMPACT | RESTRUCTURE**
```
<the item's verbatim text, exactly as the inventory printed it>
```
<one-line reason naming the layout triggers checked; the final post-round-3 suggested text, laid out one idea per line, for COMPACT and RESTRUCTURE>

  (one entry per inventory item — every added comment/docstring block, keeps
  included; the fenced verbatim quote is mandatory on every entry)
<2-3 sentence whole-PR verbosity assessment>

## Terminology and Naming
- file.py:N — <finding>

## Correctness
- file.py:N — <finding>

## Riskiness
- file.py:N — <finding>
**Overall risk: Low / Medium / High** — <one-sentence explanation>

## Typing
- file.py:N — <finding>

## Exception Precision
- file.py:N — <finding>

## Architecture & Code Quality
- file.py:N — <finding>

## Best Practices / DRY
- file.py:N — <finding>

## Test Coverage
- file.py:N — <finding>

## Parametrization
- file.py:N — <finding>

## Module Layout
- file.py — <finding> (or "Skipped (pr-review).")

## PR Body
- <finding> (or "No PR open yet — skipped.")

## Risk Summary
<2–3 sentences: biggest concern, and what a reviewer should pay closest attention to>
```

## Local overrides

If `~/.claude/skills-work/code-review-checklist.md` exists, read it and apply it as additional rules for this skill; where it conflicts with the text above, it wins.
