# Governance Review

Governance Review is the point where pipeline evidence becomes reviewed metadata. `02_pipeline` records metadata evidence during normal runs, and `03_governance` turns that evidence into explicit human approvals for business context, data-quality expectations, and sensitivity/classification.

The operating model is intentionally simple:

- `02_pipeline` records evidence such as catalogue profile rows, schema/profile guardrail outcomes, DQ outcomes, lineage, and run summaries.
- `03_governance` reviews the evidence and appends approved metadata decisions.
- AI can suggest useful drafts, but humans approve what becomes governed metadata.
- Metadata stores the approved decisions.
- Later pipeline runs load and enforce the approved metadata where relevant.

This keeps FabricOps metadata-driven and junior-friendly: the pipeline does not hide governance decisions in code, and the governance notebook does not become the runtime enforcement layer.

## What `03_governance` uses

The Governance Review notebook starts from the latest successful catalogue evidence in `METADATA_DATA_CATALOGUE`. For the selected table, reviewers can inspect the table identity, profile run, environment, dataset, table name, column names, data types, row counts, null counts, distinct counts, min/max values, distributions where available, and prior guardrail evidence recorded by pipeline runs.

That evidence answers questions such as:

- Which table and profile run are being reviewed?
- Which columns exist in the latest successful profile?
- What do the observed data types, null rates, distinct counts, and min/max values suggest?
- Did the most recent pipeline run pass schema, stability, and DQ guardrails?
- Is there enough evidence for a reviewer to approve business metadata safely?

## What reviewers approve

`03_governance` is responsible for append-only human decisions. Reviewers approve:

| Review area | Metadata table | What is approved |
|---|---|---|
| Business context | `METADATA_COLUMN_CONTEXT` | Human-readable meaning, notes, and context for columns. |
| DQ expectations | `METADATA_DQ_RULES` | Active approved data-quality rules for a table or columns. |
| Sensitivity/classification | `METADATA_COLUMN_CLASSIFICATION` | Sensitivity labels, personal-data classification, identifier type, and handling requirements. |
| Governance outcome | `METADATA_GOVERNANCE_REVIEWS` | Optional final review outcome based on evidence, blockers, and warnings. |

AI suggestions are advisory drafts only. A human reviewer must accept, edit, reject, or commit each suggestion before it becomes approved metadata.

## Human review workflow

A typical review flow is:

1. Select a profiled catalogue table with `widget_select_catalogue_table`.
2. Load profile rows for that selection with `load_catalogue_profile_rows`.
3. Review or edit business context using the column context workflow.
4. Review or edit DQ expectations using `widget_review_dq_rules`.
5. Review sensitivity and personal-data classification.
6. Commit approved rows with `record_table_governance`.
7. Optionally write a governance review outcome after checking related evidence.

The review notebook writes metadata only after explicit commit actions. Draft rows, AI suggestions, and uncommitted edits remain advisory and are not enforced by later pipeline runs.

## DQ expectations in Governance Review

`03_governance` owns DQ rule authoring, review, and approval. `METADATA_DQ_RULES` stores approved DQ rules as append-only metadata history. `02_pipeline` loads the newest active approved DQ rules for the selected table, and `enforce_dq_rules` enforces them at runtime before unsafe or misleading output is written.

DQ rule authoring stays metadata-driven. FabricOps does not expose one public callable per DQ rule, and it does not require Great Expectations or dbt at runtime.

### Approved DQ rule catalogue

!!! success "23 native DQ rule types"
    FabricOps currently supports **23 native DQ rule types**. These rules are reviewed as metadata, stored in `METADATA_DQ_RULES`, and enforced by `enforce_dq_rules` before unsafe or misleading output is written. Use targeted rules where possible, and reserve **Custom expression** (`expression_true`) for cases that cannot be captured by a smaller built-in rule.

Actual enforcement depends on the approved active metadata rows present for a table in `METADATA_DQ_RULES`; not every dataset has all 23 rule types enabled. The rules are FabricOps-native and do not require Great Expectations or dbt at runtime.

<div class="grid cards" markdown>

-   **`unique_combination`**

    Composite grain checks that prevent duplicate business keys such as `(order_id, line_no)`.

-   **`accepted_values`**

    Controlled value sets for statuses, categories, flags, and other governed domains.

-   **`regex_match`**

    Pattern validation for emails, codes, identifiers, and other formatted strings.

-   **`value_when`**

    Conditional business logic such as “when country is SG, currency must be SGD.”

</div>

Use the smallest FabricOps-native rule that expresses the requirement. Prefer explicit rule types such as `not_null`, `accepted_values`, or `between` before the Custom expression escape hatch (`expression_true`).

