# Function Reference

Use this page as a function lookup after you understand the notebook flow. The normal catalogue emphasizes Workflow functions and Composable functions as the public API; maintainer/developer views keep implementation call flow, utility support, and refactor signals available without presenting every helper as a user-facing concept.

- Use the [Glossary](glossary.md) for simple definitions of repeated FabricOps terms used on callable pages.
- Use the Function catalogue below to browse Workflow and Composable functions. Internal/private helpers are source-level implementation details shown only for maintainer source navigation, not public API.
- Use Implementation Modules only when debugging or maintaining current major source boundaries; they do not document every `.py` file.

## How to use this reference

- **Workflow functions** are guided end-to-end notebook entry points that users normally call from starter templates.
- **Composable functions** are public standalone building blocks for notebook authors customizing or decoupling from the guided workflow.
- **Utility functions** are reusable framework support for contributors and maintainers; they are not highlighted as normal user-facing API.
- **Internal/private functions** are implementation details, usually underscore-prefixed, and are shown only in maintainer/source-navigation views such as call flow.
- **Implementation modules** show source ownership, module-level dependencies, and utility/internal relationships for maintainers.
- **Function manifests** (`_data/manifest.json` and `_data/function-manifest.json`) provide machine-readable callable/module inventory for checks and automation.
- **Agent/automation metadata** (`_data/automation-manifest.json`) adds automation-oriented execution fields for planning, side-effect checks, and verification.
- **Implementation contracts** on callable pages summarize expectations maintainers must satisfy before using or changing a function.
- **Skill file** (`.agents/skills/fabricops/SKILL.md`) gives contributors repo-specific rules and points them to these generated references.

## Find a function

Use the finder below to look up Workflow and Composable functions from active v1 modules. Developer/maintainer filters can reveal Utility support functions when present, but internal/private helpers stay out of the normal catalogue. For private helper behavior, open a public function page and expand the maintainer/developer call flow. “Used in” means direct starter notebook code-cell invocation, not import-only, markdown-only, generated metadata, example-only usage, or internal/private helper usage.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search functions</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, taxonomy category, starter path, usage source, or description.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">csv</span> <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">quarantine</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing Workflow and Composable functions.</p>
  <fieldset class="callable-type-filters">
    <legend>Function taxonomy filters</legend>
    <label><input type="checkbox" data-function-type-filter="workflow" checked> Workflow</label>
    <label><input type="checkbox" data-function-type-filter="composable" checked> Composable</label>
    <label class="reference-maintainer-filter"><input type="checkbox" data-function-type-filter="utility"> Utility (maintainer)</label>
    <p class="callable-type-note"><strong>Workflow</strong>: guided end-to-end notebook entry points. <strong>Composable</strong>: public standalone building blocks for customization. <strong>Utility</strong>: developer/maintainer support, not normal notebook API. Example-only usage is tracked as source metadata instead of a function type.</p>
  </fieldset>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No functions match your search.</p>
</div>

## Function catalogue

## Functions

<div class="reference-catalogue-list">
<article id="pipeline-display_guardrail_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="display_guardrail_results" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="workflow" data-callable-purpose="Return summary, detailed, or debug guardrail display output for Fabric notebooks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return summary, detailed, or debug guardrail display output for Fabric notebooks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>_rows_for_display</code></li><li><code>build_guardrail_detail_rows</code></li><li><code>build_guardrail_summary_rows</code></li></ul></details>

  </div>
</article>
<article id="governance_review-get_latest_metadata_catalogue" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_latest_metadata_catalogue" data-callable-module="governance_review" data-callable-starter-path="99_explore" data-callable-usage-source="99_explore" data-function-type="workflow" data-callable-purpose="Fetch the latest metadata catalogue rows for a table without writing metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a></h3>
  <p class="reference-catalogue-item-purpose">Fetch the latest metadata catalogue rows for a table without writing metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 99_explore</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_configured_lakehouse_schema</code></li><li><code>read_lakehouse_table</code></li><li><code>_catalogue_lookup_value</code></li><li><code>_coerce_rows</code></li></ul></details>

  </div>
</article>
<article id="pipeline-prepare_pipeline_table_configs" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_pipeline_table_configs" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="workflow" data-callable-purpose="Prepare source or target table configs for 02_pipeline.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare source or target table configs for 02_pipeline.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 1</span></summary><ul><li><code>_add_audit_columns</code></li></ul></details>

  </div>
</article>
<article id="data_profiling-profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="99_explore" data-callable-usage-source="99_explore" data-function-type="workflow" data-callable-purpose="Profile a source or target DataFrame for schema, quality, and catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_profiling/" title="Open data_profiling module page" aria-label="Open data_profiling module page">data_profiling</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 99_explore</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>_audit_timestamp_expr</code></li><li><code>_get_audit_timezone</code></li><li><code>_build_distribution_summaries</code></li><li><code>_get_profiled_columns</code></li><li><code>_is_min_max_supported_type</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 3</span></summary><ul><li><code>_prepare_dq_profile_input_rows</code></li><li><code>enforce_profile_behavior</code></li><li><code>run_table_guardrails</code></li></ul></details>
  </div>
