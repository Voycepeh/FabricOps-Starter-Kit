# value_set

## What this rule does

Checks one column against an explicit governed set of allowed or blocked values.

## When to use it

Use for controlled domains such as statuses, categories, codes, and flags.

## Data applicability

Single categorical or code-like columns with a deliberately governed value domain.

## Parameters

```yaml
rule_type: value_set
columns: ["status"]
mode: allow
values: ["Open", "Closed"]
```

## Example rule definition

```json
{"rule_type":"value_set","columns":["status"],"mode":"allow","values":["Open","Closed"]}
```

## Sample input data

| record_id | status |
|---|---|
| 1 | Open |
| 2 | Closed |
| 3 | Pending |

## Rows that pass

| record_id | status | Why |
|---|---|---|
| 1 | Open | Value is explicitly allowed. |
| 2 | Closed | Value is explicitly allowed. |

## Rows that fail

| record_id | status | Why |
|---|---|---|
| 3 | Pending | Value is not in the governed allowed set. |

## Notes

- `mode=allow` permits only listed values.
- `mode=block` rejects listed values.
- Frequency-profile values are evidence only. Do not automatically turn observed values into a governed value set.

## Related rules

- [`conditional_values`](conditional-values.md)
- [`range`](range.md)
- [`pattern`](pattern.md)
