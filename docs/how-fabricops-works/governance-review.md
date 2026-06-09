# Governance Review

`03_governance` is the human review and approval step for governed, quality-checked, AI-ready notebooks in Microsoft Fabric. The boundary is intentionally simple:

- `03_governance` owns review and approval.
- `METADATA_DQ_RULES` stores approved DQ rules as append-only metadata history.
- `02_pipeline` loads the newest active approved DQ rules for the selected table.
- `enforce_dq_rules` enforces those rules at runtime before unsafe or misleading output is written.

DQ rule authoring stays metadata-driven. FabricOps does not expose one Python callable per DQ rule, and it does not require Great Expectations or dbt at runtime.

## Approved DQ rule catalogue

Use the smallest FabricOps-native rule that expresses the requirement. Prefer explicit rule types such as `not_null`, `accepted_values`, or `between` before the escape hatch `expression_true`.

| Rule | When to use it | Required parameters | Example JSON |
|---|---|---|---|
| `not_null` | One or more columns must be populated. | `columns` | `{"rule_type":"not_null","columns":["student_id"],"severity":"error"}` |
| `null_rate_below` | A nullable column is acceptable only below a threshold. | one `columns` value, `max_null_percent` | `{"rule_type":"null_rate_below","columns":["email"],"max_null_percent":5,"severity":"warning"}` |
| `non_empty_string` | String columns must not be null or blank. | `columns` | `{"rule_type":"non_empty_string","columns":["programme_name"],"severity":"error"}` |
| `unique` | A single column must be unique. | one `columns` value | `{"rule_type":"unique","columns":["student_id"],"severity":"error"}` |
| `unique_combination` | Two or more columns define the business grain. | two or more `columns` values | `{"rule_type":"unique_combination","columns":["student_id","semester"],"severity":"error"}` |
| `accepted_values` | A column must contain only approved values. | one `columns` value, `allowed_values` | `{"rule_type":"accepted_values","columns":["status"],"allowed_values":["Active","Inactive"],"severity":"error"}` |
| `not_in_values` | Known placeholder or blocked values should not appear. | one `columns` value, `blocked_values` | `{"rule_type":"not_in_values","columns":["country"],"blocked_values":["UNKNOWN","N/A"],"severity":"warning"}` |
| `between` | Numeric/date values should stay within a range. | one `columns` value, `min_value` or `max_value` | `{"rule_type":"between","columns":["score"],"min_value":0,"max_value":100,"severity":"error"}` |
| `greater_than` | Values must be strictly greater than a threshold. | one `columns` value, `value` | `{"rule_type":"greater_than","columns":["amount"],"value":0,"severity":"error"}` |
| `greater_than_or_equal` | Values must be at least a threshold. | one `columns` value, `value` | `{"rule_type":"greater_than_or_equal","columns":["credit_units"],"value":0,"severity":"error"}` |
| `less_than` | Values must be strictly below a threshold. | one `columns` value, `value` | `{"rule_type":"less_than","columns":["risk_score"],"value":1,"severity":"warning"}` |
| `less_than_or_equal` | Values must not exceed a threshold. | one `columns` value, `value` | `{"rule_type":"less_than_or_equal","columns":["response_rate"],"value":100,"severity":"error"}` |
| `regex_match` | A populated string must match a known format. | one `columns` value, `regex_pattern` | `{"rule_type":"regex_match","columns":["email"],"regex_pattern":"^[^@]+@[^@]+\\.[^@]+$","severity":"warning"}` |
| `date_not_future` | Dates must not be later than the run date. | one `columns` value | `{"rule_type":"date_not_future","columns":["birth_date"],"severity":"error"}` |
| `date_between` | Dates must stay within a business-approved range. | one `columns` value, `min_value` or `max_value` | `{"rule_type":"date_between","columns":["event_date"],"min_value":"2020-01-01","max_value":"2026-12-31","severity":"error"}` |
| `freshness` | A timestamp/date must be recent enough for use. | one `columns` value, `max_age_days` | `{"rule_type":"freshness","columns":["updated_at"],"max_age_days":2,"severity":"error"}` |
| `max_age_days` | A snapshot/date must not be older than a threshold. | one `columns` value, `max_age_days` | `{"rule_type":"max_age_days","columns":["snapshot_date"],"max_age_days":1,"severity":"warning"}` |
| `column_pair_equal` | Two columns should carry the same value. | exactly two `columns` values | `{"rule_type":"column_pair_equal","columns":["source_id","target_id"],"severity":"error"}` |
| `column_a_gte_column_b` | The first column must be greater than or equal to the second. | exactly two `columns` values | `{"rule_type":"column_a_gte_column_b","columns":["end_date","start_date"],"severity":"error"}` |
| `column_a_gt_column_b` | The first column must be greater than the second. | exactly two `columns` values | `{"rule_type":"column_a_gt_column_b","columns":["expiry_date","start_date"],"severity":"error"}` |
| `required_when` | One or more columns are required only when a condition is true. | `columns`, `condition` | `{"rule_type":"required_when","columns":["approved_date"],"condition":"status = 'Approved'","severity":"error"}` |
| `value_when` | A column must equal a specific value when a condition is true. | one `columns` value, `condition`, `expected_value` | `{"rule_type":"value_when","condition":"student_status = 'Graduated'","columns":["is_active"],"expected_value":false,"severity":"error"}` |
| `expression_true` | No simpler rule can express the requirement. | `expression` | `{"rule_type":"expression_true","expression":"credits_attempted >= credits_earned","severity":"error"}` |

