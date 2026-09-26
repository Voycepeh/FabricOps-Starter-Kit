# completeness

Checks whether one column is populated within an allowed missing threshold.

## Use it when

Use `completeness` when the requirement is about presence: a column must always be populated, or may be missing only up to an accepted percentage.

Examples:

- "Customer ID must always be populated."
- "Email may be missing in no more than 5% of rows."
- "Blank customer names should count as missing."

## Do not use it when

- The column must be unique: use [`uniqueness`](uniqueness.md).
- Values must come from an approved set: use [`value_set`](value-set.md).
- The column is required only under another condition: use [`conditional_completeness`](conditional-completeness.md).

## Parameters

- `columns`: exactly one target column.
- `maximum_missing_percent`: allowed missing percentage from 0 through 100.
- `treat_blank_as_missing`: whether blank or whitespace text counts as missing.

## Example

```json
{"rule_type":"completeness","columns":["customer_id"],"maximum_missing_percent":0,"treat_blank_as_missing":true}
```

"At least 95% of rows must contain an email" becomes:

```json
{"rule_type":"completeness","columns":["email"],"maximum_missing_percent":5,"treat_blank_as_missing":true}
```
