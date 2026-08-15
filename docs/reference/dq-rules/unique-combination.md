# unique_combination

## What this rule does

Checks that a group of two or more columns appears only once.

## When to use it

Use when the business grain is composite, such as order line, account month, or student semester.

## Rule applies to

**Data applicability:** Two or more profiled columns that together define the business grain, especially where catalogue distinct-count evidence should match row-level uniqueness expectations.

**Example column(s) on this page:** `order_id`, `line_no`

## Parameters

```yaml
rule_type: unique_combination
columns: ["order_id", "line_no"]
severity: error
```

## Example rule definition

```yaml
rule_id: unique_combination_example
rule_type: unique_combination
columns: ["order_id", "line_no"]
severity: error
description: "Example approved metadata rule for unique_combination."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL`, including `rule_parameters_json`.

## Sample input data

| order_id | line_no | product |
| --- | --- | --- |
| A100 | 1 | Pen |
| A100 | 2 | Book |
| A101 | 1 | Bag |
| A100 | 1 | Eraser |

## Rows that pass

| order_id | line_no | Why |
| --- | --- | --- |
| A100 | 2 | Combination appears once. |
| A101 | 1 | Combination appears once. |

## Rows that fail

| order_id | line_no | Why |
| --- | --- | --- |
| A100 | 1 | Combination appears more than once. |

## Notes

- All rows with the duplicate combination are tagged as failures.
- Use this before downstream aggregations that assume one row per grain.

## Related rules

- [`unique_values`](unique-values.md)
- [`compare_columns`](compare-columns.md)