Backward-compatible names such as `unique_key`, `regex_format`, and `value_range` are accepted only as aliases inside the rule engine. New approved metadata should use the catalogue names above.

## How to choose a rule

1. Start with completeness rules (`not_null`, `null_rate_below`, `non_empty_string`).
2. Add uniqueness rules only where the business grain is clear.
3. Use accepted or blocked values for small controlled domains.
4. Use range, comparison, date, or freshness rules for measurable constraints.
5. Use cross-column and conditional rules for relationships within the same row.
6. Use `expression_true` only when no simpler rule type can express the requirement.

Set `severity="error"` when a failure should block unsafe or misleading output. Set `severity="warning"` when the issue should be visible in evidence but should not block the run.

## Set up a rule in `03_governance`

1. Select a catalogue table from the latest successful profile evidence.
2. Open `widget_review_dq_rules`.
3. Review the selected table columns and existing active/inactive rules.
4. Choose a rule type and select the required column or columns.
5. Enter the required parameters as JSON.
6. Add a plain-language description and choose warning or error severity.
7. Preview the generated JSON.
8. Save the rule as an approved active metadata event.

Every write to `METADATA_DQ_RULES` includes rule identity, table/column identity, rule JSON, severity, description, active status, review status, approver, approval time, AI suggestion evidence when available, append-only action type, and runtime audit fields.

## Edit, deactivate, and reactivate rules

`METADATA_DQ_RULES` is append-only. FabricOps does not physically delete DQ rule rows.

- Create appends `action_type="created"` with `is_active=true`.
- Update appends a new version with `action_type="updated"`.
- Delete in the UI appends `action_type="deactivated"` with `is_active=false`.
- Reactivate appends `action_type="reactivated"` with `is_active=true`.

For a selected table, the widget display shows rule ID, rule type, column list, parameter summary, severity, active/inactive status, review status, approver, approval time, last action, commit time, and description. Multi-column rules store the full column list in `rule_parameters_json.columns` even when `column_name` is a display string.

## AI suggestions

The AI suggestion action is advisory only. It uses selected table profile evidence such as column names, data types, null counts, distinct counts, min/max values, and distributions where available. The default prompt tells AI to suggest FabricOps-native DQ rules only, return JSON only, avoid unsupported rule types, include descriptions and required parameters, and prefer simple rules before `expression_true`.

AI suggestions are drafts. Reviewers can accept, edit, reject, or commit each suggestion, but FabricOps does not auto-approve AI output.

## How `02_pipeline` enforces rules

`02_pipeline` calls `enforce_dq_rules` for the runtime DataFrame. The helper reads `METADATA_DQ_RULES` from the configured metadata lakehouse target, resolves the newest version for each rule, keeps only active approved rules, evaluates them, and returns a guardrail result with status, checks, a tagged DataFrame, and summary fields for evidence.

Error-severity failures return `status="failed"` and `can_continue=false`. Warning-severity failures return `status="warning"` and `can_continue=true`.

## Schema guardrails are separate

Do not model schema rules such as required columns, expected schema, or datatype checks as DQ rules. Schema guardrails are a separate FabricOps layer and should remain in schema validation configuration.

## Source stability is separate

Do not model source stability checks as DQ rules. Source stability compares catalogue/profile evidence across runs and is handled by the source stability guardrail layer, not by `METADATA_DQ_RULES`.
