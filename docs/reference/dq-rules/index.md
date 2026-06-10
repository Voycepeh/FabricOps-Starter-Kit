# DQ rule reference

FabricOps supports **23 native DQ rule types** for metadata-driven checks reviewed in Governance Review and enforced by `enforce_dq_rules` at pipeline runtime. Actual enforced rules depend on the approved active rows for each table in `METADATA_DQ_RULES`.

For the operating model, approval workflow, and worked examples, see [Governance Review](../../how-fabricops-works/governance-review.md).

## Completeness

- [`not_null`](not-null.md)
- [`null_rate_below`](null-rate-below.md)
- [`non_empty_string`](non-empty-string.md)
- [`required_when`](required-when.md)

## Uniqueness

- [`unique`](unique.md)
- [`unique_combination`](unique-combination.md)

## Allowed values and ranges

- [`accepted_values`](accepted-values.md)
- [`not_in_values`](not-in-values.md)
- [`between`](between.md)
- [`greater_than`](greater-than.md)
- [`greater_than_or_equal`](greater-than-or-equal.md)
- [`less_than`](less-than.md)
- [`less_than_or_equal`](less-than-or-equal.md)

## Patterns and dates

- [`regex_match`](regex-match.md)
- [`date_not_future`](date-not-future.md)
- [`date_between`](date-between.md)
- [`freshness`](freshness.md)
- [`max_age_days`](max-age-days.md)

## Cross-column logic

- [`column_pair_equal`](column-pair-equal.md)
- [`column_a_gte_column_b`](column-a-gte-column-b.md)
- [`column_a_gt_column_b`](column-a-gt-column-b.md)
- [`value_when`](value-when.md)

## Advanced

- [`expression_true` — Custom expression](expression-true.md)
