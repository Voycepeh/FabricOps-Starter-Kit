# `required_when`

Require one or more target columns when a structured row condition matches.

## Configuration

| Field | Requirement |
|---|---|
| `columns` | One or more required target columns. |
| `condition_column` | Profiled column used by the condition. |
| `condition_operator` | One of `=`, `!=`, `>`, `>=`, `<`, or `<=`. |
| `condition_value` | Governed comparison value. |

```json
{
  "rule_type": "required_when",
  "columns": ["approved_date", "approved_by"],
  "condition_column": "status",
  "condition_operator": "=",
  "condition_value": "Approved"
}
```

The widget provides controlled condition fields; arbitrary SQL expressions are not accepted.
