# Function Reference

Use this page to look up Starter Kit functions used by the template notebooks.

<div class="reference-kpi-grid" aria-label="Function reference summary">
  <section class="reference-kpi-card surface-card">
    <strong class="reference-kpi-value">21</strong>
    <span class="reference-kpi-title">Modules</span>
    <p class="reference-kpi-note">Code areas represented.</p>
  </section>
  <section class="reference-kpi-card surface-card">
    <strong class="reference-kpi-value">319</strong>
    <span class="reference-kpi-title">Total callables</span>
    <p class="reference-kpi-note">Complete discovered callable inventory.</p>
  </section>
  <section class="reference-kpi-card surface-card">
    <strong class="reference-kpi-value">26</strong>
    <span class="reference-kpi-title">Public API</span>
    <p class="reference-kpi-note">Notebook-facing entrypoints.</p>
  </section>
  <section class="reference-kpi-card surface-card">
    <strong class="reference-kpi-value">63</strong>
    <span class="reference-kpi-title">Supporting functions</span>
    <p class="reference-kpi-note">Internal functions behind the public API.</p>
  </section>
  <section class="reference-kpi-card surface-card">
    <strong class="reference-kpi-value">230</strong>
    <span class="reference-kpi-title">Private helpers to review</span>
    <p class="reference-kpi-note">Excluded from default architecture counts.</p>
  </section>
</div>

<p><small>Callable metrics are generated from the callable inventory data.</small></p>

## Find a function

Use the finder below to look up the 26 public Starter Kit functions. Internal helper records stay out of the standalone public catalogue. “Used in” means direct starter notebook code-cell invocation, not import-only, markdown-only, generated metadata, example usage, or internal helper usage.

<div class="callable-finder" data-callable-finder>
  <label class="callable-finder-label" for="callable-finder-input">Search functions</label>
  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search public functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">
  <p id="callable-finder-help" class="callable-finder-help">Search by function name, starter path, usage source, or description.</p>
  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">lineage</span> <span class="callable-finder-chip">guardrail</span></p>
  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing 26 public Starter Kit functions.</p>
  <p class="callable-finder-empty" data-callable-finder-empty hidden>No functions match your search.</p>
</div>

??? info "Maintainer tools"
    Use these links and notes when maintaining the reference system.

    - [Glossary](glossary.md): simple definitions of repeated FabricOps terms.
    - [Public callable flow map](callable-flow.md): global public callable dependency view and nested internal helper summary.
    - [Architecture](../assets/callable-functions-dashboard.html): review public API shape, chain depth, fan-out, modules touched, cross-layer warnings, and flattening recommendations.
    - [Inventory](../assets/callable-functions-inventory.html): search/filter all callables, select rows, and export AI refactor packets.
    - Function manifests: `_data/manifest.json` and `_data/function-manifest.json`.
    - Agent metadata: `_data/automation-manifest.json`.
    - Implementation contracts: expectations maintainers must satisfy before using or changing a function.
    - Skill file: `.agents/skills/fabricops/SKILL.md`.

## Function catalogue

## Functions

<div class="reference-catalogue-list">
<article id="pipeline-display_guardrail_results" class="reference-catalogue-item" data-callable-row="true" data-callable-name="display_guardrail_results" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Return summary, detailed, or debug guardrail display output for Fabric notebooks.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a></h3>
  <p class="reference-catalogue-item-purpose">Return summary, detailed, or debug guardrail display output for Fabric notebooks.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 2</span></summary><ul><li><code>build_guardrail_detail_rows</code></li><li><code>build_guardrail_summary_rows</code></li></ul></details>
  </div>
</article>
<article id="governance_review-get_latest_metadata_catalogue" class="reference-catalogue-item" data-callable-row="true" data-callable-name="get_latest_metadata_catalogue" data-callable-module="governance_review" data-callable-starter-path="99_explore" data-callable-usage-source="99_explore" data-function-type="public-starter-kit" data-callable-purpose="Fetch the latest metadata catalogue rows for a table without writing metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a></h3>
  <p class="reference-catalogue-item-purpose">Fetch the latest metadata catalogue rows for a table without writing metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 4</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="pipeline-prepare_pipeline_table_configs" class="reference-catalogue-item" data-callable-row="true" data-callable-name="prepare_pipeline_table_configs" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Prepare source or target table configs for 02_pipeline.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare source or target table configs for 02_pipeline.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="data_profiling-profile_dataframe" class="reference-catalogue-item" data-callable-row="true" data-callable-name="profile_dataframe" data-callable-module="data_profiling" data-callable-starter-path="99_explore" data-callable-usage-source="99_explore" data-function-type="public-starter-kit" data-callable-purpose="Profile a source or target DataFrame for schema, quality, and catalogue evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></h3>
  <p class="reference-catalogue-item-purpose">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 2</span></summary><ul><li><code>profile_dataframe_core</code></li><li><code>profile_dataframe_core</code></li></ul></details>
  </div>
