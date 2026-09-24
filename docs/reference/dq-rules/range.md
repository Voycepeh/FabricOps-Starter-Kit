# `range`

Apply an optional minimum, maximum, and explicit inclusive boundaries to one comparable column.

```json
{"rule_type":"range","columns":["amount"],"minimum":0,"maximum":null,"minimum_inclusive":false,"maximum_inclusive":true}
```

Rules are authored against a Data Contract, persisted in `METADATA_GUARDRAIL` only through the normal human-controlled save workflow, and enforced deterministically by `check_dq()`.

[Back to the DQ rule reference](index.md)
