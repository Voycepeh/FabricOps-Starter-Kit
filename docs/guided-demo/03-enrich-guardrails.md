# Step 3: Enrich the Data Catalogue and Author Guardrails

**Return to `01_governance` after `02_pipeline` has produced Data Catalogue and Data Profiled records. Governance reads those records, enriches the Data Catalogue, and authors Guardrails.**

!!! info "Key concepts for this step"

    [**Enrichment**](../glossary.md#enrichment) — business and governance information added after technical metadata has been captured.  
    [**Data Sensitivity**](../glossary.md#data-sensitivity) — how carefully data should be handled based on confidentiality, privacy, or risk.  
    [**Data Quality**](../glossary.md#data-quality) — the governed expectations data must meet for its intended use.  
    [**Guardrails**](../glossary.md#guardrails) — the governed rules FabricOps applies to data and pipelines.

    These concepts are the Governance focus for this step. Open the [Glossary](../glossary.md) only when another term becomes relevant.

## High-level flow

```text
Read METADATA_DATA_CATALOGUE + METADATA_DATA_PROFILED
→ Write METADATA_ENRICHMENT
→ Write METADATA_GUARDRAIL
```

## Before you begin

Confirm that Step 2 completed successfully and the relevant `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED` records exist in the configured metadata target.

???+ success "Live — Review Engineering records"

    1. Open `01_governance` in the Governance workspace.
    2. Select the governed dataset.
    3. Inspect the `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED` records written by `02_pipeline`.

    Governance reads those records from the shared metadata store. It does not create a second copy of them.

???+ success "Live — Add Enrichment"

    Add or refine Enrichment such as business descriptions, classifications, and stewardship context.

    `METADATA_ENRICHMENT` attaches business context to the canonical `METADATA_DATA_CATALOGUE` identity rather than replacing the Engineering-written records.

???+ success "Live — Author Guardrails"

    Author schema, freshness, profile-behaviour, and Data Quality Guardrails for the ETL workflow, then save the Governance records.

    | Metadata table | Governance responsibility |
    | --- | --- |
    | `METADATA_DATA_CATALOGUE` | Read the table and column identity and structure written by `02_pipeline`. |
    | `METADATA_DATA_PROFILED` | Read the registered profile metrics written by `02_pipeline`. |
    | `METADATA_ENRICHMENT` | Add descriptive business context and classifications. |
    | `METADATA_GUARDRAIL` | Author executable Guardrail rules for the ETL workflow. |
    | `METADATA_GUARDRAIL_RESULTS` | Inspect Guardrail evaluation results written by Engineering; do not edit those recorded results. |
    | `METADATA_GUARDRAIL_ROW_RESULTS` | Inspect row-level failures written by Engineering where applicable. |

??? info "Details — How the metadata moves between Engineering and Governance"

    `02_pipeline` first writes the technical metadata Governance needs. `01_governance` then adds Enrichment and Guardrails against the same governed table identity. When Engineering reruns the pipeline, those Guardrails are evaluated and the resulting records are written back to the metadata store.

    ```mermaid
    flowchart LR
        PIPELINE["02_pipeline"] --> CATALOGUE["METADATA_DATA_CATALOGUE"]
        PIPELINE --> PROFILED["METADATA_DATA_PROFILED"]
        PIPELINE --> LINEAGE["METADATA_DATA_LINEAGE"]

        CATALOGUE --> GOV["01_governance"]
        PROFILED --> GOV
        GOV --> ENRICHMENT["METADATA_ENRICHMENT"]
        GOV --> GUARDRAIL["METADATA_GUARDRAIL"]

        GUARDRAIL --> RERUN["02_pipeline rerun"]
        RERUN --> RESULTS["METADATA_GUARDRAIL_RESULTS"]
        RERUN --> ROWRESULTS["METADATA_GUARDRAIL_ROW_RESULTS"]
        RERUN --> DECISION{"Can continue?"}
        DECISION -->|Yes| CONTINUE["Continue pipeline"]
        DECISION -->|No| BLOCK["Block pipeline"]
    ```

    The diagram uses the actual FabricOps metadata tables involved in this part of the workflow.

??? info "Details — Table Guardrails versus DQ rules"

    Schema, Freshness, and Changes Guardrails operate at the table boundary and can often be evaluated before reading all business rows. DQ rules evaluate the actual DataFrame and may also record row-level failures.

## Expected result

You should now have reviewed `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, written `METADATA_ENRICHMENT`, and authored `METADATA_GUARDRAIL` records ready for the newer guarded `02_pipeline` path to evaluate.

**Previous:** [Step 2: Run the Development pipeline](02-run-pipeline.md)  
**Next:** [Step 4: Rerun the Development pipeline with Guardrails](04-run-pipeline-with-guardrails.md)

See also: [METADATA_ENRICHMENT](../reference/metadata/metadata_enrichment.md), [METADATA_GUARDRAIL](../reference/metadata/metadata_guardrail.md), and [List of DQ Rules](../reference/dq-rules/index.md).
