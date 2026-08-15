# DQ rule reference

FabricOps supports **11 lightweight DQ rule types** stored as `guardrail_type="dq"` rows in `METADATA_GUARDRAIL`.

The vocabulary is deliberately structured and governable. DQ rules use named parameters rather than arbitrary JSON expressions, Python callbacks, or plugin execution.

## Canonical rules

| Rule | Purpose | Canonical configuration |
|---|---|---|
| `null_rate_below` | Limit the percentage of null values. A threshold of `0` is strict non-null enforcement. | one column; `max_null_percent` |
| `non_empty_string` | Reject null, blank, and whitespace-only strings. | one column |
| `unique` | Require each selected column to be unique independently. | one column per rule |
| `unique_combination` | Require a combined business key to be unique. | two or more ordered `columns` |
| `accepted_values` | Allow only an approved value set. | one column; `allowed_values` |
| `not_in_values` | Reject a governed list of forbidden values. | one column; `blocked_values` |
| `between` | Enforce one-sided or two-sided bounds for numeric, date, or other comparable values. | one column; optional `minimum_value` / `maximum_value` and inclusivity flags |
| `regex_match` | Require populated strings to match a governed pattern. | one column; `regex_pattern` |
| `required_when` | Require one or more target columns when a structured condition matches. | target `columns`; condition column, operator, and value |
| `value_when` | Require one target column to equal an expected value when a structured condition matches. | one target column; structured condition; `expected_value` |
| `compare_columns` | Compare two distinct ordered columns with a controlled operator. | two ordered `columns`; `operator` |

## Practical examples

### Strict non-null

Use `null_rate_below` with a zero threshold rather than a separate `not_null` rule:

```json
{"rule_type":"null_rate_below","columns":["student_id"],"max_null_percent":0}
```

### One-sided and two-sided ranges

`between` supports `>`, `>=`, `<`, `<=`, and bounded ranges through values and inclusivity flags:

```json
{
  "rule_type": "between",
  "columns": ["amount"],
  "minimum_value": 0,
  "minimum_inclusive": false,
  "maximum_value": null,
  "maximum_inclusive": true
}
```

Date-like and other comparable values remain strings when that is their canonical value representation.

### Structured conditional rules

Conditional rules use controlled fields rather than free-form Spark SQL:

```json
{
  "rule_type": "required_when",
  "columns": ["approved_date", "approved_by"],
  "condition_column": "status",
  "condition_operator": "=",
  "condition_value": "Approved"
}
```

Supported conditional and column-comparison operators are `=`, `!=`, `>`, `>=`, `<`, and `<=`.

### Ordered column comparison

```json
{
  "rule_type": "compare_columns",
  "columns": ["end_date", "start_date"],
  "operator": ">="
}
```

Column order is meaningful: this rule checks `end_date >= start_date`.

!!! note "Freshness is a dedicated guardrail"
    Use [`check_freshness()`](../../api/reference/check_freshness.md) and the Freshness section of `widget_author_guardrails()`. Freshness is not duplicated as a DQ rule.

!!! important "No custom-expression rule"
    FabricOps intentionally does not support free-form SQL, arbitrary Python, or plugin execution in the lightweight DQ vocabulary.
