# Function Reference

Use this page as a callable lookup after you understand the notebook flow.

- Use [Template Function Map](template-function-map.md) to see what notebook users actually call.
- Use the Function catalogue below to browse the public v1 callable API.
- Use Implementation Modules only when debugging or maintaining the package internals.

> Graph exploration is intentionally deferred. Future PR may use Neo4j or a proper graph backend.

## Find a callable

Use the finder below to look up public callable functions.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search callable functions</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search callable functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, role, starter path, or what the public function does.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">csv</span> <span class="callable-finder-chip">data_quality</span> <span class="callable-finder-chip">quarantine</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing all public callables.</p>
  <fieldset class="callable-role-filters">
    <legend>Role filters</legend>
    <label><input type="checkbox" data-role-filter="essential" checked> Essential</label>
    <p class="callable-role-note"><strong>Essential</strong>: Core functions used in the starter notebook flow.</p>
    <label><input type="checkbox" data-role-filter="optional" checked> Optional</label>
    <p class="callable-role-note"><strong>Optional</strong>: Extra helper functions for advanced or situational use.</p>
  </fieldset>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No callables match your search.</p>
</div>

## Function catalogue

## All public functions

<div class="reference-catalogue-list">
<article id="build_handover" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_handover" data-callable-module="handover" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Assemble final handover evidence for reviewed notebook work.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_handover/"><code>build_handover</code></a></h3>
  <p class="reference-catalogue-item-purpose">Assemble final handover evidence for reviewed notebook work.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="build_lineage_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_lineage_records" data-callable-module="data_lineage" data-callable-starter-path="03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Build source-to-target lineage evidence records for a pipeline run.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_lineage_records/"><code>build_lineage_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build source-to-target lineage evidence records for a pipeline run.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="get_selected_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_agreement" data-callable-module="data_agreement" data-callable-starter-path="03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Return the agreement selected by widget_select_agreement.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the agreement selected by widget_select_agreement.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="get_selected_catalogue_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_catalogue_table" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-role="essential" data-callable-purpose="Return the table selected by widget_select_catalogue_table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the table selected by widget_select_catalogue_table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="load_catalogue_profile_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_catalogue_profile_rows" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-role="essential" data-callable-purpose="Load column profile rows for the selected catalogue table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load column profile rows for the selected catalogue table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_coerce_rows</code></li><li><code>_is_success</code></li><li><code>_row_metadata_table_key</code></li><li><code>_value</code></li></ul></details>

  </div>
</article>
<article id="monitor_data_changes" class="reference-catalogue-item" data-callable-row="true" data-callable-name="monitor_data_changes" data-callable-module="drift" data-callable-starter-path="03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Profile data, compare against the approved baseline, and return a drift guardrail result.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/monitor_data_changes/"><code>monitor_data_changes</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile data, compare against the approved baseline, and return a drift guardrail result.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 8</span></summary><ul><li><code>profile_dataframe</code></li><li><code>_as_monitor_only_result</code></li><li><code>_check_profile_drift</code></li><li><code>_data_change_preset_config</code></li><li><code>_extract_categorical_distribution_categories</code></li><li><code>_extract_numeric_distribution_bin_edges</code></li><li><code>_load_latest_profile</code></li><li><code>_normalize_profile</code></li></ul></details>

  </div>
</article>
<article id="profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="02_ex_agreement_topic" data-role="essential" data-callable-purpose="Profile a source or target DataFrame for schema, quality, and catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex_agreement_topic</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_build_distribution_summaries</code></li><li><code>_get_profiled_columns</code></li><li><code>_is_min_max_supported_type</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_prepare_dq_profile_input_rows</code></li><li><code>monitor_data_changes</code></li></ul></details>
  </div>
</article>
<article id="read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Read a CSV file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Read an Excel file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read an Excel file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Read a Parquet path from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Parquet path from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_get_store</code></li><li><code>_convert_single_parquet_ns_to_us</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Read a table from a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 8</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_list_data_stewards</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>load_catalogue_profile_rows</code></li><li><code>widget_select_catalogue_table</code></li><li><code>_load_notebook_registry</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Read a table from a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="record_table_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="record_table_governance" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-role="essential" data-callable-purpose="Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/record_table_governance/"><code>record_table_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 6</span></summary><ul><li><code>_build_classification_records</code></li><li><code>_build_column_context_records</code></li><li><code>_build_dq_rule_records</code></li><li><code>_commit_column_classification</code></li><li><code>_commit_column_context</code></li><li><code>_commit_dq_rules</code></li></ul></details>

  </div>
