# greater_than_or_equal

## What this rule does

Checks that populated values are greater than or equal to a threshold.

## When to use it

Use for non-negative values, minimum credits, or dates that must not precede a boundary.

## Rule applies to

**Data applicability:** Numeric, date, or otherwise comparable profiled columns that must be at least a configured threshold.

**Example column(s) on this page:** `credit_units`

## Parameters

```yaml
rule_type: greater_than_or_equal
columns: ["credit_units"]
value: 0
severity: error
```

## Example rule definition

```yaml
rule_id: greater_than_or_equal_example
rule_type: greater_than_or_equal
columns: ["credit_units"]
value: 0
severity: error
description: "Example approved metadata rule for greater_than_or_equal."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| course_id | credit_units |
| --- | --- |
| M001 | 4 |
| M002 | 0 |
| M003 | -1 |
| M004 | 2 |

## Rows that pass

| course_id | credit_units | Why |
| --- | --- | --- |
| M001 | 4 | Above threshold. |
| M002 | 0 | Equal to allowed minimum. |
| M004 | 2 | Above threshold. |

## Rows that fail

| course_id | credit_units | Why |
| --- | --- | --- |
| M003 | -1 | Below threshold. |

## Notes

- Null values do not fail this rule by themselves.
- Use `between` when both lower and upper bounds matter.

## Related rules

- [`greater_than`](greater-than.md)
- [`between`](between.md)
- [`column_a_gte_column_b`](column-a-gte-column-b.md)
