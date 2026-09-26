# range

Checks one numeric or date-like column against a minimum, maximum, or both.

## Use it when

Use `range` for explicit lower or upper bounds.

Examples:

- "Amount must be at least 0."
- "Score must be between 0 and 100 inclusive."
- "Transaction date must not be before the agreed start date" when that start date is a literal governed bound.

## Do not use it when

- The boundary comes from another column on the same row: use [`column_relationship`](column-relationship.md).
- The requirement is a fixed allowed list: use [`value_set`](value-set.md).
- The requirement is text format: use [`pattern`](pattern.md).

## Parameters

- `columns`: exactly one target column.
- `minimum` and/or `maximum`.
- `minimum_inclusive` and `maximum_inclusive`.

## Example

```json
{"rule_type":"range","columns":["amount"],"minimum":0,"minimum_inclusive":true,"maximum":100,"maximum_inclusive":false}
```
