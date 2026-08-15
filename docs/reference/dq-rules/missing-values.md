# missing_values

## What this rule does

Checks that the overall null percentage for one column stays below a configured maximum. When the table-level rate is too high, null rows are tagged as failures.

## When to use it

Use when a small amount of missing data is acceptable but a spike should be visible or blocking.

## Rule applies to

**Data applicability:** Any profiled column where some missing values are acceptable, but the catalogue null percentage must stay below an approved threshold.

**Example column(s) on this page:** `email`

## Parameters

```yaml
rule_type: missing_values
columns: ["email"]
maximum_null_percent: 25
severity: warning
```

## Example rule definition

```yaml
rule_id: missing_values_example
rule_type: missing_values
columns: ["email"]
maximum_null_percent: 25
severity: warning
description: "Example approved metadata rule for missing_values."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL`, including `rule_parameters_json`.

## Sample input data

| customer_id | email |
| --- | --- |
| C001 | amy@example.com |
| C002 | null |
| C003 | ben@example.com |
| C004 | null |

## Rows that pass

| customer_id | email | Why |
| --- | --- | --- |
| C001 | amy@example.com | Non-null value. |
| C003 | ben@example.com | Non-null value. |

## Rows that fail

| customer_id | email | Why |
| --- | --- | --- |
| C002 | null | Overall null rate is 50%, above 25%. |
| C004 | null | Overall null rate is 50%, above 25%. |

## Notes

- Blank strings are not counted as nulls. Pair with `blank_text` if blanks must fail.
- If the overall null rate is within threshold, no row fails this rule.

## Related rules

- [`missing_values`](missing-values.md)
- [`blank_text`](blank-text.md)
