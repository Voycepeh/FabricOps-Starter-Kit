# Function Reference

Use this page as a function lookup after you understand the notebook flow.

- Use [Template Function Map](template-function-map.md) to see what notebook users call from the starter notebook templates.
- Use the Function catalogue below to browse the public v1 callables by default; enable Internal for package helpers.
- Use Implementation Modules only when debugging or maintaining current major source boundaries; they do not document every `.py` file.

> Graph exploration is intentionally deferred. Future PR may use Neo4j or a proper graph backend.

## Find a function

Use the finder below to look up callable and internal FabricOps functions.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search functions</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, function type, starter path, or description.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">csv</span> <span class="callable-finder-chip">data_quality</span> <span class="callable-finder-chip">quarantine</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing callable functions.</p>
  <fieldset class="callable-type-filters">
    <legend>Function type filters</legend>
    <label><input type="checkbox" data-function-type-filter="callable" checked> Callable</label>
    <p class="callable-type-note"><strong>Callable</strong>: Public functions intended for notebook authors.</p>
    <label><input type="checkbox" data-function-type-filter="internal"> Internal</label>
    <p class="callable-type-note"><strong>Internal</strong>: Supporting functions used by the package. Shown for transparency and debugging.</p>
  </fieldset>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No functions match your search.</p>
</div>

## Function catalogue

## Functions

<div class="reference-catalogue-list">
<article id="handover-build_handover" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_handover" data-callable-module="handover" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Assemble final handover evidence for reviewed notebook work.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_handover/"><code>build_handover</code></a></h3>
  <p class="reference-catalogue-item-purpose">Assemble final handover evidence for reviewed notebook work.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_lineage-build_lineage_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_lineage_records" data-callable-module="data_lineage" data-callable-starter-path="03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Build source-to-target lineage evidence records for a pipeline run.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_lineage_records/"><code>build_lineage_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build source-to-target lineage evidence records for a pipeline run.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_agreement-get_selected_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_agreement" data-callable-module="data_agreement" data-callable-starter-path="03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Return the agreement selected by widget_select_agreement.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the agreement selected by widget_select_agreement.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-get_selected_catalogue_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_catalogue_table" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-function-type="callable" data-callable-purpose="Return the table selected by widget_select_catalogue_table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the table selected by widget_select_catalogue_table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-load_catalogue_profile_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_catalogue_profile_rows" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-function-type="callable" data-callable-purpose="Load column profile rows for the selected catalogue table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load column profile rows for the selected catalogue table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_coerce_rows</code></li><li><code>_is_success</code></li><li><code>_value</code></li><li><code>_build_metadata_table_key</code></li></ul></details>

  </div>
</article>
<article id="drift-monitor_data_changes" class="reference-catalogue-item" data-callable-row="true" data-callable-name="monitor_data_changes" data-callable-module="drift" data-callable-starter-path="03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Profile data, compare against the approved baseline, and return a drift guardrail result.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/monitor_data_changes/"><code>monitor_data_changes</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile data, compare against the approved baseline, and return a drift guardrail result.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>profile_dataframe</code></li><li><code>_check_profile_drift</code></li><li><code>_data_change_preset_config</code></li><li><code>_extract_categorical_distribution_categories</code></li><li><code>_extract_numeric_distribution_bin_edges</code></li><li><code>_load_latest_profile</code></li><li><code>_normalize_profile</code></li></ul></details>

  </div>
</article>
<article id="data_profiling-profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="02_ex_agreement_topic" data-function-type="callable" data-callable-purpose="Profile a source or target DataFrame for schema, quality, and catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_ex_agreement_topic</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_build_distribution_summaries</code></li><li><code>_get_profiled_columns</code></li><li><code>_is_min_max_supported_type</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>monitor_data_changes</code></li><li><code>_prepare_dq_profile_input_rows</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Read a CSV file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Read an Excel file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read an Excel file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Read a Parquet path from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Parquet path from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_get_store</code></li><li><code>_convert_single_parquet_ns_to_us</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Read a table from a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 8</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_list_data_stewards</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>load_catalogue_profile_rows</code></li><li><code>widget_select_catalogue_table</code></li><li><code>_load_notebook_registry</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Read a table from a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="governance_review-record_table_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="record_table_governance" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-function-type="callable" data-callable-purpose="Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/record_table_governance/"><code>record_table_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>write_lakehouse_table</code></li><li><code>_build_classification_records</code></li><li><code>_build_column_context_records</code></li><li><code>_build_dq_rule_records</code></li></ul></details>

  </div>
</article>
<article id="handover-render_handover_markdown" class="reference-catalogue-item" data-callable-row="true" data-callable-name="render_handover_markdown" data-callable-module="handover" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Render handover evidence as notebook-friendly Markdown.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/render_handover_markdown/"><code>render_handover_markdown</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render handover evidence as notebook-friendly Markdown.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_status_of</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_handover_record</code></li></ul></details>
  </div>
</article>
<article id="config-setup_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_metadata_tables" data-callable-module="config" data-callable-starter-path="00_env_config" data-function-type="callable" data-callable-purpose="Create or validate all FabricOps metadata tables through one setup action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate all FabricOps metadata tables through one setup action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_setup_data_agreement_tables</code></li><li><code>get</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>

  </div>
</article>
<article id="config-setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config" data-function-type="callable" data-callable-purpose="Shared environment setup and runtime validation for notebook templates.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Shared environment setup and runtime validation for notebook templates.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>NotebookSetupContext</code></li><li><code>_get_store</code></li><li><code>_run_config_smoke_tests</code></li><li><code>_validate_framework_config</code></li></ul></details>

  </div>
</article>
<article id="drift-stop_if_failed" class="reference-catalogue-item" data-callable-row="true" data-callable-name="stop_if_failed" data-callable-module="drift" data-callable-starter-path="03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Stop a notebook only when a schema or data-change guardrail result blocks continuation.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/stop_if_failed/"><code>stop_if_failed</code></a></h3>
  <p class="reference-catalogue-item-purpose">Stop a notebook only when a schema or data-change guardrail result blocks continuation.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>SchemaDriftError</code></li></ul></details>

  </div>
</article>
<article id="drift-validate_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="validate_schema" data-callable-module="drift" data-callable-starter-path="03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/validate_schema/"><code>validate_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_actual_schema</code></li><li><code>_normalize_datatype</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_da_agreement_template" data-function-type="callable" data-callable-purpose="Render the standalone agreement-evidence widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone agreement-evidence widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_da_agreement_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_agreement_evidence_widget</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_da_agreement_template" data-function-type="callable" data-callable-purpose="Render the standalone data-agreement intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-agreement intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_da_agreement_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_da_agreement_template" data-function-type="callable" data-callable-purpose="Render the standalone data-steward intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-steward intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_da_agreement_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_review_column_classification" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_column_classification" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-function-type="callable" data-callable-purpose="Render standalone sensitivity and PII classification review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone sensitivity and PII classification review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_review_column_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_column_context" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-function-type="callable" data-callable-purpose="Render standalone business-context review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_column_context/"><code>widget_review_column_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone business-context review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_review_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_dq_rules" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-function-type="callable" data-callable-purpose="Render standalone DQ-rule review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone DQ-rule review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_select_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_agreement" data-callable-module="data_agreement" data-callable-starter-path="02_ex_agreement_topic, 03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Render an agreement selector and optionally register the active notebook.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_agreement/"><code>widget_select_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an agreement selector and optionally register the active notebook.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_ex_agreement_topic, 03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>_html_escape</code></li><li><code>_latest_agreement_versions</code></li><li><code>_list_data_agreements</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_select_catalogue_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_catalogue_table" data-callable-module="governance_review" data-callable-starter-path="04_gov_dataset_table" data-function-type="callable" data-callable-purpose="Render a searchable selector for latest successful catalogue profiles.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a searchable selector for latest successful catalogue profiles.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">04_gov_dataset_table</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_catalogue_table_options</code></li><li><code>_coerce_rows</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Write a DataFrame to a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_store</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 7</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_write_row</code></li><li><code>_seed_minimal_sample_source_table</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>record_table_governance</code></li><li><code>_register_current_notebook</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="03_pc_agreement_pipeline_template" data-function-type="callable" data-callable-purpose="Write a DataFrame to a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_pc_agreement_pipeline_template</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_store</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-_active_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_active_steward" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__active_steward/"><code>_active_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_to_bool</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_create_or_update_data_steward</code></li><li><code>_list_data_stewards</code></li></ul></details>
  </div>
