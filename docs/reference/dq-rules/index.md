# DQ rule reference

FabricOps supports **11 lightweight DQ rule types** stored as `guardrail_type="dq"` rows in `METADATA_GUARDRAIL`.

The vocabulary is deliberately structured and governable. DQ rules use named parameters rather than arbitrary JSON expressions, Python callbacks, or plugin execution.

## Canonical rules

| Rule | Purpose | Canonical configuration |
|---|---|---|
| [`missing_values`](missing-values.md) | Limit the percentage of null values. A threshold of `0` is strict non-null enforcement. | one column; `maximum_null_percent` |
| [`blank_text`](blank-text.md) | Reject null, blank, and whitespace-only strings. | one column |
| [`unique_values`](unique-values.md) | Require each selected column to be unique independently. | one column per rule |
| [`unique_combination`](unique-combination.md) | Require a combined business key to be unique. | two or more ordered `columns` |
| [`allowed_values`](allowed-values.md) | Allow only an approved value set. | one column; `allowed_values` |
| [`blocked_values`](blocked-values.md) | Reject a governed list of forbidden values. | one column; `blocked_values` |
| [`value_range`](value-range.md) | Enforce one-sided or two-sided bounds for numeric, date, or other comparable values. | one column; optional `minimum` / `maximum` and inclusivity flags |
| [`text_pattern`](text-pattern.md) | Require populated strings to match a governed pattern. | one column; `pattern` |
| [`required_when`](required-when.md) | Require one or more target columns when a structured condition matches. | target `columns`; condition column, operator, and value |
| [`conditional_value`](conditional-value.md) | Require one target column to equal an expected value when a structured condition matches. | one target column; structured condition; `expected_value` |
| [`compare_columns`](compare-columns.md) | Compare two distinct ordered columns with a controlled operator. | two ordered `columns`; `operator` |

## Practical examples

### Strict non-null

Use `missing_values` with a zero threshold rather than a separate `not_null` rule:

```json
{"rule_type":"missing_values","columns":["student_id"],"maximum_null_percent":0}
```

### One-sided and two-sided ranges

`value_range` supports `>`, `>=`, `<`, `<=`, and bounded ranges through values and inclusivity flags:

```json
{
  "rule_type": "value_range",
  "columns": ["amount"],
  "minimum": 0,
  "minimum_inclusive": false,
  "maximum": null,
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
