# List of Metadata Tables

**FabricOps metadata tables connect Governance intent with Engineering evidence across the governed workflow.**

These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

![FabricOps metadata model](../assets/fabricops-metadata-model.png)

## Data Agreement and Data Contract

### Data Agreement

**Defines the overarching governance arrangement between accountable producer and consumer parties.**

It covers why data may be shared, who is accountable, the permitted purpose and scope, usage conditions, and the agreement review period.

### Data Contract

**Defines the machine-readable dataset-level promise governed by a Data Agreement.**

The Data Contract records the parent agreement, authorised Data Catalogue tables, and their schema fingerprints. Related Data Catalogue, Enrichment, Guardrail, Data Profiled, Data Profiled Frequency, and Data Lineage records provide the broader technical and quality context.

!!! note "Relationship"

    One Data Agreement can govern multiple Data Contracts.

| Question | Answered by |
| --- | --- |
| Why and under what governance arrangement may this data be shared? | Data Agreement |
| Exactly what data is authorised and what dataset-level promise applies? | Data Contract |

## Metadata tables

<div class="grid cards" markdown>

-   **[METADATA_DATA_STEWARD](metadata/metadata_data_steward.md)**

    Registry of Data Stewards used by the Governance workflow.

-   **[METADATA_DATA_AGREEMENT](metadata/metadata_data_agreement.md)**

    Governance arrangements between producer and consumer stewards, including purpose, usage, accountability, and lifecycle context.

-   **[METADATA_DATA_CONTRACT](metadata/metadata_data_contract.md)**

    Dataset-level contract rows linking parent Data Agreements to authorised Data Catalogue tables and schema fingerprints.

-   **[METADATA_DATA_CATALOGUE](metadata/metadata_data_catalogue.md)**

    Observed table and column identities used for governed catalogue review and runtime comparisons.

-   **[METADATA_DATA_PROFILED](metadata/metadata_data_profiled.md)**

    Compact per-column profiling statistics captured from a dataset snapshot.

-   **[METADATA_DATA_PROFILED_FREQUENCY](metadata/metadata_data_profiled_frequency.md)**

    Distinct-value frequency rows linked to compact profile summaries through `metadata_column_key`.

-   **[METADATA_DATA_LINEAGE](metadata/metadata_data_lineage.md)**

    Source and target dataset snapshots participating in one Fabric activity.

-   **[METADATA_DATA_ACCESS](metadata/metadata_data_access.md)**

    Access-review rows reserved for implemented metadata access evidence.

-   **[METADATA_ENRICHMENT](metadata/metadata_enrichment.md)**

    Descriptive and Governance values attached to Data Catalogue table and column identities.

-   **[METADATA_GUARDRAIL](metadata/metadata_guardrail.md)**

    Schema, freshness, profile-behaviour, and data-quality Guardrail intent.

-   **[METADATA_GUARDRAIL_RESULTS](metadata/metadata_guardrail_results.md)**

    Runtime Guardrail outcomes written by pipeline enforcement.

</div>

## How to read the model

**The Data Catalogue is the central dataset identity that connects observed Engineering evidence with Governance context.**

Engineering writes Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, Data Lineage, and Guardrail Results. Governance reads the observed evidence and writes Data Agreement, Data Contract, Enrichment, and Guardrail records around it.