</article>
<article id="drift-_actual_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_actual_schema" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__actual_schema/"><code>_actual_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_normalize_datatype</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>validate_schema</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_agreement_identity_text" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_agreement_identity_text" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return read-only agreement version context for the notebook form.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__agreement_identity_text/"><code>_agreement_identity_text</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return read-only agreement version context for the notebook form.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_next_minor_version</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_approved_column_identity" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_approved_column_identity" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__approved_column_identity/"><code>_approved_column_identity</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_value</code></li><li><code>_build_metadata_column_key</code></li><li><code>_build_metadata_table_key</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_build_classification_records</code></li><li><code>_build_column_context_records</code></li><li><code>_build_dq_rule_records</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_approved_dq_rules_from_review_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_approved_dq_rules_from_review_rows" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return approved canonical DQ rules from notebook review rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__approved_dq_rules_from_review_rows/"><code>_approved_dq_rules_from_review_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return approved canonical DQ rules from notebook review rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-_approved_review_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_approved_review_context" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__approved_review_context/"><code>_approved_review_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_value</code></li><li><code>_build_runtime_audit_fields</code></li><li><code>_now_utc_iso</code></li><li><code>_resolve_action_by</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_build_classification_records</code></li><li><code>_build_column_context_records</code></li><li><code>_build_dq_rule_records</code></li></ul></details>
  </div>
</article>
<article id="config-_assert_valid_dataset_contract" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_assert_valid_dataset_contract" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Raise when a dataset contract violates the expected schema.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__assert_valid_dataset_contract/"><code>_assert_valid_dataset_contract</code></a></h3>
  <p class="reference-catalogue-item-purpose">Raise when a dataset contract violates the expected schema.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>DatasetContractValidationError</code></li><li><code>_validate_dataset_contract</code></li></ul></details>

  </div>
</article>
<article id="config-_bootstrap_fabric_env" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_bootstrap_fabric_env" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Bootstrap 00_env_config environment readiness for FabricOps notebooks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__bootstrap_fabric_env/"><code>_bootstrap_fabric_env</code></a></h3>
  <p class="reference-catalogue-item-purpose">Bootstrap 00_env_config environment readiness for FabricOps notebooks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>ConfigBootstrapResult</code></li><li><code>_get_fabric_runtime_metadata</code></li><li><code>_get_store</code></li><li><code>_run_config_smoke_tests</code></li><li><code>_validate_framework_config</code></li></ul></details>

  </div>
</article>
<article id="data_profiling-_build_categorical_distribution" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_categorical_distribution" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__build_categorical_distribution/"><code>_build_categorical_distribution</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_distribution_summaries</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_build_classification_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_classification_records" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build append-only approved sensitivity and PII classification records.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__build_classification_records/"><code>_build_classification_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build append-only approved sensitivity and PII classification records.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_approved_column_identity</code></li><li><code>_approved_review_context</code></li><li><code>_json</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>record_table_governance</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_build_column_context_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_column_context_records" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build append-only approved business-context records from explicit reviews.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__build_column_context_records/"><code>_build_column_context_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build append-only approved business-context records from explicit reviews.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_approved_column_identity</code></li><li><code>_approved_review_context</code></li><li><code>_json</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>record_table_governance</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_build_distribution_summaries" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_distribution_summaries" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__build_distribution_summaries/"><code>_build_distribution_summaries</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>_build_categorical_distribution</code></li><li><code>_build_numeric_distribution</code></li><li><code>_is_categorical_type</code></li><li><code>_is_numeric_type</code></li><li><code>_numeric_bin_edges</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>profile_dataframe</code></li></ul></details>
  </div>
</article>
<article id="metadata-_build_dq_rule_key" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_dq_rule_key" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__build_dq_rule_key/"><code>_build_dq_rule_key</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_sha256_key</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_dq_rule_records</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_build_dq_rule_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_dq_rule_records" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build append-only approved DQ-rule records without enforcing them.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__build_dq_rule_records/"><code>_build_dq_rule_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build append-only approved DQ-rule records without enforcing them.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>_approved_column_identity</code></li><li><code>_approved_review_context</code></li><li><code>_canonical_dq_rule_type</code></li><li><code>_json</code></li><li><code>_build_dq_rule_key</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>record_table_governance</code></li></ul></details>
  </div>
</article>
<article id="metadata-_build_evidence_row" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_evidence_row" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build a lightweight metadata-ready evidence row.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__build_evidence_row/"><code>_build_evidence_row</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build a lightweight metadata-ready evidence row.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_now_utc_iso</code></li></ul></details>

  </div>
</article>
<article id="handover-_build_handover_record" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_handover_record" data-callable-module="handover" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Execute the `_build_handover_record` workflow step in FabricOps.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/handover__build_handover_record/"><code>_build_handover_record</code></a></h3>
  <p class="reference-catalogue-item-purpose">Execute the `_build_handover_record` workflow step in FabricOps.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_status_of</code></li><li><code>render_handover_markdown</code></li></ul></details>

  </div>
</article>
<article id="data_lineage-_build_lineage_handover_markdown" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_lineage_handover_markdown" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build a concise markdown handover summary from lineage execution results.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__build_lineage_handover_markdown/"><code>_build_lineage_handover_markdown</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build a concise markdown handover summary from lineage execution results.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="data_lineage-_build_lineage_record_from_steps" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_lineage_record_from_steps" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Create metadata-ready lineage records from validated lineage steps.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__build_lineage_record_from_steps/"><code>_build_lineage_record_from_steps</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create metadata-ready lineage records from validated lineage steps.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_validate_lineage_steps</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_lineage_records</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_build_lineage_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_lineage_records" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build metadata-ready lineage rows from validated lineage steps.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__build_lineage_records/"><code>_build_lineage_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build metadata-ready lineage rows from validated lineage steps.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_build_lineage_record_from_steps</code></li></ul></details>

  </div>
</article>
<article id="metadata-_build_metadata_column_key" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_metadata_column_key" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__build_metadata_column_key/"><code>_build_metadata_column_key</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_sha256_key</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_approved_column_identity</code></li></ul></details>
  </div>
</article>
<article id="metadata-_build_metadata_table_key" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_metadata_table_key" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__build_metadata_table_key/"><code>_build_metadata_table_key</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_sha256_key</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_approved_column_identity</code></li><li><code>_catalogue_table_options</code></li><li><code>load_catalogue_profile_rows</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_build_numeric_distribution" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_numeric_distribution" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__build_numeric_distribution/"><code>_build_numeric_distribution</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_dedupe_edges</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_distribution_summaries</code></li></ul></details>
  </div>
