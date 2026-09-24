# value_set

Checks one column against an explicit set. `mode` is `allow` or `block`; `values` is a non-empty list.

```json
{"rule_type":"value_set","columns":["status"],"mode":"allow","values":["Open","Closed"]}
```