| Rule | When to use it | Required parameters | Example JSON |
|---|---|---|---|
| `not_null` | One or more columns must not be actual null values. Blank strings are handled by `non_empty_string`. | `columns` | `{"rule_type":"not_null","columns":["student_id"],"severity":"error"}` |
| `null_rate_below` | A column null percentage must stay below a threshold; blank strings are not counted as nulls. | one `columns` value, `max_null_percent` | `{"rule_type":"null_rate_below","columns":["email"],"max_null_percent":5,"severity":"warning"}` |
| `non_empty_string` | String columns must not be null, blank, or whitespace-only. | `columns` | `{"rule_type":"non_empty_string","columns":["programme_name"],"severity":"error"}` |
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
| `expression_true` — Custom expression | Built-in FabricOps rule for trusted reviewers when no named rule can express the requirement. It accepts an `expression` parameter containing a boolean expression and fails rows where that expression evaluates false. This is not a custom Python plugin rule. | `expression` | `{"rule_type":"expression_true","expression":"credits_attempted >= credits_earned","severity":"error"}` |

FabricOps uses one canonical DQ rule vocabulary. Old or external rule names are not accepted. Approved metadata should use only the rule names listed in this catalogue.

### DQ rules in action

These examples show how approved active metadata rows are evaluated by `enforce_dq_rules`. FabricOps tags and reports DQ outcomes; v1 does not filter failed rows out of the DataFrame. Error severity stops unsafe downstream writes, while warning severity records evidence and allows the run to continue.

#### `unique_combination`

**What the rule checks:** each `order_id` + `line_no` pair appears once.

**Data applicability:** Composite business keys or table-grain columns that should be unique together.

**Example column(s) used here:** `order_id`, `line_no`

**Parameters:**

```yaml
rule_type: unique_combination
columns: ["order_id", "line_no"]
severity: error
```

**Sample input rows**

| order_id | line_no | product | qty |
|---|---:|---|---:|
| A100 | 1 | Pen | 2 |
| A100 | 2 | Book | 1 |
| A101 | 1 | Bag | 1 |
| A100 | 1 | Eraser | 1 |

**Rows that pass**

| order_id | line_no | Why |
|---|---:|---|
| A100 | 2 | Combination appears once. |
| A101 | 1 | Combination appears once. |

**Rows that fail**

| order_id | line_no | Why |
|---|---:|---|
| A100 | 1 | Combination appears more than once. |

**Why it matters:** duplicate grain rows can double-count quantities, revenue, or downstream facts.

#### `accepted_values`

**What the rule checks:** `status` uses only the governed customer lifecycle values.

**Data applicability:** Governed categorical, status, flag, code, or other controlled-domain columns.

**Example column(s) used here:** `status`

**Parameters:**

```yaml
rule_type: accepted_values
columns: ["status"]
allowed_values: ["new", "active", "inactive", "closed"]
severity: warning
```

**Sample input rows**

| customer_id | status |
|---|---|
| C001 | new |
| C002 | active |
| C003 | inactive |
| C004 | pending |

**Rows that pass**

| customer_id | status |
|---|---|
| C001 | new |
| C002 | active |
| C003 | inactive |

**Rows that fail**

| customer_id | status | Why |
|---|---|---|
| C004 | pending | `pending` is not in the allowed value list. |

**Why it matters:** controlled domains keep reports, filters, and case logic stable.

#### `regex_match`

**What the rule checks:** populated email values look like an address with text on both sides of `@` and a dot in the domain.

**Data applicability:** String or string-castable columns with a known text pattern.

**Example column(s) used here:** `email`

**Parameters:**

```yaml
rule_type: regex_match
columns: ["email"]
regex_pattern: "^[^@]+@[^@]+\\.[^@]+$"
severity: warning
```

**Sample input rows**

| staff_id | email |
|---|---|
| S001 | amy@nus.edu.sg |
| S002 | ben.lee@company.com |
| S003 | charlie.company.com |
| S004 | diana@ |

**Rows that pass**

| staff_id | email |
|---|---|
| S001 | amy@nus.edu.sg |
| S002 | ben.lee@company.com |

**Rows that fail**

| staff_id | email | Why |
|---|---|---|
| S003 | charlie.company.com | Missing `@`. |
| S004 | diana@ | Missing domain after `@`. |

**Why it matters:** pattern checks catch malformed identifiers before users rely on them.

#### `value_when`

**What the rule checks:** Singapore transactions must use SGD.

**Data applicability:** Columns whose expected value depends on conditional business logic in the same row.

**Example column(s) used here:** `currency`

**Parameters:**

