# uniqueness

## What this rule does

Checks that one column, or one combination of columns, uniquely identifies rows.

## When to use it

Use for single-column keys or composite business grain.

## Data applicability

One or more columns that together define row identity.

## Parameters

```yaml
rule_type: uniqueness
columns: ["order_id", "line_id"]
```

## Example rule definition

```json
{"rule_type":"uniqueness","columns":["order_id","line_id"]}
```

## Sample input data

| order_id | line_id | product |
|---|---:|---|
| A100 | 1 | Pen |
| A100 | 2 | Book |
| A101 | 1 | Bag |
| A100 | 1 | Eraser |

## Rows that pass

| order_id | line_id | Why |
|---|---:|---|
| A100 | 2 | Combination appears once. |
| A101 | 1 | Combination appears once. |

## Rows that fail

| order_id | line_id | Why |
|---|---:|---|
| A100 | 1 | Combination appears more than once. |

## Notes

- Composite uniqueness is one table-level rule, not separate uniqueness checks per column.
- Profile distinctness can suggest a key candidate, but runtime validation proves uniqueness.
- `product_id + product_name` being unique does **not** prove `product_id → product_name`; that is a different relationship.
- Observed example pairs must not be converted into hard-coded allowed mappings unless Governance explicitly defines them.

## Related rules

- [`completeness`](completeness.md)
- [`column_relationship`](column-relationship.md)
