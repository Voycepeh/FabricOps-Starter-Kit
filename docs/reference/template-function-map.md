# Template Function Map

Compact template-first lookup for the public helper functions used by each notebook template. Use the linked function names for detailed API reference pages.

<section class="template-function-group">
<h2><code>00_env_config</code></h2>
<p class="template-function-purpose">Shared environment bootstrap and metadata table setup.</p>
<div class="template-function-row">
<span class="template-function-segment">Environment setup</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/setup_notebook/">setup_notebook</a><a class="function-chip" href="../callables/setup_metadata_tables/">setup_metadata_tables</a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>01_da_agreement_template</code></h2>
<p class="template-function-purpose">Standalone steward, agreement, and evidence widgets for Fabric stability.</p>
<div class="template-function-row">
<span class="template-function-segment">Agreement intake</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_render_data_steward/">widget_render_data_steward</a><a class="function-chip" href="../callables/widget_render_data_agreement/">widget_render_data_agreement</a><a class="function-chip" href="../callables/widget_render_agreement_evidence/">widget_render_agreement_evidence</a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>02_ex_agreement_topic</code></h2>
<p class="template-function-purpose">Explore approved agreement data and profile sources.</p>
<div class="template-function-row">
<span class="template-function-segment">Exploration</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_select_agreement/">widget_select_agreement</a><a class="function-chip" href="../callables/read_lakehouse_table/">read_lakehouse_table</a><a class="function-chip" href="../callables/read_lakehouse_csv/">read_lakehouse_csv</a><a class="function-chip" href="../callables/read_lakehouse_parquet/">read_lakehouse_parquet</a><a class="function-chip" href="../callables/read_lakehouse_excel/">read_lakehouse_excel</a><a class="function-chip" href="../callables/read_warehouse_table/">read_warehouse_table</a><a class="function-chip" href="../callables/profile_dataframe/">profile_dataframe</a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>03_pc_agreement_pipeline_template</code></h2>
<p class="template-function-purpose">Production pipeline guardrails, IO, lineage, and publishing.</p>
<div class="template-function-row">
<span class="template-function-segment">Pipeline run</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_select_agreement/">widget_select_agreement</a><a class="function-chip" href="../callables/get_selected_agreement/">get_selected_agreement</a><a class="function-chip" href="../callables/read_lakehouse_table/">read_lakehouse_table</a><a class="function-chip" href="../callables/read_lakehouse_csv/">read_lakehouse_csv</a><a class="function-chip" href="../callables/read_lakehouse_parquet/">read_lakehouse_parquet</a><a class="function-chip" href="../callables/read_lakehouse_excel/">read_lakehouse_excel</a><a class="function-chip" href="../callables/read_warehouse_table/">read_warehouse_table</a><a class="function-chip" href="../callables/validate_schema/">validate_schema</a><a class="function-chip" href="../callables/monitor_data_changes/">monitor_data_changes</a><a class="function-chip" href="../callables/stop_if_failed/">stop_if_failed</a><a class="function-chip" href="../callables/write_lakehouse_table/">write_lakehouse_table</a><a class="function-chip" href="../callables/write_warehouse_table/">write_warehouse_table</a><a class="function-chip" href="../callables/build_lineage_records/">build_lineage_records</a></span>
</div>
</section>

<section class="template-function-group">
<h2><code>04_gov_dataset_table</code></h2>
<p class="template-function-purpose">Table-scoped governance review and approved metadata recording.</p>
<div class="template-function-row">
<span class="template-function-segment">Governance review</span>
<span class="function-chip-wrap"><a class="function-chip" href="../callables/widget_select_catalogue_table/">widget_select_catalogue_table</a><a class="function-chip" href="../callables/get_selected_catalogue_table/">get_selected_catalogue_table</a><a class="function-chip" href="../callables/load_catalogue_profile_rows/">load_catalogue_profile_rows</a><a class="function-chip" href="../callables/widget_review_column_context/">widget_review_column_context</a><a class="function-chip" href="../callables/widget_review_dq_rules/">widget_review_dq_rules</a><a class="function-chip" href="../callables/widget_review_column_classification/">widget_review_column_classification</a><a class="function-chip" href="../callables/record_table_governance/">record_table_governance</a></span>
</div>
</section>

