# column_a_gte_column_b

## What this rule does

Checks that the first column is greater than or equal to the second column.

## When to use it

Use for end dates after start dates, minimum/maximum pairs, or numeric bounds where equality is allowed.

## Rule applies to

**Data applicability:** Pairs of comparable profiled columns in the same row where the first selected column must be greater than or equal to the second selected column.

**Example column(s) on this page:** `end_date`, `start_date`

## Parameters

```yaml
rule_type: column_a_gte_column_b
columns: ["end_date", "start_date"]
severity: error
```

## Example rule definition

```yaml
rule_id: column_a_gte_column_b_example
rule_type: column_a_gte_column_b
columns: ["end_date", "start_date"]
severity: error
description: "Example approved metadata rule for column_a_gte_column_b."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL_RULES`, including `rule_parameters_json`.

## Sample input data

| period_id | start_date | end_date |
| --- | --- | --- |
| P001 | 2026-01-01 | 2026-01-31 |
| P002 | 2026-02-01 | 2026-02-01 |
| P003 | 2026-03-10 | 2026-03-01 |
| P004 | 2026-04-01 | null |

## Rows that pass

| period_id | start_date | end_date | Why |
| --- | --- | --- | --- |
| P001 | 2026-01-01 | 2026-01-31 | End is after start. |
| P002 | 2026-02-01 | 2026-02-01 | Equality is allowed. |

## Rows that fail

| period_id | start_date | end_date | Why |
| --- | --- | --- | --- |
| P003 | 2026-03-10 | 2026-03-01 | End is before start. |
| P004 | 2026-04-01 | null | Only one side is null. |

## Notes

- Rows fail when exactly one compared column is null.
- Use `column_a_gt_column_b` when equality should fail.

## Related rules

- [`column_a_gt_column_b`](column-a-gt-column-b.md)
- [`column_pair_equal`](column-pair-equal.md)
- [`greater_than_or_equal`](greater-than-or-equal.md)
