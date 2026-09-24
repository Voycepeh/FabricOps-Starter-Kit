# DQ rule reference

FabricOps supports **six governed DQ rule families** stored in `METADATA_GUARDRAIL`. Rules use structured parameters rather than arbitrary SQL, Python, executable expressions, or plugins.

| Rule | Purpose | Canonical configuration |
|---|---|---|
| [`completeness`](completeness.md) | Bound missing values, optionally including blank text. | one column; `maximum_missing_percent`; `treat_blank_as_missing` |
| [`uniqueness`](uniqueness.md) | Enforce a single-column or composite key. | one or more ordered `columns` |
| [`value_set`](value-set.md) | Allow or block a stable governed value set. | one column; `mode`; `values` |
| [`range`](range.md) | Enforce defensible comparable bounds. | one column; bounds and inclusivity flags |
| [`pattern`](pattern.md) | Match semantically structured text. | one column; `pattern` |
| [`compare`](compare.md) | Compare two columns with a controlled operator. | two ordered `columns`; `operator` |

## Authoring boundary

FabricOps DQ expresses understandable integrity expectations. Complex conditional business logic belongs in project-owned PySpark transformations. A project can derive and persist a validation or business-state column, then govern that output with one of these simple rules.

The **Suggest rules** action in `widget_data_contract()` uses Microsoft Fabric AI Functions and user-editable family prompts from `GOVERNANCE_CONFIG.ai_enrichment.dq_prompts`. It receives governed Catalogue, Enrichment, and profile summaries—never a new raw-data sample. Its validated output only populates editable controls. A human must review, select, edit, and use the normal save/freeze workflow; AI never persists, approves, freezes, activates, or enforces a rule.

!!! important "Deterministic enforcement"
    `check_dq()` evaluates persisted, reviewed rules with deterministic PySpark. AI is an authoring assistant only.
