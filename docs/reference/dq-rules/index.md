# DQ rule reference

FabricOps supports **23 native DQ rule types** for metadata-driven checks. Reviewers approve these rules in Governance Review, FabricOps stores them as `guardrail_type="dq"` rows in `METADATA_GUARDRAIL_RULES`, and `run_table_guardrails` evaluates the active approved rules during later `02_pipeline` runs.

FabricOps uses one canonical DQ rule vocabulary. It does **not** require Great Expectations or dbt at runtime, and it does not expose one Python callable per rule. Rules are metadata: choose the rule type, provide the required parameters, approve the row, and let the pipeline load the approved metadata.

For the Governance Review operating model, see [Governance Review](../../guided-demo/03-enrich-guardrails.md).

## How to read the catalogue

Each rule below shows:

- **Rule**: the `rule_type` value to store in `METADATA_GUARDRAIL_RULES` for rows with `guardrail_type="dq"`.
- **When to use it**: the plain-language reason a reviewer would approve the rule.
- **Required parameters**: the minimum fields that must be present in the rule JSON. Most rules also include `rule_type`, `severity`, and a description in the approved metadata row.
- **Example JSON**: a small public-safe example that can be adapted in `01_governance`.
- **Reference**: a link to the detailed rule page.

Use the smallest named rule that expresses the expectation. Save `expression_true` for trusted reviewers when no simpler FabricOps-native rule fits.

## Completeness

Completeness rules check whether required data is present.

| Rule | When to use it | Required parameters | Example JSON | Reference |
|---|---|---|---|---|
| `not_null` | One or more columns must not contain actual null values. Use `non_empty_string` when blanks and whitespace should also fail. | `columns` | `{"rule_type":"not_null","columns":["student_id"],"severity":"error"}` | [`not_null`](not-null.md) |
| `null_rate_below` | A column can have some nulls, but the null percentage must stay below an approved threshold. | one `columns` value, `max_null_percent` | `{"rule_type":"null_rate_below","columns":["email"],"max_null_percent":5,"severity":"warning"}` | [`null_rate_below`](null-rate-below.md) |
| `non_empty_string` | String values must not be null, blank, or whitespace-only. | `columns` | `{"rule_type":"non_empty_string","columns":["programme_name"],"severity":"error"}` | [`non_empty_string`](non-empty-string.md) |
| `required_when` | One or more columns are required only when a row-level condition is true. | `columns`, `condition` | `{"rule_type":"required_when","columns":["approved_date"],"condition":"status = 'Approved'","severity":"error"}` | [`required_when`](required-when.md) |

## Uniqueness

Uniqueness rules check whether identifiers or business-grain columns repeat unexpectedly.

| Rule | When to use it | Required parameters | Example JSON | Reference |
|---|---|---|---|---|
| `unique` | A single column should identify each row on its own. | one `columns` value | `{"rule_type":"unique","columns":["student_id"],"severity":"error"}` | [`unique`](unique.md) |
| `unique_combination` | Two or more columns define the table grain and the combination must be unique. | two or more `columns` values | `{"rule_type":"unique_combination","columns":["student_id","semester"],"severity":"error"}` | [`unique_combination`](unique-combination.md) |

## Allowed values and ranges

Allowed-value and range rules check controlled domains and measurable thresholds.

| Rule | When to use it | Required parameters | Example JSON | Reference |
|---|---|---|---|---|
| `accepted_values` | A column must contain only values from an approved list, such as statuses, categories, flags, or codes. | one `columns` value, `allowed_values` | `{"rule_type":"accepted_values","columns":["status"],"allowed_values":["Active","Inactive"],"severity":"error"}` | [`accepted_values`](accepted-values.md) |
| `not_in_values` | Known placeholders, blocked codes, or invalid values should not appear. | one `columns` value, `blocked_values` | `{"rule_type":"not_in_values","columns":["country"],"blocked_values":["UNKNOWN","N/A"],"severity":"warning"}` | [`not_in_values`](not-in-values.md) |
| `between` | Numeric, date, or comparable values should stay inside an approved lower and/or upper range. | one `columns` value, `min_value` or `max_value` | `{"rule_type":"between","columns":["score"],"min_value":0,"max_value":100,"severity":"error"}` | [`between`](between.md) |
| `greater_than` | Values must be strictly greater than an approved threshold. | one `columns` value, `value` | `{"rule_type":"greater_than","columns":["amount"],"value":0,"severity":"error"}` | [`greater_than`](greater-than.md) |
| `greater_than_or_equal` | Values must be at least an approved threshold. | one `columns` value, `value` | `{"rule_type":"greater_than_or_equal","columns":["credit_units"],"value":0,"severity":"error"}` | [`greater_than_or_equal`](greater-than-or-equal.md) |
| `less_than` | Values must be strictly below an approved threshold. | one `columns` value, `value` | `{"rule_type":"less_than","columns":["risk_score"],"value":1,"severity":"warning"}` | [`less_than`](less-than.md) |
| `less_than_or_equal` | Values must not exceed an approved threshold. | one `columns` value, `value` | `{"rule_type":"less_than_or_equal","columns":["response_rate"],"value":100,"severity":"error"}` | [`less_than_or_equal`](less-than-or-equal.md) |

