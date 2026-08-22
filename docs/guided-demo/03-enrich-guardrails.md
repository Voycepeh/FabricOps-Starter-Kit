# Step 3: Enrich the Data Catalogue and Author Guardrails

**Return to `01_governance` after `02_pipeline` has produced the Data Catalogue and Data Profiled evidence. Governance reads that evidence, enriches it, and authors Guardrails.**

## Before you begin

Confirm that Step 2 completed successfully and the relevant Data Catalogue and Data Profiled records exist in the configured metadata target.

## What to do

1. Open `01_governance` in the Governance workspace.
2. Select the governed dataset.
3. Inspect the Data Catalogue and Data Profiled evidence written by `02_pipeline`.
4. Add or refine Enrichment such as business descriptions, classifications, and stewardship context.
5. Author schema, freshness, profile-behaviour, and data-quality Guardrails for the ETL workflow.
6. Save the authored Governance records.

## Governance responsibilities

| Metadata area | Governance responsibility |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Read the observed table and column evidence written by `02_pipeline`. |
| `METADATA_ENRICHMENT` | Add descriptive business context and classifications. |
| `METADATA_GUARDRAIL` | Author executable Guardrail intent for the ETL workflow. |
| `METADATA_GUARDRAIL_RESULTS` | Inspect runtime outcomes written by Engineering; do not edit them as observed evidence. |

!!! important "Keep observed evidence and Governance intent separate"

    Governance does not create another copy of the Data Catalogue or Data Profiled records. It reads Engineering evidence and adds Enrichment and Guardrail intent around it.

??? info "Why FabricOps separates observed evidence from authored Governance metadata"

    Profiling can discover the physical table and column structure, but it cannot discover business meaning, stewardship intent, classifications, or the rules that Governance wants Engineering to enforce.

    FabricOps therefore keeps the responsibilities separate:

    ```text
    Engineering observation
    → Data Catalogue / Data Profiled / Data Lineage / Guardrail Results

    Governance authoring
    → Enrichment / Guardrails / Data Agreement / Data Contract
    ```

    This avoids rewriting observed facts as manually maintained Governance records. Enrichment attaches business context to the canonical Data Catalogue identity, while Guardrails define executable intent around that observed asset.

??? info "Why table Guardrails and DQ rules are authored separately"

    Schema, Freshness, and Changes Guardrails operate at the table boundary and can often be evaluated before reading all business rows. DQ rules evaluate the actual DataFrame and may also record row-level failures.

    Keeping those authoring paths separate makes the distinction visible: table observation and structural checks are not the same thing as row-level data-quality validation, even though both contribute to the governed ETL run.

## Expected result

You should now have:

- reviewed Engineering evidence
- authored Enrichment records
- authored Guardrails ready for `02_pipeline` to evaluate

**Previous:** [Step 2: Run the Common Pipeline Patterns](02-run-pipeline.md)  
**Next:** [Step 4: Rerun the Development pipeline with Guardrails](04-run-pipeline-with-guardrails.md)

See also: [METADATA_ENRICHMENT](../reference/metadata/metadata_enrichment.md), [METADATA_GUARDRAIL](../reference/metadata/metadata_guardrail.md), and [List of DQ Rules](../reference/dq-rules/index.md).
