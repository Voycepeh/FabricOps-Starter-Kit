# freshness

## What this rule does

Checks that a populated date or timestamp is not older than the configured number of days from the run date.

## When to use it

Use for operational tables where stale data should block or warn before reporting.

## Rule applies to

**Data applicability:** Date or timestamp profiled columns that represent update, ingest, event, or snapshot recency and should stay within a maximum age from the run date.

**Example column(s) on this page:** `updated_at`

## Parameters

```yaml
rule_type: freshness
columns: ["updated_at"]
max_age_days: 2
severity: error
```

## Example rule definition

```yaml
rule_id: freshness_example
rule_type: freshness
columns: ["updated_at"]
max_age_days: 2
severity: error
description: "Example approved metadata rule for freshness."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL_RULES`, including `rule_parameters_json`.

## Sample input data

| record_id | updated_at |
| --- | --- |
| R001 | 2026-06-10 |
| R002 | 2026-06-09 |
| R003 | 2026-06-08 |
| R004 | 2026-06-01 |

## Rows that pass

| record_id | updated_at | Why |
| --- | --- | --- |
| R001 | 2026-06-10 | Same as example run date. |
| R002 | 2026-06-09 | Within 2 days. |
| R003 | 2026-06-08 | At the 2-day threshold. |

## Rows that fail

| record_id | updated_at | Why |
| --- | --- | --- |
| R004 | 2026-06-01 | Older than 2 days. |

## Notes

- Examples assume a run date of 2026-06-10 for illustration.
- `freshness` and `max_age_days` share the same age-threshold behavior.

## Related rules

- [`max_age_days`](max-age-days.md)
- [`date_not_future`](date-not-future.md)
- [`date_between`](date-between.md)
