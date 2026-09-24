# column_relationship

Compares two different columns row by row with `=`, `!=`, `>`, `>=`, `<`, or `<=`. Both-null values pass equality; one-null ordered comparisons fail. This is explicitly authored at table level and is not AI inferred.

```json
{"rule_type":"column_relationship","columns":["end_date","start_date"],"operator":">="}
```
