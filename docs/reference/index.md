# Function Reference

Use this page as a function lookup after you understand the notebook flow. The default catalogue shows public v1 callables that notebook authors can import from the package root; the Template Function Map shows where those callables are used in starter templates; Implementation Modules show the active source modules that maintainers debug and extend.

- Use [Template Function Map](template-function-map.md) to see what notebook users call from the starter notebook templates.
- Use the Function catalogue below to browse public v1 callables. Internal helper details are embedded inside callable pages instead of normal catalogue entries.
- Use Implementation Modules only when debugging or maintaining current major source boundaries; they do not document every `.py` file.

## How to use this reference

- **Callable helpers** are public v1 functions intended for notebook authors and human operators.
- **Internal helpers** are maintainer implementation details embedded inside the public callable pages that use them.
- **Implementation modules** show source ownership, module-level dependencies, and helper relationships for maintainers.
- **Function manifests** (`manifest.json` and `function-manifest.json`) provide machine-readable callable/module inventory for checks and automation.
- **Agent manifest** (`agent-manifest.json`) adds AI-oriented execution fields for planning, side-effect checks, and verification.
- **AI implementation contracts** on callable pages summarize expectations agents must satisfy before using or changing a function.
- **Skill file** (`.agents/skills/fabricops/SKILL.md`) gives agents repo-specific rules and points them to these generated references.

## Find a function

Use the finder below to look up public callables from active v1 modules. For internal helper behavior, open the public callable page and expand Implementation details.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search functions</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, function type, starter path, or description.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">csv</span> <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">quarantine</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing callable functions.</p>
  <fieldset class="callable-type-filters">
    <legend>Function type filters</legend>
    <label><input type="checkbox" data-function-type-filter="callable" checked> Callable</label>
    <p class="callable-type-note"><strong>Callable</strong>: Public functions intended for notebook authors.</p>
  </fieldset>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No functions match your search.</p>
</div>

## Function catalogue

## Functions

<div class="reference-catalogue-list">
<article id="data_lineage-build_lineage_records" class="reference-catalogue-item" data-callable-row="true" data-callable-name="build_lineage_records" data-callable-module="data_lineage" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Build source-to-target lineage evidence records for a pipeline run.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/build_lineage_records/"><code>build_lineage_records</code></a></h3>
  <p class="reference-catalogue-item-purpose">Build source-to-target lineage evidence records for a pipeline run.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_lineage/" title="Open data_lineage module page" aria-label="Open data_lineage module page">data_lineage</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_current_audit_timestamp</code></li></ul></details>

  </div>
</article>
<article id="governance_review-enforce_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_dq_rules" data-callable-module="governance_review" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Enforce approved active DQ rules as a target-write guardrail without filtering rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce approved active DQ rules as a target-write guardrail without filtering rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_dq_failed_row_count</code></li><li><code>_dq_summary</code></li><li><code>_dq_tagged_dataframe</code></li><li><code>_load_active_dq_rules</code></li><li><code>_run_dq_guardrail_checks</code></li><li><code>_summarize_dq_guardrail</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="guardrails-enforce_freshness" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_freshness" data-callable-module="guardrails" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Enforce whether the latest data arrived within the configured freshness lag.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_freshness/"><code>enforce_freshness</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce whether the latest data arrived within the configured freshness lag.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/guardrails/" title="Open guardrails module page" aria-label="Open guardrails module page">guardrails</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_coerce_date</code></li><li><code>_iso_date_value</code></li><li><code>_max_column_value</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="guardrails-enforce_profile_behavior" class="reference-catalogue-item" data-callable-row="true" data-callable-name="enforce_profile_behavior" data-callable-module="guardrails" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/guardrails/" title="Open guardrails module page" aria-label="Open guardrails module page">guardrails</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 11</span></summary><ul><li><code>profile_dataframe</code></li><li><code>read_lakehouse_table</code></li><li><code>_catalogue_value</code></li><li><code>_guardrail_exclude_columns</code></li><li><code>_is_greater_than</code></li><li><code>_is_less_than</code></li><li><code>_is_missing_table_error</code></li><li><code>_latest_catalogue_behavior_profile_row</code></li><li><code>_profile_row_count</code></li><li><code>_profile_watermark_bounds</code></li><li><code>_string_value</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-get_selected_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_agreement" data-callable-module="data_agreement" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Return the agreement selected by widget_select_agreement.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the agreement selected by widget_select_agreement.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-get_selected_catalogue_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_catalogue_table" data-callable-module="governance_review" data-callable-starter-path="03_governance" data-function-type="callable" data-callable-purpose="Return the table selected by widget_select_catalogue_table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the table selected by widget_select_catalogue_table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_governance</span></p>
  <div class="reference-catalogue-item-counts">


  </div>
