# `value_set`

Apply an allow-list or block-list to one stable categorical domain.

```json
{"rule_type":"value_set","columns":["status"],"mode":"allow","values":["Pending","Paid","Shipped"]}
```

Rules are authored against a Data Contract, persisted in `METADATA_GUARDRAIL` only through the normal human-controlled save workflow, and enforced deterministically by `check_dq()`.

[Back to the DQ rule reference](index.md)
