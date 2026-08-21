# List of Metadata Tables

FabricOps metadata tables describe the governed workflow evidence written by the notebook templates. These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

The diagram below shows how the FabricOps metadata tables relate to one another across agreement, profiling, guardrail, lineage, and pipeline-run evidence.

![FabricOps metadata model](../assets/fabricops-metadata-model.png)

## Metadata tables

<style>
.metadata-table-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; margin: 1.25rem 0 2rem; }
.metadata-table-card { display: flex; flex-direction: column; gap: .55rem; padding: 1rem 1.1rem; border: 1px solid rgba(0, 150, 136, .24); border-radius: .7rem; background: rgba(0, 150, 136, .055); color: inherit !important; text-decoration: none !important; box-shadow: 0 1px 2px rgba(0, 0, 0, .04); transition: border-color .15s ease, background .15s ease, transform .15s ease; }
.metadata-table-card:hover { border-color: rgba(0, 150, 136, .48); background: rgba(0, 150, 136, .085); transform: translateY(-1px); }
.metadata-table-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: .75rem; }
.metadata-table-card__title { font-family: var(--md-code-font-family); font-size: .82rem; font-weight: 700; color: var(--md-primary-fg-color); overflow-wrap: anywhere; }
.metadata-table-card__arrow { flex: 0 0 auto; font-size: 1rem; color: var(--md-primary-fg-color); }
.metadata-table-card__purpose { line-height: 1.45; }
.metadata-table-card__meta { display: grid; grid-template-columns: 6.4rem minmax(0, 1fr); gap: .5rem; align-items: start; font-size: .84rem; line-height: 1.4; }
.metadata-table-card__meta strong, .metadata-table-card__relationships-label { color: var(--md-default-fg-color--light); font-size: .74rem; letter-spacing: .02em; text-transform: uppercase; }
.metadata-table-card__relationships { display: flex; flex-direction: column; gap: .35rem; padding-top: .15rem; }
.metadata-table-card__relationships-header { display: flex; align-items: baseline; justify-content: space-between; gap: .75rem; }
.metadata-table-card__relationships-count { font-size: .74rem; color: var(--md-default-fg-color--light); white-space: nowrap; }
.metadata-table-card__relationship-summary { display: grid; grid-template-columns: 3.5rem minmax(0, 1fr); gap: .5rem; align-items: start; }
.metadata-table-card__relationship-list { display: flex; flex-wrap: wrap; gap: .35rem .5rem; min-width: 0; }
.metadata-table-card__relationship-list code { font-size: .74rem; overflow-wrap: anywhere; }
.metadata-table-card__cardinality { font-weight: 700; color: var(--md-primary-fg-color); white-space: nowrap; }
.metadata-table-card__empty { font-size: .8rem; color: var(--md-default-fg-color--light); }
@media (max-width: 720px) { .metadata-table-grid { gap: .8rem; } .metadata-table-card { padding: .9rem 1rem; } .metadata-table-card__meta { grid-template-columns: 1fr; gap: .15rem; } .metadata-table-card__relationship-summary { grid-template-columns: 3rem minmax(0, 1fr); } }
</style>

