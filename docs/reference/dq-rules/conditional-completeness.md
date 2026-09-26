# conditional_completeness

Requires a target column to be populated only when a condition on another column matches. The condition supports `=` or `!=`. Set `treat_blank_as_missing` explicitly to control whether blank or whitespace text counts as missing.

```json
{"rule_type":"conditional_completeness","columns":["status","approved_date"],"condition_operator":"=","condition_value":"Approved","treat_blank_as_missing":true}
```
