# uniqueness

Checks the configured table row key for duplicates.

FabricOps authors this rule from **Grain & Row Key** on the Table tab. Select one column for a single row key or multiple columns for a composite row key. The selected columns are stored as one table-level rule and are never split into per-column uniqueness checks.

Per-column profile distinctness is evidence for key suggestion. A column observed at 100% distinct with no missing values is a strong single-key candidate. Marginal per-column statistics cannot prove that a composite key is unique, so the configured uniqueness guardrail validates the selected combination against table data during pipeline execution.

```json
{"rule_type":"uniqueness","columns":["order_id","line_id"]}
```
