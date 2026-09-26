# custom_expression

Provides the advanced escape hatch for project-owned row-level business logic.

## Use it when

Use `custom_expression` only when no structured FabricOps DQ pattern can represent the requirement without changing its meaning.

A good example is governed arithmetic:

> Total amount must equal quantity × unit price × (1 - discount).

## Do not use it when

Do not use `custom_expression` merely because a requirement involves multiple columns. First consider:

- [`uniqueness`](uniqueness.md) for a single or composite row key.
- [`column_relationship`](column-relationship.md) for direct row-level comparison.
- [`conditional_completeness`](conditional-completeness.md) for conditional requiredness.
- [`conditional_values`](conditional-values.md) for conditional governed sets.

Do not encode profile examples or frequency evidence as literal allowed combinations unless Governance explicitly defines those combinations as the rule.

## Expression boundary

The expression language is `pyspark` and must produce a boolean Spark `Column`. FabricOps accepts only a constrained, side-effect-free grammar built from `F.col`, `F.lit`, comparisons, `&`, `|`, `~`, arithmetic (`+`, `-`, `*`, `/`, `%`), and an explicit method whitelist: `isNull`, `isNotNull`, `isin`, `rlike`, `contains`, `startswith`, and `endswith`.

FabricOps does not use unrestricted `eval`, Python UDFs, imports, or arbitrary function calls.

## Review

A `custom_expression` is staged with Engineering review pending. An engineer must review and approve the resolved expression before the Data Contract can be frozen.

## Example

```json
{"rule_type":"custom_expression","expression_language":"pyspark","expression":"F.col(\"total_amount\") == F.col(\"quantity\") * F.col(\"unit_price\") * (F.lit(1) - F.col(\"discount\"))","description":"Total amount must equal quantity times unit price after discount"}
```

Exponentiation and floor division are not accepted. `true` passes and `false` fails.
