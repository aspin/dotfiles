---
name: doc-review
description: Manually invoked review checklist for documents drafted on your behalf — Confluence pages, design docs, specs, runbooks, test-results pages. Use before publishing a new document or a substantial update to one, or when invoked as /doc-review. Bias hard toward compactness. Flags over-explanation of concepts the audience already knows, invented entities/terminology, inference presented as fact, unmarked assumptions, incomplete worked examples, change-narration mixed into state description, and test-results pages that pack runs into tables instead of per-run sections with logs.
---

# Doc Review

Structured review for documents drafted for the user. The recurring failure mode is verbosity: documents explain too much, invent vocabulary, and state inferences as facts. Run this before publishing a new document or a substantial update.

## Execution: always in a separate subagent

Same rationale as code-review-checklist: the drafting conversation is biased — terms and "facts" invented during the session look natural to the author. Dispatch the review to a fresh subagent with the document content (or page ID and how to fetch it), the sources it was built from, and this skill's full instructions. Present the report as-is.

## Review Areas

### 1. Compactness (the primary check)

The audience is the team that designed and operates the system. They own the domain vocabulary; the document does not need to teach it back to them.

- **Delete explanations of concepts the audience already carries**: what a record type is for, how a platform mechanism works, general engineering principles. Explanation is warranted only for material this document introduces.
- **Two-question test per paragraph** (adapted from code-review-checklist §1): (1) could the reader reconstruct this from the tables, examples, and context in view? (2) is it grounded in something durable, or is it narration that will drift as the design changes? Failing either → delete, don't reword.
- **Iterative compaction, 3 rounds per surviving paragraph**: delete the reconstructible; then drop qualifiers, examples, and restated context; then ask once more whether the remainder can shrink or go entirely.
- **One idea per sentence.** No semicolon chains. Procedural or enumerable content becomes bullets.
- **Tables carry the content.** Prose around a table adds only what the table cannot say. A sentence that restates a table row is a defect.
- **No meta-narration**: how the document came to be, what was discussed, what changed since the last version. Version history and the ticket carry that.

### 1b. Runbook / as-built page compaction

- **Runbook holds only steps still to be run; the execution log holds what happened.** A completed one-time step (a merged code migration, a dev-only fixup) collapses to a log row. Dev incidents and their lessons live once, in the log — not restated as runbook warnings or risk bullets.
- **Never duplicate what the tool says about itself.** CLI flag semantics belong in `--help`; error/refusal behavior belongs in the tool's own output (dry-run-first discipline surfaces it). The runbook shows bare command lines plus at most one line of purpose.
- **No inventories that rot**: PR lists, per-module artifact tables, identifier-variant enumerations. The ticket and the code are the index. An artifact table lists runnable entry points only, one line each — never internal helper modules.
- **Settled decisions lose their rationale narration.** State the as-built decision; delete "why not X" paragraphs and design-debate framing once shipped. (For as-built docs this overrides the keep-rejected-alternatives instinct — the ticket and page history carry the debate.)
- **Environment-scoped artifacts compress**: a dev-only workaround is one "dev only" clause plus its log row, not a runbook subsection.
- **Risks are live, forward-looking, and specific.** An incident already recorded in the log is not a risk; a general engineering truth is not a risk.
- **Guardrail — compaction must not delete future-run protections.** Before endorsing a deletion, ask: does the engineer executing the *next* environment's run need this at the keyboard? Step-ordering constraints, pre-flight data audits, and soak/monitoring instructions keep one line each even in the tersest revision. Open questions are moved to tickets, never silently dropped.

### 1c. Test-results / evidence pages

- **Intro is bare links.** Ticket and PR as two bullets. No branch heads,
  commit shas, environment narration, or timezone notes up top — the run
  sections carry their own context.
- **One section per run/scenario, never a mega table.** A results table
  packing ten runs into one column of prose is a defect. Each run gets its
  own heading.
- **Each run section leads with two small tables: the state under test.**
  One table for the record(s)/entity under test (id, current version, key
  fields, state), one for the data the run acts on — scoped to only what
  THIS run demonstrates, not every record in the environment. The
  state-under-test comes before the result.
- **Then a one-line "Demonstrates:" statement, then findings as a bullet
  list.** Never a results paragraph. Each finding is one bullet.
- **Report what the errors were, never how many.** "8 review errors" /
  counting error categories is useless — say what each relevant error
  actually was (which record, which classification, why). Likewise do not
  pile up raw event tallies ("36 orders + 24 invoices + 12 shipments"); say
  what happened ("all of the batch's events were withheld together").
- **Explain a non-obvious outcome in one plain sentence of cause.** Not a
  version UUID, not "see run 4" alone. E.g. "Order `A-17` includes a
  shipment, shipments cannot be created with a past ship date, and an order
  saves all its line items or none, so all its events were withheld." State
  the mechanism.
- **Each run section includes the service's runtime logs**, in a
  collapsible block, as complete as captured. Trim only mechanical noise
  (repeated context kwargs, ANSI) and collapse mass-repeated lines to
  samples plus a count (a run of per-date empty polling passes
  collapses to one "(N passes returned 0 events)" line; a long ambient
  kwarg list collapses to its first element plus "...(N more)"). During
  testing, capture each run's log to its own file so nothing is lost to
  overwrites — the user will ask "do we not have logs for this?", and a
  "full log not retained" caveat is a finding against the testing session.
