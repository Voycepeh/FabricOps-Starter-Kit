# column_relationship

## What this rule does

Compares two different columns on the same row using `=`, `!=`, `>`, `>=`, `<`, or `<=`.

## When to use it

Use for direct row-level comparisons such as date ordering, amount comparisons, or paired identifiers.

## Data applicability

Exactly two columns that can be compared meaningfully on the same row.

## Parameters

```yaml
rule_type: column_relationship
columns: ["end_date", "start_date"]
operator: ">="
```

## Example rule definition

```json
{"rule_type":"column_relationship","columns":["end_date","start_date"],"operator":">="}
```

## Sample input data

| record_id | start_date | end_date |
|---|---|---|
| 1 | 2026-01-01 | 2026-01-03 |
| 2 | 2026-01-05 | 2026-01-05 |
| 3 | 2026-01-10 | 2026-01-08 |

## Rows that pass

| record_id | Why |
|---|---|
| 1 | End date is after start date. |
| 2 | End date equals start date and `>=` allows equality. |

## Rows that fail

| record_id | Why |
|---|---|
| 3 | End date is before start date. |

## Notes

- This compares values within each row.
- It does not validate uniqueness or functional dependency across rows.
- Both-null values pass equality; one-null ordered comparisons fail.

## Related rules

- [`uniqueness`](uniqueness.md)
- [`conditional_completeness`](conditional-completeness.md)
- [`conditional_values`](conditional-values.md)
