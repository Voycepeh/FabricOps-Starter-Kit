# List of Metadata Tables

![FabricOps metadata model: Governance and Engineering schemas, with a manifest-backed Activated Pipeline contracts and separate run-linked Guardrail Results](../assets/fabricops-metadata-model.svg)

FabricOps metadata is stored in one Metadata Lakehouse with two physical schemas:

- **Governance** stores authored governance definitions.
- **Engineering** stores technical observations, profiling, lineage, access observations, and runtime results.

`table_id` connects the same governed asset across both schemas. `contract_id` and `contract_version` identify one exact Data Contract version.

`METADATA_DATA_CONTRACT.contract_payload_json` is the JSON string column containing authored Guardrails, Enrichment and profiling policies for each contract version.

## Metadata tables

<style>
.metadata-table-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; margin: 1.25rem 0 2rem; }
.metadata-table-card { --metadata-schema-accent: var(--md-default-fg-color--light); --metadata-schema-tint: color-mix(in srgb, var(--metadata-schema-accent) 10%, transparent); display: flex; flex-direction: column; gap: .55rem; padding: 1rem 1.1rem; border: 1px solid var(--md-default-fg-color--lightest); border-left: .25rem solid var(--metadata-schema-accent); border-radius: .7rem; background: var(--md-default-bg-color); color: inherit !important; text-decoration: none !important; box-shadow: 0 1px 2px rgba(0, 0, 0, .04); transition: border-color .15s ease, background .15s ease, transform .15s ease; }
.metadata-table-card--governance { --metadata-schema-accent: #7e57c2; }
.metadata-table-card--engineering { --metadata-schema-accent: #1976d2; }
.metadata-table-card:hover { background: var(--metadata-schema-tint); transform: translateY(-1px); }
.metadata-table-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: .75rem; }
.metadata-table-card__identity { display: flex; flex-wrap: wrap; gap: .4rem .6rem; align-items: center; min-width: 0; }
.metadata-table-card__title { font-family: var(--md-code-font-family); font-size: .82rem; font-weight: 700; color: var(--metadata-schema-accent); overflow-wrap: anywhere; }
.metadata-table-card__schema { display: inline-flex; align-items: center; padding: .12rem .45rem; border: 1px solid color-mix(in srgb, var(--metadata-schema-accent) 38%, transparent); border-radius: 999px; background: var(--metadata-schema-tint); color: var(--metadata-schema-accent); font-size: .67rem; font-weight: 700; letter-spacing: .025em; line-height: 1.35; }
.metadata-table-card__arrow { flex: 0 0 auto; font-size: 1rem; color: var(--metadata-schema-accent); }
.metadata-table-card__purpose { line-height: 1.45; }
.metadata-table-card__meta { display: grid; grid-template-columns: 6.4rem minmax(0, 1fr); gap: .5rem; align-items: start; font-size: .84rem; line-height: 1.4; }
.metadata-table-card__meta strong, .metadata-table-card__relationships-label { color: var(--md-default-fg-color--light); font-size: .74rem; letter-spacing: .02em; text-transform: uppercase; }
.metadata-table-card__relationships { display: flex; flex-direction: column; gap: .35rem; padding-top: .15rem; }
.metadata-table-card__relationship-summary { display: grid; grid-template-columns: 3.5rem minmax(0, 1fr); gap: .5rem; align-items: start; }
.metadata-table-card__relationship-list { display: flex; flex-wrap: wrap; gap: .35rem .5rem; min-width: 0; }
.metadata-table-card__relationship-list code { font-size: .74rem; overflow-wrap: anywhere; }
.metadata-table-card__cardinality { font-weight: 700; color: var(--md-primary-fg-color); white-space: nowrap; }
@media (max-width: 720px) { .metadata-table-grid { gap: .8rem; } .metadata-table-card { padding: .9rem 1rem; } .metadata-table-card__meta { grid-template-columns: 1fr; gap: .15rem; } .metadata-table-card__relationship-summary { grid-template-columns: 3rem minmax(0, 1fr); } }
</style>

<div class="metadata-table-grid">
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_pipeline_registry/" aria-label="Open METADATA_PIPELINE_REGISTRY schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_PIPELINE_REGISTRY</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Permanent UUIDv4 identity and environment-specific notebook bindings; registration never authorizes Live. A seeded Authority control row serializes binding transactions in this same table.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One logical pipeline per environment, plus one serialization control row (central, *).</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>pipeline_id</code> <span class="metadata-table-card__key-separator">+</span> <code>environment_name</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_PIPELINE_RUN</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_pipeline_run/" aria-label="Open METADATA_PIPELINE_RUN schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_PIPELINE_RUN</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">One complete logical run, exact table mappings, operation results, per-table profiling activity outcomes, warnings and pinned activation revision. Profiling completion joins persisted result snapshots; Grain Discovery and empty Frequency Profiling use minimal success markers in operation_summary_json.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One Live pipeline execution attempt. Test results remain in memory.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>run_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_PIPELINE_REGISTRY</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_SOURCE_OBSERVATION</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_GUARDRAIL_RESULTS</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--governance" href="metadata_data_steward/" aria-label="Open METADATA_DATA_STEWARD schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_STEWARD</span>
      <span class="metadata-table-card__schema">governance</span>
    </span>
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
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_AGREEMENT</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--governance" href="metadata_data_agreement/" aria-label="Open METADATA_DATA_AGREEMENT schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_AGREEMENT</span>
      <span class="metadata-table-card__schema">governance</span>
    </span>
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
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_STEWARD</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--governance" href="metadata_data_contract/" aria-label="Open METADATA_DATA_CONTRACT schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_CONTRACT</span>
      <span class="metadata-table-card__schema">governance</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Reusable immutable frozen table definition with Enrichment, executable Guardrails and independent profiling policies. Agreement linkage belongs to Activated Pipeline.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One Draft or Frozen version of one table contract; Frozen contents are immutable.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>contract_id</code> <span class="metadata-table-card__key-separator">+</span> <code>contract_version</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → M</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_ACTIVATION_STATE</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CATALOGUE</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_GUARDRAIL_RESULTS</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--governance" href="metadata_activation_state/" aria-label="Open METADATA_ACTIVATION_STATE schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_ACTIVATION_STATE</span>
      <span class="metadata-table-card__schema">governance</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Single atomic central authority for environment activation revisions, immutable approval history, table contracts, writer ownership, running execution reservations and renewable profiling claims.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One central authority row containing environment snapshots.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>authority_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → M</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CONTRACT</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_data_catalogue/" aria-label="Open METADATA_DATA_CATALOGUE schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_CATALOGUE</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
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
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CONTRACT</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_SOURCE_OBSERVATION</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_PROFILED</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_LINEAGE</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → N</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_ACCESS</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_source_observation/" aria-label="Open METADATA_SOURCE_OBSERVATION schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_SOURCE_OBSERVATION</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Store source evidence observed by one logical pipeline for one governed target, including source_table_name and target_table_name captured for that observation. run_id joins METADATA_PIPELINE_RUN.run_id for planned executions; _activity_id retains the actual Fabric activity shared by different attempts. Legacy and standalone observations may have no run_id. observation_status=observed means the run captured the evidence but has not accepted it; observation_status=committed records accepted incremental progress, and drift_committed records the Source Drift baseline. Warehouse publication_observed and publication_committed rows store target-only retry receipts with empty source identity and no watermark; they also cover Full Read and source-free writes.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One observed or committed partition-state row within one logical notebook, source table, target table, and observation; target-only Warehouse publication receipt rows have an empty source identity.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>observation_id</code> <span class="metadata-table-card__key-separator">+</span> <code>partition_value</code> <span class="metadata-table-card__key-separator">+</span> <code>observation_status</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_PIPELINE_RUN</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CATALOGUE</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_data_profiled/" aria-label="Open METADATA_DATA_PROFILED schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_PROFILED</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See column-level profile metrics for a dataset snapshot. table_name and column_name record the names observed when written and do not follow later Catalogue renames.</span>
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
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CATALOGUE</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">1 → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_PROFILED_FREQUENCY</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_data_profiled_frequency/" aria-label="Open METADATA_DATA_PROFILED_FREQUENCY schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_PROFILED_FREQUENCY</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Frequency distributions retain Table ID, Column ID, environment, captured names and datatype. Independently scheduled Frequency Profiling owns its activity snapshot and leaves profile_id null; combined standalone profiling may link a statistical Profile. Captured names do not follow later renames.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One ranked value for a column and frequency activity snapshot. The statistical Profile reference is optional.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>frequency_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_PROFILED</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_data_lineage/" aria-label="Open METADATA_DATA_LINEAGE schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_LINEAGE</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See which registered tables participated as sources and targets in pipeline activities; table_name records the name at the participation write while table_id remains stable. The current notebook's Lineage defines Data Contract resolution scope.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One registered table participating as a source or target in one pipeline activity.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>lineage_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CATALOGUE</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_data_access/" aria-label="Open METADATA_DATA_ACCESS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_DATA_ACCESS</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">See observable Workspace, OneLake Security, and SQL access for registered governed physical tables across configured Fabric data items; table_name records the Catalogue name matched at scan time. This is not an effective-access resolver.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One observed access grant for one principal or access selector and one governed table within one access snapshot.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>access_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CATALOGUE</code>
      </span>
    </span>
  </span>
</a>
<a class="metadata-table-card metadata-table-card--engineering" href="metadata_guardrail_results/" aria-label="Open METADATA_GUARDRAIL_RESULTS schema">
  <span class="metadata-table-card__header">
    <span class="metadata-table-card__identity">
      <span class="metadata-table-card__title">METADATA_GUARDRAIL_RESULTS</span>
      <span class="metadata-table-card__schema">engineering</span>
    </span>
    <span class="metadata-table-card__arrow" aria-hidden="true">→</span>
  </span>
  <span class="metadata-table-card__purpose">Store aggregate Live Guardrail summaries for exact participating contract versions, captured table name, readable rule context, and continuation decisions; caller-owned failed business rows are not persisted here. Captured context does not follow later table or rule changes.</span>
  <span class="metadata-table-card__meta">
    <strong>Grain</strong>
    <span>One persisted Live Guardrail outcome for one exact Data Contract version; Testing returns outcomes in memory only.</span>
  </span>
  <span class="metadata-table-card__meta">
    <strong>Primary key</strong>
    <span><code>guardrail_result_id</code></span>
  </span>
  <span class="metadata-table-card__relationships">
    <span class="metadata-table-card__relationships-label">Relationships</span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_PIPELINE_RUN</code>
      </span>
    </span>
    <span class="metadata-table-card__relationship-summary">
      <span class="metadata-table-card__cardinality">N → 1</span>
      <span class="metadata-table-card__relationship-list">
        <code>METADATA_DATA_CONTRACT</code>
      </span>
    </span>
  </span>
</a>
</div>
