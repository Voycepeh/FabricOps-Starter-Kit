# completeness

Checks presence for one column. Configure `maximum_missing_percent` from 0 through 100 and explicitly set `treat_blank_as_missing`. Blank and whitespace text is only missing when that boolean is `true`.

```json
{"rule_type":"completeness","columns":["email"],"maximum_missing_percent":0,"treat_blank_as_missing":true}
```
