# Function Reference

Use this page to look up Starter Kit functions and public config classes used by the template notebooks.

<div class="reference-kpi-grid" aria-label="Function reference summary">
  <section class="reference-kpi-card surface-card">
    <strong class="reference-kpi-value">27</strong>
    <span class="reference-kpi-title">Public functions</span>
    <p class="reference-kpi-note">Notebook-facing Starter Kit functions.</p>
  </section>
  <section class="reference-kpi-card surface-card">
    <strong class="reference-kpi-value">7</strong>
    <span class="reference-kpi-title">Public classes</span>
    <p class="reference-kpi-note">Public config classes.</p>
  </section>
</div>

<p><small>Function metrics are generated from the function inventory data.</small></p>

## Find a function

Use the finder below to search 27 public functions and 7 public classes. Implementation helper records stay out of the standalone public catalogue. “Used in” means direct starter notebook code-cell invocation, not import-only, markdown-only, generated metadata, example usage, or implementation helper usage.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search public functions and classes</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search public functions and classes" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function or class name, module, starter path, usage source, or description.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">lineage</span> <span class="callable-finder-chip">guardrail</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing 27 public functions and 7 public classes.</p>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No public functions or classes match your search.</p>
</div>

??? info "Maintainer tools"
    Use these links and notes when maintaining the reference system.

    Maintainer inventory metrics:

    - Source Python files count: 30
    - Total callables: 427
    - Supporting functions: 96
    - Private helpers to review: 297

    - [Glossary](glossary.md): simple definitions of repeated FabricOps terms.
    - [Function Call Graph](function-call-graph.md): global public function dependency view and nested helper summary.
    - [Function Call Graph](../assets/function-call-graph-dashboard.html): review public function dependencies, chain depth, fan-out, source Python files, architecture boundaries, and cleanup recommendations.
    - [Function Inventory](../assets/function-inventory.html): search/filter function-level code assets, select rows, and export AI refactor packets.
    - Function manifests: `_data/manifest.json` and `_data/function-manifest.json`.
    - Agent metadata: `_data/automation-manifest.json`.
    - Implementation contracts: expectations maintainers must satisfy before using or changing a function.
    - Skill file: `.agents/skills/fabricops/SKILL.md`.

## Function catalogue

## Public functions and classes

<div class="reference-catalogue-list">
<article id="config.shared-ConfigSmokeCheckResult" class="reference-catalogue-item" data-callable-row="true" data-callable-name="ConfigSmokeCheckResult" data-callable-module="config" data-function-type="public-class" data-callable-purpose="Represent pass, warning, failure, or skipped readiness check output.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/ConfigSmokeCheckResult/"><code>ConfigSmokeCheckResult</code></a></h3>
  <p class="reference-catalogue-item-purpose">Represent pass, warning, failure, or skipped readiness check output.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public config class</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="config.shared-DataAgreementConfig" class="reference-catalogue-item" data-callable-row="true" data-callable-name="DataAgreementConfig" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-class" data-callable-purpose="Define agreement metadata table names and steward/agreement widget fields.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/DataAgreementConfig/"><code>DataAgreementConfig</code></a></h3>
  <p class="reference-catalogue-item-purpose">Define agreement metadata table names and steward/agreement widget fields.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public config class</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="pipeline-display_guardrail_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="display_guardrail_results" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Return summary, detailed, or debug guardrail display output for Fabric notebooks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return summary, detailed, or debug guardrail display output for Fabric notebooks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 14</span></summary><ul><li><code>_display_guardrail_results_workflow</code></li><li><code>build_guardrail_detail_rows</code></li><li><code>build_guardrail_summary_rows</code></li><li><code>_guardrail_reason</code></li><li><code>_next_action</code></li><li><code>_result_can_continue</code></li><li><code>_result_status</code></li><li><code>_table_keys</code></li><li><code>_yes_no</code></li><li><code>_dq_reason</code></li><li><code>_freshness_reason</code></li><li><code>_profile_behavior_reason</code></li><li><code>_result_reason</code></li><li><code>_schema_reason</code></li></ul></details>
  </div>