</article>
<article id="render_handover_markdown" class="reference-catalogue-item" data-callable-row="true" data-callable-name="render_handover_markdown" data-callable-module="handover" data-callable-starter-path="—" data-role="essential" data-callable-purpose="Render handover evidence as notebook-friendly Markdown.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/render_handover_markdown/"><code>render_handover_markdown</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render handover evidence as notebook-friendly Markdown.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_status_of</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_handover_record</code></li></ul></details>
  </div>
</article>
<article id="setup_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_metadata_tables" data-callable-module="config" data-callable-starter-path="00_env_config" data-role="essential" data-callable-purpose="Create or validate all FabricOps metadata tables through one setup action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate all FabricOps metadata tables through one setup action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">00_env_config</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_setup_data_agreement_tables</code></li><li><code>get</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>

  </div>
</article>
<article id="setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config" data-role="essential" data-callable-purpose="Shared environment setup and runtime validation for notebook templates.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Shared environment setup and runtime validation for notebook templates.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">00_env_config</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>NotebookSetupContext</code></li><li><code>_get_store</code></li><li><code>_run_config_smoke_tests</code></li><li><code>_validate_framework_config</code></li></ul></details>

  </div>
</article>
<article id="stop_if_failed" class="reference-catalogue-item" data-callable-row="true" data-callable-name="stop_if_failed" data-callable-module="drift" data-callable-starter-path="03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Stop a notebook only when a schema or data-change guardrail result blocks continuation.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/stop_if_failed/"><code>stop_if_failed</code></a></h3>
  <p class="reference-catalogue-item-purpose">Stop a notebook only when a schema or data-change guardrail result blocks continuation.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>SchemaDriftError</code></li></ul></details>

  </div>
</article>
<article id="validate_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="validate_schema" data-callable-module="drift" data-callable-starter-path="03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/validate_schema/"><code>validate_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_actual_schema</code></li><li><code>_check_schema</code></li></ul></details>

  </div>
</article>
<article id="widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_da_agreement_template" data-role="essential" data-callable-purpose="Render the standalone agreement-evidence widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone agreement-evidence widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">01_da_agreement_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_agreement_evidence_widget</code></li></ul></details>

  </div>
</article>
<article id="widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_da_agreement_template" data-role="essential" data-callable-purpose="Render the standalone data-agreement intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-agreement intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">01_da_agreement_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_da_agreement_template" data-role="essential" data-callable-purpose="Render the standalone data-steward intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-steward intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">01_da_agreement_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="widget_review_column_classification" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_column_classification" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-role="essential" data-callable-purpose="Render standalone sensitivity and PII classification review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone sensitivity and PII classification review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="widget_review_column_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_column_context" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-role="essential" data-callable-purpose="Render standalone business-context review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_column_context/"><code>widget_review_column_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone business-context review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="widget_review_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_dq_rules" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-role="essential" data-callable-purpose="Render standalone DQ-rule review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone DQ-rule review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="widget_select_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_agreement" data-callable-module="data_agreement" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Render an agreement selector and optionally register the active notebook.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_agreement/"><code>widget_select_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an agreement selector and optionally register the active notebook.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>_html_escape</code></li><li><code>_latest_agreement_versions</code></li><li><code>_load_agreements</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li></ul></details>

  </div>
</article>
<article id="widget_select_catalogue_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_catalogue_table" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-role="essential" data-callable-purpose="Render a searchable selector for latest successful catalogue profiles.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a searchable selector for latest successful catalogue profiles.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_catalogue_table_options</code></li><li><code>_coerce_rows</code></li></ul></details>

  </div>
</article>
<article id="write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Write a DataFrame to a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_store</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 10</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_write_row</code></li><li><code>_write_dq_rules</code></li><li><code>_seed_minimal_sample_source_table</code></li><li><code>_commit_column_classification</code></li><li><code>_commit_column_context</code></li><li><code>_commit_dq_rules</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>_register_current_notebook</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc_agreement_pipeline_template" data-role="essential" data-callable-purpose="Write a DataFrame to a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-role reference-chip-essential">Essential</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_store</code></li></ul></details>

  </div>
</article>
</div>

