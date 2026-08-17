# List of Metadata Tables

FabricOps metadata tables describe the governed workflow evidence written by the notebook templates. These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.

The diagram below shows how the FabricOps metadata tables relate to one another across agreement, profiling, guardrail, lineage, and pipeline-run evidence.

![FabricOps metadata model](../assets/fabricops-metadata-model.png)

## Metadata tables

<style>
.metadata-table-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin: 1.25rem 0 2rem; }
.metadata-table-card { display: flex; flex-direction: column; gap: .55rem; padding: 1rem 1.1rem; border: 1px solid rgba(0, 150, 136, .24); border-radius: .7rem; background: rgba(0, 150, 136, .055); color: inherit !important; text-decoration: none !important; box-shadow: 0 1px 2px rgba(0, 0, 0, .04); transition: border-color .15s ease, background .15s ease, transform .15s ease; }
.metadata-table-card:hover { border-color: rgba(0, 150, 136, .48); background: rgba(0, 150, 136, .085); transform: translateY(-1px); }
.metadata-table-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: .75rem; }
.metadata-table-card__title { font-family: var(--md-code-font-family); font-size: .82rem; font-weight: 700; color: var(--md-primary-fg-color); overflow-wrap: anywhere; }
.metadata-table-card__arrow { flex: 0 0 auto; font-size: 1rem; color: var(--md-primary-fg-color); }
.metadata-table-card__purpose { line-height: 1.45; }
.metadata-table-card__meta { display: grid; grid-template-columns: 6.4rem minmax(0, 1fr); gap: .5rem; align-items: start; font-size: .84rem; line-height: 1.4; }
.metadata-table-card__meta strong, .metadata-table-card__relationships-label { color: var(--md-default-fg-color--light); font-size: .74rem; letter-spacing: .02em; text-transform: uppercase; }
.metadata-table-card__relationships { display: flex; flex-direction: column; gap: .35rem; padding-top: .15rem; }
.metadata-table-card__relationship { display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; font-size: .76rem; line-height: 1.35; }
.metadata-table-card__relationship code { font-size: .72rem; overflow-wrap: anywhere; }
.metadata-table-card__cardinality { font-weight: 700; color: var(--md-primary-fg-color); white-space: nowrap; }
.metadata-table-card__empty { font-size: .8rem; color: var(--md-default-fg-color--light); }
@media (max-width: 720px) { .metadata-table-grid { grid-template-columns: 1fr; gap: .8rem; } .metadata-table-card { padding: .9rem 1rem; } .metadata-table-card__meta { grid-template-columns: 5.6rem minmax(0, 1fr); } }
</style>

