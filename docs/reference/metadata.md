# List of Metadata Tables

FabricOps metadata is stored in one Metadata Lakehouse with two physical schemas:

- **Governance** stores authored governance definitions.
- **Engineering** stores technical observations, profiling, lineage, access observations, and runtime results.

`table_id` connects the same governed asset across both schemas. `contract_id` and `contract_version` identify one exact Data Contract version.

`METADATA_DATA_CONTRACT.contract_payload_json` is the JSON string column containing authored Guardrails, Enrichment and profiling policies for each contract version.

## Metadata relationships

<div class="fabricops-metadata-explorer" data-metadata-explorer>
  <nav class="metadata-explorer-fallback" aria-label="Metadata table references">
    <a href="metadata_pipeline_registry/">METADATA_PIPELINE_REGISTRY</a>
    <a href="metadata_pipeline_run/">METADATA_PIPELINE_RUN</a>
    <a href="metadata_data_steward/">METADATA_DATA_STEWARD</a>
    <a href="metadata_data_agreement/">METADATA_DATA_AGREEMENT</a>
    <a href="metadata_data_contract/">METADATA_DATA_CONTRACT</a>
    <a href="metadata_activation_state/">METADATA_ACTIVATION_STATE</a>
    <a href="metadata_data_catalogue/">METADATA_DATA_CATALOGUE</a>
    <a href="metadata_source_observation/">METADATA_SOURCE_OBSERVATION</a>
    <a href="metadata_data_profiled/">METADATA_DATA_PROFILED</a>
    <a href="metadata_data_profiled_frequency/">METADATA_DATA_PROFILED_FREQUENCY</a>
    <a href="metadata_data_lineage/">METADATA_DATA_LINEAGE</a>
    <a href="metadata_data_access/">METADATA_DATA_ACCESS</a>
    <a href="metadata_guardrail_results/">METADATA_GUARDRAIL_RESULTS</a>
  </nav>
</div>