</article>
<article id="metadata-_build_runtime_audit_fields" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_build_runtime_audit_fields" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build reusable framework-managed audit fields for metadata-table rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__build_runtime_audit_fields/"><code>_build_runtime_audit_fields</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build reusable framework-managed audit fields for metadata-table rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_context_get</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 4</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_save_agreement_evidence_records</code></li><li><code>_approved_review_context</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_business_agreement_snapshot" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_business_agreement_snapshot" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return user-facing agreement values used to detect business changes.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__business_agreement_snapshot/"><code>_business_agreement_snapshot</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return user-facing agreement values used to detect business changes.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_deserialize_custom_fields</code></li><li><code>_serialize_custom_fields</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_create_or_update_data_agreement</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_call_name" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_call_name" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__call_name/"><code>_call_name</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_scan_notebook_lineage</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_canonical_dq_rule_type" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_canonical_dq_rule_type" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__canonical_dq_rule_type/"><code>_canonical_dq_rule_type</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_build_dq_rule_records</code></li><li><code>_extract_candidate_rules_from_responses</code></li><li><code>_validate_dq_rules</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_catalogue_table_options" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_catalogue_table_options" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return one option per logical table using its latest successful profile.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__catalogue_table_options/"><code>_catalogue_table_options</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return one option per logical table using its latest successful profile.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_is_success</code></li><li><code>_value</code></li><li><code>_build_metadata_table_key</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>widget_select_catalogue_table</code></li></ul></details>
  </div>
</article>
<article id="drift-_categorical_distance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_categorical_distance" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__categorical_distance/"><code>_categorical_distance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_check_profile_drift</code></li></ul></details>
  </div>
</article>
<article id="config-_check_fabric_ai_functions_available" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_check_fabric_ai_functions_available" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Check whether Fabric AI Functions can be imported in the current runtime.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__check_fabric_ai_functions_available/"><code>_check_fabric_ai_functions_available</code></a></h3>
  <p class="reference-catalogue-item-purpose">Check whether Fabric AI Functions can be imported in the current runtime.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="fabric_input_output-_check_naming_convention" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_check_naming_convention" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Check whether a Fabric notebook name starts with an allowed prefix.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/fabric_input_output__check_naming_convention/"><code>_check_naming_convention</code></a></h3>
  <p class="reference-catalogue-item-purpose">Check whether a Fabric notebook name starts with an allowed prefix.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_fabric_runtime_context</code></li></ul></details>

  </div>
</article>
<article id="drift-_check_profile_drift" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_check_profile_drift" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Compare profile metrics against a baseline profile and drift thresholds.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__check_profile_drift/"><code>_check_profile_drift</code></a></h3>
  <p class="reference-catalogue-item-purpose">Compare profile metrics against a baseline profile and drift thresholds.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_categorical_distance</code></li><li><code>_normalize_profile</code></li><li><code>_numeric_psi</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>monitor_data_changes</code></li></ul></details>
  </div>
</article>
<article id="config-_check_spark_session" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_check_spark_session" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Check whether a Spark session is available.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__check_spark_session/"><code>_check_spark_session</code></a></h3>
  <p class="reference-catalogue-item-purpose">Check whether a Spark session is available.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_run_config_smoke_tests</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_coerce_row_dicts" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_coerce_row_dicts" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__coerce_row_dicts/"><code>_coerce_row_dicts</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 4</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_latest_agreement_versions</code></li><li><code>_latest_by_key</code></li><li><code>_list_all_data_agreement_rows</code></li></ul></details>
  </div>
</article>
<article id="metadata-_coerce_row_dicts" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_coerce_row_dicts" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__coerce_row_dicts/"><code>_coerce_row_dicts</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_column_names</code></li><li><code>_registry_rows_with_defaults</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_coerce_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_coerce_rows" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__coerce_rows/"><code>_coerce_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 5</span></summary><ul><li><code>_extract_assignment_payload</code></li><li><code>_extract_pii_suggestions</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>load_catalogue_profile_rows</code></li><li><code>widget_select_catalogue_table</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_collect_custom_fields" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_collect_custom_fields" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Collect and validate configured custom-field widget values.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__collect_custom_fields/"><code>_collect_custom_fields</code></a></h3>
  <p class="reference-catalogue-item-purpose">Collect and validate configured custom-field widget values.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>get</code></li><li><code>_to_iso_date</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="metadata-_column_context_rows_for_spark" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_column_context_rows_for_spark" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__column_context_rows_for_spark/"><code>_column_context_rows_for_spark</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_register_current_notebook</code></li><li><code>_setup_notebook_registry_table</code></li><li><code>_write_metadata_rows</code></li></ul></details>
  </div>
</article>
<article id="metadata-_column_names" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_column_names" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__column_names/"><code>_column_names</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_coerce_row_dicts</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_config_value" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_config_value" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__config_value/"><code>_config_value</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 8</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_ensure_metadata_tables</code></li><li><code>_get_widget_visible_fields</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_list_data_stewards</code></li><li><code>_render_maintenance_widget</code></li><li><code>_save_agreement_evidence_records</code></li></ul></details>
  </div>
</article>
<article id="config-_configure_fabric_ai_functions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_configure_fabric_ai_functions" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Apply optional default Fabric AI Function configuration.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__configure_fabric_ai_functions/"><code>_configure_fabric_ai_functions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Apply optional default Fabric AI Function configuration.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="metadata-_context_get" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_context_get" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__context_get/"><code>_context_get</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 5</span></summary><ul><li><code>_build_runtime_audit_fields</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li><li><code>_resolve_action_by</code></li><li><code>_runtime_context</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-_convert_single_parquet_ns_to_us" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_convert_single_parquet_ns_to_us" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Convert one Parquet file from nanosecond to microsecond timestamps.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/fabric_input_output__convert_single_parquet_ns_to_us/"><code>_convert_single_parquet_ns_to_us</code></a></h3>
  <p class="reference-catalogue-item-purpose">Convert one Parquet file from nanosecond to microsecond timestamps.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>read_lakehouse_parquet</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_create_or_update_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_create_or_update_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Append a new agreement or a new semantic version of an existing one.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__create_or_update_data_agreement/"><code>_create_or_update_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Append a new agreement or a new semantic version of an existing one.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 11</span></summary><ul><li><code>_business_agreement_snapshot</code></li><li><code>_config_value</code></li><li><code>_generate_agreement_id</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_list_data_stewards</code></li><li><code>_next_minor_version</code></li><li><code>_parse_contract_version</code></li><li><code>_parse_iso_date</code></li><li><code>_serialize_custom_fields</code></li><li><code>_write_row</code></li><li><code>_build_runtime_audit_fields</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_create_or_update_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_create_or_update_data_steward" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Append a created or updated steward assignment with runtime audit fields.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__create_or_update_data_steward/"><code>_create_or_update_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Append a created or updated steward assignment with runtime audit fields.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 8</span></summary><ul><li><code>_active_steward</code></li><li><code>_config_value</code></li><li><code>_generate_steward_id</code></li><li><code>_parse_iso_date</code></li><li><code>_serialize_custom_fields</code></li><li><code>_to_bool</code></li><li><code>_write_row</code></li><li><code>_build_runtime_audit_fields</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="metadata-_current_notebook_active_registrations" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_current_notebook_active_registrations" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return active agreement registrations for the running notebook.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__current_notebook_active_registrations/"><code>_current_notebook_active_registrations</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return active agreement registrations for the running notebook.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_context_get</code></li><li><code>_load_notebook_registry</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="drift-_data_change_preset_config" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_data_change_preset_config" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__data_change_preset_config/"><code>_data_change_preset_config</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>monitor_data_changes</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_dedupe_edges" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_dedupe_edges" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__dedupe_edges/"><code>_dedupe_edges</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_build_numeric_distribution</code></li><li><code>_numeric_bin_edges</code></li></ul></details>
  </div>