</article>
<article id="config.shared-FabricStore" class="reference-catalogue-item" data-callable-row="true" data-callable-name="FabricStore" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-class" data-callable-purpose="Describe one configured Fabric store used by path routing.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/FabricStore/"><code>FabricStore</code></a></h3>
  <p class="reference-catalogue-item-purpose">Describe one configured Fabric store used by path routing.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public config class</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="config.shared-FrameworkConfig" class="reference-catalogue-item" data-callable-row="true" data-callable-name="FrameworkConfig" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-class" data-callable-purpose="Combine path, governance, data agreement, and audit timezone settings for notebooks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/FrameworkConfig/"><code>FrameworkConfig</code></a></h3>
  <p class="reference-catalogue-item-purpose">Combine path, governance, data agreement, and audit timezone settings for notebooks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public config class</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="config.get_fabric_context-get_fabric_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_fabric_context" data-callable-module="config" data-function-type="public-starter-kit" data-callable-purpose="Create a context dictionary for helper context overrides.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_fabric_context/"><code>get_fabric_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create a context dictionary for helper context overrides.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 1</span></summary><ul><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="governance_review-get_latest_metadata_catalogue" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_latest_metadata_catalogue" data-callable-module="governance_review" data-callable-starter-path="99_explore" data-callable-usage-source="99_explore" data-function-type="public-starter-kit" data-callable-purpose="Fetch the latest metadata catalogue rows for a table without writing metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a></h3>
  <p class="reference-catalogue-item-purpose">Fetch the latest metadata catalogue rows for a table without writing metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 21</span></summary><ul><li><code>_latest_metadata_catalogue_lookup_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>_catalogue_lookup_value</code></li><li><code>_coerce_rows</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li><li><code>get_store</code></li><li><code>_normalize_schema_name</code></li><li><code>get_spark_session</code></li><li><code>read_delta_path</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>_normalize_path_config</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="config.shared-GovernanceConfig" class="reference-catalogue-item" data-callable-row="true" data-callable-name="GovernanceConfig" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-class" data-callable-purpose="Define governance labels, PII options, and enrichment widget custom fields.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/GovernanceConfig/"><code>GovernanceConfig</code></a></h3>
  <p class="reference-catalogue-item-purpose">Define governance labels, PII options, and enrichment widget custom fields.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public config class</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="config.shared-NotebookSetupContext" class="reference-catalogue-item" data-callable-row="true" data-callable-name="NotebookSetupContext" data-callable-module="config" data-function-type="public-class" data-callable-purpose="Carry resolved paths, runtime metadata, smoke checks, and readiness status.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/NotebookSetupContext/"><code>NotebookSetupContext</code></a></h3>
  <p class="reference-catalogue-item-purpose">Carry resolved paths, runtime metadata, smoke checks, and readiness status.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public config class</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="config.shared-PathConfig" class="reference-catalogue-item" data-callable-row="true" data-callable-name="PathConfig" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-class" data-callable-purpose="Group configured Fabric stores by environment and target name.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/PathConfig/"><code>PathConfig</code></a></h3>
  <p class="reference-catalogue-item-purpose">Group configured Fabric stores by environment and target name.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public config class</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="pipeline-prepare_pipeline_table_configs" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_pipeline_table_configs" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Prepare source or target table configs for 02_pipeline.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare source or target table configs for 02_pipeline.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 4</span></summary><ul><li><code>_prepare_pipeline_table_configs_workflow</code></li><li><code>get_current_audit_timestamp</code></li><li><code>get_audit_timezone</code></li><li><code>_validate_audit_timezone</code></li></ul></details>
  </div>
