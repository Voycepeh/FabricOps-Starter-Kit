# column_a_gt_column_b

## What this rule does

Checks that the first column is strictly greater than the second column.

## When to use it

Use for expiry dates after start dates, positive duration checks, or ordered numeric measures where equality is invalid.

## Rule applies to

**Data applicability:** Pairs of comparable profiled columns in the same row where the first selected column must be strictly greater than the second selected column.

**Example column(s) on this page:** `expiry_date`, `start_date`

## Parameters

```yaml
rule_type: column_a_gt_column_b
columns: ["expiry_date", "start_date"]
severity: error
```

## Example rule definition

```yaml
rule_id: column_a_gt_column_b_example
rule_type: column_a_gt_column_b
columns: ["expiry_date", "start_date"]
severity: error
description: "Example approved metadata rule for column_a_gt_column_b."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| contract_id | start_date | expiry_date |
| --- | --- | --- |
| C001 | 2026-01-01 | 2026-12-31 |
| C002 | 2026-02-01 | 2026-02-01 |
| C003 | 2026-03-10 | 2026-03-01 |
| C004 | null | null |

## Rows that pass

| contract_id | start_date | expiry_date | Why |
| --- | --- | --- | --- |
| C001 | 2026-01-01 | 2026-12-31 | Expiry is after start. |
| C004 | null | null | Both values are null, so no one-sided null failure occurs. |

## Rows that fail

| contract_id | start_date | expiry_date | Why |
| --- | --- | --- | --- |
| C002 | 2026-02-01 | 2026-02-01 | Equality is not allowed. |
| C003 | 2026-03-10 | 2026-03-01 | Expiry is before start. |

## Notes

- Rows fail when exactly one compared column is null.
- Add `not_null` if both dates must always be present.

## Related rules

- [`column_a_gte_column_b`](column-a-gte-column-b.md)
- [`column_pair_equal`](column-pair-equal.md)
- [`greater_than`](greater-than.md)