</article>
<article id="metadata-_default_evidence_types" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_default_evidence_types" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return canonical evidence type names used across metadata records.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__default_evidence_types/"><code>_default_evidence_types</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return canonical evidence type names used across metadata records.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="config-_default_schema_text" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_default_schema_text" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__default_schema_text/"><code>_default_schema_text</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_load_schema</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_deserialize_custom_fields" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_deserialize_custom_fields" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Deserialize stored custom-field JSON for widget display.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__deserialize_custom_fields/"><code>_deserialize_custom_fields</code></a></h3>
  <p class="reference-catalogue-item-purpose">Deserialize stored custom-field JSON for widget display.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_business_agreement_snapshot</code></li><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_display_review_guidance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_display_review_guidance" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__display_review_guidance/"><code>_display_review_guidance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_value</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>widget_review_column_classification</code></li><li><code>widget_review_column_context</code></li><li><code>widget_review_dq_rules</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_draft_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_draft_business_context" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Draft column business-context suggestions with Fabric AI.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__draft_business_context/"><code>_draft_business_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Draft column business-context suggestions with Fabric AI.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_run_fabric_ai_drafting</code></li></ul></details>

  </div>
</article>
<article id="governance_review-_draft_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_draft_dq_rules" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Draft candidate DQ rules from metadata profiles or a raw DataFrame fallback.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__draft_dq_rules/"><code>_draft_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Draft candidate DQ rules from metadata profiles or a raw DataFrame fallback.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_extract_candidate_rules_from_responses</code></li><li><code>_prepare_dq_profile_input_rows</code></li><li><code>_run_fabric_ai_drafting</code></li></ul></details>

  </div>
</article>
<article id="governance_review-_draft_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_draft_governance" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Draft sensitivity and PII classification suggestions with Fabric AI.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__draft_governance/"><code>_draft_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Draft sensitivity and PII classification suggestions with Fabric AI.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_run_fabric_ai_drafting</code></li></ul></details>

  </div>
</article>
<article id="governance_review-_enforce_dq" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_enforce_dq" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Enforce approved DQ rules and return structured deterministic outputs.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__enforce_dq/"><code>_enforce_dq</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce approved DQ rules and return structured deterministic outputs.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>DQEnforcementResult</code></li><li><code>_load_active_dq_rules</code></li><li><code>_run_dq_rules</code></li><li><code>_split_dq_rows</code></li><li><code>_validate_dq_rules</code></li></ul></details>

  </div>
</article>
<article id="data_lineage-_enrich_lineage_steps_with_ai" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_enrich_lineage_steps_with_ai" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Optionally enrich deterministic lineage steps using an AI helper callable.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__enrich_lineage_steps_with_ai/"><code>_enrich_lineage_steps_with_ai</code></a></h3>
  <p class="reference-catalogue-item-purpose">Optionally enrich deterministic lineage steps using an AI helper callable.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_fallback_copilot_lineage_prompt</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-_ensure_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_ensure_metadata_tables" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Idempotently create or validate lightweight ``01_da`` metadata tables.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__ensure_metadata_tables/"><code>_ensure_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Idempotently create or validate lightweight ``01_da`` metadata tables.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_coerce_row_dicts</code></li><li><code>_config_value</code></li><li><code>read_lakehouse_table</code></li><li><code>write_lakehouse_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_setup_data_agreement_tables</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_extract_assignment_payload" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_extract_assignment_payload" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Extract dictionary payloads from AI response rows with optional table-key narrowing.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__extract_assignment_payload/"><code>_extract_assignment_payload</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract dictionary payloads from AI response rows with optional table-key narrowing.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_coerce_rows</code></li><li><code>_parse_ai_dict_response</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_extract_candidate_rules_from_responses</code></li><li><code>_extract_column_business_context_suggestions</code></li><li><code>_extract_pii_suggestions</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_extract_candidate_rules_from_responses" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_extract_candidate_rules_from_responses" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Extract deduplicated candidate DQ rules from AI response rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__extract_candidate_rules_from_responses/"><code>_extract_candidate_rules_from_responses</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract deduplicated candidate DQ rules from AI response rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_canonical_dq_rule_type</code></li><li><code>_extract_assignment_payload</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_draft_dq_rules</code></li></ul></details>
  </div>
</article>
<article id="drift-_extract_categorical_distribution_categories" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_extract_categorical_distribution_categories" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return categorical baseline vocabularies from a profile payload.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__extract_categorical_distribution_categories/"><code>_extract_categorical_distribution_categories</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return categorical baseline vocabularies from a profile payload.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_normalize_profile</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>monitor_data_changes</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_extract_column_business_context_suggestions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_extract_column_business_context_suggestions" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Extract review-ready business-context suggestions from AI responses.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__extract_column_business_context_suggestions/"><code>_extract_column_business_context_suggestions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract review-ready business-context suggestions from AI responses.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_extract_assignment_payload</code></li></ul></details>

  </div>
</article>
<article id="metadata-_extract_columns_from_profile" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_extract_columns_from_profile" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__extract_columns_from_profile/"><code>_extract_columns_from_profile</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="drift-_extract_numeric_distribution_bin_edges" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_extract_numeric_distribution_bin_edges" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return numeric distribution bin edges from a profile payload.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__extract_numeric_distribution_bin_edges/"><code>_extract_numeric_distribution_bin_edges</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return numeric distribution bin edges from a profile payload.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_normalize_profile</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>monitor_data_changes</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_extract_pii_suggestions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_extract_pii_suggestions" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Extract sensitivity and personal-data suggestions from Spark/list response payloads.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__extract_pii_suggestions/"><code>_extract_pii_suggestions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract sensitivity and personal-data suggestions from Spark/list response payloads.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_coerce_rows</code></li><li><code>_extract_assignment_payload</code></li></ul></details>

  </div>
</article>
<article id="data_lineage-_fallback_copilot_lineage_prompt" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_fallback_copilot_lineage_prompt" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Build a fallback Copilot prompt for manual lineage enrichment.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__fallback_copilot_lineage_prompt/"><code>_fallback_copilot_lineage_prompt</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build a fallback Copilot prompt for manual lineage enrichment.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_enrich_lineage_steps_with_ai</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_flatten_chain" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_flatten_chain" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__flatten_chain/"><code>_flatten_chain</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_name</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_scan_notebook_lineage</code></li></ul></details>
  </div>
</article>
<article id="config-_format_error_path" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_format_error_path" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__format_error_path/"><code>_format_error_path</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_validate_dataset_contract</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_generate_agreement_id" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_generate_agreement_id" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__generate_agreement_id/"><code>_generate_agreement_id</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_create_or_update_data_agreement</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_generate_steward_id" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_generate_steward_id" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Generate a stable public-safe steward identifier from business fields.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__generate_steward_id/"><code>_generate_steward_id</code></a></h3>
  <p class="reference-catalogue-item-purpose">Generate a stable public-safe steward identifier from business fields.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_create_or_update_data_steward</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-_get_fabric_runtime_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_fabric_runtime_context" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return the Fabric notebook runtime context when available.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/fabric_input_output__get_fabric_runtime_context/"><code>_get_fabric_runtime_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the Fabric notebook runtime context when available.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_check_naming_convention</code></li></ul></details>
  </div>