</article>
<article id="io.read_lakehouse_csv-read_lakehouse_csv" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_csv" data-callable-module="fabric_input_output" data-function-type="public-starter-kit" data-callable-purpose="Read a CSV file from a Fabric resolved path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a CSV file from a Fabric resolved path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="io.read_lakehouse_excel-read_lakehouse_excel" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_excel" data-callable-module="fabric_input_output" data-function-type="public-starter-kit" data-callable-purpose="Read an Excel workbook from a Fabric resolved path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read an Excel workbook from a Fabric resolved path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="io.read_lakehouse_parquet-read_lakehouse_parquet" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_parquet" data-callable-module="fabric_input_output" data-function-type="public-starter-kit" data-callable-purpose="Read a Parquet path from a Fabric resolved path.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Parquet path from a Fabric resolved path.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="io.read_lakehouse_table-read_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline, 99_explore" data-callable-usage-source="02_pipeline, 99_explore" data-function-type="public-starter-kit" data-callable-purpose="Read a Delta table from a configured Fabric lakehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a Delta table from a configured Fabric lakehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="io.read_warehouse_query-read_warehouse_query" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_query" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_query/"><code>read_warehouse_query</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="io.read_warehouse_table-read_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="read_warehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Read a table from a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Read a table from a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="pipeline-run_table_guardrails" class="reference-catalogue-item" data-callable-row="true" data-callable-name="run_table_guardrails" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline, example_dq_rule_smoke_test" data-function-type="public-starter-kit" data-callable-purpose="Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></h3>
  <p class="reference-catalogue-item-purpose">Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, example_dq_rule_smoke_test</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, example_dq_rule_smoke_test</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 14</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>profile_dataframe_core</code></li><li><code>enforce_freshness</code></li><li><code>enforce_freshness_rule</code></li><li><code>enforce_profile_behavior</code></li><li><code>stop_if_failed</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>write_lakehouse_table_core</code></li><li><code>build_guardrail_detail_rows</code></li><li><code>build_guardrail_summary_rows</code></li><li><code>write_catalogue_evidence</code></li><li><code>profile_dataframe_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="config-setup_metadata_tables" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_metadata_tables" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-starter-kit" data-callable-purpose="Create or validate all FabricOps metadata tables through one setup action.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></h3>
  <p class="reference-catalogue-item-purpose">Create or validate all FabricOps metadata tables through one setup action.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 4</span></summary><ul><li><code>read_lakehouse_table_core</code></li><li><code>write_lakehouse_table_core</code></li><li><code>resolve_fabric_context</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="config-setup_notebook" class="reference-catalogue-item" data-callable-row="true" data-callable-name="setup_notebook" data-callable-module="config" data-callable-starter-path="00_env_config" data-callable-usage-source="00_env_config" data-function-type="public-starter-kit" data-callable-purpose="Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a></h3>
  <p class="reference-catalogue-item-purpose">Prepare a FabricOps notebook by validating configuration, resolving environment targets, and returning reusable runtime context.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">00_env_config</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 00_env_config</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="pipeline-start_pipeline_run" class="reference-catalogue-item" data-callable-row="true" data-callable-name="start_pipeline_run" data-callable-module="pipeline" data-callable-starter-path="02_pipeline, 99_explore" data-callable-usage-source="02_pipeline, 99_explore" data-function-type="public-starter-kit" data-callable-purpose="Start a guided notebook run and store runtime defaults.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></h3>
  <p class="reference-catalogue-item-purpose">Start a guided notebook run and store runtime defaults.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 99_explore</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 99_explore</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 7</span></summary><ul><li><code>get_selected_agreement</code></li><li><code>widget_select_agreement</code></li><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="governance_review-widget_author_dq_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_dq_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render interactive manual DQ guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive manual DQ guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>guardrail_authoring_status</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="governance_review-widget_author_schema_freshness_profile_rules" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_author_schema_freshness_profile_rules" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render interactive schema, freshness, and profile-behavior guardrail authoring controls.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive schema, freshness, and profile-behavior guardrail authoring controls.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>guardrail_authoring_status</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="governance_review-widget_enrich_table_metadata" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_enrich_table_metadata" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render a consolidated column enrichment widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render a consolidated column enrichment widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 6</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>build_enrichment_rule_records</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li><li><code>guardrail_authoring_status</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-widget_render_agreement_evidence" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_agreement_evidence" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="public-starter-kit" data-callable-purpose="Render the standalone agreement-evidence widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone agreement-evidence widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 01_agreement</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-widget_render_data_agreement" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_agreement" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="public-starter-kit" data-callable-purpose="Render the standalone data-agreement intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-agreement intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 01_agreement</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="data_agreement-widget_render_data_steward" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_render_data_steward" data-callable-module="data_agreement" data-callable-starter-path="01_agreement" data-callable-usage-source="01_agreement" data-function-type="public-starter-kit" data-callable-purpose="Render the standalone data-steward intake widget.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render the standalone data-steward intake widget.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">01_agreement</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 01_agreement</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="governance_review-widget_review_guardrail_governance" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_review_guardrail_governance" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render interactive controls for reviewing proposed and bypassed guardrail rules.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render interactive controls for reviewing proposed and bypassed guardrail rules.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>apply_governance_enrichment_action</code></li><li><code>apply_governance_rule_action</code></li><li><code>load_rule_review_history</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="governance_review-widget_select_guardrail_target" class="reference-catalogue-item" data-callable-row="true" data-callable-name="widget_select_guardrail_target" data-callable-module="governance_review" data-callable-starter-path="02_pipeline, 03_governance" data-callable-usage-source="02_pipeline, 03_governance" data-function-type="public-starter-kit" data-callable-purpose="Render an interactive target selector for guardrail authoring and governance review.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></h3>
  <p class="reference-catalogue-item-purpose">Render an interactive target selector for guardrail authoring and governance review.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, 03_governance</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, 03_governance</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 5</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>resolve_table_governance_policy</code></li><li><code>configured_lakehouse_schema</code></li><li><code>read_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="io.write_lakehouse_table-write_lakehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_lakehouse_table" data-callable-module="fabric_input_output" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test" data-function-type="public-starter-kit" data-callable-purpose="Write a Spark DataFrame to a configured Fabric lakehouse Delta table.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a Spark DataFrame to a configured Fabric lakehouse Delta table.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline, example_pipeline_demo, example_dq_rule_smoke_test</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