</article>
<article id="data_profiling.profile_dataframe-profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="99_explore" data-callable-usage-source="99_explore" data-function-type="public-starter-kit" data-callable-purpose="Profile a source or target DataFrame for schema, quality, and catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="io.read_lakehouse_csv-read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="io" data-function-type="public-starter-kit" data-callable-purpose="Read a CSV file from a configured Fabric-resolved path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a configured Fabric-resolved path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 14</span></summary><ul><li><code>get_spark_session</code></li><li><code>read_csv_path</code></li><li><code>resolve_configured_file_path</code></li><li><code>resolve_lakehouse_file_location</code></li><li><code>resolve_target_store</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_relative_path</code></li><li><code>_validate_warehouse_store</code></li><li><code>resolve_lakehouse_file_path</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="io.read_lakehouse_excel-read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="io" data-function-type="public-starter-kit" data-callable-purpose="Read an Excel file from a configured Fabric-resolved path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read an Excel file from a configured Fabric-resolved path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 15</span></summary><ul><li><code>get_spark_session</code></li><li><code>read_excel_file</code></li><li><code>resolve_configured_file_path</code></li><li><code>_load_pandas</code></li><li><code>resolve_lakehouse_file_location</code></li><li><code>resolve_target_store</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_relative_path</code></li><li><code>_validate_warehouse_store</code></li><li><code>resolve_lakehouse_file_path</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="io.read_lakehouse_parquet-read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="io" data-function-type="public-starter-kit" data-callable-purpose="Read a Parquet path from a configured Fabric-resolved path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Parquet path from a configured Fabric-resolved path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 14</span></summary><ul><li><code>convert_single_parquet_ns_to_us</code></li><li><code>get_spark_session</code></li><li><code>resolve_configured_file_path</code></li><li><code>resolve_lakehouse_file_path</code></li><li><code>_join_lakehouse_area_path</code></li><li><code>_validate_relative_path</code></li><li><code>resolve_lakehouse_file_location</code></li><li><code>resolve_target_store</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="io.read_lakehouse_table-read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="io" data-callable-starter-path="02_pipeline, 99_explore" data-callable-usage-source="02_pipeline, 99_explore" data-function-type="public-starter-kit" data-callable-purpose="Read a Delta table from a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Delta table from a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 16</span></summary><ul><li><code>get_spark_session</code></li><li><code>read_delta_path</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li><li><code>_join_lakehouse_area_path</code></li><li><code>_normalize_schema_name</code></li></ul></details>
  </div>