```yaml
rule_type: value_when
columns: ["currency"]
condition: "country_code = 'SG'"
expected_value: "SGD"
severity: error
```

**Sample input rows**

| txn_id | country_code | currency |
|---|---|---|
| T001 | SG | SGD |
| T002 | US | USD |
| T003 | SG | USD |
| T004 | SG | null |

**Rows that pass**

| txn_id | country_code | currency | Why |
|---|---|---|---|
| T001 | SG | SGD | Required value is present. |
| T002 | US | USD | Condition is false, so the rule does not apply. |

**Rows that fail**

| txn_id | country_code | currency | Why |
|---|---|---|---|
| T003 | SG | USD | `country_code = 'SG'` requires `currency = 'SGD'`. |
| T004 | SG | null | Null is not null-safe equal to `SGD`. |

**Why it matters:** conditional checks encode business rules that simple column-level checks cannot express.

### How to choose a DQ rule

1. Start with completeness rules (`not_null`, `null_rate_below`, `non_empty_string`).
2. Add uniqueness rules only where the business grain is clear.
3. Use accepted or blocked values for small controlled domains.
4. Use range, comparison, date, or freshness rules for measurable constraints.
5. Use cross-column and conditional rules for relationships within the same row.
6. Use `expression_true` only when no simpler rule type can express the requirement. It accepts a Spark SQL boolean expression, and only trusted reviewers should approve expression rules.

Set `severity="error"` when a failure should block unsafe or misleading output. Set `severity="warning"` when the issue should be visible in evidence but should not block the run.

### Set up a DQ rule in `03_governance`

1. Select a catalogue table from the latest successful profile evidence.
2. Open `widget_review_dq_rules`.
3. Review the selected table columns and existing active/inactive rules.
4. Choose a rule type and select the required column or columns.
5. Enter the required parameters as JSON.
6. Add a plain-language description and choose warning or error severity.
7. Preview the generated JSON.
8. Save the rule as an approved active metadata event.

Every write to `METADATA_DQ_RULES` includes rule identity, table/column identity, rule JSON, severity, description, active status, review status, approver, approval time, AI suggestion evidence when available, append-only action type, and runtime audit fields.

### Edit, deactivate, and reactivate DQ rules

`METADATA_DQ_RULES` is append-only. FabricOps does not physically delete DQ rule rows.

- Create appends `action_type="created"` with `is_active=true`.
- Update appends a new version with `action_type="updated"`.
- Delete in the UI appends `action_type="deactivated"` with `is_active=false`.
- Reactivate appends `action_type="reactivated"` with `is_active=true`.

For a selected table, the widget display shows rule ID, rule type, column list, parameter summary, severity, active/inactive status, review status, approver, approval time, last action, commit time, and description. Multi-column rules store the full column list in `rule_parameters_json.columns` even when `column_name` is a display string.

### AI suggestions for DQ rules

The AI suggestion action is advisory only. It uses selected table profile evidence such as column names, data types, null counts, distinct counts, min/max values, and distributions where available. The default prompt tells AI to suggest FabricOps-native DQ rules only, return JSON only, avoid unsupported rule types, include descriptions and required parameters, and prefer simple named rules before `expression_true`.

AI suggestions are drafts. Reviewers can accept, edit, reject, or commit each suggestion, but FabricOps does not auto-approve AI output.

## How approved metadata returns to the pipeline

Approved metadata affects later runs only after it is written to metadata tables.

- Approved business context and classification are available as metadata evidence for downstream reporting, handover, and governance review.
- Approved active DQ rules are read by `02_pipeline` when it calls `enforce_dq_rules`.
- `enforce_dq_rules` reads `METADATA_DQ_RULES` from the configured metadata lakehouse target, resolves the newest version for each rule, keeps only active approved rules, evaluates them, and returns a guardrail result with status, checks, a tagged DataFrame, and summary fields for evidence.

Error-severity DQ failures return `status="failed"` and `can_continue=false`. Warning-severity DQ failures return `status="warning"` and `can_continue=true`.

## What this page is not

Governance Review is not a full data product platform, an external DQ framework wrapper, or a replacement for normal pipeline engineering. It does not move DQ authoring into `02_pipeline`, expose one public Python function per rule, or require Great Expectations or dbt at runtime.

### Schema guardrails are separate

Do not model schema rules such as required columns, expected schema, or datatype checks as DQ rules. Schema guardrails are a separate FabricOps layer and should remain in schema validation configuration.

### Source stability is separate

Do not model source stability checks as DQ rules. Source stability compares catalogue/profile evidence across runs and is handled by the source stability guardrail layer, not by `METADATA_DQ_RULES`.