<article id="pipeline-write_pipeline_lineage" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_lineage" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Write many-to-many source-to-target lineage evidence.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write many-to-many source-to-target lineage evidence.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 4</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="pipeline-write_pipeline_run_summary" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_pipeline_run_summary" data-callable-module="pipeline" data-callable-starter-path="02_pipeline" data-callable-usage-source="02_pipeline" data-function-type="public-starter-kit" data-callable-purpose="Write one pipeline runtime summary row to metadata.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write one pipeline runtime summary row to metadata.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">02_pipeline</span></p>
  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> 02_pipeline</p>
  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">
    <details class="reference-count-details"><summary><span class="reference-chip reference-chip-count">Downstream callables: 4</span></summary><ul><li><code>resolve_fabric_context</code></li><li><code>configured_lakehouse_schema</code></li><li><code>write_lakehouse_table_core</code></li><li><code>get_default_fabric_context</code></li></ul></details>
  </div>
</article>
<article id="io.write_warehouse_table-write_warehouse_table" class="reference-catalogue-item" data-callable-row="true" data-callable-name="write_warehouse_table" data-callable-module="fabric_input_output" data-function-type="public-starter-kit" data-callable-purpose="Write a DataFrame to a configured Fabric warehouse target.">
  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a></h3>
  <p class="reference-catalogue-item-purpose">Write a DataFrame to a configured Fabric warehouse target.</p>
  <p class="reference-catalogue-item-meta reference-catalogue-item-badges"><span class="reference-chip">Public Starter Kit function</span><span class="reference-chip">—</span></p>

  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>
  <div class="reference-catalogue-item-counts">

  </div>
</article>
</div>