</article>
<article id="config-_get_fabric_runtime_metadata" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_fabric_runtime_metadata" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Best-effort retrieval of Fabric runtime metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__get_fabric_runtime_metadata/"><code>_get_fabric_runtime_metadata</code></a></h3>
  <p class="reference-catalogue-item-purpose">Best-effort retrieval of Fabric runtime metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_bootstrap_fabric_env</code></li><li><code>_run_config_smoke_tests</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_get_governance_metadata_schemas" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_governance_metadata_schemas" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return typed Spark schemas prepared by ``00_env_config`` for governance.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__get_governance_metadata_schemas/"><code>_get_governance_metadata_schemas</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return typed Spark schemas prepared by ``00_env_config`` for governance.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_schema</code></li><li><code>_spark_types</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_setup_governance_metadata_tables</code></li></ul></details>
  </div>
</article>
<article id="metadata-_get_notebook_registry_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_notebook_registry_schema" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return the required notebook registry metadata schema.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__get_notebook_registry_schema/"><code>_get_notebook_registry_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the required notebook registry metadata schema.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_get_notebookutils" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_notebookutils" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return a notebookutils-like object when the Fabric runtime exposes one.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__get_notebookutils/"><code>_get_notebookutils</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return a notebookutils-like object when the Fabric runtime exposes one.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_prepare_evidence_file_references</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_get_profiled_columns" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_profiled_columns" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return non-technical column names from a Spark DataFrame.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__get_profiled_columns/"><code>_get_profiled_columns</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return non-technical column names from a Spark DataFrame.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>profile_dataframe</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-_get_spark" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_spark" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return an explicit Spark session or the active notebook global `spark`.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/fabric_input_output__get_spark/"><code>_get_spark</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return an explicit Spark session or the active notebook global `spark`.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 6</span></summary><ul><li><code>_seed_minimal_sample_source_table</code></li><li><code>read_lakehouse_csv</code></li><li><code>read_lakehouse_excel</code></li><li><code>read_lakehouse_parquet</code></li><li><code>read_lakehouse_table</code></li><li><code>read_warehouse_table</code></li></ul></details>
  </div>
</article>
<article id="config-_get_store" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_store" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Resolve a configured Fabric path for an environment and target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__get_store/"><code>_get_store</code></a></h3>
  <p class="reference-catalogue-item-purpose">Resolve a configured Fabric path for an environment and target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 10</span></summary><ul><li><code>_bootstrap_fabric_env</code></li><li><code>_run_config_smoke_tests</code></li><li><code>setup_notebook</code></li><li><code>read_lakehouse_csv</code></li><li><code>read_lakehouse_excel</code></li><li><code>read_lakehouse_parquet</code></li><li><code>read_lakehouse_table</code></li><li><code>read_warehouse_table</code></li><li><code>write_lakehouse_table</code></li><li><code>write_warehouse_table</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_get_widget_visible_fields" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_get_widget_visible_fields" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return configured editable columns without backend audit fields.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__get_widget_visible_fields/"><code>_get_widget_visible_fields</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return configured editable columns without backend audit fields.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_config_value</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_html_escape" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_html_escape" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return display-safe HTML text for notebook context snippets.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__html_escape/"><code>_html_escape</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return display-safe HTML text for notebook context snippets.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_render_searchable_selector</code></li><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_is_categorical_type" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_is_categorical_type" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return whether a Spark type string is suitable for categorical distributions.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__is_categorical_type/"><code>_is_categorical_type</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return whether a Spark type string is suitable for categorical distributions.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_distribution_summaries</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_is_min_max_supported_type" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_is_min_max_supported_type" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return whether min/max aggregation is safe for a Spark type string.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return whether min/max aggregation is safe for a Spark type string.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>profile_dataframe</code></li></ul></details>
  </div>
</article>
<article id="drift-_is_missing_table_error" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_is_missing_table_error" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__is_missing_table_error/"><code>_is_missing_table_error</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_load_latest_profile</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_is_numeric_type" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_is_numeric_type" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return whether a Spark type string is suitable for numeric distributions.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__is_numeric_type/"><code>_is_numeric_type</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return whether a Spark type string is suitable for numeric distributions.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_distribution_summaries</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_is_success" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_is_success" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__is_success/"><code>_is_success</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_value</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_catalogue_table_options</code></li><li><code>load_catalogue_profile_rows</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_is_table_not_found_error" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_is_table_not_found_error" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return whether a Spark/read exception clearly means the table is absent.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__is_table_not_found_error/"><code>_is_table_not_found_error</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return whether a Spark/read exception clearly means the table is absent.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_setup_governance_metadata_tables</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_json" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_json" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__json/"><code>_json</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_build_classification_records</code></li><li><code>_build_column_context_records</code></li><li><code>_build_dq_rule_records</code></li></ul></details>
  </div>
</article>
<article id="metadata-_key_part" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_key_part" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__key_part/"><code>_key_part</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_sha256_key</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_latest_agreement_versions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_latest_agreement_versions" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return the latest semantic version for each stable agreement ID.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__latest_agreement_versions/"><code>_latest_agreement_versions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the latest semantic version for each stable agreement ID.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_coerce_row_dicts</code></li><li><code>_parse_contract_version</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_list_data_agreements</code></li><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_latest_by_key" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_latest_by_key" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__latest_by_key/"><code>_latest_by_key</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_coerce_row_dicts</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_list_data_stewards</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_latest_dq_rule_versions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_latest_dq_rule_versions" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Resolve the latest DQ metadata row per rule key with deterministic ties.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__latest_dq_rule_versions/"><code>_latest_dq_rule_versions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Resolve the latest DQ metadata row per rule key with deterministic ties.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_spark_sql_helpers</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_load_active_dq_rules</code></li></ul></details>
  </div>
</article>
<article id="metadata-_latest_registration_events" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_latest_registration_events" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__latest_registration_events/"><code>_latest_registration_events</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_notebook_registration_key</code></li><li><code>_registry_rows_with_defaults</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_load_notebook_registry</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_list_all_data_agreement_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_list_all_data_agreement_rows" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="List all append-only agreement rows from the metadata lakehouse.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__list_all_data_agreement_rows/"><code>_list_all_data_agreement_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">List all append-only agreement rows from the metadata lakehouse.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_coerce_row_dicts</code></li><li><code>_config_value</code></li><li><code>read_lakehouse_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_list_data_agreements</code></li><li><code>_render_agreement_evidence_widget</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_list_data_agreements" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_list_data_agreements" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="List latest versioned agreements from the configured metadata lakehouse.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__list_data_agreements/"><code>_list_data_agreements</code></a></h3>
  <p class="reference-catalogue-item-purpose">List latest versioned agreements from the configured metadata lakehouse.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_latest_agreement_versions</code></li><li><code>_list_all_data_agreement_rows</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_render_maintenance_widget</code></li><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_list_data_stewards" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_list_data_stewards" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="List latest append-only steward rows from the metadata lakehouse.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__list_data_stewards/"><code>_list_data_stewards</code></a></h3>
  <p class="reference-catalogue-item-purpose">List latest append-only steward rows from the metadata lakehouse.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_active_steward</code></li><li><code>_config_value</code></li><li><code>_latest_by_key</code></li><li><code>read_lakehouse_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_render_maintenance_widget</code></li><li><code>_setup_data_agreement_tables</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_literal" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_literal" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__literal/"><code>_literal</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_resolve_write_target</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_load_active_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_load_active_dq_rules" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Load latest active approved DQ rule payloads from append-only metadata history.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__load_active_dq_rules/"><code>_load_active_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load latest active approved DQ rule payloads from append-only metadata history.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_latest_dq_rule_versions</code></li><li><code>_spark_sql_helpers</code></li><li><code>_validate_dq_rules</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_enforce_dq</code></li></ul></details>
  </div>
