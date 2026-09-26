# conditional_completeness

## What this rule does

Requires a target column to be populated only when a condition on another column matches.

## When to use it

Use for conditional requiredness such as “Approved records require an approved date.”

## Data applicability

One condition column and one target column.

## Parameters

```yaml
rule_type: conditional_completeness
columns: ["status", "approved_date"]
condition_operator: "="
condition_value: "Approved"
treat_blank_as_missing: true
```

## Example rule definition

```json
{"rule_type":"conditional_completeness","columns":["status","approved_date"],"condition_operator":"=","condition_value":"Approved","treat_blank_as_missing":true}
```

## Sample input data

| record_id | status | approved_date |
|---|---|---|
| 1 | Approved | 2026-01-01 |
| 2 | Approved | null |
| 3 | Draft | null |

## Rows that pass

| record_id | Why |
|---|---|
| 1 | Condition matches and target is populated. |
| 3 | Condition does not match, so the rule does not apply. |

## Rows that fail

| record_id | Why |
|---|---|
| 2 | Condition matches but target is missing. |

## Notes

- The condition supports `=` or `!=`.
- Use `completeness` when the target is always required.
- Use `conditional_values` when the target must belong to a governed set instead of merely being populated.

## Related rules

- [`completeness`](completeness.md)
- [`conditional_values`](conditional-values.md)