- **Reproduce a missing demonstration rather than hand-wave it.** A
  deterministic run (an abort, a validation failure) can just be re-run to
  capture its real log; a state-dependent one (a revision correction) can
  be reproduced by advancing the fixture one more step. Prefer real
  captured evidence over a prose summary of what a lost log said.
- **Cut ambient environment artifacts** that aren't what the page
  demonstrates. Shared-dev noise (unrelated records the run also touched)
  gets at most one "not part of this test — see the log" bullet, never its
  own findings. When something looks incidental, the user will ask "is this
  relevant?" — answer by cutting it or naming it as ambient.
- **No fixture-creation mechanics.** State what test data exists (the
  records, their fields); delete how it was seeded (which API, which
  client, idempotency workarounds). Same for any implementation aside —
  if it explains the harness rather than the result, cut it.
- **One fact per cell/bullet.** Don't fold several facts into a
  parenthetical inside a table cell (quantities, amounts, caveats); split
  them into separate bullets or rows.
- **All identifiers and dates in code style** (backticks): UUIDs, record
  ids, record names, dates — in prose and tables alike.
- **State simple facts plainly.** No compressed asides like "(same date
  fixes)" that force the reader to reconstruct history; one plain sentence.
- **No "state left behind" or "follow-ups" sections.** Tickets carry
  follow-ups; the environment's state is discoverable. If a leftover
  genuinely needs action, it is a ticket, not a page section.
- **Identify entities by name, never a bare id.** Every table row and
  reference names the thing (`Acme Corp annual invoice`), with the UUID as
  a secondary column — a UUID alone is unreadable. This applies to the lead
  state tables and to any "what's under test" listing.
- **Logs render as a two-column table: level lozenge + message. No
  timestamp column.** Cut every log timestamp — row order carries
  sequence. Map level to a status lozenge (info→neutral, warning→yellow,
  error→red) and bold the error/warning and key outcome rows.
- **A run that wrote records gets its verification query in its own section**, not in
  a trailing "how to query" dump. If records were written, the query to find
  them lives beside that run; reuse across runs is a one-line pointer, not a
  repeated block. Delete any trailing query section once distributed.
- **Name test data plainly — never "seed"/"seeded".** Say what the data is
  (the records under test, their fields); the harness verb is noise.
- **Delete verification-only prose a query already proves.** An
  "rows verified via the API" paragraph is
  restating what the per-run writes and the negative-check query show —
  cut it.

### 2. Invented entities and terminology

- Every record type, identifier, system, and term of art must already exist — in the codebase, the system of record, or prior docs — or be standard domain vocabulary a new engineer could look up. Verify (grep / the system of record's API / source docs) before treating a name as real.
- **Do not mint new records, categories, or identifiers to make a flow feel complete.** If an existing construct plausibly covers the role, use it. If something genuinely new seems required, present it once as an explicit proposal with a placeholder marker and a matching open item — never as established fact.

### 3. Facts vs. inferences

- Every claim about data flows, sources, timing, and ownership must trace to a confirmed source: an owner's statement, code, or an authoritative document. Domain-convention reasoning ("this is how this kind of integration usually works") is an inference, not a fact.
- Meeting notes can be stale or superseded. Prefer the most recent statement from the owner; when sources conflict, ask instead of picking.
- Every unconfirmed assertion gets an inline "(to be confirmed)" and a matching entry in the open items list. Inference written in the same voice as fact is a defect even when it turns out correct.

### 4. Adaptation integrity (documents derived from another document)

- **Separate functional differences from error fixes.** Corrections of mistakes or out-of-date content in the source document must not be presented as differences of the new state. The "differences" list contains only genuine behavioral/structural differences.
- Do not clone the source's errors for the sake of being 1:1 — fix them, and give the author the list of fixes to confirm.

### 5. Internal consistency and completeness

- Worked examples must balance: every side of each flow is shown (or the omission is explicitly noted), totals reconcile from section to section, and quantities/prices/signs are consistent across tables.
- The open items list exists, and matches the inline "(to be confirmed)" markers one-to-one.
- Links resolve: source threads, tickets, and referenced pages are linked, not described.

## Applying feedback rounds

Feedback usually arrives as several bullets, and page edits are applied by rewriting the whole body — which silently drops items. For every feedback round:

1. Enumerate each bullet as its own checklist item before editing (a todo list or an explicit list).
2. After the update, verify each item against the body actually sent — item by item, not from memory.
3. Report the per-item outcome back, including anything deliberately not done.

## Output Format

```
## Compactness
**N. <section> — DELETE | COMPACT**
> <verbatim quoted text>
<one-line reason; final suggested text for COMPACT>

<2-3 sentence whole-document verbosity assessment: what fraction of the prose
should go, and the worst-offending sections>

## Invented entities and terminology
- <finding with quoted term and proposed replacement>

## Facts vs. inferences
- <claim> — <source it traces to, or "unconfirmed: needs inline marker + open item">

## Adaptation integrity
- <finding>

## Consistency and completeness
- <finding>

## Summary
<2-3 sentences: is the document publishable, and what must change first>
```

If a section has no findings, write "Nothing flagged."

## Local overrides

If `~/.agents/skills-work/doc-review.md` exists, read it and apply it as additional rules for this skill; where it conflicts with the text above, it wins.
