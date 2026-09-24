# custom_expression

Provides the advanced escape hatch for project-owned row-level business logic. The expression language is `pyspark`; expressions must produce a boolean Spark `Column`. FabricOps accepts only a constrained, side-effect-free grammar built from `F.col`, `F.lit`, comparisons, `&`, `|`, `~`, and an explicit method whitelist: `isNull`, `isNotNull`, `isin`, `rlike`, `contains`, `startswith`, and `endswith`. Method arguments must be literal values. It never uses unrestricted `eval`, Python UDFs, imports, or arbitrary function calls.

```json
{"rule_type":"custom_expression","expression_language":"pyspark","expression":"(F.col(\"status\") != \"Closed\") | F.col(\"closed_date\").isNotNull()","description":"Closed records require a close date"}
```

`true` passes and `false` fails. FabricOps records results and applies Warn/Block and row tagging, but does not persist a validation column.