</article>
<article id="io.read_warehouse_query-read_warehouse_query" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_query" data-callable-module="io" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_query/"><code>read_warehouse_query</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 12</span></summary><ul><li><code>get_spark_session</code></li><li><code>read_warehouse_synapsesql</code></li><li><code>resolve_configured_warehouse_query_target</code></li><li><code>validate_select_query</code></li><li><code>_require_fabric_connector</code></li><li><code>resolve_target_store</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="io.read_warehouse_table-read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="io" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Read a table from a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 15</span></summary><ul><li><code>get_spark_session</code></li><li><code>read_warehouse_synapsesql</code></li><li><code>resolve_configured_warehouse_table</code></li><li><code>_require_fabric_connector</code></li><li><code>resolve_target_store</code></li><li><code>resolve_warehouse_table_location</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_build_warehouse_object_name</code></li><li><code>_normalize_schema_name</code></li><li><code>_normalize_table_name</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="pipeline-run_table_guardrails" class="reference-catalogue-item" data-callable-row="true" data-callable-name="run_table_guardrails" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline, example_dq_rule_smoke_test" data-function-type="public-starter-kit" data-callable-purpose="Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, example_dq_rule_smoke_test</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, example_dq_rule_smoke_test</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 119</span></summary><ul><li><code>_run_table_guardrails_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>profile_dataframe_core</code></li><li><code>_run_active_dq_guardrail</code></li><li><code>_check_schema_rule_runtime</code></li><li><code>_check_schema_runtime</code></li><li><code>enforce_freshness</code></li><li><code>enforce_freshness_rule</code></li><li><code>enforce_profile_behavior</code></li><li><code>stop_if_failed</code></li><li><code>_build_metadata_table_key</code></li><li><code>_write_guardrail_result_row</code></li><li><code>_active_pipeline_context</code></li><li><code>_build_guardrail_blocking_message_from_bundle</code></li><li><code>_build_guardrail_evidence_definitions</code></li><li><code>_table_key</code></li><li><code>_table_name</code></li><li><code>build_guardrail_detail_rows</code></li><li><code>build_guardrail_summary_rows</code></li><li><code>write_catalogue_evidence</code></li><li><code>build_audit_timestamp_expr</code></li><li><code>get_audit_timezone</code></li><li><code>get_default_fabric_context</code></li><li><code>build_distribution_summaries</code></li><li><code>is_min_max_supported_type</code></li><li><code>resolve_profiled_columns</code></li><li><code>_dq_failed_row_count</code></li><li><code>_dq_summary</code></li><li><code>_dq_tagged_dataframe</code></li><li><code>_load_active_dq_rules</code></li><li><code>_read_guardrail_rule_metadata</code></li><li><code>_run_dq_guardrail_checks</code></li><li><code>_summarize_dq_guardrail</code></li><li><code>_accepted_profile_rows</code></li><li><code>_actual_schema</code></li><li><code>_apply_bypass_post_review_warning</code></li><li><code>_catalogue_value</code></li><li><code>_coerce_date</code></li><li><code>_guardrail_exclude_columns</code></li><li><code>_is_missing_table_error</code></li><li><code>_iso_date_value</code></li><li><code>_json_dumps_stable</code></li><li><code>_max_column_value</code></li><li><code>_normalize_datatype</code></li><li><code>_parse_rule_parameters</code></li><li><code>_profile_hash</code></li><li><code>_profile_payload_from_profile</code></li><li><code>_select_profile_behavior_rule</code></li><li><code>_select_table_guardrail_rule</code></li><li><code>_string_value</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>write_lakehouse_table_core</code></li><li><code>_audit_timestamp_value</code></li><li><code>_build_runtime_audit_fields</code></li><li><code>_stable_metadata_key</code></li><li><code>coerce_metadata_row_types</code></li><li><code>_blocking_guardrail_message</code></li><li><code>_canonical_catalogue_profile_df</code></li><li><code>_definition_name</code></li><li><code>_guardrail_reason</code></li><li><code>_next_action</code></li><li><code>_normalize_catalogue_evidence_types</code></li><li><code>_now_iso</code></li><li><code>_result_can_continue</code></li><li><code>_result_status</code></li><li><code>_runtime_audit_fields</code></li><li><code>_table_keys</code></li><li><code>_yes_no</code></li><li><code>metadata_table_schema_registry</code></li><li><code>_validate_audit_timezone</code></li><li><code>get_current_audit_timestamp</code></li><li><code>get_store</code></li><li><code>_build_categorical_distribution</code></li><li><code>_build_numeric_distribution</code></li><li><code>_numeric_bin_edges</code></li><li><code>_canonical_dq_rule_type</code></li><li><code>_coerce_rows</code></li><li><code>_dq_check_status</code></li><li><code>_dq_failed_expression</code></li><li><code>_latest_dq_rule_versions</code></li><li><code>_normalize_dq_severity</code></li><li><code>_spark_sql_helpers</code></li><li><code>_validate_dq_rules</code></li><li><code>_is_active_guardrail_rule</code></li><li><code>_normalize_profile</code></li><li><code>_profile_row_count</code></li><li><code>_row_to_dict</code></li><li><code>_rule_review_status</code></li><li><code>_schema_signature</code></li><li><code>_normalize_schema_name</code></li><li><code>get_spark_session</code></li><li><code>normalize_write_mode</code></li><li><code>read_delta_path</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>_coerce_metadata_value</code></li><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>_dq_reason</code></li><li><code>_freshness_reason</code></li><li><code>_profile_behavior_reason</code></li><li><code>_result_reason</code></li><li><code>_schema_reason</code></li><li><code>_timestamp_value</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_normalize_path_config</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>spark_types</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="config.setup_metadata_tables-setup_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_metadata_tables" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-starter-kit" data-callable-purpose="Create or validate all FabricOps metadata tables through one setup action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate all FabricOps metadata tables through one setup action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 16</span></summary><ul><li><code>metadata_table_field_names</code></li><li><code>metadata_table_schema_registry</code></li><li><code>_active_steward_count</code></li><li><code>_qualified_table</code></li><li><code>_resolve_metadata_schema</code></li><li><code>_setup_metadata_table_registry</code></li><li><code>validate_framework_config</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_is_missing_table_error</code></li><li><code>_read_table_direct</code></li><li><code>_write_empty_table_direct</code></li><li><code>_validate_audit_timezone</code></li><li><code>get_store</code></li><li><code>spark_types</code></li><li><code>_normalize_path_config</code></li></ul></details>
  </div>
