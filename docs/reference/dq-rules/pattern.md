# `pattern`

Require populated structured text to match a governed regular expression. Null handling belongs to completeness.

```json
{"rule_type":"pattern","columns":["email"],"pattern":"^[^@]+@[^@]+$"}
```

Rules are authored against a Data Contract, persisted in `METADATA_GUARDRAIL` only through the normal human-controlled save workflow, and enforced deterministically by `check_dq()`.

[Back to the DQ rule reference](index.md)
