# Governance review

FabricOps separates operational activation from formal governance review.

Engineering users can create <span class="glossary-term" title="Reviewed descriptive metadata such as business meaning, ownership, sensitivity, classification, and usage context.">enrichment</span> and <span class="glossary-term" title="A check that evaluates schema, freshness, profile behavior, or data quality during a pipeline run.">guardrail</span> records from 02_pipeline. They may save records as drafts, submit them for governance review, or apply them immediately when pipeline continuity requires it. Immediate application makes the record active, but marks it as active pending governance review.

Formal review happens only in 03_governance. Governance users can approve, reject, replace, deactivate, or supersede records; this notebook records governance decisions for table governance history. Replacing a record does not overwrite history; it creates a new version and marks the previous version as superseded.

Enforcement in 02_pipeline consumes active guardrail records. Governance review determines whether those records are approved, rejected, or superseded.

## Lifecycle fields

`activation_state` controls whether a metadata record affects runtime:

- `active` records can be consumed by runtime.
- `pending` records are awaiting formal review and are not consumed by runtime.
- `inactive` records are drafts, rejected, inactive, or superseded and are not consumed by runtime.

`is_active` is derived from `activation_state == "active"` where possible.

`review_state` captures lifecycle and review meaning:

- `draft`
- `pending_governance_review`
- `active_pending_governance_review`
- `governance_approved`
- `rejected_by_governance`
- `superseded`
- `inactive`

## Notebook ownership

`02_pipeline` reads profiles from `METADATA_DATA_CATALOGUE` and is for engineering authoring. It can create draft, pending governance review, or active pending governance review records, but it cannot formally approve or reject enrichment or guardrail records.

`03_governance` is the formal review notebook. It reads review history from `METADATA_ENRICHMENT_RULES` and `METADATA_GUARDRAIL_RULES`, and appends formal review outcomes back to those same history tables. It does not write enforcement results; 02_pipeline runtime outcomes remain owned by `METADATA_GUARDRAIL_RESULTS`.

03_governance is structured as a step by step review notebook. Each widget is placed in its own section and code cell so governance users can run target selection, enrichment authoring, guardrail authoring, and formal review independently.

## Formal review actions

The formal review widget is `widget_review_table_governance`. For the selected table, governance reviewers can review enrichment and guardrail records in sections for records needing governance review, currently active records, rejected or inactive records, and superseded history.

Supported formal actions are:

- Approve
- Approve and activate
- Reject
- Replace
- Deactivate
- View history

Replace is append-only: FabricOps appends a superseded row for the previous record and appends a new active `governance_approved` version for the replacement.

## Runtime filtering

Enforcement consumes active guardrail records based on `activation_state` or `is_active`. This includes active engineering-applied records with `review_state = active_pending_governance_review` because those records are operationally active by design.

Draft, pending, rejected, inactive, and superseded records are excluded from runtime consumption.

## Review history sources

Review history is derived from append-only rows in:

- `METADATA_ENRICHMENT_RULES`
- `METADATA_GUARDRAIL_RULES`

FabricOps does not use `METADATA_COLUMN_CONTEXT`, `METADATA_COLUMN_CLASSIFICATION`, or `METADATA_GOVERNANCE_REVIEWS` as formal review output tables.


## Key callable references

- [widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/)
- [widget_enrich_table_metadata](../api/reference/widget_enrich_table_metadata/)
- [widget_author_guardrail_rules](../api/reference/widget_author_guardrail_rules/)
- [widget_review_table_governance](../api/reference/widget_review_table_governance/)
- [widget_review_guardrail_governance](../api/reference/widget_review_guardrail_governance/)
