# greater_than

## What this rule does

Checks that populated values are strictly greater than a threshold.

## When to use it

Use when zero or the threshold itself is invalid, such as positive amount checks.

## Rule applies to

**Data applicability:** Numeric, date, or otherwise comparable profiled columns that must be strictly above a configured threshold.

**Example column(s) on this page:** `amount`

## Parameters

```yaml
rule_type: greater_than
columns: ["amount"]
value: 0
severity: error
```

## Example rule definition

```yaml
rule_id: greater_than_example
rule_type: greater_than
columns: ["amount"]
value: 0
severity: error
description: "Example approved metadata rule for greater_than."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| txn_id | amount |
| --- | --- |
| T001 | 25.50 |
| T002 | 0 |
| T003 | -4.00 |
| T004 | 8.75 |

## Rows that pass

| txn_id | amount | Why |
| --- | --- | --- |
| T001 | 25.50 | Greater than 0. |
| T004 | 8.75 | Greater than 0. |

## Rows that fail

| txn_id | amount | Why |
| --- | --- | --- |
| T002 | 0 | Equal to threshold, not greater. |
| T003 | -4.00 | Below threshold. |

## Notes

- Null values do not fail this rule by themselves.
- Use `greater_than_or_equal` when the threshold value is valid.

## Related rules

- [`greater_than_or_equal`](greater-than-or-equal.md)
- [`between`](between.md)
