# uniqueness

Checks duplicate keys. One column is a column-level rule; two or more columns form one table-level composite rule and are never split into per-column rules.

```json
{"rule_type":"uniqueness","columns":["order_id","line_id"]}
```
