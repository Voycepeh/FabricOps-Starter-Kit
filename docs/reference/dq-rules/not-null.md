# not_null

## What this rule does

Checks that one or more selected columns are actual non-null values. Blank strings are not treated as nulls; use `non_empty_string` for blanks.

## When to use it

Use when a column is mandatory for joins, reporting, or safe downstream interpretation.

## Rule applies to

**Data applicability:** Any profiled column where catalogue null-count evidence should remain zero because the value is mandatory for safe downstream use.

**Example column(s) on this page:** `customer_id`

## Parameters

```yaml
rule_type: not_null
columns: ["customer_id"]
severity: error
```

## Example rule definition

```yaml
rule_id: not_null_example
rule_type: not_null
columns: ["customer_id"]
severity: error
description: "Example approved metadata rule for not_null."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| row_id | customer_id | region |
| --- | --- | --- |
| 1 | C001 | APAC |
| 2 | C002 | EMEA |
| 3 | null | APAC |
| 4 | C004 | AMER |

## Rows that pass

| row_id | customer_id | Why |
| --- | --- | --- |
| 1 | C001 | Value is present. |
| 2 | C002 | Value is present. |
| 4 | C004 | Value is present. |

## Rows that fail

| row_id | customer_id | Why |
| --- | --- | --- |
| 3 | null | Mandatory identifier is null. |

## Notes

- Multiple columns can be supplied; the row fails if any selected column is null.
- Use `non_empty_string` when whitespace-only values should also fail.

## Related rules

- [`non_empty_string`](non-empty-string.md)
- [`required_when`](required-when.md)
- [`null_rate_below`](null-rate-below.md)
