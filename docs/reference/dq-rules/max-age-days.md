# max_age_days

## What this rule does

Checks that a populated snapshot or business date is not older than the configured number of days from the run date.

## When to use it

Use for snapshot tables, extracts, or SLA checks where maximum age is the clearest language.

## Rule applies to

**Data applicability:** Date or timestamp profiled columns that represent snapshot, extract, update, or business recency and should not be older than a configured number of days from the run date.

**Example column(s) on this page:** `snapshot_date`

## Parameters

```yaml
rule_type: max_age_days
columns: ["snapshot_date"]
max_age_days: 1
severity: warning
```

## Example rule definition

```yaml
rule_id: max_age_days_example
rule_type: max_age_days
columns: ["snapshot_date"]
max_age_days: 1
severity: warning
description: "Example approved metadata rule for max_age_days."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| snapshot_id | snapshot_date |
| --- | --- |
| SNP001 | 2026-06-10 |
| SNP002 | 2026-06-09 |
| SNP003 | 2026-06-08 |
| SNP004 | null |

## Rows that pass

| snapshot_id | snapshot_date | Why |
| --- | --- | --- |
| SNP001 | 2026-06-10 | Same as example run date. |
| SNP002 | 2026-06-09 | At the 1-day threshold. |
| SNP004 | null | Null does not fail this rule by itself. |

## Rows that fail

| snapshot_id | snapshot_date | Why |
| --- | --- | --- |
| SNP003 | 2026-06-08 | Older than 1 day. |

## Notes

- Examples assume a run date of 2026-06-10 for illustration.
- Add `not_null` if a snapshot date is mandatory.

## Related rules

- [`freshness`](freshness.md)
- [`date_not_future`](date-not-future.md)
