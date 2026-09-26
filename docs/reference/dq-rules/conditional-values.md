# conditional_values

## What this rule does

Checks a target column against a governed value set only when a condition on another column matches.

## When to use it

Use for conditional controlled domains such as “When country is SG, currency must be SGD.”

## Data applicability

One condition column and one target column.

## Parameters

```yaml
rule_type: conditional_values
columns: ["country", "currency"]
condition_operator: "="
condition_value: "SG"
mode: allow
values: ["SGD"]
```

## Example rule definition

```json
{"rule_type":"conditional_values","columns":["country","currency"],"condition_operator":"=","condition_value":"SG","mode":"allow","values":["SGD"]}
```

## Sample input data

| txn_id | country | currency |
|---|---|---|
| T001 | SG | SGD |
| T002 | US | USD |
| T003 | SG | USD |

## Rows that pass

| txn_id | Why |
|---|---|
| T001 | Condition matches and target value is allowed. |
| T002 | Condition does not match, so the rule does not apply. |

## Rows that fail

| txn_id | Why |
|---|---|
| T003 | Condition matches but target value is outside the governed set. |

## Notes

- The condition supports `=` or `!=`.
- `mode` is `allow` or `block`.
- Do not infer contractual mappings from observed frequency pairs.

## Related rules

- [`value_set`](value-set.md)
- [`conditional_completeness`](conditional-completeness.md)
- [`custom_expression`](custom-expression.md)
