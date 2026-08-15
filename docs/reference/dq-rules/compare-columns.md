# `compare_columns`

Compare two distinct ordered columns with a controlled operator.

## Configuration

| Field | Requirement |
|---|---|
| `columns` | Exactly two distinct column names. The first is Column A and the second is Column B. |
| `operator` | One of `=`, `!=`, `>`, `>=`, `<`, or `<=`. |

```json
{
  "rule_type": "compare_columns",
  "columns": ["end_date", "start_date"],
  "operator": ">=",
  "severity": "error"
}
```

This example means `end_date >= start_date`. Reversing the columns or changing the operator creates a different canonical rule identity.
