# null_rate_below

## What this rule does

Checks that the overall null percentage for one column stays below a configured maximum. When the table-level rate is too high, null rows are tagged as failures.

## When to use it

Use when a small amount of missing data is acceptable but a spike should be visible or blocking.

## Rule applies to

`email`

## Parameters

```yaml
rule_type: null_rate_below
columns: ["email"]
max_null_percent: 25
severity: warning
```

## Example rule definition

```yaml
rule_id: null_rate_below_example
rule_type: null_rate_below
columns: ["email"]
max_null_percent: 25
severity: warning
description: "Example approved metadata rule for null_rate_below."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

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

- Blank strings are not counted as nulls. Pair with `non_empty_string` if blanks must fail.
- If the overall null rate is within threshold, no row fails this rule.

## Related rules

- [`not_null`](not-null.md)
- [`non_empty_string`](non-empty-string.md)