<div class="metadata-table-grid">
<a class="metadata-table-card" href="metadata_data_steward/" aria-label="Open METADATA_DATA_STEWARD schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_STEWARD</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Know who is responsible for the data.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One registered Data Steward.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>steward_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">1 table</span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_AGREEMENT</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_data_agreement/" aria-label="Open METADATA_DATA_AGREEMENT schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_AGREEMENT</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Define why the data is shared, with whom, and under what conditions.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One version of one Data Agreement.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>agreement_id</code> <span class="metadata-table-card__key-separator">+</span> <code>agreement_version</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">1 table</span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CONTRACT</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_data_contract/" aria-label="Open METADATA_DATA_CONTRACT schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_CONTRACT</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Define what the data is, how it looks, its sensitivity, quality requirements, schema, freshness, approved usages, and link it to the Data Agreement.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One immutable Data Contract version for one governed table under one exact Data Agreement version.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>contract_id</code> <span class="metadata-table-card__key-separator">+</span> <code>contract_version</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">0 tables</span>
    </span>
    <span class="metadata-table-card__empty">No downstream tables.</span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_data_catalogue/" aria-label="Open METADATA_DATA_CATALOGUE schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_CATALOGUE</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">The current structural registry of known table and column assets. table_id identifies the logical table, and column_id identifies the logical column while its normalized column name remains the same. data_type stores the current structural datatype, and is_active indicates whether the asset currently exists. Datatype changes preserve column_id, removed columns become inactive, and returning columns reuse their deterministic ID. METADATA_DATA_PROFILED retains historical observations.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One table or column asset in one environment.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>environment_name</code> <span class="metadata-table-card__key-separator">+</span> <code>table_id</code> <span class="metadata-table-card__key-separator">+</span> <code>column_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">7 tables</span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CONTRACT</code>
        <code>METADATA_SOURCE_OBSERVATION</code>
        <code>METADATA_DATA_PROFILED</code>
        <code>METADATA_DATA_LINEAGE</code>
        <code>METADATA_ENRICHMENT</code>
        <code>METADATA_DATA_ACCESS</code>
        <code>METADATA_GUARDRAIL</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_source_observation/" aria-label="Open METADATA_SOURCE_OBSERVATION schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_SOURCE_OBSERVATION</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See what FabricOps previously observed about the source data.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One partition observation within one source-table observation.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>observation_id</code> <span class="metadata-table-card__key-separator">+</span> <code>partition_value</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">0 tables</span>
    </span>
    <span class="metadata-table-card__empty">No downstream tables.</span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_data_profiled/" aria-label="Open METADATA_DATA_PROFILED schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_PROFILED</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See the column-level profile metrics captured for a dataset snapshot.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One observed column in one profiling snapshot.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>profile_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">2 tables</span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_PROFILED_FREQUENCY</code>
        <code>METADATA_DATA_LINEAGE</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_data_profiled_frequency/" aria-label="Open METADATA_DATA_PROFILED_FREQUENCY schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_PROFILED_FREQUENCY</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See the frequency distribution captured for a profiled column.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One flattened ranked value within one logical frequency distribution for a column Profile.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>frequency_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">0 tables</span>
    </span>
    <span class="metadata-table-card__empty">No downstream tables.</span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_data_lineage/" aria-label="Open METADATA_DATA_LINEAGE schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_LINEAGE</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See where the data came from and where it ends up.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One table participating as a source or target in one pipeline/profiling execution.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>lineage_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">0 tables</span>
    </span>
    <span class="metadata-table-card__empty">No downstream tables.</span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_enrichment/" aria-label="Open METADATA_ENRICHMENT schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_ENRICHMENT</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Add business and governance context to the data.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One appended enrichment value for one table or column identity in one environment.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>enrichment_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">0 tables</span>
    </span>
    <span class="metadata-table-card__empty">No downstream tables.</span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_data_access/" aria-label="Open METADATA_DATA_ACCESS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_ACCESS</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See who has row-level access to the data.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One RLS assignment for one user and one Catalogue table in one environment.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>access_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">0 tables</span>
    </span>
    <span class="metadata-table-card__empty">No downstream tables.</span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_guardrail/" aria-label="Open METADATA_GUARDRAIL schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_GUARDRAIL</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Define the expectations the data used in the ETL pipeline should meet.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One configured Guardrail rule for one Catalogue table or column in one environment.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>guardrail_rule_id</code> <span class="metadata-table-card__key-separator">+</span> <code>guardrail_version</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">1 table</span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_GUARDRAIL_RESULTS</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_guardrail_results/" aria-label="Open METADATA_GUARDRAIL_RESULTS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_GUARDRAIL_RESULTS</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See whether the expectations of the data in the ETL pipeline run are met.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One runtime outcome for one Guardrail rule in one pipeline run.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>guardrail_result_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">1 table</span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_GUARDRAIL_ROW_RESULTS</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata_guardrail_row_results/" aria-label="Open METADATA_GUARDRAIL_ROW_RESULTS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_GUARDRAIL_ROW_RESULTS</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See the individual records that failed a Data Quality rule.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One failed record belonging to one Guardrail Result.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>guardrail_row_result_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-header">
      <span class="metadata-table-card__relationships-label">Used by</span>
      <span class="metadata-table-card__relationships-count">0 tables</span>
    </span>
    <span class="metadata-table-card__empty">No downstream tables.</span>
  </span>
</a>
</div>
