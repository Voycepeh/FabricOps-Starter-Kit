# `completeness`

Bound missing values for one column. Blank or whitespace-only text is included only when `treat_blank_as_missing` is true.

```json
{"rule_type":"completeness","columns":["customer_email"],"maximum_missing_percent":0,"treat_blank_as_missing":true}
```

Rules are authored against a Data Contract, persisted in `METADATA_GUARDRAIL` only through the normal human-controlled save workflow, and enforced deterministically by `check_dq()`.

[Back to the DQ rule reference](index.md)
