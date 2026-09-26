# range

## What this rule does

Checks one numeric or date-like column against a governed minimum, maximum, or both.

## When to use it

Use for scores, percentages, quantities, dates, and other values with known valid bounds.

## Data applicability

Single comparable columns with explicit lower or upper limits.

## Parameters

```yaml
rule_type: range
columns: ["score"]
minimum: 0
minimum_inclusive: true
maximum: 100
maximum_inclusive: true
```

## Example rule definition

```json
{"rule_type":"range","columns":["score"],"minimum":0,"minimum_inclusive":true,"maximum":100,"maximum_inclusive":true}
```

## Sample input data

| assessment_id | score |
|---|---:|
| A001 | 88 |
| A002 | 0 |
| A003 | 104 |
| A004 | -2 |

## Rows that pass

| assessment_id | score | Why |
|---|---:|---|
| A001 | 88 | Inside the governed range. |
| A002 | 0 | On the inclusive lower bound. |

## Rows that fail

| assessment_id | score | Why |
|---|---:|---|
| A003 | 104 | Above the maximum. |
| A004 | -2 | Below the minimum. |

## Notes

- Supply a minimum, maximum, or both.
- Inclusivity is configured independently for each bound.
- If the boundary comes from another column on the same row, use [`column_relationship`](column-relationship.md).

## Related rules

- [`value_set`](value-set.md)
- [`column_relationship`](column-relationship.md)
