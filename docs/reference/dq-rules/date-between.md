# date_between

## What this rule does

Checks that populated dates stay inside an approved date range.

## When to use it

Use for event windows, supported history ranges, academic terms, or operational reporting periods.

## Rule applies to

**Data applicability:** Date or timestamp profiled columns where catalogue min/max evidence should stay inside an approved business date window.

**Example column(s) on this page:** `event_date`

## Parameters

```yaml
rule_type: date_between
columns: ["event_date"]
min_value: "2026-01-01"
max_value: "2026-12-31"
severity: error
```

## Example rule definition

```yaml
rule_id: date_between_example
rule_type: date_between
columns: ["event_date"]
min_value: "2026-01-01"
max_value: "2026-12-31"
severity: error
description: "Example approved metadata rule for date_between."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL_RULES`, including `rule_parameters_json`.

## Sample input data

| event_id | event_date |
| --- | --- |
| E001 | 2026-01-15 |
| E002 | 2025-12-31 |
| E003 | 2026-12-31 |
| E004 | 2027-01-01 |

## Rows that pass

| event_id | event_date | Why |
| --- | --- | --- |
| E001 | 2026-01-15 | Inside range. |
| E003 | 2026-12-31 | On inclusive upper bound. |

## Rows that fail

| event_id | event_date | Why |
| --- | --- | --- |
| E002 | 2025-12-31 | Before minimum. |
| E004 | 2027-01-01 | After maximum. |

## Notes

- You may provide only `min_value` or only `max_value` for one-sided date boundaries.
- Null values do not fail this rule by themselves.

## Related rules

- [`date_not_future`](date-not-future.md)
- [`between`](between.md)
- [`freshness`](freshness.md)
