# value_when

## What this rule does

Checks that one column equals an expected value when a condition is true.

## When to use it

Use for conditional business rules such as country-specific currency, status flags, or derived classifications.

## Rule applies to

**Data applicability:** Profiled columns whose expected value depends on a Spark SQL condition over the same row, usually for conditional business logic.

**Example column(s) on this page:** `currency`

## Parameters

```yaml
rule_type: value_when
columns: ["currency"]
condition: "country_code = 'SG'"
expected_value: "SGD"
severity: error
```

## Example rule definition

```yaml
rule_id: value_when_example
rule_type: value_when
columns: ["currency"]
condition: "country_code = 'SG'"
expected_value: "SGD"
severity: error
description: "Example approved metadata rule for value_when."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| txn_id | country_code | currency |
| --- | --- | --- |
| T001 | SG | SGD |
| T002 | US | USD |
| T003 | SG | USD |
| T004 | SG | null |

## Rows that pass

| txn_id | country_code | currency | Why |
| --- | --- | --- | --- |
| T001 | SG | SGD | Condition true and expected value is present. |
| T002 | US | USD | Condition false, so rule does not apply. |

## Rows that fail

| txn_id | country_code | currency | Why |
| --- | --- | --- | --- |
| T003 | SG | USD | Expected `SGD` when country is SG. |
| T004 | SG | null | Null is not null-safe equal to `SGD`. |

## Notes

- The condition is expressed using Spark SQL syntax.
- Use `accepted_values` for unconditional controlled domains.

## Related rules

- [`required_when`](required-when.md)
- [`accepted_values`](accepted-values.md)
- [`expression_true`](expression-true.md)