</article>
<article id="config-_load_and_validate_dataset_contract" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_load_and_validate_dataset_contract" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Load a dataset contract file and return schema validation findings.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__load_and_validate_dataset_contract/"><code>_load_and_validate_dataset_contract</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load a dataset contract file and return schema validation findings.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_load_dataset_contract</code></li><li><code>_validate_dataset_contract</code></li></ul></details>

  </div>
</article>
<article id="config-_load_dataset_contract" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_load_dataset_contract" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Load a dataset contract YAML file into a dictionary.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__load_dataset_contract/"><code>_load_dataset_contract</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load a dataset contract YAML file into a dictionary.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_load_and_validate_dataset_contract</code></li></ul></details>
  </div>
</article>
<article id="drift-_load_latest_profile" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_load_latest_profile" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Load an explicit profile-drift baseline from profile metadata rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__load_latest_profile/"><code>_load_latest_profile</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load an explicit profile-drift baseline from profile metadata rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_is_missing_table_error</code></li><li><code>_normalize_profile</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>monitor_data_changes</code></li></ul></details>
  </div>
</article>
<article id="metadata-_load_notebook_registry" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_load_notebook_registry" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__load_notebook_registry/"><code>_load_notebook_registry</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_latest_registration_events</code></li><li><code>_registry_rows_with_defaults</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_current_notebook_active_registrations</code></li></ul></details>
  </div>
</article>
<article id="config-_load_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_load_schema" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__load_schema/"><code>_load_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_default_schema_text</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_validate_dataset_contract</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_name" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_name" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__name/"><code>_name</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_flatten_chain</code></li><li><code>_scan_notebook_lineage</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_next_minor_version" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_next_minor_version" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return the next minor contract version, defaulting to ``1.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__next_minor_version/"><code>_next_minor_version</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the next minor contract version, defaulting to ``1.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_parse_contract_version</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_agreement_identity_text</code></li><li><code>_create_or_update_data_agreement</code></li></ul></details>
  </div>
</article>
<article id="metadata-_normalise_records_by_column" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_normalise_records_by_column" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__normalise_records_by_column/"><code>_normalise_records_by_column</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="drift-_normalize_datatype" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_normalize_datatype" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__normalize_datatype/"><code>_normalize_datatype</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_actual_schema</code></li><li><code>validate_schema</code></li></ul></details>
  </div>
</article>
<article id="config-_normalize_name" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_normalize_name" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__normalize_name/"><code>_normalize_name</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_validate_notebook_name</code></li></ul></details>
  </div>
</article>
<article id="drift-_normalize_profile" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_normalize_profile" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__normalize_profile/"><code>_normalize_profile</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_normalize_profile</code></li><li><code>_parse_distribution</code></li><li><code>_row_get</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 6</span></summary><ul><li><code>_check_profile_drift</code></li><li><code>_extract_categorical_distribution_categories</code></li><li><code>_extract_numeric_distribution_bin_edges</code></li><li><code>_load_latest_profile</code></li><li><code>_normalize_profile</code></li><li><code>monitor_data_changes</code></li></ul></details>
  </div>
</article>
<article id="metadata-_notebook_registration_key" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_notebook_registration_key" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__notebook_registration_key/"><code>_notebook_registration_key</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 4</span></summary><ul><li><code>_latest_registration_events</code></li><li><code>_register_current_notebook</code></li><li><code>_registry_rows_with_defaults</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="metadata-_notebook_registry_base_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_notebook_registry_base_schema" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return columns required by legacy notebook registry tables.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__notebook_registry_base_schema/"><code>_notebook_registry_base_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return columns required by legacy notebook registry tables.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="metadata-_now_utc_iso" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_now_utc_iso" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__now_utc_iso/"><code>_now_utc_iso</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_approved_review_context</code></li><li><code>_build_evidence_row</code></li></ul></details>
  </div>
</article>
<article id="data_profiling-_numeric_bin_edges" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_numeric_bin_edges" data-callable-module="data_profiling" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_profiling__numeric_bin_edges/"><code>_numeric_bin_edges</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_dedupe_edges</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_distribution_summaries</code></li></ul></details>
  </div>
</article>
<article id="drift-_numeric_psi" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_numeric_psi" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__numeric_psi/"><code>_numeric_psi</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_proportions</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_check_profile_drift</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_parse_ai_dict_response" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_parse_ai_dict_response" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Parse JSON/Python-dict AI response text into a dictionary.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__parse_ai_dict_response/"><code>_parse_ai_dict_response</code></a></h3>
  <p class="reference-catalogue-item-purpose">Parse JSON/Python-dict AI response text into a dictionary.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_extract_assignment_payload</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_parse_contract_version" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_parse_contract_version" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Parse a semantic contract version into a comparable tuple.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__parse_contract_version/"><code>_parse_contract_version</code></a></h3>
  <p class="reference-catalogue-item-purpose">Parse a semantic contract version into a comparable tuple.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_latest_agreement_versions</code></li><li><code>_next_minor_version</code></li></ul></details>
  </div>
</article>
<article id="drift-_parse_distribution" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_parse_distribution" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__parse_distribution/"><code>_parse_distribution</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_normalize_profile</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_parse_iso_date" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_parse_iso_date" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return an ISO date string or raise a clear intake validation error.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__parse_iso_date/"><code>_parse_iso_date</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return an ISO date string or raise a clear intake validation error.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_prepare_business_context_profile_input" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_prepare_business_context_profile_input" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Prepare profile rows for business-context AI drafting.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__prepare_business_context_profile_input/"><code>_prepare_business_context_profile_input</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare profile rows for business-context AI drafting.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-_prepare_dq_profile_input_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_prepare_dq_profile_input_rows" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Prepare DQ prompt profile rows from a profile DataFrame or raw DataFrame.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__prepare_dq_profile_input_rows/"><code>_prepare_dq_profile_input_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare DQ prompt profile rows from a profile DataFrame or raw DataFrame.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>profile_dataframe</code></li><li><code>_spark_sql_helpers</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_draft_dq_rules</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_prepare_evidence_file_references" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_prepare_evidence_file_references" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Parse and validate manually supplied evidence file paths before writes.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__prepare_evidence_file_references/"><code>_prepare_evidence_file_references</code></a></h3>
  <p class="reference-catalogue-item-purpose">Parse and validate manually supplied evidence file paths before writes.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_notebookutils</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_save_agreement_evidence_records</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_prepare_profile_rows_with_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_prepare_profile_rows_with_context" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Join approved column business context into profile rows for AI drafting.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__prepare_profile_rows_with_context/"><code>_prepare_profile_rows_with_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Join approved column business context into profile rows for AI drafting.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="drift-_proportions" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_proportions" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__proportions/"><code>_proportions</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_numeric_psi</code></li></ul></details>
  </div>
