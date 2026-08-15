# `value_when`

Require one target column to equal an expected value when a structured row condition matches.

## Configuration

| Field | Requirement |
|---|---|
| `columns` | Exactly one target column. |
| `condition_column` | Profiled column used by the condition. |
| `condition_operator` | One of `=`, `!=`, `>`, `>=`, `<`, or `<=`. |
| `condition_value` | Governed comparison value. |
| `expected_value` | Required value for the target column when the condition matches. |

```json
{
  "rule_type": "value_when",
  "columns": ["is_active"],
  "condition_column": "status",
  "condition_operator": "=",
  "condition_value": "Graduated",
  "expected_value": false
}
```
