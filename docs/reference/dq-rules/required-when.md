# required_when

## What this rule does

Checks that selected columns are present and non-blank when a condition is true.

## When to use it

Use for conditional mandatory fields such as approved date for approved records or cancellation reason for cancelled records.

## Rule applies to

**Data applicability:** Profiled columns that are conditionally mandatory when a Spark SQL condition over the same row is true.

**Example column(s) on this page:** `approved_date`

## Parameters

```yaml
rule_type: required_when
columns: ["approved_date"]
condition: "status = 'Approved'"
severity: error
```

## Example rule definition

```yaml
rule_id: required_when_example
rule_type: required_when
columns: ["approved_date"]
condition: "status = 'Approved'"
severity: error
description: "Example approved metadata rule for required_when."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| request_id | status | approved_date |
| --- | --- | --- |
| R001 | Approved | 2026-05-01 |
| R002 | Draft | null |
| R003 | Approved | null |
| R004 | Approved |     |

## Rows that pass

| request_id | status | approved_date | Why |
| --- | --- | --- | --- |
| R001 | Approved | 2026-05-01 | Condition true and value present. |
| R002 | Draft | null | Condition false, so field is not required. |

## Rows that fail

| request_id | status | approved_date | Why |
| --- | --- | --- | --- |
| R003 | Approved | null | Condition true and value is null. |
| R004 | Approved | (spaces) | Condition true and value is blank. |

## Notes

- The condition is expressed using Spark SQL syntax.
- For unconditional mandatory fields, use `not_null` or `non_empty_string`.

## Related rules

- [`value_when`](value-when.md)
- [`not_null`](not-null.md)
- [`non_empty_string`](non-empty-string.md)
