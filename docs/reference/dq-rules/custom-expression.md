# custom_expression

## What this rule does

Evaluates a constrained PySpark boolean expression and fails rows where the expression is false.

## When to use it

Use only when no smaller structured FabricOps rule can represent the governance requirement without changing its meaning.

## Data applicability

Row-level business logic that genuinely requires a boolean expression after the named rule types have been ruled out.

## Parameters

```yaml
rule_type: custom_expression
expression_language: pyspark
expression: 'F.col("total_amount") == F.col("quantity") * F.col("unit_price") * (F.lit(1) - F.col("discount"))'
```

## Example rule definition

```json
{"rule_type":"custom_expression","expression_language":"pyspark","expression":"F.col(\"total_amount\") == F.col(\"quantity\") * F.col(\"unit_price\") * (F.lit(1) - F.col(\"discount\"))","description":"Total amount must equal quantity times unit price after discount"}
```

## Sample input data

| order_id | quantity | unit_price | discount | total_amount |
|---|---:|---:|---:|---:|
| A001 | 2 | 50 | 0.0 | 100 |
| A002 | 2 | 50 | 0.1 | 90 |
| A003 | 2 | 50 | 0.1 | 80 |

## Rows that pass

| order_id | Why |
|---|---|
| A001 | Formula evaluates true. |
| A002 | Formula evaluates true. |

## Rows that fail

| order_id | Why |
|---|---|
| A003 | Expected total is 90, not 80. |

## Notes

- Do not use this merely because a requirement involves multiple columns.
- First consider `uniqueness`, `column_relationship`, `conditional_completeness`, and `conditional_values`.
- Observed profile values must not be encoded as literal allowed combinations unless Governance explicitly defines them.
- The expression grammar is constrained and side-effect free; FabricOps does not use unrestricted `eval`, Python UDFs, imports, or arbitrary calls.
- Engineering review is required before freeze.

## Related rules

- [`column_relationship`](column-relationship.md)
- [`conditional_completeness`](conditional-completeness.md)
- [`conditional_values`](conditional-values.md)
