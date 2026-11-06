---
name: reviewing-code
description: Use when reviewing generated or written code for quality — comments, dead code, test value, naming, and type precision
---

# Reviewing Code

## Overview

Surgical review: flag only what's wrong, don't refactor beyond the issue.

## Comments

Remove unless the logic is non-obvious. Comments explain **why**, never **what**.

**Remove:**
- Narrating what the code does (`# Pre-filter before hitting the API`)
- Restating the type annotation (`# (user_id, display_name) — ...`)
- Obvious docstring content that mirrors the function signature

**Keep:**
- Invariants the reader would otherwise have to deduce (`# The fetcher already filters these out — this satisfies the type checker's narrowing`)
- Non-obvious parameter meanings (`# Disable the staleness check so backfills don't raise StaleRecordError`)
- Data groupings in config files (`# Group A — stay on the legacy region`)

## Dead Code

Remove any code that is already covered by a broader check.

Common examples:
- Explicit membership check for something an earlier predicate already catches (e.g., `if role == ADMIN` when `is_privileged(role)` already returns True for that value)
- Imports of names no longer referenced after a refactor
- `str()` calls on values that are already `str` subtypes (`NewType("UserName", str)`)

## Tests

Each test must add **distinct coverage**. Ask: if I delete this test, does any real behavior go untested?

**Remove when:**
- The function under test is fully mocked, so the test only verifies the mock was called (which is already covered by another test with the same mock)
- The test duplicates a fixture or helper already in `conftest.py` rather than importing it

**Keep when:**
- The test exercises a real code path not covered elsewhere
- The test captures a subtle exclusion rule (wrong namespace, reserved prefix, exception list)

## Naming

File and module names must reflect their content semantically.

- `exceptions.py` containing no exceptions → `migration_config.py`
- Generic `utils.py` → name for what it actually holds

## Type Precision

Use the most specific type available, not a structural equivalent.

- `OrderId(uuid4())` not `uuid4()` when the field expects `OrderId`
- `UserId` not `UUID` in a mapping keyed by user IDs
- `CustomerName` not `str` when assigning to a typed field

## Shared Test Utilities

Helpers used by more than one test file belong in the nearest `conftest.py`. Never duplicate them inline — future changes will only get applied to one copy.

## Logs

Every log line must be actionable. Include relevant IDs, amounts, state. Cut anything that will always be ignored.

```python
# ❌ noise
logger.info("Processing customer")

# ✅ actionable
logger.info("Sent invoices", customer_id=customer_id, invoice_count=len(invoices))
```
