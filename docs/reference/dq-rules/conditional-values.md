# conditional_values

Checks a target column against a governed value set only when a condition on another column matches. The condition supports `=` or `!=`. `mode` is `allow` or `block`; `values` is a non-empty list.

```json
{"rule_type":"conditional_values","columns":["country","currency"],"condition_operator":"=","condition_value":"SG","mode":"allow","values":["SGD"]}
```
