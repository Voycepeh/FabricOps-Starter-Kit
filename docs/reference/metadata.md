# List of Metadata Tables

FabricOps metadata tables describe the governed workflow evidence written by the notebook templates. These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

The metadata lifecycle begins with steward, agreement, and contract context. Development pipelines then record observed catalogue, profile, and lineage evidence. Governance reads that evidence and records enrichment and guardrail intent. Later pipeline runs enforce active guardrails and write their runtime outcomes separately to `METADATA_GUARDRAIL_RESULTS`.

The previous metadata-model image has been removed because its table names and relationships no longer match the implemented schema registry. Use the generated table pages below as the current technical reference; a replacement lifecycle diagram should be produced in a separate visual-assets PR from the canonical schema source.

<div class="grid cards" markdown>

-   **[METADATA_DATA_STEWARD](metadata/metadata_data_steward.md)**

    Active and historical data steward records used by agreement intake.

-   **[METADATA_DATA_AGREEMENT](metadata/metadata_data_agreement.md)**

    Agreement records that describe approved use, steward, recipient, and lifecycle context.

-   **[METADATA_DATA_CONTRACT](metadata/metadata_data_contract.md)**

    Contract rows reserved for implemented data contract lifecycle evidence.

-   **[METADATA_DATA_CATALOGUE](metadata/metadata_data_catalogue.md)**

    Observed table and column identities used for governed catalogue review and runtime comparisons.

-   **[METADATA_DATA_PROFILED](metadata/metadata_data_profiled.md)**

    Detailed per-column profiling evidence captured from a profiled dataset snapshot.

-   **[METADATA_DATA_LINEAGE](metadata/metadata_data_lineage.md)**

    Runtime lineage participation rows that connect a profiled dataset snapshot to a Fabric activity.

-   **[METADATA_DATA_ACCESS](metadata/metadata_data_access.md)**

    Access-review rows reserved for implemented metadata access evidence.

-   **[METADATA_ENRICHMENT](metadata/metadata_enrichment.md)**

    Append-only enrichment intent and approved business context for governed tables and columns.

-   **[METADATA_GUARDRAIL](metadata/metadata_guardrail.md)**

    Append-only schema, freshness, profile-behavior, and DQ guardrail intent rows.

-   **[METADATA_GUARDRAIL_RESULTS](metadata/metadata_guardrail_results.md)**

    Runtime guardrail outcomes written by pipeline enforcement.

</div>
