# column_relationship

Compares two different columns on the same row with `=`, `!=`, `>`, `>=`, `<`, or `<=`.

## Use it when

Use `column_relationship` when the business requirement is a direct row-level comparison between two columns.

Examples:

- "End date must be on or after start date."
- "Credits earned cannot exceed credits attempted."
- "Source ID must equal target ID."

## Do not use it when

- A column or column combination must be unique: use [`uniqueness`](uniqueness.md).
- One column is required only when another has a specific value: use [`conditional_completeness`](conditional-completeness.md).
- A target column has an allowed set only under a condition: use [`conditional_values`](conditional-values.md).
- One column determines another across rows, such as `product_id → product_name`. This rule compares values within a row; it does not validate functional dependency across rows.

## Null behavior

Both-null values pass equality. One-null ordered comparisons fail.

## Example

```json
{"rule_type":"column_relationship","columns":["end_date","start_date"],"operator":">="}
```
