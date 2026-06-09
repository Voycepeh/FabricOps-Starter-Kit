# Template Function Map

Compact template-first lookup for the public helper functions used by each notebook template. Use the linked function names for detailed API reference pages.

<section class="template-function-group">
<h2><code>00_env_config</code></h2>
<p class="template-function-purpose">Shared environment bootstrap and metadata table setup.</p>
<div class="template-function-row">
<span class="template-function-segment">Environment setup</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/setup_notebook/"><code>setup_notebook</code></a><a class="function-chip" href="../callables/setup_metadata_tables/"><code>setup_metadata_tables</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>01_agreement</code></h2>
<p class="template-function-purpose">Standalone steward, agreement, and evidence widgets for Fabric stability.</p>
<div class="template-function-row">
<span class="template-function-segment">Agreement intake</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_render_data_steward/"><code>widget_render_data_steward</code></a><a class="function-chip" href="../callables/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a><a class="function-chip" href="../callables/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>02_pipeline</code></h2>
<p class="template-function-purpose">Thin production orchestration that keeps normal reads, profiling, guardrails, DQ checks, and writes visible while hiding metadata evidence plumbing.</p>
<div class="template-function-row">
<span class="template-function-segment">Pipeline run</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_select_agreement/"><code>widget_select_agreement</code></a><a class="function-chip" href="../callables/get_selected_agreement/"><code>get_selected_agreement</code></a><a class="function-chip" href="../callables/read_lakehouse_table/"><code>read_lakehouse_table</code></a><a class="function-chip" href="../callables/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a><a class="function-chip" href="../callables/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a><a class="function-chip" href="../callables/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a><a class="function-chip" href="../callables/read_warehouse_table/"><code>read_warehouse_table</code></a><a class="function-chip" href="../callables/profile_dataframe/"><code>profile_dataframe</code></a><a class="function-chip" href="../callables/validate_schema/"><code>validate_schema</code></a><a class="function-chip" href="../callables/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a><a class="function-chip" href="../callables/enforce_dq_rules/"><code>enforce_dq_rules</code></a><a class="function-chip" href="../callables/stop_if_failed/"><code>stop_if_failed</code></a><a class="function-chip" href="../callables/write_lakehouse_table/"><code>write_lakehouse_table</code></a><a class="function-chip" href="../callables/write_warehouse_table/"><code>write_warehouse_table</code></a><a class="function-chip" href="../callables/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a><a class="function-chip" href="../callables/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a><a class="function-chip" href="../callables/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>03_governance</code></h2>
<p class="template-function-purpose">Table-scoped governance review and approved metadata recording.</p>
<div class="template-function-row">
<span class="template-function-segment">Governance review</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a><a class="function-chip" href="../callables/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a><a class="function-chip" href="../callables/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a><a class="function-chip" href="../callables/widget_review_column_context/"><code>widget_review_column_context</code></a><a class="function-chip" href="../callables/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a><a class="function-chip" href="../callables/widget_review_column_classification/"><code>widget_review_column_classification</code></a><a class="function-chip" href="../callables/record_table_governance/"><code>record_table_governance</code></a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>99_explore</code></h2>
<p class="template-function-purpose">Optional discovery, profiling, troubleshooting, investigation, and ad hoc analysis support.</p>
<div class="template-function-row">
<span class="template-function-segment">Exploration</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_select_agreement/"><code>widget_select_agreement</code></a><a class="function-chip" href="../callables/read_lakehouse_table/"><code>read_lakehouse_table</code></a><a class="function-chip" href="../callables/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a><a class="function-chip" href="../callables/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a><a class="function-chip" href="../callables/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a><a class="function-chip" href="../callables/read_warehouse_table/"><code>read_warehouse_table</code></a><a class="function-chip" href="../callables/profile_dataframe/"><code>profile_dataframe</code></a></span>
</div>
</section>