</article>
<article id="governance_review-load_catalogue_profile_rows" class="reference-catalogue-item" data-callable-row="true" data-callable-name="load_catalogue_profile_rows" data-callable-module="governance_review" data-callable-starter-path="03_governance" data-function-type="callable" data-callable-purpose="Load column profile rows for the selected catalogue table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></h3>
  <p class="reference-catalogue-item-purpose">Load column profile rows for the selected catalogue table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_governance</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_coerce_rows</code></li><li><code>_is_success</code></li><li><code>_value</code></li><li><code>_build_metadata_table_key</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>_review_governance_evidence</code></li></ul></details>
  </div>
</article>
<article id="pipeline-prepare_pipeline_table_configs" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_pipeline_table_configs" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Prepare source or target table configs for 02_pipeline.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare source or target table configs for 02_pipeline.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_add_audit_columns</code></li></ul></details>

  </div>
</article>
<article id="data_profiling-profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="99_explore" data-function-type="callable" data-callable-purpose="Profile a source or target DataFrame for schema, quality, and catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">99_explore</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>_audit_timestamp_expr</code></li><li><code>_validate_audit_timezone</code></li><li><code>_build_distribution_summaries</code></li><li><code>_get_profiled_columns</code></li><li><code>_is_min_max_supported_type</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_prepare_dq_profile_input_rows</code></li><li><code>enforce_profile_behavior</code></li><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read a CSV file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li><li><code>_lakehouse_file_path</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read an Excel file from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read an Excel file from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li><li><code>_lakehouse_file_path</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read a Parquet path from a configured Fabric lakehouse Files path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Parquet path from a configured Fabric lakehouse Files path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_get_store</code></li><li><code>_convert_single_parquet_ns_to_us</code></li><li><code>_get_spark</code></li><li><code>_lakehouse_file_path</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read a table from a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 6</span></summary><ul><li><code>_get_store</code></li><li><code>_current_database_matches</code></li><li><code>_get_spark</code></li><li><code>_normalize_table_name</code></li><li><code>_registered_table_identifier</code></li><li><code>_uses_registered_metadata_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 11</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_list_all_data_agreement_rows</code></li><li><code>_list_data_stewards</code></li><li><code>_read_metadata_rows</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>enforce_dq_rules</code></li><li><code>load_catalogue_profile_rows</code></li><li><code>widget_select_catalogue_table</code></li><li><code>enforce_profile_behavior</code></li><li><code>_load_notebook_registry</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Read a table from a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_get_store</code></li><li><code>_get_spark</code></li></ul></details>

  </div>
</article>
<article id="governance_review-record_table_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="record_table_governance" data-callable-module="governance_review" data-callable-starter-path="03_governance" data-function-type="callable" data-callable-purpose="Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/record_table_governance/"><code>record_table_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_governance</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>write_lakehouse_table</code></li><li><code>_build_classification_records</code></li><li><code>_build_column_context_records</code></li><li><code>_build_dq_rule_records</code></li><li><code>_review_governance_evidence</code></li></ul></details>

  </div>
</article>
<article id="pipeline-run_table_guardrails" class="reference-catalogue-item" data-callable-row="true" data-callable-name="run_table_guardrails" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 12</span></summary><ul><li><code>_get_audit_timezone</code></li><li><code>profile_dataframe</code></li><li><code>enforce_dq_rules</code></li><li><code>enforce_freshness</code></li><li><code>enforce_profile_behavior</code></li><li><code>stop_if_failed</code></li><li><code>validate_schema</code></li><li><code>_build_guardrail_evidence_definitions</code></li><li><code>_guardrail_can_continue</code></li><li><code>_table_key</code></li><li><code>_table_name</code></li><li><code>write_catalogue_evidence</code></li></ul></details>

  </div>
</article>
<article id="config-setup_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_metadata_tables" data-callable-module="config" data-callable-starter-path="00_env_config" data-function-type="callable" data-callable-purpose="Create or validate all FabricOps metadata tables through one setup action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate all FabricOps metadata tables through one setup action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>_get_active_metadata_tables</code></li><li><code>_metadata_tables_from_setup_results</code></li><li><code>_validate_metadata_table_registration</code></li><li><code>_setup_data_agreement_tables</code></li><li><code>get</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>_setup_notebook_registry_table</code></li></ul></details>

  </div>
</article>
<article id="config-setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config" data-function-type="callable" data-callable-purpose="Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">00_env_config</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>NotebookSetupContext</code></li><li><code>_get_store</code></li><li><code>_run_config_smoke_tests</code></li><li><code>_validate_framework_config</code></li></ul></details>

  </div>
