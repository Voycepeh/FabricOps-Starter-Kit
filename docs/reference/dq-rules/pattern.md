# pattern

Checks populated text in one column against a regular expression.

## Use it when

Use `pattern` when the requirement is about text shape or format.

Examples:

- "Email must have an approved email format."
- "Product code must follow AAA-9999."
- "Postal code must contain six digits."

## Do not use it when

- The requirement is an explicit list of values: use [`value_set`](value-set.md).
- The requirement is numeric or date bounds: use [`range`](range.md).
- The requirement compares two columns: use [`column_relationship`](column-relationship.md).

Observed sample strings may help infer a proposed regex, but they are evidence only and must not be treated as the full permitted domain.

## Example

```json
{"rule_type":"pattern","columns":["email"],"pattern":"^[^@]+@[^@]+\\.[^@]+$"}
```