</article>
<article id="config.setup_notebook-setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-starter-kit" data-callable-purpose="Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 12</span></summary><ul><li><code>_setup_notebook_workflow</code></li><li><code>_run_config_smoke_tests</code></li><li><code>_validate_framework_config</code></li><li><code>get_current_audit_timestamp</code></li><li><code>get_store</code></li><li><code>_check_spark_session</code></li><li><code>_get_fabric_runtime_metadata</code></li><li><code>_normalize_path_config</code></li><li><code>_validate_notebook_name</code></li><li><code>get_audit_timezone</code></li><li><code>validate_framework_config</code></li><li><code>_validate_audit_timezone</code></li></ul></details>
  </div>
</article>
<article id="pipeline-start_pipeline_run" class="reference-catalogue-item" data-callable-row="true" data-callable-name="start_pipeline_run" data-callable-module="pipeline" data-callable-starter-path="02_pipeline, 99_explore" data-callable-usage-source="02_pipeline, 99_explore" data-function-type="public-starter-kit" data-callable-purpose="Start a guided notebook run and store runtime defaults.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></h3>
  <p class="reference-catalogue-item-purpose">Start a guided notebook run and store runtime defaults.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 55</span></summary><ul><li><code>_start_pipeline_run_workflow</code></li><li><code>get_selected_agreement</code></li><li><code>widget_select_agreement</code></li><li><code>_now_iso</code></li><li><code>get_current_audit_timestamp</code></li><li><code>resolve_fabric_context</code></li><li><code>_latest_agreement_versions</code></li><li><code>_list_data_agreements</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li><li><code>_html_escape</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>get_audit_timezone</code></li><li><code>get_default_fabric_context</code></li><li><code>_audit_date</code></li><li><code>_coerce_row_dicts</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_parse_contract_version</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>_audit_timestamp_value</code></li><li><code>_context_get</code></li><li><code>_load_notebook_registry</code></li><li><code>_notebook_registration_key</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>coerce_metadata_row_types</code></li><li><code>_widget_common</code></li><li><code>metadata_table_schema_registry</code></li><li><code>_validate_audit_timezone</code></li><li><code>get_store</code></li><li><code>_config_value</code></li><li><code>_normalize_schema_name</code></li><li><code>normalize_write_mode</code></li><li><code>read_lakehouse_table_core</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>_coerce_metadata_value</code></li><li><code>_coerce_row_dicts</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_normalize_path_config</code></li><li><code>get_spark_session</code></li><li><code>read_delta_path</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>spark_types</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_author_dq_rules-widget_author_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_dq_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render interactive manual DQ guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive manual DQ guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 3</span></summary><ul><li><code>_dq_rule_authoring_widget_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_author_schema_freshness_profile_rules-widget_author_schema_freshness_profile_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_schema_freshness_profile_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render interactive schema, freshness, and profile-behavior guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive schema, freshness, and profile-behavior guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 3</span></summary><ul><li><code>_schema_freshness_profile_rule_authoring_widget_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_enrich_table_metadata-widget_enrich_table_metadata" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_enrich_table_metadata" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render a consolidated column enrichment widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a consolidated column enrichment widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 3</span></summary><ul><li><code>_table_metadata_enrichment_widget_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_render_agreement_evidence-widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="public-starter-kit" data-callable-purpose="Render the standalone agreement-evidence widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone agreement-evidence widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 01_agreement</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 47</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_render_agreement_evidence_widget_workflow</code></li><li><code>get_default_fabric_context</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_save_agreement_evidence_records</code></li><li><code>_widget_common</code></li><li><code>get_current_audit_timestamp</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>_build_runtime_audit_fields</code></li><li><code>_coerce_row_dicts</code></li><li><code>_config_value</code></li><li><code>_html_escape</code></li><li><code>_prepare_evidence_file_references</code></li><li><code>_write_row</code></li><li><code>get_audit_timezone</code></li><li><code>get_store</code></li><li><code>_normalize_schema_name</code></li><li><code>get_spark_session</code></li><li><code>read_delta_path</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>write_lakehouse_table_core</code></li><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>coerce_metadata_row_types</code></li><li><code>_get_notebookutils</code></li><li><code>metadata_table_schema_registry</code></li><li><code>_normalize_path_config</code></li><li><code>_validate_audit_timezone</code></li><li><code>normalize_write_mode</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>_coerce_metadata_value</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>spark_types</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_render_data_agreement-widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="public-starter-kit" data-callable-purpose="Render the standalone data-agreement intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-agreement intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 01_agreement</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 67</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_render_maintenance_widget_shared_workflow</code></li><li><code>get_default_fabric_context</code></li><li><code>_agreement_identity_text</code></li><li><code>_collect_custom_fields</code></li><li><code>_config_value</code></li><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_deserialize_custom_fields</code></li><li><code>_get_widget_visible_fields</code></li><li><code>_list_data_agreements</code></li><li><code>_list_data_stewards</code></li><li><code>_render_custom_fields</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_standard_widget</code></li><li><code>_to_bool</code></li><li><code>_to_iso_date</code></li><li><code>read_lakehouse_table_core</code></li><li><code>_build_runtime_audit_fields</code></li><li><code>_active_steward</code></li><li><code>_audit_date</code></li><li><code>_business_agreement_snapshot</code></li><li><code>_generate_agreement_id</code></li><li><code>_generate_steward_id</code></li><li><code>_html_escape</code></li><li><code>_latest_agreement_versions</code></li><li><code>_latest_by_key</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_next_minor_version</code></li><li><code>_parse_contract_version</code></li><li><code>_parse_iso_date</code></li><li><code>_serialize_custom_fields</code></li><li><code>_widget_common</code></li><li><code>_write_row</code></li><li><code>get_current_audit_timestamp</code></li><li><code>get_store</code></li><li><code>configured_lakehouse_schema</code></li><li><code>get_spark_session</code></li><li><code>read_delta_path</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>write_lakehouse_table_core</code></li><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>coerce_metadata_row_types</code></li><li><code>_coerce_row_dicts</code></li><li><code>metadata_table_schema_registry</code></li><li><code>_normalize_path_config</code></li><li><code>get_audit_timezone</code></li><li><code>_normalize_schema_name</code></li><li><code>normalize_write_mode</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>_coerce_metadata_value</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_validate_audit_timezone</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>spark_types</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_render_data_steward-widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="public-starter-kit" data-callable-purpose="Render the standalone data-steward intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-steward intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 01_agreement</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 67</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_render_maintenance_widget_shared_workflow</code></li><li><code>get_default_fabric_context</code></li><li><code>_agreement_identity_text</code></li><li><code>_collect_custom_fields</code></li><li><code>_config_value</code></li><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_deserialize_custom_fields</code></li><li><code>_get_widget_visible_fields</code></li><li><code>_list_data_agreements</code></li><li><code>_list_data_stewards</code></li><li><code>_render_custom_fields</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_standard_widget</code></li><li><code>_to_bool</code></li><li><code>_to_iso_date</code></li><li><code>read_lakehouse_table_core</code></li><li><code>_build_runtime_audit_fields</code></li><li><code>_active_steward</code></li><li><code>_audit_date</code></li><li><code>_business_agreement_snapshot</code></li><li><code>_generate_agreement_id</code></li><li><code>_generate_steward_id</code></li><li><code>_html_escape</code></li><li><code>_latest_agreement_versions</code></li><li><code>_latest_by_key</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_next_minor_version</code></li><li><code>_parse_contract_version</code></li><li><code>_parse_iso_date</code></li><li><code>_serialize_custom_fields</code></li><li><code>_widget_common</code></li><li><code>_write_row</code></li><li><code>get_current_audit_timestamp</code></li><li><code>get_store</code></li><li><code>configured_lakehouse_schema</code></li><li><code>get_spark_session</code></li><li><code>read_delta_path</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>write_lakehouse_table_core</code></li><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>coerce_metadata_row_types</code></li><li><code>_coerce_row_dicts</code></li><li><code>metadata_table_schema_registry</code></li><li><code>_normalize_path_config</code></li><li><code>get_audit_timezone</code></li><li><code>_normalize_schema_name</code></li><li><code>normalize_write_mode</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>_coerce_metadata_value</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_validate_audit_timezone</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>spark_types</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_review_guardrail_governance-widget_review_guardrail_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_guardrail_governance" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render interactive controls for reviewing proposed and bypassed guardrail rules.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive controls for reviewing proposed and bypassed guardrail rules.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 3</span></summary><ul><li><code>_guardrail_governance_review_widget_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="widgets.widget_select_guardrail_target-widget_select_guardrail_target" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_guardrail_target" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render an interactive target selector for guardrail authoring and governance review.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an interactive target selector for guardrail authoring and governance review.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 3</span></summary><ul><li><code>_guardrail_target_selection_widget_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="io.write_lakehouse_table-write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="io" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test" data-function-type="public-starter-kit" data-callable-purpose="Write a Spark DataFrame to a configured Fabric lakehouse Delta table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a Spark DataFrame to a configured Fabric lakehouse Delta table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 17</span></summary><ul><li><code>normalize_write_mode</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li><li><code>_join_lakehouse_area_path</code></li><li><code>_normalize_schema_name</code></li></ul></details>
  </div>
