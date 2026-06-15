# date_not_future

## What this rule does

Checks that populated date values are not later than the pipeline run date.

## When to use it

Use for birth dates, transaction dates, application dates, or any date that should not be in the future.

## Rule applies to

**Data applicability:** Date or timestamp profiled columns that should never be later than the pipeline run date.

**Example column(s) on this page:** `birth_date`

## Parameters

```yaml
rule_type: date_not_future
columns: ["birth_date"]
severity: error
```

## Example rule definition

```yaml
rule_id: date_not_future_example
rule_type: date_not_future
columns: ["birth_date"]
severity: error
description: "Example approved metadata rule for date_not_future."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL_RULES`, including `rule_parameters_json`.

## Sample input data

| person_id | birth_date |
| --- | --- |
| P001 | 1998-04-12 |
| P002 | 2026-06-10 |
| P003 | 2026-12-01 |
| P004 | null |

## Rows that pass

| person_id | birth_date | Why |
| --- | --- | --- |
| P001 | 1998-04-12 | Before run date. |
| P002 | 2026-06-10 | Same as example run date. |
| P004 | null | Null does not fail this rule by itself. |

## Rows that fail

| person_id | birth_date | Why |
| --- | --- | --- |
| P003 | 2026-12-01 | Later than the example run date. |

## Notes

- Examples assume a run date of 2026-06-10 for illustration.
- Add `not_null` if the date must be present.

## Related rules

- [`date_between`](date-between.md)
- [`freshness`](freshness.md)
- [`max_age_days`](max-age-days.md)