</article>
<article id="fabric_input_output-read_data" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_data" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-callable-usage-source="02_pipeline, 99_explore" data-function-type="workflow" data-callable-purpose="Read Lakehouse tables, Lakehouse files, or Warehouse tables through one notebook-facing IO function.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_data/"><code>read_data</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read Lakehouse tables, Lakehouse files, or Warehouse tables through one notebook-facing IO function.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 99_explore</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 6</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>read_lakehouse_csv</code></li><li><code>read_lakehouse_excel</code></li><li><code>read_lakehouse_parquet</code></li><li><code>read_lakehouse_table</code></li><li><code>read_warehouse_table</code></li></ul></details>

  </div>
</article>
<article id="pipeline-run_table_guardrails" class="reference-catalogue-item" data-callable-row="true" data-callable-name="run_table_guardrails" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline, example_dq_rule_smoke_test" data-function-type="workflow" data-callable-purpose="Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, example_dq_rule_smoke_test</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, example_dq_rule_smoke_test</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 18</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>profile_dataframe</code></li><li><code>_run_active_dq_guardrail</code></li><li><code>enforce_freshness</code></li><li><code>enforce_freshness_rule</code></li><li><code>enforce_profile_behavior</code></li><li><code>stop_if_failed</code></li><li><code>_build_metadata_table_key</code></li><li><code>_write_guardrail_result_row</code></li><li><code>_active_pipeline_context</code></li><li><code>_build_guardrail_blocking_message_from_bundle</code></li><li><code>_build_guardrail_evidence_definitions</code></li><li><code>_guardrail_can_continue</code></li><li><code>_table_key</code></li><li><code>_table_name</code></li><li><code>build_guardrail_detail_rows</code></li><li><code>build_guardrail_summary_rows</code></li><li><code>write_catalogue_evidence</code></li></ul></details>

  </div>
</article>
<article id="config-setup_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_metadata_tables" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="workflow" data-callable-purpose="Create or validate all FabricOps metadata tables through one setup action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate all FabricOps metadata tables through one setup action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 10</span></summary><ul><li><code>_get_metadata_table_schema_registry</code></li><li><code>_metadata_schema_field_names</code></li><li><code>_metadata_tables_from_setup_results</code></li><li><code>_resolve_metadata_schema</code></li><li><code>_setup_metadata_table_registry</code></li><li><code>_validate_framework_config</code></li><li><code>_validate_metadata_table_registration</code></li><li><code>_list_data_stewards</code></li><li><code>get</code></li><li><code>_get_governance_metadata_schemas</code></li></ul></details>

  </div>
</article>
<article id="config-setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="workflow" data-callable-purpose="Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/config/" title="Open config module page" aria-label="Open config module page">config</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 00_env_config</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>NotebookSetupContext</code></li><li><code>_get_store</code></li><li><code>_run_config_smoke_tests</code></li><li><code>_validate_framework_config</code></li></ul></details>

  </div>
</article>
<article id="pipeline-start_pipeline_run" class="reference-catalogue-item" data-callable-row="true" data-callable-name="start_pipeline_run" data-callable-module="pipeline" data-callable-starter-path="02_pipeline, 99_explore" data-callable-usage-source="02_pipeline, 99_explore" data-function-type="workflow" data-callable-purpose="Start a guided notebook run and store runtime defaults.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></h3>
  <p class="reference-catalogue-item-purpose">Start a guided notebook run and store runtime defaults.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 99_explore</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 6</span></summary><ul><li><code>get_selected_agreement</code></li><li><code>widget_select_agreement</code></li><li><code>_PipelineRunContext</code></li><li><code>_notebook_global</code></li><li><code>_now_iso</code></li><li><code>_runtime_metadata_value</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_author_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_dq_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="workflow" data-callable-purpose="Render interactive manual DQ guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive manual DQ guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_dq_records_from_selection</code></li><li><code>_latest_rule</code></li><li><code>_rule_params</code></li><li><code>_write_rule_records</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_author_schema_freshness_profile_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_schema_freshness_profile_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="workflow" data-callable-purpose="Render interactive schema, freshness, and profile-behavior guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive schema, freshness, and profile-behavior guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_latest_rule</code></li><li><code>_rule_params</code></li><li><code>_schema_freshness_profile_records_from_selection</code></li><li><code>_write_rule_records</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_enrich_table_metadata" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_enrich_table_metadata" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="workflow" data-callable-purpose="Render a consolidated column enrichment widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a consolidated column enrichment widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 8</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_collect_enrichment_extra_fields</code></li><li><code>_enrichment_options</code></li><li><code>_render_enrichment_extra_fields</code></li><li><code>_selected_catalogue_rows_for_enrichment</code></li><li><code>_value</code></li><li><code>_write_table_metadata_enrichment_records</code></li><li><code>build_enrichment_rule_records</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="workflow" data-callable-purpose="Render the standalone agreement-evidence widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone agreement-evidence widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 01_agreement</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_render_agreement_evidence_widget</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="workflow" data-callable-purpose="Render the standalone data-agreement intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-agreement intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 01_agreement</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="workflow" data-callable-purpose="Render the standalone data-steward intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-steward intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 01_agreement</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 2</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_render_maintenance_widget</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_review_guardrail_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_guardrail_governance" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="workflow" data-callable-purpose="Render interactive controls for reviewing proposed and bypassed guardrail rules.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive controls for reviewing proposed and bypassed guardrail rules.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 4</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>apply_governance_enrichment_action</code></li><li><code>apply_governance_rule_action</code></li><li><code>load_rule_review_history</code></li></ul></details>

  </div>