<div class="metadata-table-grid">
<a class="metadata-table-card" href="metadata/metadata_data_steward.md" aria-label="Open METADATA_DATA_STEWARD schema">
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
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_STEWARD.steward_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_AGREEMENT.provider_steward_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_STEWARD.steward_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_AGREEMENT.recipient_steward_id</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_data_agreement.md" aria-label="Open METADATA_DATA_AGREEMENT schema">
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
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_STEWARD.steward_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_AGREEMENT.provider_steward_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_STEWARD.steward_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_AGREEMENT.recipient_steward_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_AGREEMENT.agreement_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_CONTRACT.agreement_id</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_data_contract.md" aria-label="Open METADATA_DATA_CONTRACT schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_CONTRACT</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Define what the data is, how it looks, its sensitivity, quality requirements, schema, freshness, approved usages, and link it to the Data Agreement.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One authorised catalogue table and schema fingerprint governed by one Data Agreement.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>agreement_id</code> <span class="metadata-table-card__key-separator">+</span> <code>metadata_table_key</code> <span class="metadata-table-card__key-separator">+</span> <code>schema_fingerprint</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_AGREEMENT.agreement_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_CONTRACT.agreement_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_CONTRACT.metadata_table_key</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_data_catalogue.md" aria-label="Open METADATA_DATA_CATALOGUE schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_CATALOGUE</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See the tables and columns FabricOps has observed.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One table or column asset in one environment.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>environment_name</code> <span class="metadata-table-card__key-separator">+</span> <code>table_id</code> <span class="metadata-table-card__key-separator">+</span> <code>column_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_CONTRACT.metadata_table_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_SOURCE_OBSERVATION.table_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED.table_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.column_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED.column_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_LINEAGE.table_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_ENRICHMENT.metadata_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.column_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_ENRICHMENT.metadata_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL.metadata_table_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.column_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL.metadata_column_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_RESULTS.metadata_table_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_ROW_RESULTS.metadata_table_key</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_source_observation.md" aria-label="Open METADATA_SOURCE_OBSERVATION schema">
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
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_SOURCE_OBSERVATION.table_id</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_data_profiled.md" aria-label="Open METADATA_DATA_PROFILED schema">
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
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED.table_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.column_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED.column_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_PROFILED.profile_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED_FREQUENCY.profile_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_PROFILED.profile_snapshot_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED_FREQUENCY.profile_snapshot_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_PROFILED.profile_snapshot_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_LINEAGE.profile_snapshot_id</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_data_profiled_frequency.md" aria-label="Open METADATA_DATA_PROFILED_FREQUENCY schema">
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
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_PROFILED.profile_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED_FREQUENCY.profile_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_PROFILED.profile_snapshot_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_PROFILED_FREQUENCY.profile_snapshot_id</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_data_lineage.md" aria-label="Open METADATA_DATA_LINEAGE schema">
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
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_LINEAGE.table_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_PROFILED.profile_snapshot_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_DATA_LINEAGE.profile_snapshot_id</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_enrichment.md" aria-label="Open METADATA_ENRICHMENT schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_ENRICHMENT</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Add business and governance context to the data.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One appended enrichment value for one table or column identity.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>enrichment_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_ENRICHMENT.metadata_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.column_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_ENRICHMENT.metadata_key</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_data_access.md" aria-label="Open METADATA_DATA_ACCESS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_DATA_ACCESS</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See who can use the data and how it can be used.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One access review record for one user and governed scope.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span>Not defined in the current implementation.</span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__empty">No immediate logical relationship is defined.</span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_guardrail.md" aria-label="Open METADATA_GUARDRAIL schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_GUARDRAIL</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Define the expectations the data used in the ETL pipeline should meet.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One authored guardrail configuration row for one rule lifecycle or version.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>guardrail_rule_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL.metadata_table_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.column_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL.metadata_column_key</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_GUARDRAIL.guardrail_rule_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_RESULTS.guardrail_rule_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_GUARDRAIL.guardrail_rule_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_ROW_RESULTS.guardrail_rule_id</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_guardrail_results.md" aria-label="Open METADATA_GUARDRAIL_RESULTS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_GUARDRAIL_RESULTS</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See whether the expectations of the data in the ETL pipeline run are met.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One runtime outcome for one guardrail rule in one pipeline run.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>guardrail_result_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_GUARDRAIL.guardrail_rule_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_RESULTS.guardrail_rule_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_RESULTS.metadata_table_key</code>
    </span>
  </span>
</a>
<a class="metadata-table-card" href="metadata/metadata_guardrail_row_results.md" aria-label="Open METADATA_GUARDRAIL_ROW_RESULTS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__title">METADATA_GUARDRAIL_ROW_RESULTS</span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See the failed or quarantined rows produced by a Data Quality guardrail.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One failed-row evidence record produced by one Guardrail rule evaluation.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>guardrail_row_result_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_GUARDRAIL.guardrail_rule_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_ROW_RESULTS.guardrail_rule_id</code>
    </span>
    <span class="metadata-table-card__relationship">
      <code>METADATA_DATA_CATALOGUE.table_id</code>
      <span class="metadata-table-card__cardinality">1 → N</span>
      <code>METADATA_GUARDRAIL_ROW_RESULTS.metadata_table_key</code>
    </span>
  </span>
</a>
</div>
