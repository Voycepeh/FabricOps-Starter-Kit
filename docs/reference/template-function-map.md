# Template Function Map

Compact template-first lookup for the public helper functions used by each notebook template. Use the linked function names for detailed API reference pages.

<section class="template-function-group">
<h2><code>00_env_config</code></h2>
<p class="template-function-purpose">Shared environment bootstrap and metadata table setup.</p>
<div class="template-function-row">
<span class="template-function-segment">Environment setup</span>
<span class="function-chip-wrap"><a class="function-chip" href="../api/reference/setup_notebook/"><code>setup_notebook</code></a><a class="function-chip" href="../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>01_agreement</code></h2>
<p class="template-function-purpose">Standalone steward, agreement, and evidence widgets for Fabric stability.</p>
<div class="template-function-row">
<span class="template-function-segment">Agreement intake</span>
<span class="function-chip-wrap"><a class="function-chip" href="../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a><a class="function-chip" href="../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a><a class="function-chip" href="../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>02_pipeline</code></h2>
<p class="template-function-purpose">Thin production orchestration that keeps source reads, beginner-editable configs, transform logic, target writes, lineage relationships, and pipeline naming visible while package helpers handle reusable config enrichment, guardrails, and evidence plumbing.</p>
<div class="template-function-row">
<span class="template-function-segment">Pipeline run</span>
<span class="function-chip-wrap"><a class="function-chip" href="../api/reference/widget_select_agreement/"><code>widget_select_agreement</code></a><a class="function-chip" href="../api/reference/get_selected_agreement/"><code>get_selected_agreement</code></a><a class="function-chip" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a><a class="function-chip" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a><a class="function-chip" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a><a class="function-chip" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a><a class="function-chip" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a><a class="function-chip" href="../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a><a class="function-chip" href="../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><a class="function-chip" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a><a class="function-chip" href="../api/reference/write_warehouse_table/"><code>write_warehouse_table</code></a><a class="function-chip" href="../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a><a class="function-chip" href="../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a><a class="function-chip" href="../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a><a class="function-chip" href="../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a><a class="function-chip" href="../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>03_governance</code></h2>
<p class="template-function-purpose">Guardrail governance review using the current supported review widget flow.</p>
<div class="template-function-row">
<span class="template-function-segment">Guardrail governance review</span>
<span class="function-chip-wrap"><a class="function-chip" href="../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a><a class="function-chip" href="../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a><a class="function-chip" href="../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>99_explore</code></h2>
<p class="template-function-purpose">Optional discovery, profiling, troubleshooting, investigation, and ad hoc analysis support.</p>
<div class="template-function-row">
<span class="template-function-segment">Exploration</span>
<span class="function-chip-wrap"><a class="function-chip" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a><a class="function-chip" href="../api/reference/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a><a class="function-chip" href="../api/reference/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a><a class="function-chip" href="../api/reference/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a><a class="function-chip" href="../api/reference/read_warehouse_table/"><code>read_warehouse_table</code></a><a class="function-chip" href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>example_pipeline_demo</code></h2>
<p class="template-function-purpose">Optional demo generator that prepares deterministic demo source/target tables plus metadata for the widget-driven pipeline and governance flow.</p>
<div class="template-function-row">
<span class="template-function-segment">Demo generator</span>
<span class="function-chip-wrap"><a class="function-chip" href="../api/reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a><a class="function-chip" href="../api/reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a></span>
</div>
</section>