## Patterns and dates

Pattern and date rules check formats, valid dates, and freshness expectations.

| Rule | When to use it | Required parameters | Example JSON | Reference |
|---|---|---|---|---|
| `regex_match` | Populated string values must match a known format, such as an email-like value, code, or identifier pattern. | one `columns` value, `regex_pattern` | `{"rule_type":"regex_match","columns":["email"],"regex_pattern":"^[^@]+@[^@]+\\.[^@]+$","severity":"warning"}` | [`regex_match`](regex-match.md) |
| `date_not_future` | Date values must not be later than the run date. | one `columns` value | `{"rule_type":"date_not_future","columns":["birth_date"],"severity":"error"}` | [`date_not_future`](date-not-future.md) |
| `date_between` | Dates must stay within an approved business range. | one `columns` value, `min_value` or `max_value` | `{"rule_type":"date_between","columns":["event_date"],"min_value":"2020-01-01","max_value":"2026-12-31","severity":"error"}` | [`date_between`](date-between.md) |
| `freshness` | A timestamp or date must be recent enough for operational use. | one `columns` value, `max_age_days` | `{"rule_type":"freshness","columns":["updated_at"],"max_age_days":2,"severity":"error"}` | [`freshness`](freshness.md) |
| `max_age_days` | A snapshot or effective date must not be older than an approved number of days. | one `columns` value, `max_age_days` | `{"rule_type":"max_age_days","columns":["snapshot_date"],"max_age_days":1,"severity":"warning"}` | [`max_age_days`](max-age-days.md) |

## Cross-column logic

Cross-column rules check relationships between values in the same row.

| Rule | When to use it | Required parameters | Example JSON | Reference |
|---|---|---|---|---|
| `column_pair_equal` | Two columns should carry the same value in each row. | exactly two `columns` values | `{"rule_type":"column_pair_equal","columns":["source_id","target_id"],"severity":"error"}` | [`column_pair_equal`](column-pair-equal.md) |
| `column_a_gte_column_b` | The first column must be greater than or equal to the second column. | exactly two `columns` values | `{"rule_type":"column_a_gte_column_b","columns":["end_date","start_date"],"severity":"error"}` | [`column_a_gte_column_b`](column-a-gte-column-b.md) |
| `column_a_gt_column_b` | The first column must be greater than the second column. | exactly two `columns` values | `{"rule_type":"column_a_gt_column_b","columns":["expiry_date","start_date"],"severity":"error"}` | [`column_a_gt_column_b`](column-a-gt-column-b.md) |
| `value_when` | A column must equal an approved value when a row-level condition is true. | one `columns` value, `condition`, `expected_value` | `{"rule_type":"value_when","condition":"student_status = 'Graduated'","columns":["is_active"],"expected_value":false,"severity":"error"}` | [`value_when`](value-when.md) |

## Advanced

Advanced rules are useful, but they need extra review because they are harder for junior engineers to read quickly.

| Rule | When to use it | Required parameters | Example JSON | Reference |
|---|---|---|---|---|
| `expression_true` — Custom expression | Use only when no smaller named rule can express the expectation. The `expression` is a Spark SQL boolean expression, not a custom Python plugin. | `expression` | `{"rule_type":"expression_true","expression":"credits_attempted >= credits_earned","severity":"error"}` | [`expression_true`](expression-true.md) |

## Choosing a rule

1. Start with completeness rules such as `not_null`, `null_rate_below`, and `non_empty_string`.
2. Add uniqueness rules only where the table grain is clear.
3. Use accepted or blocked values for small governed domains.
4. Use range, comparison, date, or freshness rules for measurable constraints.
5. Use cross-column and conditional rules for relationships within the same row.
6. Use `expression_true` only when a trusted reviewer confirms that no simpler named rule fits.

Set `severity="error"` when a failure should block unsafe or misleading output. Set `severity="warning"` when the issue should be visible in evidence but should not block the run.

## Runtime behavior

`METADATA_GUARDRAIL_RULES` is append-only for DQ rows. Create, update, deactivate, and reactivate actions add new metadata rows instead of deleting history. During a pipeline run, `run_table_guardrails` resolves the newest version of each rule, keeps only active approved rules, evaluates them, and records the DQ outcome as guardrail evidence.
