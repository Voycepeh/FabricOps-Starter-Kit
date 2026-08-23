# Step 3: Enrich the Data Catalogue and Author Guardrails

**Return to `01_governance` after `02_pipeline` has produced Data Catalogue and Data Profiled evidence. Governance reads that evidence, enriches it, and authors Guardrails.**

## High-level flow

```text
Review Engineering evidence → Add Enrichment → Author Guardrails → Save Governance intent
```

## Before you begin

Confirm that Step 2 completed successfully and the relevant Data Catalogue and Data Profiled records exist in the configured metadata target.

???+ success "Live — Review Engineering evidence"

    1. Open `01_governance` in the Governance workspace.
    2. Select the governed dataset.
    3. Inspect the Data Catalogue and Data Profiled evidence written by `02_pipeline`.

    Governance reads the observed table and column evidence. It does not create a second copy of those records.

???+ success "Live — Add Enrichment"

    Add or refine Enrichment such as business descriptions, classifications, and stewardship context.

    `METADATA_ENRICHMENT` attaches business context to the canonical Data Catalogue identity rather than replacing observed Engineering metadata.

???+ success "Live — Author Guardrails"

    Author schema, freshness, profile-behaviour, and data-quality Guardrails for the ETL workflow, then save the Governance records.

    | Metadata area | Governance responsibility |
    | --- | --- |
    | `METADATA_DATA_CATALOGUE` | Read the observed table and column evidence written by `02_pipeline`. |
    | `METADATA_ENRICHMENT` | Add descriptive business context and classifications. |
    | `METADATA_GUARDRAIL` | Author executable Guardrail intent for the ETL workflow. |
    | `METADATA_GUARDRAIL_RESULTS` | Inspect runtime outcomes written by Engineering; do not edit them as observed evidence. |

??? info "Details — Why observed evidence and Governance intent stay separate"

    Profiling can discover physical table and column structure, but it cannot discover business meaning, stewardship intent, classifications, or Governance rules.

    ```text
    Engineering observation
    → Data Catalogue / Data Profiled / Data Lineage / Guardrail Results

    Governance authoring
    → Enrichment / Guardrails / Data Agreement / Data Contract
    ```

??? info "Details — Table Guardrails versus DQ rules"

    Schema, Freshness, and Changes Guardrails operate at the table boundary and can often be evaluated before reading all business rows. DQ rules evaluate the actual DataFrame and may also record row-level failures.

## Expected result

You should now have reviewed Engineering evidence, authored Enrichment, and authored Guardrails ready for the newer guarded `02_pipeline` path to evaluate.

**Previous:** [Step 2: Run the Development pipeline](02-run-pipeline.md)  
**Next:** [Step 4: Rerun the Development pipeline with Guardrails](04-run-pipeline-with-guardrails.md)

See also: [METADATA_ENRICHMENT](../reference/metadata/metadata_enrichment.md), [METADATA_GUARDRAIL](../reference/metadata/metadata_guardrail.md), and [List of DQ Rules](../reference/dq-rules/index.md).
