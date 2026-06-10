# less_than

## What this rule does

Checks that populated values are strictly less than a threshold.

## When to use it

Use for ratios or risk values where the boundary itself is not allowed.

## Rule applies to

**Data applicability:** Numeric, date, or otherwise comparable profiled columns that must be strictly below a configured threshold.

**Example column(s) on this page:** `risk_score`

## Parameters

```yaml
rule_type: less_than
columns: ["risk_score"]
value: 1
severity: warning
```

## Example rule definition

```yaml
rule_id: less_than_example
rule_type: less_than
columns: ["risk_score"]
value: 1
severity: warning
description: "Example approved metadata rule for less_than."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| case_id | risk_score |
| --- | --- |
| R001 | 0.20 |
| R002 | 0.99 |
| R003 | 1.00 |
| R004 | 1.20 |

## Rows that pass

| case_id | risk_score | Why |
| --- | --- | --- |
| R001 | 0.20 | Less than 1. |
| R002 | 0.99 | Less than 1. |

## Rows that fail

| case_id | risk_score | Why |
| --- | --- | --- |
| R003 | 1.00 | Equal to threshold, not less. |
| R004 | 1.20 | Above threshold. |

## Notes

- Null values do not fail this rule by themselves.
- Use `less_than_or_equal` when the threshold value is valid.

## Related rules

- [`less_than_or_equal`](less-than-or-equal.md)
- [`between`](between.md)
