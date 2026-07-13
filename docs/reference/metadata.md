# List of Metadata Tables

FabricOps metadata tables describe the governed workflow evidence written by the notebook templates. These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

The diagram below shows how the FabricOps metadata tables relate to one another across agreement, profiling, guardrail, lineage, and pipeline-run evidence.

![FabricOps metadata model](../assets/fabricops-metadata-model.png)

<div class="grid cards" markdown>

-   **[METADATA_DATA_ACCESS](metadata/metadata_data_access.md)**

    Externally collected access inventory for workspace, object, schema, and table access review.

-   **[METADATA_DATA_AGREEMENT](metadata/metadata_data_agreement.md)**

    Agreement records that describe approved use, steward, recipient, and lifecycle context.

-   **[METADATA_DATA_AGREEMENT_EVIDENCE](metadata/metadata_data_agreement_evidence.md)**

    Supporting agreement files and related metadata captured during agreement intake.

-   **[METADATA_DATA_CATALOGUE](metadata/metadata_data_catalogue.md)**

    Observed table and column profiles used for catalogue review and runtime comparisons.

-   **[METADATA_DATA_LINEAGE](metadata/metadata_data_lineage.md)**

    Metadata Data Lineage metadata table.

-   **[METADATA_DATA_STEWARD](metadata/metadata_data_steward.md)**

    Active and historical data steward records used by agreement intake.

-   **[METADATA_ENRICHMENT_RULES](metadata/metadata_enrichment_rules.md)**

    Append-only enrichment and business metadata intent authored and reviewed through governance workflows.

-   **[METADATA_GUARDRAIL_RESULTS](metadata/metadata_guardrail_results.md)**

    Runtime guardrail outcomes written by pipeline enforcement.

-   **[METADATA_GUARDRAIL_RULES](metadata/metadata_guardrail_rules.md)**

    Approved or pending schema, freshness, profile behavior, and DQ guardrail intent.

</div>
