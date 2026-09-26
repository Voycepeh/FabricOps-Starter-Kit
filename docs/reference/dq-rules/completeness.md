# completeness

## What this rule does

Checks whether one column is populated within an allowed missing threshold.

## When to use it

Use when a field is mandatory, or when a small amount of missing data is acceptable but should stay below a governed threshold.

## Data applicability

Single columns where missingness is meaningful. `treat_blank_as_missing` controls whether blank or whitespace text counts as missing.

## Parameters

```yaml
rule_type: completeness
columns: ["customer_id"]
maximum_missing_percent: 0
treat_blank_as_missing: true
```

## Example rule definition

```json
{"rule_type":"completeness","columns":["customer_id"],"maximum_missing_percent":0,"treat_blank_as_missing":true}
```

## Sample input data

| row_id | customer_id |
|---|---|
| 1 | C001 |
| 2 | C002 |
| 3 | null |
| 4 | " " |

## Rows that pass

| row_id | customer_id | Why |
|---|---|---|
| 1 | C001 | Value is present. |
| 2 | C002 | Value is present. |

## Rows that fail

| row_id | customer_id | Why |
|---|---|---|
| 3 | null | Missing value. |
| 4 | " " | Blank counts as missing because `treat_blank_as_missing=true`. |

## Notes

- Set `maximum_missing_percent=0` for a required field.
- Use a higher threshold when limited missingness is acceptable.
- If requiredness depends on another column, use [`conditional_completeness`](conditional-completeness.md).

## Related rules

- [`conditional_completeness`](conditional-completeness.md)
- [`uniqueness`](uniqueness.md)