</article>
<article id="governance_review-widget_select_guardrail_target" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_guardrail_target" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="workflow" data-callable-purpose="Render an interactive target selector for guardrail authoring and governance review.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an interactive target selector for guardrail authoring and governance review.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/governance_review/" title="Open governance_review module page" aria-label="Open governance_review module page">governance_review</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, 03_governance</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_filter_table_rows</code></li><li><code>_read_metadata_table_or_empty</code></li><li><code>resolve_table_governance_policy</code></li><li><code>_build_metadata_table_key</code></li></ul></details>

  </div>
</article>
<article id="fabric_input_output-write_data" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_data" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test" data-function-type="workflow" data-callable-purpose="Write Lakehouse or Warehouse targets through one notebook-facing IO function.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_data/"><code>write_data</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write Lakehouse or Warehouse targets through one notebook-facing IO function.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/fabric_input_output/" title="Open fabric_input_output module page" aria-label="Open fabric_input_output module page">fabric_input_output</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 3</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>write_lakehouse_table</code></li><li><code>write_warehouse_table</code></li></ul></details>

  </div>
</article>
<article id="pipeline-write_pipeline_lineage" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_lineage" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="workflow" data-callable-purpose="Write many-to-many source-to-target lineage evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write many-to-many source-to-target lineage evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_configured_lakehouse_schema</code></li><li><code>write_lakehouse_table</code></li><li><code>_build_metadata_table_key</code></li><li><code>_definition_name</code></li><li><code>_now_iso</code></li><li><code>_runtime_audit_fields</code></li></ul></details>

  </div>
</article>
<article id="pipeline-write_pipeline_run_summary" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_run_summary" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="workflow" data-callable-purpose="Write one pipeline runtime summary row to metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write one pipeline runtime summary row to metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/pipeline/" title="Open pipeline module page" aria-label="Open pipeline module page">pipeline</a><span class="reference-chip reference-chip-type reference-chip-workflow">Workflow</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 7</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_configured_lakehouse_schema</code></li><li><code>write_lakehouse_table</code></li><li><code>_active_pipeline_context</code></li><li><code>_definition_name</code></li><li><code>_now_iso</code></li><li><code>_summary_status</code></li></ul></details>

  </div>
</article>
<article id="data_agreement-get_selected_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_selected_agreement" data-callable-module="data_agreement" data-function-type="composable" data-callable-purpose="Return the agreement selected by widget_select_agreement.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return the agreement selected by widget_select_agreement.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-composable">Composable</span><span class="reference-chip">—</span></p>

  <div class="reference-catalogue-item-counts">

    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>start_pipeline_run</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-widget_select_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_agreement" data-callable-module="data_agreement" data-function-type="composable" data-callable-purpose="Render an agreement selector and optionally register the active notebook.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_agreement/"><code>widget_select_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an agreement selector and optionally register the active notebook.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><a class="reference-module-link" href="../api/modules/data_agreement/" title="Open data_agreement module page" aria-label="Open data_agreement module page">data_agreement</a><span class="reference-chip reference-chip-type reference-chip-composable">Composable</span><span class="reference-chip">—</span></p>

  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Outbound 8</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>_html_escape</code></li><li><code>_latest_agreement_versions</code></li><li><code>_list_data_agreements</code></li><li><code>_render_searchable_selector</code></li><li><code>_require_ipywidgets</code></li><li><code>_current_notebook_active_registrations</code></li><li><code>_register_current_notebook</code></li></ul></details>
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Inbound 1</span></summary><ul><li><code>start_pipeline_run</code></li></ul></details>
  </div>
</article>
</div>

## Composable functions

These exported public functions are standalone building blocks for customization or decoupled notebook authoring. They are not directly called by core starter template code cells and are not included in the Workflow count.

- [`get_selected_agreement`](../api/reference/get_selected_agreement/)
- [`widget_select_agreement`](../api/reference/widget_select_agreement/)

