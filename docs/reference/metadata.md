# List of Metadata Tables

FabricOps metadata tables describe the data, agreements, stewards, catalogue, lineage, guardrail rules, guardrail results, notebook registry, and pipeline runs created by the notebook workflow. These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

<figure class="metadata-model-image">
  <img src="../../assets/fabricops-metadata-model.png" alt="FabricOps metadata model" />
</figure>

<div class="grid cards" markdown>

-   **[METADATA_DATA_ACCESS](metadata/metadata_data_access.md)**

    Externally collected access inventory for workspace, object, schema, and table access review.

    `External inventory ingestion / governance access review.`

-   **[METADATA_DATA_AGREEMENT](metadata/metadata_data_agreement.md)**

    Agreement records that describe approved use, steward, recipient, and lifecycle context.

    `01_agreement.ipynb, 02_pipeline.ipynb`

-   **[METADATA_DATA_AGREEMENT_EVIDENCE](metadata/metadata_data_agreement_evidence.md)**

    Supporting agreement files and related metadata captured during agreement intake.

    `01_agreement.ipynb`

-   **[METADATA_DATA_CATALOGUE](metadata/metadata_data_catalogue.md)**

    Observed table and column profiles used for catalogue review and runtime comparisons. This is runtime metadata, not approved guardrail intent.

    `02_pipeline.ipynb, 03_governance.ipynb, 99_explore.ipynb`

-   **[METADATA_DATA_LINEAGE_TABLE](metadata/metadata_data_lineage_table.md)**

    Source-to-target lineage rows written by pipeline runs.

    `02_pipeline.ipynb`

-   **[METADATA_DATA_STEWARD](metadata/metadata_data_steward.md)**

    Active and historical data steward records used by agreement intake.

    `01_agreement.ipynb`

-   **[METADATA_ENRICHMENT_RULES](metadata/metadata_enrichment_rules.md)**

    Append-only enrichment and business metadata intent authored and reviewed through governance workflows.

    `02_pipeline.ipynb, 03_governance.ipynb`

-   **[METADATA_GUARDRAIL_RESULTS](metadata/metadata_guardrail_results.md)**

    Runtime guardrail outcomes written by pipeline enforcement.

    `02_pipeline.ipynb`

-   **[METADATA_GUARDRAIL_RULES](metadata/metadata_guardrail_rules.md)**

    Approved or pending schema, freshness, profile behavior, and DQ guardrail intent.

    `02_pipeline.ipynb, 03_governance.ipynb`

-   **[METADATA_NOTEBOOK_REGISTRY](metadata/metadata_notebook_registry.md)**

    Active notebook registration records linking notebooks to agreement, environment, dataset, and pipeline context.

    `02_pipeline.ipynb`

-   **[METADATA_PIPELINE_RUNS](metadata/metadata_pipeline_runs.md)**

    Pipeline run summaries for execution, guardrail, lineage, and catalogue status.

    `02_pipeline.ipynb`

</div>
