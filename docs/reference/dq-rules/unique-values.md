# unique_values

## What this rule does

Checks that one column has no duplicate values across the DataFrame.

## When to use it

Use for natural keys, source identifiers, or generated business IDs that must identify one row.

## Rule applies to

**Data applicability:** A single profiled column that should identify one row per value, where duplicate values indicate duplicate or ambiguous business keys.

**Example column(s) on this page:** `student_id`

## Parameters

```yaml
rule_type: unique_values
columns: ["student_id"]
severity: error
```

## Example rule definition

```yaml
rule_id: unique_example
rule_type: unique_values
columns: ["student_id"]
severity: error
description: "Example approved metadata rule for unique_values."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL`, including `rule_parameters_json`.

## Sample input data

| student_id | name |
| --- | --- |
| S001 | Amy |
| S002 | Ben |
| S003 | Chandra |
| S002 | Benedict |

## Rows that pass

| student_id | name | Why |
| --- | --- | --- |
| S001 | Amy | Value appears once. |
| S003 | Chandra | Value appears once. |

## Rows that fail

| student_id | name | Why |
| --- | --- | --- |
| S002 | Ben | `S002` appears more than once. |
| S002 | Benedict | `S002` appears more than once. |

## Notes

- Rows sharing the duplicate value are all tagged as failures.
- For multi-column business grain, use `unique_combination`.

## Related rules

- [`unique_combination`](unique-combination.md)
- [`missing_values`](missing-values.md)
