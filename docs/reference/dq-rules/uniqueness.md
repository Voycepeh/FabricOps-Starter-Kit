# `uniqueness`

Require one column or an ordered combination of columns to be unique.

```json
{"rule_type":"uniqueness","columns":["order_id","line_number"]}
```

Rules are authored against a Data Contract, persisted in `METADATA_GUARDRAIL` only through the normal human-controlled save workflow, and enforced deterministically by `check_dq()`.

[Back to the DQ rule reference](index.md)
