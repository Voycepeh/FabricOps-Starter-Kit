# `value_range`

Keep one comparable column inside an approved one-sided or two-sided range.

## Configuration

| Field | Requirement |
|---|---|
| `columns` | Exactly one column. |
| `minimum` | Optional lower bound. Numeric, date-like, and other comparable values are supported. |
| `minimum_inclusive` | `true` for `>=`; `false` for `>`. Defaults to `true`. |
| `maximum` | Optional upper bound. |
| `maximum_inclusive` | `true` for `<=`; `false` for `<`. Defaults to `true`. |

At least one bound is required.

```json
{
  "rule_type": "value_range",
  "columns": ["percentage"],
  "minimum": 0,
  "minimum_inclusive": true,
  "maximum": 100,
  "maximum_inclusive": true
}
```

Use the same rule for date-like comparable values; there is no separate date-range rule.