</article>
<article id="guardrails-stop_if_failed" class="reference-catalogue-item" data-callable-row="true" data-callable-name="stop_if_failed" data-callable-module="guardrails" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/stop_if_failed/"><code>stop_if_failed</code></a></h3>
  <p class="reference-catalogue-item-purpose">Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/guardrails/" title="Open guardrails module page" aria-label="Open guardrails module page">guardrails</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>SchemaDriftError</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="guardrails-validate_schema" class="reference-catalogue-item" data-callable-row="true" data-callable-name="validate_schema" data-callable-module="guardrails" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/validate_schema/"><code>validate_schema</code></a></h3>
  <p class="reference-catalogue-item-purpose">Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/guardrails/" title="Open guardrails module page" aria-label="Open guardrails module page">guardrails</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>_actual_schema</code></li><li><code>_normalize_datatype</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-function-type="callable" data-callable-purpose="Render the standalone agreement-evidence widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone agreement-evidence widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_agreement</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_agreement_evidence_widget</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-function-type="callable" data-callable-purpose="Render the standalone data-agreement intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-agreement intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_agreement</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-function-type="callable" data-callable-purpose="Render the standalone data-steward intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-steward intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">01_agreement</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_review_column_classification" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_column_classification" data-callable-module="governance_review" data-callable-starter-path="03_governance" data-function-type="callable" data-callable-purpose="Render standalone sensitivity and PII classification review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone sensitivity and PII classification review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_governance</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_review_column_context" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_column_context" data-callable-module="governance_review" data-callable-starter-path="03_governance" data-function-type="callable" data-callable-purpose="Render standalone business-context review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_column_context/"><code>widget_review_column_context</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone business-context review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_governance</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_display_review_guidance</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_review_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_dq_rules" data-callable-module="governance_review" data-callable-starter-path="03_governance" data-function-type="callable" data-callable-purpose="Render standalone DQ-rule review guidance for selected profile rows.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render standalone DQ-rule review guidance for selected profile rows.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_governance</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 6</span></summary><ul><li><code>_canonical_dq_rule_type</code></li><li><code>_dq_parameter_fields_for_rule_type</code></li><li><code>_dq_rule_display_rows</code></li><li><code>_draft_dq_rules</code></li><li><code>_validate_dq_rules</code></li><li><code>_value</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_select_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_agreement" data-callable-module="data_agreement" data-callable-starter-path="02_pipeline, 99_explore" data-function-type="callable" data-callable-purpose="Render an agreement selector and optionally register the active notebook.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_agreement/"><code>widget_select_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an agreement selector and optionally register the active notebook.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>_html_escape</code></li><li><code>_latest_agreement_versions</code></li><li><code>_list_data_agreements</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_select_catalogue_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_catalogue_table" data-callable-module="governance_review" data-callable-starter-path="03_governance" data-function-type="callable" data-callable-purpose="Render a searchable selector for latest successful catalogue profiles.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a searchable selector for latest successful catalogue profiles.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">03_governance</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>read_lakehouse_table</code></li><li><code>_catalogue_table_options</code></li><li><code>_coerce_rows</code></li></ul></details>

  </div>
</article>
<article id="pipeline-write_catalogue_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_catalogue_evidence" data-callable-module="pipeline" data-callable-starter-path="—" data-function-type="callable" data-callable-purpose="Enrich profile rows with guardrail context and write catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Enrich profile rows with guardrail context and write catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">—</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>write_lakehouse_table</code></li><li><code>_build_metadata_table_key</code></li><li><code>_canonical_catalogue_profile_df</code></li><li><code>_definition_name</code></li><li><code>_dq_summary_fields</code></li><li><code>_now_iso</code></li><li><code>_runtime_audit_fields</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Write a DataFrame to a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>_get_store</code></li><li><code>_normalize_table_name</code></li><li><code>_registered_table_identifier</code></li><li><code>_uses_registered_metadata_table</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 10</span></summary><ul><li><code>_ensure_metadata_tables</code></li><li><code>_write_row</code></li><li><code>_review_governance_evidence</code></li><li><code>_setup_governance_metadata_tables</code></li><li><code>record_table_governance</code></li><li><code>_register_current_notebook</code></li><li><code>_setup_notebook_registry_table</code></li><li><code>write_catalogue_evidence</code></li><li><code>write_pipeline_lineage</code></li><li><code>write_pipeline_run_summary</code></li></ul></details>
  </div>
</article>
<article id="pipeline-write_pipeline_lineage" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_lineage" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Write many-to-many source-to-target lineage evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write many-to-many source-to-target lineage evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>write_lakehouse_table</code></li><li><code>_build_metadata_table_key</code></li><li><code>_definition_name</code></li><li><code>_now_iso</code></li><li><code>_runtime_audit_fields</code></li></ul></details>

  </div>
</article>
<article id="pipeline-write_pipeline_run_summary" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_run_summary" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Write one pipeline runtime summary row to metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write one pipeline runtime summary row to metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>write_lakehouse_table</code></li><li><code>_definition_name</code></li><li><code>_now_iso</code></li><li><code>_summary_status</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline" data-function-type="callable" data-callable-purpose="Write a DataFrame to a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-callable">Callable</span><span class="reference-chip">02_pipeline</span></p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_get_store</code></li></ul></details>

  </div>
</article>
</div>

