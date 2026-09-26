# uniqueness

Checks the configured table row key for duplicate values or duplicate column combinations.

## Use it when

Use `uniqueness` when one column or one combination of columns must uniquely identify rows.

Examples:

- "Order ID must be unique."
- "Order ID and line number together must uniquely identify each row."
- "No duplicate combinations of academic year, student ID, and module code."

FabricOps authors this rule from **Grain & Row Key** on the Table tab. A composite key is stored as one table-level rule and is never split into independent per-column uniqueness checks.

## Do not use it when

- Each value must merely be populated: use [`completeness`](completeness.md).
- Two columns must compare on each row: use [`column_relationship`](column-relationship.md).
- The requirement is that one value determines another value, such as `product_id → product_name`. Composite uniqueness does not prove that functional dependency.

## Profile evidence

A column observed at 100% distinct with no missing values is a strong single-key candidate. Per-column profile statistics cannot prove composite uniqueness, so the configured rule validates the selected combination against table data during pipeline execution.

Observed example values are evidence only. They must not be converted into hard-coded allowed pairs unless Governance explicitly defines those pairs as the requirement.

## Example

```json
{"rule_type":"uniqueness","columns":["order_id","line_id"]}
```