</article>
<article id="pipeline-write_pipeline_lineage" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_lineage" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Write many-to-many source-to-target lineage evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write many-to-many source-to-target lineage evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 39</span></summary><ul><li><code>_write_pipeline_lineage_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>_build_metadata_table_key</code></li><li><code>coerce_metadata_row_types</code></li><li><code>_definition_name</code></li><li><code>_runtime_audit_fields</code></li><li><code>_timestamp_value</code></li><li><code>metadata_table_schema_registry</code></li><li><code>get_default_fabric_context</code></li><li><code>get_store</code></li><li><code>_normalize_schema_name</code></li><li><code>normalize_write_mode</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>_audit_timestamp_value</code></li><li><code>_build_runtime_audit_fields</code></li><li><code>_coerce_metadata_value</code></li><li><code>_stable_metadata_key</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_normalize_path_config</code></li><li><code>get_current_audit_timestamp</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>spark_types</code></li><li><code>get_audit_timezone</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_validate_audit_timezone</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="pipeline-write_pipeline_run_summary" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_run_summary" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Write one pipeline runtime summary row to metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write one pipeline runtime summary row to metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 39</span></summary><ul><li><code>_write_pipeline_run_summary_workflow</code></li><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>coerce_metadata_row_types</code></li><li><code>_active_pipeline_context</code></li><li><code>_definition_name</code></li><li><code>_runtime_audit_fields</code></li><li><code>_summary_status</code></li><li><code>_timestamp_value</code></li><li><code>metadata_table_schema_registry</code></li><li><code>get_default_fabric_context</code></li><li><code>get_store</code></li><li><code>_normalize_schema_name</code></li><li><code>normalize_write_mode</code></li><li><code>resolve_configured_lakehouse_table</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_delta_path</code></li><li><code>_audit_timestamp_value</code></li><li><code>_build_runtime_audit_fields</code></li><li><code>_coerce_metadata_value</code></li><li><code>_schema</code></li><li><code>audit_schema_fields</code></li><li><code>_normalize_path_config</code></li><li><code>get_current_audit_timestamp</code></li><li><code>resolve_lakehouse_table_location</code></li><li><code>resolve_target_store</code></li><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>spark_types</code></li><li><code>get_audit_timezone</code></li><li><code>_normalize_table_name</code></li><li><code>_resolve_lakehouse_schema</code></li><li><code>_resolve_lakehouse_table_path</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_validate_audit_timezone</code></li><li><code>_join_lakehouse_area_path</code></li></ul></details>
  </div>
</article>
<article id="io.write_warehouse_table-write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="io" data-function-type="public-starter-kit" data-callable-purpose="Write a DataFrame to a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 15</span></summary><ul><li><code>resolve_configured_warehouse_table</code></li><li><code>validate_dataframe_writer</code></li><li><code>write_warehouse_synapsesql</code></li><li><code>_require_fabric_connector</code></li><li><code>resolve_target_store</code></li><li><code>resolve_warehouse_table_location</code></li><li><code>get_store</code></li><li><code>resolve_fabric_context</code></li><li><code>_build_warehouse_object_name</code></li><li><code>_normalize_schema_name</code></li><li><code>_normalize_table_name</code></li><li><code>_validate_lakehouse_store</code></li><li><code>_validate_warehouse_store</code></li><li><code>_normalize_path_config</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
</div>

