# Step 3: Enrich the Data Catalogue and define guardrails

Run `01_governance` after `02_pipeline` has profiled the ETL inputs and outputs. `02_pipeline` writes the Data Catalogue, Profile, and supporting technical evidence into metadata; Governance reads that evidence rather than creating a separate copy.

## What to do

1. Open `01_governance` after pipeline catalogue and profile evidence exists.
2. Select the governed dataset and inspect the Catalogue and Profile evidence written by `02_pipeline`.
3. Add or refine business descriptions, classifications, stewardship context, and other Data Catalogue enrichment.
4. Define schema, freshness, profile-behaviour, and data-quality guardrails for the ETL workflow.
5. Rerun `02_pipeline` so Engineering can re-validate the workflow with those guardrails.

## Governance responsibilities

Keep observed Engineering evidence separate from Governance enrichment and guardrail intent:

| Metadata area | Governance responsibility |
| ------------- | ------------------------- |
| `METADATA_DATA_CATALOGUE` | Read the observed table and column evidence written by `02_pipeline`. |
| `METADATA_ENRICHMENT` | Add descriptive business context and classifications. |
| `METADATA_GUARDRAIL` | Define executable guardrail intent for the ETL workflow. |
| `METADATA_GUARDRAIL_RESULTS` | Inspect runtime outcomes written by Engineering; do not edit them as observed evidence. |

## Expected evidence

Governance enrichment and guardrail intent are stored in the configured metadata target. The observed Catalogue and Profile evidence remains owned by the `02_pipeline` workflow.

Previous: [Step 2: Run the first Development pipeline](02-run-pipeline.md).

Next, continue to [Step 4: Rerun the Development pipeline with guardrails](04-run-pipeline-with-guardrails.md).

See also: [METADATA_ENRICHMENT](../reference/metadata/metadata_enrichment.md), [METADATA_GUARDRAIL](../reference/metadata/metadata_guardrail.md), and [List of DQ Rules](../reference/dq-rules/index.md).
