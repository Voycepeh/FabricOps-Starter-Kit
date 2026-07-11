# Review Guardrails

Run `03_governance` to review enrichment and guardrail intent before relying on active rules in future pipeline runs. Governance review starts from observed pipeline metadata, records governance decisions, and keeps approved intent separate from runtime outcomes.

![FabricOps governance review](../assets/fabricops-goverance-review.png)

## What to do

1. Open `03_governance` after pipeline profile and guardrail evidence exists.
2. Select the governed table context from current catalogue evidence.
3. Review schema, freshness, profile behavior, DQ, runtime result context, and enrichment records.
4. Add or refine business descriptions, classifications, stewardship context, review notes, and guardrail fields exposed by the widgets.
5. Approve, reject, replace, deactivate, or request follow-up using the review widgets.
6. Rerun `02_pipeline` when you want active guardrails enforced against fresh data.

## Review responsibilities

`03_governance` reviews intent; it does not rewrite observed physical evidence. Keep the metadata responsibilities separated:

| Metadata area | Governance responsibility |
| ------------- | ------------------------- |
| `METADATA_DATA_CATALOGUE` | Read observed table and column profiles as evidence for review. |
| `METADATA_ENRICHMENT_RULES` | Append descriptive enrichment and lifecycle decisions. |
| `METADATA_GUARDRAIL_RULES` | Approve, reject, replace, deactivate, or update executable rule intent. |
| `METADATA_GUARDRAIL_RESULTS` | Inspect runtime outcomes as context; do not edit them as review decisions. |

Active guardrail records can be consumed by `02_pipeline`. Draft, pending, rejected, inactive, and superseded records are excluded from active runtime consumption unless the workflow explicitly applies an operationally active post-review state.

## Expected evidence

Guardrail and enrichment review decisions are appended to their metadata tables, and active rules become available to runtime enforcement. Future `02_pipeline` runs depend on these active records to evaluate approved expectations.

Next, continue to [Explore Metadata Outputs](explore-metadata-outputs.md).

See also: [METADATA_GUARDRAIL_RULES](../reference/metadata/metadata_guardrail_rules.md) and [List of DQ Rules](../reference/dq-rules/index.md).
