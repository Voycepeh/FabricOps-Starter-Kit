# Step 3: Review catalogue evidence and define guardrails

Run `03_review` in the Governance workspace to review catalogue evidence, add descriptions and classifications, and define guardrail intent before relying on active rules in future pipeline runs. Governance review starts from observed pipeline metadata, records governance decisions, and keeps approved intent separate from runtime outcomes.

![FabricOps governance review](../assets/fabricops-goverance-review.png)

## What to do

1. Open `03_review` after pipeline profile and catalogue evidence exists.
2. Select the governed table context from current catalogue evidence.
3. Review schema, freshness, profile behavior, data-quality, runtime result context, and enrichment records.
4. Add or refine business descriptions, classifications, stewardship context, schema enforcement expectations, data-quality guardrails, review notes, and guardrail fields exposed by the widgets.
5. Approve, reject, replace, deactivate, or request follow-up using the review widgets.
6. Rerun `02_pipeline` when you want active guardrails enforced against fresh data.

## Review responsibilities

`03_review` reviews intent; it does not rewrite observed physical evidence. Keep the metadata responsibilities separated:

| Metadata area | Governance responsibility |
| ------------- | ------------------------- |
| `METADATA_DATA_CATALOGUE` | Read observed table and column profiles as evidence for review. |
| `METADATA_ENRICHMENT` | Append descriptive enrichment and lifecycle decisions. |
| `METADATA_GUARDRAIL` | Approve, reject, replace, deactivate, or update executable rule intent. |
| `METADATA_GUARDRAIL_RESULTS` | Inspect runtime outcomes as context; do not edit them as review decisions. |

Active guardrail records can be consumed by `02_pipeline`. Draft, pending, rejected, inactive, and superseded records are excluded from active runtime consumption unless the workflow explicitly applies an operationally active post-review state.

## Expected evidence

Guardrail and enrichment review decisions are appended to their metadata tables, and active rules become available to runtime enforcement. Future `02_pipeline` runs depend on these active records to evaluate approved expectations.

Previous: [Step 2: Run the first Development pipeline](run-pipeline.md).

Next, continue to [Step 4: Rerun the Development pipeline with guardrails](run-pipeline-with-guardrails.md).

See also: [METADATA_GUARDRAIL](../reference/metadata/metadata_guardrail.md) and [List of DQ Rules](../reference/dq-rules/index.md).
