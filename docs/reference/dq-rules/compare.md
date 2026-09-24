# `compare`

Compare two distinct ordered columns with one of `=`, `!=`, `>`, `>=`, `<`, or `<=`.

```json
{"rule_type":"compare","columns":["end_date","start_date"],"operator":">="}
```

Rules are authored against a Data Contract, persisted in `METADATA_GUARDRAIL` only through the normal human-controlled save workflow, and enforced deterministically by `check_dq()`.

[Back to the DQ rule reference](index.md)