</article>
<article id="metadata-_register_current_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_register_current_notebook" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Append a runtime notebook registration row.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__register_current_notebook/"><code>_register_current_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Append a runtime notebook registration row.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>write_lakehouse_table</code></li><li><code>_column_context_rows_for_spark</code></li><li><code>_context_get</code></li><li><code>_notebook_registration_key</code></li><li><code>_runtime_context</code></li><li><code>_safe_str</code></li><li><code>_write_metadata_rows_legacy</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="metadata-_registry_rows_with_defaults" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_registry_rows_with_defaults" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__registry_rows_with_defaults/"><code>_registry_rows_with_defaults</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_coerce_row_dicts</code></li><li><code>_notebook_registration_key</code></li><li><code>_safe_str</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_latest_registration_events</code></li><li><code>_load_notebook_registry</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_render_agreement_evidence_widget" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_render_agreement_evidence_widget" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Render optional agreement evidence upload controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__render_agreement_evidence_widget/"><code>_render_agreement_evidence_widget</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render optional agreement evidence upload controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>_list_all_data_agreement_rows</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_save_agreement_evidence_records</code></li><li><code>_widget_common</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>widget_render_agreement_evidence</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_render_custom_fields" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_render_custom_fields" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Create widgets for configured organization-specific fields.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__render_custom_fields/"><code>_render_custom_fields</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create widgets for configured organization-specific fields.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>get</code></li><li><code>_require_ipywidgets</code></li><li><code>_to_bool</code></li><li><code>_widget_common</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_render_maintenance_widget" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_render_maintenance_widget" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__render_maintenance_widget/"><code>_render_maintenance_widget</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 15</span></summary><ul><li><code>_agreement_identity_text</code></li><li><code>_collect_custom_fields</code></li><li><code>_config_value</code></li><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_deserialize_custom_fields</code></li><li><code>_get_widget_visible_fields</code></li><li><code>_list_data_agreements</code></li><li><code>_list_data_stewards</code></li><li><code>_render_custom_fields</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_standard_widget</code></li><li><code>_to_bool</code></li><li><code>_to_iso_date</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>widget_render_data_agreement</code></li><li><code>widget_render_data_steward</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_render_searchable_selector" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_render_searchable_selector" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Render a table-backed selector with search and stable-value tracking.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__render_searchable_selector/"><code>_render_searchable_selector</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a table-backed selector with search and stable-value tracking.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_html_escape</code></li><li><code>_widget_common</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_render_agreement_evidence_widget</code></li><li><code>_render_maintenance_widget</code></li><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_require_ipywidgets" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_require_ipywidgets" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return ipywidgets or raise an actionable optional-dependency error.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__require_ipywidgets/"><code>_require_ipywidgets</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return ipywidgets or raise an actionable optional-dependency error.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 5</span></summary><ul><li><code>_render_agreement_evidence_widget</code></li><li><code>_render_custom_fields</code></li><li><code>_render_maintenance_widget</code></li><li><code>_standard_widget</code></li><li><code>widget_select_agreement</code></li></ul></details>
  </div>
</article>
<article id="metadata-_resolve_action_by" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_resolve_action_by" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__resolve_action_by/"><code>_resolve_action_by</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_context_get</code></li><li><code>_runtime_context</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_approved_review_context</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_resolve_write_target" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_resolve_write_target" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__resolve_write_target/"><code>_resolve_write_target</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_literal</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_scan_notebook_lineage</code></li></ul></details>
  </div>
</article>
<article id="drift-_row_get" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_row_get" data-callable-module="drift" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/drift__row_get/"><code>_row_get</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/drift/" title="Open drift module page" aria-label="Open drift module page">drift</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_normalize_profile</code></li></ul></details>
  </div>
</article>
<article id="config-_run_config_smoke_tests" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_run_config_smoke_tests" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Run 00_env_config readiness smoke checks for configuration bootstrap.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__run_config_smoke_tests/"><code>_run_config_smoke_tests</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run 00_env_config readiness smoke checks for configuration bootstrap.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>ConfigSmokeCheckResult</code></li><li><code>_check_spark_session</code></li><li><code>_get_fabric_runtime_metadata</code></li><li><code>_get_store</code></li><li><code>_validate_notebook_name</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_bootstrap_fabric_env</code></li><li><code>setup_notebook</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_run_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_run_dq_rules" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Run DQ rules and return rule-level PASS/FAIL evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__run_dq_rules/"><code>_run_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run DQ rules and return rule-level PASS/FAIL evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_spark_sql_helpers</code></li><li><code>_split_dq_rows</code></li><li><code>_validate_dq_rules</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_enforce_dq</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_run_fabric_ai_drafting" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_run_fabric_ai_drafting" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Run Fabric AI prompt drafting against prepared profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__run_fabric_ai_drafting/"><code>_run_fabric_ai_drafting</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run Fabric AI prompt drafting against prepared profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_draft_business_context</code></li><li><code>_draft_dq_rules</code></li><li><code>_draft_governance</code></li></ul></details>
  </div>
</article>
<article id="metadata-_runtime_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_runtime_context" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__runtime_context/"><code>_runtime_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_context_get</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 4</span></summary><ul><li><code>_build_runtime_audit_fields</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li><li><code>_resolve_action_by</code></li></ul></details>
  </div>
</article>
<article id="metadata-_safe_str" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_safe_str" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__safe_str/"><code>_safe_str</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 5</span></summary><ul><li><code>_build_runtime_audit_fields</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li><li><code>_registry_rows_with_defaults</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_save_agreement_evidence_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_save_agreement_evidence_records" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Append manually uploaded evidence file-reference metadata rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__save_agreement_evidence_records/"><code>_save_agreement_evidence_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Append manually uploaded evidence file-reference metadata rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_config_value</code></li><li><code>_prepare_evidence_file_references</code></li><li><code>_write_row</code></li><li><code>_build_runtime_audit_fields</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_agreement_evidence_widget</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_scan_notebook_cells" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_scan_notebook_cells" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Scan multiple notebook cells and append cell references to lineage steps.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__scan_notebook_cells/"><code>_scan_notebook_cells</code></a></h3>
  <p class="reference-catalogue-item-purpose">Scan multiple notebook cells and append cell references to lineage steps.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_scan_notebook_lineage</code></li></ul></details>

  </div>
</article>
<article id="data_lineage-_scan_notebook_lineage" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_scan_notebook_lineage" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Extract deterministic lineage steps from notebook code using AST parsing.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__scan_notebook_lineage/"><code>_scan_notebook_lineage</code></a></h3>
  <p class="reference-catalogue-item-purpose">Extract deterministic lineage steps from notebook code using AST parsing.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>_call_name</code></li><li><code>_flatten_chain</code></li><li><code>_name</code></li><li><code>_resolve_write_target</code></li><li><code>_step</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_scan_notebook_cells</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_schema" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__schema/"><code>_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_spark_types</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_get_governance_metadata_schemas</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_schema_field_names" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_schema_field_names" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__schema_field_names/"><code>_schema_field_names</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_setup_governance_metadata_tables</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-_seed_minimal_sample_source_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_seed_minimal_sample_source_table" data-callable-module="fabric_input_output" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Create and persist a minimal demo source table for end-to-end samples.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/fabric_input_output__seed_minimal_sample_source_table/"><code>_seed_minimal_sample_source_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create and persist a minimal demo source table for end-to-end samples.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_spark</code></li><li><code>write_lakehouse_table</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-_serialize_custom_fields" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_serialize_custom_fields" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Serialize organization-specific intake values to deterministic JSON.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__serialize_custom_fields/"><code>_serialize_custom_fields</code></a></h3>
  <p class="reference-catalogue-item-purpose">Serialize organization-specific intake values to deterministic JSON.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_business_agreement_snapshot</code></li><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_setup_data_agreement_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_setup_data_agreement_tables" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Prepare intake tables and report whether agreement intake has a steward.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__setup_data_agreement_tables/"><code>_setup_data_agreement_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare intake tables and report whether agreement intake has a steward.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_list_data_stewards</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>setup_metadata_tables</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_setup_governance_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_setup_governance_metadata_tables" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Create or validate governance metadata tables via the configured route.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__setup_governance_metadata_tables/"><code>_setup_governance_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate governance metadata tables via the configured route.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 6</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>write_lakehouse_table</code></li><li><code>_coerce_rows</code></li><li><code>_get_governance_metadata_schemas</code></li><li><code>_is_table_not_found_error</code></li><li><code>_schema_field_names</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>setup_metadata_tables</code></li></ul></details>
  </div>
