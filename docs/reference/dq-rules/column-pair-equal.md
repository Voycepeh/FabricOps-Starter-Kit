# column_pair_equal

## What this rule does

Checks that two columns carry the same value using null-safe equality.

## When to use it

Use for reconciled identifiers, copied reference values, or source/target fields that should match.

## Rule applies to

`source_id`, `target_id`

## Parameters

```yaml
rule_type: column_pair_equal
columns: ["source_id", "target_id"]
severity: error
```

## Example rule definition

```yaml
rule_id: column_pair_equal_example
rule_type: column_pair_equal
columns: ["source_id", "target_id"]
severity: error
description: "Example approved metadata rule for column_pair_equal."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| row_id | source_id | target_id |
| --- | --- | --- |
| 1 | A100 | A100 |
| 2 | B200 | B201 |
| 3 | null | null |
| 4 | C300 | null |

## Rows that pass

| row_id | source_id | target_id | Why |
| --- | --- | --- | --- |
| 1 | A100 | A100 | Values match. |
| 3 | null | null | Both are null, so null-safe equality passes. |

## Rows that fail

| row_id | source_id | target_id | Why |
| --- | --- | --- | --- |
| 2 | B200 | B201 | Values differ. |
| 4 | C300 | null | Only one side is null. |

## Notes

- This rule uses null-safe equality, so two nulls pass.
- Use `not_null` as well if both values must be present.

## Related rules

- [`column_a_gte_column_b`](column-a-gte-column-b.md)
- [`column_a_gt_column_b`](column-a-gt-column-b.md)
- [`value_when`](value-when.md)
