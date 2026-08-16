# List of Metadata Tables

FabricOps metadata tables describe the governed workflow evidence written by the notebook templates. These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

The diagram below shows how the FabricOps metadata tables relate to one another across agreement, profiling, guardrail, lineage, and pipeline-run evidence.

![FabricOps metadata model](../assets/fabricops-metadata-model.png)

## Data Agreement versus Data Contract

A Data Agreement is the overarching governance agreement between the accountable data producer and consumer parties, represented by their data stewards. It defines why the data may be shared, who is accountable, the permitted purpose and scope, usage conditions, and the agreement’s review period.

A Data Contract is the machine-readable dataset-level promise governed by a Data Agreement. In the current FabricOps metadata model, the contract records the parent agreement, authorised catalogue tables, and their schema fingerprints. Related catalogue, enrichment, guardrail, profiling, and lineage metadata provide the broader technical and quality context for those tables.

One Data Agreement can govern multiple Data Contracts.

The agreement answers: Why and under what governance arrangement may this data be shared?

The contract answers: Exactly what data will be delivered, in what structure, at what quality, and how reliably?

<div class="grid cards" markdown>

-   **[METADATA_DATA_STEWARD](metadata/metadata_data_steward.md)**

    Data steward person registry used by agreement intake; responsibility effective periods belong to METADATA_DATA_AGREEMENT.

-   **[METADATA_DATA_AGREEMENT](metadata/metadata_data_agreement.md)**

    Data Agreement records that describe the overarching governance arrangement between producer and consumer stewards, including approved purpose, usage, accountability, and lifecycle context.

-   **[METADATA_DATA_CONTRACT](metadata/metadata_data_contract.md)**

    Dataset-level contract rows linking parent Data Agreements to authorised catalogue tables and their schema fingerprints.

-   **[METADATA_DATA_CATALOGUE](metadata/metadata_data_catalogue.md)**

    Maintain the stable table and column identities that connect FabricOps metadata.

-   **[METADATA_DATA_PROFILED](metadata/metadata_data_profiled.md)**

    Compact per-column summary statistics captured from a profiled dataset snapshot.

-   **[METADATA_DATA_PROFILED_FREQUENCY](metadata/metadata_data_profiled_frequency.md)**

    Flattened distinct-value frequency rows linked to their exact profile_record_id.

-   **[METADATA_DATA_LINEAGE](metadata/metadata_data_lineage.md)**

    Each row records a profiled dataset snapshot participating as a source or target in one Fabric activity.

-   **[METADATA_DATA_ACCESS](metadata/metadata_data_access.md)**

    Access-review rows reserved for implemented metadata access evidence.

-   **[METADATA_ENRICHMENT](metadata/metadata_enrichment.md)**

    Append-only generic descriptive and governance values for catalogue table and column identities.

-   **[METADATA_GUARDRAIL](metadata/metadata_guardrail.md)**

    Append-only schema, freshness, profile-behavior, and DQ guardrail intent rows.

-   **[METADATA_GUARDRAIL_RESULTS](metadata/metadata_guardrail_results.md)**

    Runtime guardrail outcomes written by pipeline enforcement.

-   **[METADATA_GUARDRAIL_ROW_RESULTS](metadata/metadata_guardrail_row_results.md)**

    Failed source-row and failed-DQ-rule evidence linked to runtime guardrail outcomes.

-   **[METADATA_SOURCE_OBSERVATION](metadata/metadata_source_observation.md)**

    Append-only compact partition observations used for cheap pre-read source checking; each row links to METADATA_DATA_CATALOGUE through metadata_table_key.

</div>