</article>
<article id="metadata-_setup_notebook_registry_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_setup_notebook_registry_table" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Create or validate the notebook registry metadata table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__setup_notebook_registry_table/"><code>_setup_notebook_registry_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate the notebook registry metadata table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 8</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>write_lakehouse_table</code></li><li><code>_coerce_row_dicts</code></li><li><code>_column_context_rows_for_spark</code></li><li><code>_column_names</code></li><li><code>_get_notebook_registry_schema</code></li><li><code>_notebook_registration_key</code></li><li><code>_safe_str</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>setup_metadata_tables</code></li></ul></details>
  </div>
</article>
<article id="metadata-_sha256_key" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_sha256_key" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__sha256_key/"><code>_sha256_key</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_key_part</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_build_dq_rule_key</code></li><li><code>_build_metadata_column_key</code></li><li><code>_build_metadata_table_key</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_spark_sql_helpers" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_spark_sql_helpers" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return Spark SQL helper modules lazily for DQ runtime helpers.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__spark_sql_helpers/"><code>_spark_sql_helpers</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return Spark SQL helper modules lazily for DQ runtime helpers.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 5</span></summary><ul><li><code>_latest_dq_rule_versions</code></li><li><code>_load_active_dq_rules</code></li><li><code>_prepare_dq_profile_input_rows</code></li><li><code>_run_dq_rules</code></li><li><code>_split_dq_rows</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_spark_types" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_spark_types" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return Spark SQL type classes lazily so package import stays lightweight.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__spark_types/"><code>_spark_types</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return Spark SQL type classes lazily so package import stays lightweight.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_get_governance_metadata_schemas</code></li><li><code>_schema</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_split_dq_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_split_dq_rows" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Split source rows into valid rows, quarantine rows, and failure evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__split_dq_rows/"><code>_split_dq_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Split source rows into valid rows, quarantine rows, and failure evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_spark_sql_helpers</code></li><li><code>_validate_dq_rules</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_enforce_dq</code></li><li><code>_run_dq_rules</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_standard_widget" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_standard_widget" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__standard_widget/"><code>_standard_widget</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_require_ipywidgets</code></li><li><code>_to_bool</code></li><li><code>_widget_common</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="handover-_status_of" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_status_of" data-callable-module="handover" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/handover__status_of/"><code>_status_of</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/handover/" title="Open handover module page" aria-label="Open handover module page">handover</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_build_handover_record</code></li><li><code>render_handover_markdown</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_step" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_step" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__step/"><code>_step</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_scan_notebook_lineage</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_to_bool" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_to_bool" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Normalize common notebook and metadata boolean representations.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__to_bool/"><code>_to_bool</code></a></h3>
  <p class="reference-catalogue-item-purpose">Normalize common notebook and metadata boolean representations.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 5</span></summary><ul><li><code>_active_steward</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_render_custom_fields</code></li><li><code>_render_maintenance_widget</code></li><li><code>_standard_widget</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_to_iso_date" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_to_iso_date" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__to_iso_date/"><code>_to_iso_date</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_collect_custom_fields</code></li><li><code>_render_maintenance_widget</code></li></ul></details>
  </div>
</article>
<article id="config-_validate_dataset_contract" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_validate_dataset_contract" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Validate a loaded dataset contract against the JSON schema.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__validate_dataset_contract/"><code>_validate_dataset_contract</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate a loaded dataset contract against the JSON schema.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_format_error_path</code></li><li><code>_load_schema</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_assert_valid_dataset_contract</code></li><li><code>_load_and_validate_dataset_contract</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_validate_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_validate_dq_rules" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Validate canonical DQ rules before loading or enforcement.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__validate_dq_rules/"><code>_validate_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate canonical DQ rules before loading or enforcement.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_canonical_dq_rule_type</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 4</span></summary><ul><li><code>_enforce_dq</code></li><li><code>_load_active_dq_rules</code></li><li><code>_run_dq_rules</code></li><li><code>_split_dq_rows</code></li></ul></details>
  </div>
</article>
<article id="config-_validate_framework_config" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_validate_framework_config" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Validate and normalize framework configuration input.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__validate_framework_config/"><code>_validate_framework_config</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate and normalize framework configuration input.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>FrameworkConfig</code></li><li><code>keys</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_bootstrap_fabric_env</code></li><li><code>setup_notebook</code></li></ul></details>
  </div>
</article>
<article id="data_lineage-_validate_lineage_steps" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_validate_lineage_steps" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Validate lineage step structure and flag records requiring human review.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_lineage__validate_lineage_steps/"><code>_validate_lineage_steps</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate lineage step structure and flag records requiring human review.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_build_lineage_record_from_steps</code></li></ul></details>
  </div>
</article>
<article id="config-_validate_notebook_name" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_validate_notebook_name" data-callable-module="config" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/config__validate_notebook_name/"><code>_validate_notebook_name</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_normalize_name</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_run_config_smoke_tests</code></li></ul></details>
  </div>
</article>
<article id="governance_review-_value" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_value" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/governance_review__value/"><code>_value</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 6</span></summary><ul><li><code>_approved_column_identity</code></li><li><code>_approved_review_context</code></li><li><code>_catalogue_table_options</code></li><li><code>_display_review_guidance</code></li><li><code>_is_success</code></li><li><code>load_catalogue_profile_rows</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_widget_common" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_widget_common" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Return common style and layout keyword arguments for form controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__widget_common/"><code>_widget_common</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return common style and layout keyword arguments for form controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 4</span></summary><ul><li><code>_render_agreement_evidence_widget</code></li><li><code>_render_custom_fields</code></li><li><code>_render_searchable_selector</code></li><li><code>_standard_widget</code></li></ul></details>
  </div>
</article>
<article id="metadata-_write_column_business_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_write_column_business_context" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__write_column_business_context/"><code>_write_column_business_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_write_metadata_rows</code></li></ul></details>

  </div>
</article>
<article id="metadata-_write_column_governance_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_write_column_governance_context" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__write_column_governance_context/"><code>_write_column_governance_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_write_metadata_rows</code></li></ul></details>

  </div>
</article>
<article id="metadata-_write_metadata_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_write_metadata_rows" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Write metadata rows to a legacy lakehouse metadata path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__write_metadata_rows/"><code>_write_metadata_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write metadata rows to a legacy lakehouse metadata path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_column_context_rows_for_spark</code></li><li><code>_write_metadata_rows_legacy</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_write_column_business_context</code></li><li><code>_write_column_governance_context</code></li></ul></details>
  </div>
</article>
<article id="metadata-_write_metadata_rows_legacy" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_write_metadata_rows_legacy" data-callable-module="metadata" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Write metadata rows using the pre-route lakehouse path convention.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/metadata__write_metadata_rows_legacy/"><code>_write_metadata_rows_legacy</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write metadata rows using the pre-route lakehouse path convention.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/metadata/" title="Open metadata module page" aria-label="Open metadata module page">metadata</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 2</span></summary><ul><li><code>_register_current_notebook</code></li><li><code>_write_metadata_rows</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-_write_row" class="reference-catalogue-item" data-callable-row="true" data-callable-name="_write_row" data-callable-module="data_agreement" data-callable-starter-path="—" data-function-type="internal" data-callable-purpose="Internal helper used by the package.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="internal/data_agreement__write_row/"><code>_write_row</code></a></h3>
  <p class="reference-catalogue-item-purpose">Internal helper used by the package.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-internal">Internal</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>write_lakehouse_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_create_or_update_data_agreement</code></li><li><code>_create_or_update_data_steward</code></li><li><code>_save_agreement_evidence_records</code></li></ul></details>
  </div>
</article>
</div>

