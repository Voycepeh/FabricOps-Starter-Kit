# Public callable flow map

Generated maintainer view of public FabricOps callable entry points, public-to-public dependencies, and nested internal helper usage. It complements the per-callable **Call flow** sections and does not replace them.

Use this page as a review aid for separation, helper reuse, and refactor planning; it is not an automatic refactor instruction.

## Maintainer overview

Bird eye refactor dashboard for internal helper shapes. Helpers appear once in the main inventory with multiple plain-language refactor reasons when more than one rule matches.

Use the interactive dashboard to search helper names, modules, refactor reasons, callers, or callees; the JSON remains the source of truth.

<div class="callable-flow-signal-cards" markdown="0">
<div class="callable-flow-signal-card is-neutral">
<div class="callable-flow-signal-card-value">238</div>
<div class="callable-flow-signal-card-label">All discovered internal functions</div>
</div>
<div class="callable-flow-signal-card is-neutral">
<div class="callable-flow-signal-card-value">210</div>
<div class="callable-flow-signal-card-label">Public-flow helper nodes</div>
</div>
<div class="callable-flow-signal-card is-neutral">
<div class="callable-flow-signal-card-value">208</div>
<div class="callable-flow-signal-card-label">Reachable internal functions</div>
</div>
<div class="callable-flow-signal-card is-neutral">
<div class="callable-flow-signal-card-value">30</div>
<div class="callable-flow-signal-card-label">Outside public flow</div>
</div>
<div class="callable-flow-signal-card is-high">
<div class="callable-flow-signal-card-value">21</div>
<div class="callable-flow-signal-card-label">High priority candidates</div>
</div>
<div class="callable-flow-signal-card is-medium">
<div class="callable-flow-signal-card-value">83</div>
<div class="callable-flow-signal-card-label">Medium priority candidates</div>
</div>
<div class="callable-flow-signal-card is-protect">
<div class="callable-flow-signal-card-value">22</div>
<div class="callable-flow-signal-card-label">Protect helpers</div>
</div>
<div class="callable-flow-signal-card is-info">
<div class="callable-flow-signal-card-value">21</div>
<div class="callable-flow-signal-card-label">Likely wrapper / inline candidates</div>
</div>
<div class="callable-flow-signal-card is-neutral">
<div class="callable-flow-signal-card-value">20</div>
<div class="callable-flow-signal-card-label">Public API entrypoints</div>
</div>
</div>

<p class="callable-flow-cta" markdown="1">
[Open interactive refactor dashboard](refactor-dashboard.html){ .md-button } [Download callable-flow JSON](_data/callable-flow.json){ .md-button }
</p>

## Callable helper summary

Count wording: **all discovered internal functions** is the full internal function inventory. **Public-flow helper nodes** is the historical callable-flow helper-node count, which can include reachable internal classes used like helpers. **Reachable internal functions** counts only internal functions reached by walking exported public callable entry points in the static call graph. **Outside public flow** counts discovered internal functions that are not reached by that public-entrypoint walk and are audited separately below.

Compact public callable summary for spotting entry points with many helper dependencies. Use the inventory below for helper-level cleanup triage.

<div class="callable-flow-table-wrap" markdown="0">
<table class="callable-flow-table">
<thead>
<tr>
<th class="flow-cell-name">Public callable</th>
<th class="flow-cell-module">Module</th>
<th class="flow-cell-number">Unique internal helper count</th>
<th class="flow-cell-wide">Direct internal helpers</th>
<th class="flow-cell-number">Deepest call chain depth</th>
<th class="flow-cell-number">Repeated helper count</th>
<th class="flow-cell-flag">Calls another public callable</th>
</tr>
</thead>
<tbody>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L500-L504"><code>_rows_for_display</code></a></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">11</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-number">10</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L78-L93"><code>_catalogue_lookup_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L538-L548"><code>_add_audit_columns</code></a></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
<td class="flow-cell-module"><code>data_profiling</code></td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L216-L221"><code>_audit_timestamp_expr</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L59-L82"><code>_get_profiled_columns</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L85-L105"><code>_is_min_max_supported_type</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/read_data/"><code>read_data</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-number">87</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L154-L156"><code>_active_pipeline_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L491-L497"><code>_build_guardrail_blocking_message_from_bundle</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L654-L684"><code>_build_guardrail_evidence_definitions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L650-L651"><code>_guardrail_can_continue</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L642-L643"><code>_table_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L646-L647"><code>_table_name</code></a></td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">Yes</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-number">32</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1047-L1076"><code>_get_metadata_table_schema_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1022-L1026"><code>_metadata_schema_field_names</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L981-L992"><code>_metadata_tables_from_setup_results</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1103-L1110"><code>_resolve_metadata_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1112-L1142"><code>_setup_metadata_table_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L563-L634"><code>_validate_framework_config</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L272-L313"><code>_get_governance_metadata_schemas</code></a></td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L736-L836"><code>_run_config_smoke_tests</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L563-L634"><code>_validate_framework_config</code></a></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-number">34</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L46-L52"><code>_notebook_global</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L23-L40"><code>_PipelineRunContext</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L55-L60"><code>_runtime_metadata_value</code></a></td>
<td class="flow-cell-number">7</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-number">26</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2399-L2435"><code>_dq_records_from_selection</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2060-L2073"><code>_latest_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2076-L2082"><code>_rule_params</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2085-L2096"><code>_write_rule_records</code></a></td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-number">26</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2060-L2073"><code>_latest_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2076-L2082"><code>_rule_params</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2182-L2249"><code>_schema_freshness_profile_records_from_selection</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2085-L2096"><code>_write_rule_records</code></a></td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-number">33</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L588-L590"><code>_collect_enrichment_extra_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L555-L564"><code>_enrichment_options</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L567-L585"><code>_render_enrichment_extra_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L593-L605"><code>_selected_catalogue_rows_for_enrichment</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L750-L760"><code>_write_table_metadata_enrichment_records</code></a></td>
<td class="flow-cell-number">7</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-number">27</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a></td>
<td class="flow-cell-number">7</td>
<td class="flow-cell-number">10</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-number">46</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-number">7</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-number">46</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-number">7</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-number">14</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2043-L2057"><code>_filter_table_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2026-L2040"><code>_read_metadata_table_or_empty</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a></td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/write_data/"><code>write_data</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-number">19</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L163-L164"><code>_definition_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L189-L200"><code>_runtime_audit_fields</code></a></td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-flag">No</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-number">14</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L154-L156"><code>_active_pipeline_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L163-L164"><code>_definition_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L167-L186"><code>_summary_status</code></a></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-flag">No</td>
</tr>
</tbody>
</table>
</div>

## Internal helper nesting inventory

Complete one-row-per-internal-helper inventory for refactor cleanup. It includes shared helpers and single-use helpers so maintainers can decide whether to flatten, merge, protect, promote, or review each function.

<div class="callable-flow-table-wrap" markdown="0">
<table class="callable-flow-table">
<thead>
<tr>
<th class="flow-cell-name">Internal helper</th>
<th class="flow-cell-module">Module</th>
<th class="flow-cell-qualified">Qualified name</th>
<th class="flow-cell-wide">Refactor reason / priority</th>
<th class="flow-cell-wide">Called by</th>
<th class="flow-cell-wide">Calls</th>
<th class="flow-cell-number">Inbound</th>
<th class="flow-cell-number">Outbound</th>
<th class="flow-cell-number">Depth</th>
<th class="flow-cell-wide">Public entrypoint lineage</th>
<th class="flow-cell-wide">Suggested action</th>
</tr>
</thead>
<tbody>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L216-L221"><code>_audit_timestamp_expr</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._audit_timestamp_expr</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347"><code>profile_dataframe</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L995-L1019"><code>_detect_nested_metadata_delta_folders</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._detect_nested_metadata_delta_folders</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1088-L1094"><code>_metadata_table_columns</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._metadata_table_columns</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1112-L1142"><code>_setup_metadata_table_registry</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1079-L1085"><code>_coerce_row_dicts</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._normalize_path_config</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1062-L1072"><code>_agreement_identity_text</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._agreement_identity_text</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L579-L582"><code>_next_minor_version</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L366-L399"><code>_collect_custom_fields</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._collect_custom_fields</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L630-L633"><code>_to_iso_date</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L158-L180"><code>_get_widget_visible_fields</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._get_widget_visible_fields</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L410-L416"><code>_latest_by_key</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._latest_by_key</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L702-L752"><code>_prepare_evidence_file_references</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._prepare_evidence_file_references</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L754-L785"><code>_save_agreement_evidence_records</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L690-L699"><code>_get_notebookutils</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2399-L2435"><code>_dq_records_from_selection</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_records_from_selection</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2438-L2606"><code>widget_author_dq_rules</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L341-L347"><code>_first_present</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._first_present</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L360-L380"><code>_catalogue_physical_identity</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1309-L1330"><code>_latest_dq_rule_versions</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._latest_dq_rule_versions</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L950-L954"><code>_latest_row</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._latest_row</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2182-L2249"><code>_schema_freshness_profile_records_from_selection</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._schema_freshness_profile_records_from_selection</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2252-L2397"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L593-L605"><code>_selected_catalogue_rows_for_enrichment</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._selected_catalogue_rows_for_enrichment</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L763-L897"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L567-L569"><code>_iso_date_value</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._iso_date_value</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L572-L670"><code>enforce_freshness</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L547-L564"><code>_coerce_date</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L217-L218"><code>_profile_hash</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._profile_hash</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L213-L214"><code>_json_dumps_stable</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L499-L511"><code>_profile_row_count</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._profile_row_count</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L226-L247"><code>_profile_payload_from_profile</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L411-L479"><code>_normalize_profile</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L221-L223"><code>_schema_signature</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._schema_signature</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L226-L247"><code>_profile_payload_from_profile</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L194-L209"><code>_actual_schema</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L538-L548"><code>_add_audit_columns</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._add_audit_columns</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L551-L640"><code>prepare_pipeline_table_configs</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L341-L353"><code>_dq_reason</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._dq_reason</code></td>
<td class="flow-cell-wide">Likely wrapper / inline candidate, Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L356-L366"><code>_guardrail_reason</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L272-L276"><code>_result_reason</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Inline candidate</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1324-L1329"><code>_check_spark_session</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._check_spark_session</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L736-L836"><code>_run_config_smoke_tests</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1079-L1085"><code>_coerce_row_dicts</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._coerce_row_dicts</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1088-L1094"><code>_metadata_table_columns</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1097-L1099"><code>_create_empty_metadata_dataframe</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._create_empty_metadata_dataframe</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1112-L1142"><code>_setup_metadata_table_registry</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L952-L978"><code>_get_active_metadata_tables</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._get_active_metadata_tables</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L563-L634"><code>_validate_framework_config</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L272-L313"><code>_get_governance_metadata_schemas</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1332-L1371"><code>_get_fabric_runtime_metadata</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._get_fabric_runtime_metadata</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L736-L836"><code>_run_config_smoke_tests</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1047-L1076"><code>_get_metadata_table_schema_registry</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._get_metadata_table_schema_registry</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1029-L1044"><code>_string_metadata_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L563-L634"><code>_validate_framework_config</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L272-L313"><code>_get_governance_metadata_schemas</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L981-L992"><code>_metadata_tables_from_setup_results</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._metadata_tables_from_setup_results</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L736-L836"><code>_run_config_smoke_tests</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._run_config_smoke_tests</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L839-L949"><code>setup_notebook</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1324-L1329"><code>_check_spark_session</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1332-L1371"><code>_get_fabric_runtime_metadata</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L722-L733"><code>_validate_notebook_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L517-L522"><code>ConfigSmokeCheckResult</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1112-L1142"><code>_setup_metadata_table_registry</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._setup_metadata_table_registry</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1097-L1099"><code>_create_empty_metadata_dataframe</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1022-L1026"><code>_metadata_schema_field_names</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1088-L1094"><code>_metadata_table_columns</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L316-L336"><code>_is_table_not_found_error</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1029-L1044"><code>_string_metadata_schema</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._string_metadata_schema</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1047-L1076"><code>_get_metadata_table_schema_registry</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._validate_metadata_table_registration</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L995-L1019"><code>_detect_nested_metadata_delta_folders</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L952-L978"><code>_get_active_metadata_tables</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1103-L1110"><code>_resolve_metadata_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L563-L634"><code>_validate_framework_config</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L722-L733"><code>_validate_notebook_name</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._validate_notebook_name</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L736-L836"><code>_run_config_smoke_tests</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L636-L640"><code>_business_agreement_snapshot</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._business_agreement_snapshot</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L119-L148"><code>_deserialize_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L102-L116"><code>_serialize_custom_fields</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L636-L640"><code>_business_agreement_snapshot</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L626-L627"><code>_generate_agreement_id</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L579-L582"><code>_next_minor_version</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L570-L576"><code>_parse_contract_version</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L497-L507"><code>_parse_iso_date</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L102-L116"><code>_serialize_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">11</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L438-L448"><code>_active_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L451-L455"><code>_generate_steward_id</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L497-L507"><code>_parse_iso_date</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L102-L116"><code>_serialize_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L626-L627"><code>_generate_agreement_id</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._generate_agreement_id</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L451-L455"><code>_generate_steward_id</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._generate_steward_id</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L690-L699"><code>_get_notebookutils</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._get_notebookutils</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L702-L752"><code>_prepare_evidence_file_references</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1407-L1440"><code>widget_render_agreement_evidence</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L754-L785"><code>_save_agreement_evidence_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L313-L363"><code>_render_custom_fields</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._render_custom_fields</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L754-L785"><code>_save_agreement_evidence_records</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._save_agreement_evidence_records</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L702-L752"><code>_prepare_evidence_file_references</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1046-L1059"><code>_standard_widget</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._standard_widget</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_lineage.py#L8-L42"><code>_validate_lineage_steps</code></a></td>
<td class="flow-cell-module"><code>data_lineage</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_lineage._validate_lineage_steps</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_lineage.py#L45-L93"><code>_build_lineage_records</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L153-L190"><code>_build_categorical_distribution</code></a></td>
<td class="flow-cell-module"><code>data_profiling</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_profiling._build_categorical_distribution</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries</code></a></td>
<td class="flow-cell-module"><code>data_profiling</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347"><code>profile_dataframe</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L153-L190"><code>_build_categorical_distribution</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L121-L150"><code>_build_numeric_distribution</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L108-L118"><code>_numeric_bin_edges</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L121-L150"><code>_build_numeric_distribution</code></a></td>
<td class="flow-cell-module"><code>data_profiling</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_profiling._build_numeric_distribution</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L59-L82"><code>_get_profiled_columns</code></a></td>
<td class="flow-cell-module"><code>data_profiling</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_profiling._get_profiled_columns</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347"><code>profile_dataframe</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L85-L105"><code>_is_min_max_supported_type</code></a></td>
<td class="flow-cell-module"><code>data_profiling</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_profiling._is_min_max_supported_type</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347"><code>profile_dataframe</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L108-L118"><code>_numeric_bin_edges</code></a></td>
<td class="flow-cell-module"><code>data_profiling</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_profiling._numeric_bin_edges</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L730-L783"><code>_convert_single_parquet_ns_to_us</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L786-L910"><code>read_lakehouse_parquet</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/read_data/"><code>read_data</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L131-L135"><code>_qualified_table_name</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._qualified_table_name</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L157-L161"><code>_resolve_lakehouse_table_identifier</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1794-L1806"><code>_authoring_lifecycle</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._authoring_lifecycle</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1808-L1840"><code>guardrail_authoring_status</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1764-L1766"><code>_is_no_approval_required</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1775-L1791"><code>_lifecycle_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._build_dq_rule_records</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1113-L1224"><code>record_table_governance</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L213-L225"><code>_approved_column_identity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L207-L210"><code>_approved_review_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L197-L198"><code>_canonical_dq_rule_type</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L460-L482"><code>_dq_rule_parameter_payload</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L547-L552"><code>_json</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L201-L204"><code>_normalize_dq_severity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L78-L93"><code>_catalogue_lookup_value</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._catalogue_lookup_value</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194"><code>get_latest_metadata_catalogue</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L237-L263"><code>_check_metadata_schema_field_names</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._check_metadata_schema_field_names</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L266-L269"><code>_schema</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L588-L590"><code>_collect_enrichment_extra_fields</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._collect_enrichment_extra_fields</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L763-L897"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1468-L1471"><code>_dq_check_status</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_check_status</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1548-L1558"><code>_dq_failed_row_count</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_failed_row_count</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1384-L1466"><code>_dq_failed_expression</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L460-L482"><code>_dq_rule_parameter_payload</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_rule_parameter_payload</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L899-L914"><code>_dq_rule_parameters_summary</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_rule_parameters_summary</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L917-L947"><code>_dq_rule_display_rows</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1561-L1576"><code>_dq_summary</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_summary</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1579-L1596"><code>_summarize_dq_guardrail</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1512-L1545"><code>_dq_tagged_dataframe</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1384-L1466"><code>_dq_failed_expression</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L201-L204"><code>_normalize_dq_severity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L555-L564"><code>_enrichment_options</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._enrichment_options</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L763-L897"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L608-L625"><code>_enrichment_payload_from_review</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._enrichment_payload_from_review</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L628-L747"><code>build_enrichment_rule_records</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._evaluate_governance_readiness</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1113-L1224"><code>record_table_governance</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L950-L954"><code>_latest_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L965-L966"><code>_read_metadata_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L957-L958"><code>_status_is_failed</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L961-L962"><code>_status_is_warning</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">10</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2043-L2057"><code>_filter_table_rows</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._filter_table_rows</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2099-L2180"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1775-L1791"><code>_lifecycle_fields</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._lifecycle_fields</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1794-L1806"><code>_authoring_lifecycle</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._load_active_dq_rules</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L197-L198"><code>_canonical_dq_rule_type</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1309-L1330"><code>_latest_dq_rule_versions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L201-L204"><code>_normalize_dq_severity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1600-L1607"><code>_read_guardrail_rule_metadata</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._read_guardrail_rule_metadata</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L965-L966"><code>_read_metadata_rows</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._read_metadata_rows</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2026-L2040"><code>_read_metadata_table_or_empty</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._read_metadata_table_or_empty</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2099-L2180"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L316-L336"><code>_is_table_not_found_error</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L567-L585"><code>_render_enrichment_extra_fields</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._render_enrichment_extra_fields</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L763-L897"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._run_active_dq_guardrail</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1548-L1558"><code>_dq_failed_row_count</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1561-L1576"><code>_dq_summary</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1512-L1545"><code>_dq_tagged_dataframe</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1600-L1607"><code>_read_guardrail_rule_metadata</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1579-L1596"><code>_summarize_dq_guardrail</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1468-L1471"><code>_dq_check_status</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1384-L1466"><code>_dq_failed_expression</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L201-L204"><code>_normalize_dq_severity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L266-L269"><code>_schema</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._schema</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L272-L313"><code>_get_governance_metadata_schemas</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L237-L263"><code>_check_metadata_schema_field_names</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L228-L234"><code>_spark_types</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L957-L958"><code>_status_is_failed</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._status_is_failed</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L961-L962"><code>_status_is_warning</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._status_is_warning</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L278-L307"><code>_accepted_profile_rows</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._accepted_profile_rows</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L482-L489"><code>_row_to_dict</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._check_schema_rule_runtime</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L46-L51"><code>_parse_rule_parameters</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L492-L496"><code>_guardrail_exclude_columns</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._guardrail_exclude_columns</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L915-L918"><code>_is_missing_table_error</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._is_missing_table_error</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L514-L544"><code>_max_column_value</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._max_column_value</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L572-L670"><code>enforce_freshness</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L226-L247"><code>_profile_payload_from_profile</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._profile_payload_from_profile</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L411-L479"><code>_normalize_profile</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L499-L511"><code>_profile_row_count</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L221-L223"><code>_schema_signature</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L251-L276"><code>_select_profile_behavior_rule</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._select_profile_behavior_rule</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L482-L489"><code>_row_to_dict</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L56-L61"><code>_coerce_row_dicts</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._coerce_row_dicts</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L398-L448"><code>_load_notebook_registry</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L451-L507"><code>_current_notebook_active_registrations</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L398-L448"><code>_load_notebook_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L398-L448"><code>_load_notebook_registry</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._load_notebook_registry</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L451-L507"><code>_current_notebook_active_registrations</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L56-L61"><code>_coerce_row_dicts</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L44-L53"><code>_notebook_registration_key</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._register_current_notebook</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L44-L53"><code>_notebook_registration_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L142-L151"><code>_rows_for_spark</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L142-L151"><code>_rows_for_spark</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._rows_for_spark</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L477-L488"><code>_blocking_guardrail_message</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._blocking_guardrail_message</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L491-L497"><code>_build_guardrail_blocking_message_from_bundle</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L491-L497"><code>_build_guardrail_blocking_message_from_bundle</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._build_guardrail_blocking_message_from_bundle</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L477-L488"><code>_blocking_guardrail_message</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L654-L684"><code>_build_guardrail_evidence_definitions</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._build_guardrail_evidence_definitions</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L642-L643"><code>_table_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L646-L647"><code>_table_name</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L203-L231"><code>_canonical_catalogue_profile_df</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._canonical_catalogue_profile_df</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L307-L311"><code>_freshness_reason</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._freshness_reason</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L356-L366"><code>_guardrail_reason</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L272-L276"><code>_result_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L260-L262"><code>_result_status</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L650-L651"><code>_guardrail_can_continue</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._guardrail_can_continue</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L234-L251"><code>_normalize_catalogue_evidence_types</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._normalize_catalogue_evidence_types</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L46-L52"><code>_notebook_global</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._notebook_global</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L63-L151"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L23-L40"><code>_PipelineRunContext</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._PipelineRunContext</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L63-L151"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L314-L338"><code>_profile_behavior_reason</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._profile_behavior_reason</code></td>
<td class="flow-cell-wide">Used by only one function</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L356-L366"><code>_guardrail_reason</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L272-L276"><code>_result_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L260-L262"><code>_result_status</code></a></td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L500-L504"><code>_rows_for_display</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._rows_for_display</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L507-L535"><code>display_guardrail_results</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L55-L60"><code>_runtime_metadata_value</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._runtime_metadata_value</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L63-L151"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L293-L304"><code>_schema_reason</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._schema_reason</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L356-L366"><code>_guardrail_reason</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L167-L186"><code>_summary_status</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._summary_status</code></td>
<td class="flow-cell-wide">Used by only one function, End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Review abstraction value</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1022-L1026"><code>_metadata_schema_field_names</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._metadata_schema_field_names</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1112-L1142"><code>_setup_metadata_table_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L300-L312"><code>_normalize_widget_config</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._normalize_widget_config</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._validate_audit_timezone</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L563-L634"><code>_validate_framework_config</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a>, <a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._coerce_row_dicts</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L585-L601"><code>_latest_agreement_versions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L410-L416"><code>_latest_by_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L119-L148"><code>_deserialize_custom_fields</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._deserialize_custom_fields</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L636-L640"><code>_business_agreement_snapshot</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L195-L198"><code>_html_escape</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._html_escape</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L570-L576"><code>_parse_contract_version</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._parse_contract_version</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L585-L601"><code>_latest_agreement_versions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L579-L582"><code>_next_minor_version</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L497-L507"><code>_parse_iso_date</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._parse_iso_date</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L102-L116"><code>_serialize_custom_fields</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._serialize_custom_fields</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L636-L640"><code>_business_agreement_snapshot</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L630-L633"><code>_to_iso_date</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._to_iso_date</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L366-L399"><code>_collect_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._widget_common</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L313-L363"><code>_render_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1046-L1059"><code>_standard_widget</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L221-L231"><code>_lakehouse_file_path</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L551-L594"><code>read_lakehouse_csv</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L913-L1000"><code>read_lakehouse_excel</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L786-L910"><code>read_lakehouse_parquet</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/read_data/"><code>read_data</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._normalize_schema_name</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L131-L135"><code>_qualified_table_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L21-L25"><code>_PandasProxy</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._PandasProxy</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1769-L1772"><code>_assert_governance_review_context</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._assert_governance_review_context</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1900-L1953"><code>apply_governance_enrichment_action</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1847-L1898"><code>apply_governance_rule_action</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L197-L198"><code>_canonical_dq_rule_type</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L917-L947"><code>_dq_rule_display_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1764-L1766"><code>_is_no_approval_required</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._is_no_approval_required</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1794-L1806"><code>_authoring_lifecycle</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1808-L1840"><code>guardrail_authoring_status</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L316-L336"><code>_is_table_not_found_error</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._is_table_not_found_error</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1112-L1142"><code>_setup_metadata_table_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2026-L2040"><code>_read_metadata_table_or_empty</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L547-L552"><code>_json</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._json</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L628-L747"><code>build_enrichment_rule_records</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2060-L2073"><code>_latest_rule</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._latest_rule</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2438-L2606"><code>widget_author_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2252-L2397"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1842-L1844"><code>_record_identity</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._record_identity</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1900-L1953"><code>apply_governance_enrichment_action</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1847-L1898"><code>apply_governance_rule_action</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2076-L2082"><code>_rule_params</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._rule_params</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2438-L2606"><code>widget_author_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2252-L2397"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L228-L234"><code>_spark_types</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._spark_types</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L272-L313"><code>_get_governance_metadata_schemas</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L266-L269"><code>_schema</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1579-L1596"><code>_summarize_dq_guardrail</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._summarize_dq_guardrail</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1561-L1576"><code>_dq_summary</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L547-L564"><code>_coerce_date</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._coerce_date</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L567-L569"><code>_iso_date_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L572-L670"><code>enforce_freshness</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L213-L214"><code>_json_dumps_stable</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._json_dumps_stable</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L217-L218"><code>_profile_hash</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L145-L191"><code>_normalize_datatype</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._normalize_datatype</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L194-L209"><code>_actual_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L482-L489"><code>_row_to_dict</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._row_to_dict</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L278-L307"><code>_accepted_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L251-L276"><code>_select_profile_behavior_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L44-L53"><code>_notebook_registration_key</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._notebook_registration_key</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L398-L448"><code>_load_notebook_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._safe_str</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L451-L507"><code>_current_notebook_active_registrations</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._stable_metadata_key</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L154-L156"><code>_active_pipeline_context</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._active_pipeline_context</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L163-L164"><code>_definition_name</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._definition_name</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1062-L1149"><code>write_pipeline_lineage</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L279-L290"><code>_next_action</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._next_action</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L445-L474"><code>build_guardrail_detail_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L265-L269"><code>_result_can_continue</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._result_can_continue</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L445-L474"><code>build_guardrail_detail_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L272-L276"><code>_result_reason</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._result_reason</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L341-L353"><code>_dq_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L307-L311"><code>_freshness_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L356-L366"><code>_guardrail_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L314-L338"><code>_profile_behavior_reason</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L642-L643"><code>_table_key</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._table_key</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L654-L684"><code>_build_guardrail_evidence_definitions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L369-L376"><code>_table_keys</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._table_keys</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L445-L474"><code>build_guardrail_detail_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L646-L647"><code>_table_name</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._table_name</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L654-L684"><code>_build_guardrail_evidence_definitions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L255-L257"><code>_yes_no</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._yes_no</code></td>
<td class="flow-cell-wide">End-of-chain helper</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L445-L474"><code>build_guardrail_detail_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Keep / protect</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._get_audit_timezone</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L216-L221"><code>_audit_timestamp_expr</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347"><code>profile_dataframe</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a>, <a href="../../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1103-L1110"><code>_resolve_metadata_schema</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._resolve_metadata_schema</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L438-L448"><code>_active_steward</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._active_steward</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L585-L601"><code>_latest_agreement_versions</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L616-L623"><code>_list_data_agreements</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L570-L576"><code>_parse_contract_version</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L616-L623"><code>_list_data_agreements</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L402-L407"><code>_coerce_row_dicts</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L616-L623"><code>_list_data_agreements</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._list_data_agreements</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L585-L601"><code>_latest_agreement_versions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._list_data_stewards</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L438-L448"><code>_active_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L410-L416"><code>_latest_by_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L579-L582"><code>_next_minor_version</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._next_minor_version</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1062-L1072"><code>_agreement_identity_text</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L570-L576"><code>_parse_contract_version</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1464-L1482"><code>widget_render_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1443-L1461"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1062-L1072"><code>_agreement_identity_text</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L366-L399"><code>_collect_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L119-L148"><code>_deserialize_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L158-L180"><code>_get_widget_visible_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L616-L623"><code>_list_data_agreements</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L313-L363"><code>_render_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1046-L1059"><code>_standard_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L630-L633"><code>_to_iso_date</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">15</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L201-L311"><code>_render_searchable_selector</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._render_searchable_selector</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L195-L198"><code>_html_escape</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L183-L192"><code>_widget_common</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._write_row</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L754-L785"><code>_save_agreement_evidence_records</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_lineage.py#L45-L93"><code>_build_lineage_records</code></a></td>
<td class="flow-cell-module"><code>data_lineage</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_lineage._build_lineage_records</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_lineage.py#L8-L42"><code>_validate_lineage_steps</code></a></td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._resolve_lakehouse_schema</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L157-L161"><code>_resolve_lakehouse_table_identifier</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L157-L161"><code>_resolve_lakehouse_table_identifier</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._resolve_lakehouse_table_identifier</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L131-L135"><code>_qualified_table_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a></td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._resolve_lakehouse_table_path</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L213-L225"><code>_approved_column_identity</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._approved_column_identity</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L628-L747"><code>build_enrichment_rule_records</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L207-L210"><code>_approved_review_context</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._approved_review_context</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L628-L747"><code>build_enrichment_rule_records</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._base_guardrail_rule_record</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2399-L2435"><code>_dq_records_from_selection</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2182-L2249"><code>_schema_freshness_profile_records_from_selection</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1808-L1840"><code>guardrail_authoring_status</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L360-L380"><code>_catalogue_physical_identity</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._catalogue_physical_identity</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L383-L438"><code>_catalogue_profile_target_model</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L341-L347"><code>_first_present</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L383-L438"><code>_catalogue_profile_target_model</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._catalogue_profile_target_model</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L360-L380"><code>_catalogue_physical_identity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L74-L75"><code>_is_success</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a></td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1384-L1466"><code>_dq_failed_expression</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_failed_expression</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1548-L1558"><code>_dq_failed_row_count</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1512-L1545"><code>_dq_tagged_dataframe</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L917-L947"><code>_dq_rule_display_rows</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._dq_rule_display_rows</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L197-L198"><code>_canonical_dq_rule_type</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L899-L914"><code>_dq_rule_parameters_summary</code></a></td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L272-L313"><code>_get_governance_metadata_schemas</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._get_governance_metadata_schemas</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L952-L978"><code>_get_active_metadata_tables</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1047-L1076"><code>_get_metadata_table_schema_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L266-L269"><code>_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L228-L234"><code>_spark_types</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L74-L75"><code>_is_success</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._is_success</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L383-L438"><code>_catalogue_profile_target_model</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1695-L1719"><code>_prepare_dq_profile_input_rows</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347"><code>profile_dataframe</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a></td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L350-L357"><code>_profile_sort_key</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._profile_sort_key</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a></td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._validate_dq_rules</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1384-L1466"><code>_dq_failed_expression</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L197-L198"><code>_canonical_dq_rule_type</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L201-L204"><code>_normalize_dq_severity</code></a></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2002-L2004"><code>_write_enrichment_records</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._write_enrichment_records</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L750-L760"><code>_write_table_metadata_enrichment_records</code></a></td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">—</td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2085-L2096"><code>_write_rule_records</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._write_rule_records</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2438-L2606"><code>widget_author_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2252-L2397"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L750-L760"><code>_write_table_metadata_enrichment_records</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._write_table_metadata_enrichment_records</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2002-L2004"><code>_write_enrichment_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L763-L897"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L194-L209"><code>_actual_schema</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._actual_schema</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L221-L223"><code>_schema_signature</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L145-L191"><code>_normalize_datatype</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._apply_bypass_post_review_warning</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L113-L131"><code>enforce_freshness_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._check_schema_runtime</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L194-L209"><code>_actual_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L145-L191"><code>_normalize_datatype</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._is_active_guardrail_rule</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L251-L276"><code>_select_profile_behavior_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L411-L479"><code>_normalize_profile</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._normalize_profile</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L411-L479"><code>_normalize_profile</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L226-L247"><code>_profile_payload_from_profile</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L499-L511"><code>_profile_row_count</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L411-L479"><code>_normalize_profile</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L46-L51"><code>_parse_rule_parameters</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._parse_rule_parameters</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L113-L131"><code>enforce_freshness_rule</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._rule_review_status</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._select_table_guardrail_rule</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L113-L131"><code>enforce_freshness_rule</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L482-L489"><code>_row_to_dict</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._build_dq_rule_key</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L628-L747"><code>build_enrichment_rule_records</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._build_metadata_column_key</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L213-L225"><code>_approved_column_identity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._runtime_context</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L451-L507"><code>_current_notebook_active_registrations</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a></td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._write_guardrail_result_row</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1609-L1692"><code>_run_active_dq_guardrail</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a></td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-number">4</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L356-L366"><code>_guardrail_reason</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._guardrail_reason</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L445-L474"><code>build_guardrail_detail_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L341-L353"><code>_dq_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L307-L311"><code>_freshness_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L314-L338"><code>_profile_behavior_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L272-L276"><code>_result_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L260-L262"><code>_result_status</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L293-L304"><code>_schema_reason</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L189-L200"><code>_runtime_audit_fields</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._runtime_audit_fields</code></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1062-L1149"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso</code></a></td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide">Review manually</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._current_audit_timestamp</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_lineage.py#L45-L93"><code>_build_lineage_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1561-L1576"><code>_dq_summary</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1695-L1719"><code>_prepare_dq_profile_input_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L538-L548"><code>_add_audit_columns</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a></td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._get_store</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L995-L1019"><code>_detect_nested_metadata_delta_folders</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1103-L1110"><code>_resolve_metadata_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L736-L836"><code>_run_config_smoke_tests</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L839-L949"><code>setup_notebook</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L551-L594"><code>read_lakehouse_csv</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L913-L1000"><code>read_lakehouse_excel</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L786-L910"><code>read_lakehouse_parquet</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L597-L659"><code>read_warehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L662-L727"><code>write_warehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a></td>
<td class="flow-cell-number">14</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L563-L634"><code>_validate_framework_config</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.config._validate_framework_config</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L952-L978"><code>_get_active_metadata_tables</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1047-L1076"><code>_get_metadata_table_schema_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1194-L1321"><code>setup_metadata_tables</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L839-L949"><code>setup_notebook</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L471-L513"><code>FrameworkConfig</code></a></td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/setup_notebook/"><code>setup_notebook</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L151-L155"><code>_config_value</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._config_value</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L158-L180"><code>_get_widget_visible_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L458-L490"><code>_list_data_stewards</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L754-L785"><code>_save_agreement_evidence_records</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">7</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L63-L72"><code>_require_ipywidgets</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._require_ipywidgets</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1286-L1404"><code>_render_agreement_evidence_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L313-L363"><code>_render_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1046-L1059"><code>_standard_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L419-L435"><code>_to_bool</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.data_agreement._to_bool</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L438-L448"><code>_active_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L313-L363"><code>_render_custom_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1075-L1283"><code>_render_maintenance_widget</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1046-L1059"><code>_standard_widget</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._configured_lakehouse_schema</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1600-L1607"><code>_read_guardrail_rule_metadata</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L965-L966"><code>_read_metadata_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2026-L2040"><code>_read_metadata_table_or_empty</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2085-L2096"><code>_write_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L750-L760"><code>_write_table_metadata_enrichment_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194"><code>get_latest_metadata_catalogue</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1113-L1224"><code>record_table_governance</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L398-L448"><code>_load_notebook_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1062-L1149"><code>write_pipeline_lineage</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a></td>
<td class="flow-cell-number">17</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L187-L218"><code>_get_spark</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._get_spark</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L551-L594"><code>read_lakehouse_csv</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L913-L1000"><code>read_lakehouse_excel</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L786-L910"><code>read_lakehouse_parquet</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L597-L659"><code>read_warehouse_table</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L131-L135"><code>_qualified_table_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L157-L161"><code>_resolve_lakehouse_table_identifier</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._coerce_rows</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L965-L966"><code>_read_metadata_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2026-L2040"><code>_read_metadata_table_or_empty</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194"><code>get_latest_metadata_catalogue</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1722-L1760"><code>resolve_table_governance_policy</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">6</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L201-L204"><code>_normalize_dq_severity</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._normalize_dq_severity</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L485-L545"><code>_build_dq_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1512-L1545"><code>_dq_tagged_dataframe</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._spark_sql_helpers</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1384-L1466"><code>_dq_failed_expression</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1548-L1558"><code>_dq_failed_row_count</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1512-L1545"><code>_dq_tagged_dataframe</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1309-L1330"><code>_latest_dq_rule_versions</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1695-L1719"><code>_prepare_dq_profile_input_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1600-L1607"><code>_read_guardrail_rule_metadata</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.governance_review._value</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L213-L225"><code>_approved_column_identity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L207-L210"><code>_approved_review_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L360-L380"><code>_catalogue_physical_identity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L383-L438"><code>_catalogue_profile_target_model</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L341-L347"><code>_first_present</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L74-L75"><code>_is_success</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L950-L954"><code>_latest_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L350-L357"><code>_profile_sort_key</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L593-L605"><code>_selected_catalogue_rows_for_enrichment</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L763-L897"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">12</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._catalogue_value</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L278-L307"><code>_accepted_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L46-L51"><code>_parse_rule_parameters</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L251-L276"><code>_select_profile_behavior_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L113-L131"><code>enforce_freshness_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.guardrails._string_value</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L278-L307"><code>_accepted_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L226-L247"><code>_profile_payload_from_profile</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L251-L276"><code>_select_profile_behavior_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L113-L131"><code>enforce_freshness_rule</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._build_metadata_table_key</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L213-L225"><code>_approved_column_identity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L360-L380"><code>_catalogue_physical_identity</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2099-L2180"><code>widget_select_guardrail_target</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L687-L950"><code>run_table_guardrails</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1062-L1149"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a></td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L643-L687"><code>_create_or_update_data_agreement</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L510-L567"><code>_create_or_update_data_steward</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L754-L785"><code>_save_agreement_evidence_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L207-L210"><code>_approved_review_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L189-L200"><code>_runtime_audit_fields</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a></td>
<td class="flow-cell-number">7</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._context_get</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L451-L507"><code>_current_notebook_active_registrations</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">3</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._now_utc_iso</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L207-L210"><code>_approved_review_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1794-L1806"><code>_authoring_lifecycle</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1900-L1953"><code>apply_governance_enrichment_action</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1847-L1898"><code>apply_governance_rule_action</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2608-L2662"><code>build_table_governance_policy_record</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1113-L1224"><code>record_table_governance</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a></td>
<td class="flow-cell-number">9</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a></td>
<td class="flow-cell-module"><code>metadata</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.metadata._resolve_action_by</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L207-L210"><code>_approved_review_context</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1794-L1806"><code>_authoring_lifecycle</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L969-L1111"><code>_evaluate_governance_readiness</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1900-L1953"><code>apply_governance_enrichment_action</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1847-L1898"><code>apply_governance_rule_action</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2608-L2662"><code>build_table_governance_policy_record</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1113-L1224"><code>record_table_governance</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a></td>
<td class="flow-cell-number">8</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._now_iso</code></td>
<td class="flow-cell-wide">Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L189-L200"><code>_runtime_audit_fields</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L63-L151"><code>start_pipeline_run</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1062-L1149"><code>write_pipeline_lineage</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a></td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-number">1</td>
<td class="flow-cell-wide"><a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L260-L262"><code>_result_status</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-qualified"><code>fabricops_kit.pipeline._result_status</code></td>
<td class="flow-cell-wide">End-of-chain helper, Used by many functions</td>
<td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L307-L311"><code>_freshness_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L356-L366"><code>_guardrail_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L314-L338"><code>_profile_behavior_reason</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L445-L474"><code>build_guardrail_detail_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-wide">—</td>
<td class="flow-cell-number">5</td>
<td class="flow-cell-number">0</td>
<td class="flow-cell-number">2</td>
<td class="flow-cell-wide"><a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
<td class="flow-cell-wide">Shared helper – preserve carefully</td>
</tr>
</tbody>
</table>
</div>

## Internal functions outside public callable flow

Generated audit of discovered internal functions that are absent from the public callable-flow helper inventory. These functions may still be valid internal APIs, template-facing advanced helpers, test/docs support, dynamically referenced functions, or maintainer-review candidates.

<div class="callable-flow-table-wrap" markdown="0">
<table class="callable-flow-table">
<thead>
<tr>
<th class="flow-cell-name">Function</th>
<th class="flow-cell-module">Module</th>
<th class="flow-cell-wide">Reason excluded from public flow</th>
<th class="flow-cell-wide">Detected usage</th>
<th class="flow-cell-wide">Suggested action</th>
</tr>
</thead>
<tbody>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>get_fabric_context</code>, <code>resolve_fabric_context</code><br><strong>Tests:</strong> tests/unit/test_config.py<br><strong>Dynamic/text refs:</strong> docs/api/reference/get_latest_metadata_catalogue.md, docs/api/reference/read_data.md, docs/api/reference/run_table_guardrails.md, docs/api/reference/setup_metadata_tables.md, docs/api/reference/start_pipeline_run.md, docs/api/reference/widget_author_dq_rules.md, docs/api/reference/widget_author_schema_freshness_profile_rules.md, docs/api/reference/widget_enrich_table_metadata.md, docs/api/reference/widget_render_agreement_evidence.md, docs/api/reference/widget_render_data_agreement.md, docs/api/reference/widget_render_data_steward.md, docs/api/reference/widget_review_guardrail_governance.md, docs/api/reference/widget_select_guardrail_target.md, docs/api/reference/write_data.md, docs/api/reference/write_pipeline_lineage.md, docs/api/reference/write_pipeline_run_summary.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Keep internal</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L86-L138"><code>get_fabric_context</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Tests:</strong> tests/unit/test_config.py<br><strong>Dynamic/text refs:</strong> docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Needs maintainer review</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context</code></a></td>
<td class="flow-cell-module"><code>config</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>widget_select_agreement</code>, <code>read_lakehouse_csv</code>, <code>read_lakehouse_excel</code>, <code>read_lakehouse_parquet</code>, <code>read_lakehouse_table</code>, <code>read_warehouse_table</code>, <code>write_lakehouse_table</code>, <code>write_warehouse_table</code><br><strong>Public callers:</strong> <a href="../../api/reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a href="../../api/reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../api/reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a href="../../api/reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../../api/reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>, <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a><br><strong>Tests:</strong> tests/unit/test_config.py, tests/unit/test_governance_review_migration.py, tests/unit/test_metadata.py, tests/unit/test_pipeline_helpers.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/data_agreement.md, docs/api/modules/fabric_input_output.md, docs/api/modules/governance_review.md, docs/api/modules/pipeline.md, docs/api/reference/get_latest_metadata_catalogue.md, docs/api/reference/read_data.md, docs/api/reference/run_table_guardrails.md, docs/api/reference/setup_metadata_tables.md, docs/api/reference/start_pipeline_run.md, docs/api/reference/widget_author_dq_rules.md, docs/api/reference/widget_author_schema_freshness_profile_rules.md, docs/api/reference/widget_enrich_table_metadata.md, docs/api/reference/widget_render_agreement_evidence.md, docs/api/reference/widget_render_data_agreement.md, docs/api/reference/widget_render_data_steward.md, docs/api/reference/widget_review_guardrail_governance.md, docs/api/reference/widget_select_guardrail_target.md, docs/api/reference/write_data.md, docs/api/reference/write_pipeline_lineage.md, docs/api/reference/write_pipeline_run_summary.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1027-L1043"><code>get_selected_agreement</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a><br><strong>Tests:</strong> tests/unit/test_governance_review_migration.py, tests/unit/test_metadata.py, tests/unit/test_pipeline_helpers.py, tests/unit/test_reference_agent_docs.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/pipeline.md, docs/api/reference/get_latest_metadata_catalogue.md, docs/api/reference/start_pipeline_run.md, docs/notebook-templates-implementation-guide/agreement-setup.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, docs/reference/metadata/metadata_data_agreement.md, docs/reference/metadata/metadata_notebook_registry.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement</code></a></td>
<td class="flow-cell-module"><code>data_agreement</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/start_pipeline_run/"><code>start_pipeline_run</code></a><br><strong>Tests:</strong> tests/unit/test_governance_review_migration.py, tests/unit/test_metadata.py, tests/unit/test_pipeline_helpers.py, tests/unit/test_reference_agent_docs.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/metadata.md, docs/api/modules/pipeline.md, docs/api/reference/get_latest_metadata_catalogue.md, docs/api/reference/start_pipeline_run.md, docs/notebook-templates-implementation-guide/agreement-setup.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md, docs/reference/metadata/metadata_data_agreement.md, docs/reference/metadata/metadata_data_agreement_evidence.md, docs/reference/metadata/metadata_data_steward.md, docs/reference/metadata/metadata_notebook_registry.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L551-L594"><code>read_lakehouse_csv</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/read_data/"><code>read_data</code></a><br><strong>Tests:</strong> tests/integration/test_storage_io.py, tests/templates/test_pipeline_thin_orchestration.py, tests/templates/test_production_flow.py, tests/unit/test_fabric_input_output_routing.py, tests/unit/test_function_catalogue.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/fabric_input_output.md, docs/api/reference/read_data.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L913-L1000"><code>read_lakehouse_excel</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/read_data/"><code>read_data</code></a><br><strong>Tests:</strong> tests/integration/test_storage_io.py, tests/templates/test_pipeline_thin_orchestration.py, tests/templates/test_production_flow.py, tests/unit/test_fabric_input_output_routing.py, tests/unit/test_function_catalogue.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/fabric_input_output.md, docs/api/reference/read_data.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L786-L910"><code>read_lakehouse_parquet</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/read_data/"><code>read_data</code></a><br><strong>Tests:</strong> tests/integration/test_storage_io.py, tests/templates/test_pipeline_thin_orchestration.py, tests/templates/test_production_flow.py, tests/unit/test_fabric_input_output_routing.py, tests/unit/test_function_catalogue.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/fabric_input_output.md, docs/api/reference/read_data.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>_setup_metadata_table_registry</code>, <code>_validate_metadata_table_registration</code>, <code>_list_all_data_agreement_rows</code>, <code>_list_data_stewards</code>, <code>_read_guardrail_rule_metadata</code>, <code>_read_metadata_rows</code>, <code>_read_metadata_table_or_empty</code>, <code>load_catalogue_profile_rows</code>, <code>enforce_profile_behavior</code>, <code>_load_notebook_registry</code><br><strong>Public callers:</strong> <a href="../../api/reference/read_data/"><code>read_data</code></a>, <a href="../../api/reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a><br><strong>Tests:</strong> tests/integration/test_metadata_persistence.py, tests/integration/test_spark_flows.py, tests/integration/test_storage_io.py, tests/templates/test_pipeline_thin_orchestration.py, tests/templates/test_production_flow.py, tests/unit/test_config.py, tests/unit/test_core_transforms.py, tests/unit/test_dq_rules.py, tests/unit/test_fabric_input_output_routing.py, tests/unit/test_function_catalogue.py, tests/unit/test_governance_review_migration.py, tests/unit/test_metadata.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/data_agreement.md, docs/api/modules/fabric_input_output.md, docs/api/modules/governance_review.md, docs/api/modules/guardrails.md, docs/api/modules/metadata.md, docs/api/reference/get_latest_metadata_catalogue.md, docs/api/reference/read_data.md, docs/api/reference/run_table_guardrails.md, docs/api/reference/setup_metadata_tables.md, docs/api/reference/start_pipeline_run.md, docs/api/reference/widget_render_agreement_evidence.md, docs/api/reference/widget_render_data_agreement.md, docs/api/reference/widget_render_data_steward.md, docs/api/reference/widget_select_guardrail_target.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L597-L659"><code>read_warehouse_table</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/read_data/"><code>read_data</code></a><br><strong>Tests:</strong> tests/integration/test_storage_io.py, tests/templates/test_pipeline_thin_orchestration.py, tests/templates/test_production_flow.py, tests/unit/test_fabric_input_output_routing.py, tests/unit/test_function_catalogue.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/fabric_input_output.md, docs/api/reference/read_data.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>_setup_metadata_table_registry</code>, <code>_write_row</code>, <code>_write_rule_records</code>, <code>_write_table_metadata_enrichment_records</code>, <code>record_table_governance</code>, <code>_register_current_notebook</code>, <code>_write_guardrail_result_row</code>, <code>write_catalogue_evidence</code><br><strong>Public callers:</strong> <a href="../../api/reference/write_data/"><code>write_data</code></a>, <a href="../../api/reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../api/reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a><br><strong>Tests:</strong> tests/integration/test_metadata_persistence.py, tests/integration/test_spark_flows.py, tests/integration/test_storage_io.py, tests/templates/test_engineering_flow.py, tests/templates/test_pipeline_thin_orchestration.py, tests/unit/test_config.py, tests/unit/test_core_transforms.py, tests/unit/test_fabric_input_output_routing.py, tests/unit/test_function_catalogue.py, tests/unit/test_governance_review_migration.py, tests/unit/test_guardrail_authoring_model.py, tests/unit/test_metadata.py, tests/unit/test_metadata_writer_ownership.py, tests/unit/test_pipeline_helpers.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/data_agreement.md, docs/api/modules/fabric_input_output.md, docs/api/modules/governance_review.md, docs/api/modules/metadata.md, docs/api/modules/pipeline.md, docs/api/reference/run_table_guardrails.md, docs/api/reference/setup_metadata_tables.md, docs/api/reference/start_pipeline_run.md, docs/api/reference/widget_author_dq_rules.md, docs/api/reference/widget_author_schema_freshness_profile_rules.md, docs/api/reference/widget_enrich_table_metadata.md, docs/api/reference/widget_render_agreement_evidence.md, docs/api/reference/widget_render_data_agreement.md, docs/api/reference/widget_render_data_steward.md, docs/api/reference/write_data.md, docs/api/reference/write_pipeline_lineage.md, docs/api/reference/write_pipeline_run_summary.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L662-L727"><code>write_warehouse_table</code></a></td>
<td class="flow-cell-module"><code>fabric_input_output</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/write_data/"><code>write_data</code></a><br><strong>Tests:</strong> tests/integration/test_storage_io.py, tests/templates/test_pipeline_thin_orchestration.py, tests/unit/test_fabric_input_output_routing.py, tests/unit/test_function_catalogue.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/config.md, docs/api/modules/fabric_input_output.md, docs/api/reference/setup_metadata_tables.md, docs/api/reference/write_data.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1900-L1953"><code>apply_governance_enrichment_action</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a><br><strong>Dynamic/text refs:</strong> docs/api/modules/governance_review.md, docs/api/modules/metadata.md, docs/api/reference/widget_review_guardrail_governance.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1847-L1898"><code>apply_governance_rule_action</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a><br><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_guardrail_authoring_model.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/governance_review.md, docs/api/modules/metadata.md, docs/api/reference/widget_review_guardrail_governance.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L628-L747"><code>build_enrichment_rule_records</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>record_table_governance</code><br><strong>Public callers:</strong> <a href="../../api/reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a><br><strong>Tests:</strong> tests/unit/test_core_transforms.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/governance_review.md, docs/api/modules/metadata.md, docs/api/reference/widget_enrich_table_metadata.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2608-L2662"><code>build_table_governance_policy_record</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>mark_table_governed</code>, <code>mark_table_ungoverned</code><br><strong>Tests:</strong> tests/contract/test_public_contract.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/metadata.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Keep internal</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1808-L1840"><code>guardrail_authoring_status</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>_base_guardrail_rule_record</code>, <code>build_enrichment_rule_records</code><br><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_guardrail_authoring_model.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/governance_review.md, docs/api/reference/widget_author_dq_rules.md, docs/api/reference/widget_author_schema_freshness_profile_rules.md, docs/api/reference/widget_enrich_table_metadata.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Keep internal</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>_evaluate_governance_readiness</code><br><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_core_transforms.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/fabric_input_output.md, docs/api/modules/governance_review.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Keep internal</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1955-L2000"><code>load_rule_review_history</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a><br><strong>Tests:</strong> tests/unit/test_core_transforms.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/governance_review.md, docs/api/reference/widget_review_guardrail_governance.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2665-L2667"><code>mark_table_governed</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_guardrail_authoring_model.py<br><strong>Dynamic/text refs:</strong> docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Needs maintainer review</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2670-L2672"><code>mark_table_ungoverned</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_guardrail_authoring_model.py<br><strong>Dynamic/text refs:</strong> docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Needs maintainer review</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1113-L1224"><code>record_table_governance</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/integration/test_spark_flows.py, tests/unit/test_core_transforms.py, tests/unit/test_guardrail_authoring_model.py, tests/unit/test_metadata_writer_ownership.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/fabric_input_output.md, docs/api/modules/metadata.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Needs maintainer review</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1722-L1760"><code>resolve_table_governance_policy</code></a></td>
<td class="flow-cell-module"><code>governance_review</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a><br><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_guardrail_authoring_model.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/governance_review.md, docs/api/reference/widget_select_guardrail_target.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L572-L670"><code>enforce_freshness</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>enforce_freshness_rule</code><br><strong>Public callers:</strong> <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><br><strong>Tests:</strong> tests/unit/test_guardrail_authoring_model.py, tests/unit/test_pipeline_helpers.py, tests/unit/test_reference_agent_docs.py, tests/unit/test_validation.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/pipeline.md, docs/api/reference/run_table_guardrails.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L113-L131"><code>enforce_freshness_rule</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><br><strong>Tests:</strong> tests/unit/test_guardrail_authoring_model.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/pipeline.md, docs/api/reference/run_table_guardrails.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><br><strong>Tests:</strong> tests/unit/test_guardrail_authoring_model.py, tests/unit/test_metadata_writer_ownership.py, tests/unit/test_pipeline_helpers.py, tests/unit/test_reference_agent_docs.py, tests/unit/test_validation.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/data_profiling.md, docs/api/modules/fabric_input_output.md, docs/api/modules/metadata.md, docs/api/modules/pipeline.md, docs/api/reference/profile_dataframe.md, docs/api/reference/run_table_guardrails.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L921-L941"><code>stop_if_failed</code></a></td>
<td class="flow-cell-module"><code>guardrails</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><br><strong>Tests:</strong> tests/integration/test_spark_flows.py, tests/unit/test_function_catalogue.py, tests/unit/test_pipeline_helpers.py, tests/unit/test_validation.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/pipeline.md, docs/api/reference/display_guardrail_results.md, docs/api/reference/run_table_guardrails.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L445-L474"><code>build_guardrail_detail_rows</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><br><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_generated_docs_links.py, tests/unit/test_guardrail_display_modes.py, tests/unit/test_reference_agent_docs.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/pipeline.md, docs/api/reference/display_guardrail_results.md, docs/api/reference/run_table_guardrails.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L379-L442"><code>build_guardrail_summary_rows</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Internal callers:</strong> <code>_build_guardrail_blocking_message_from_bundle</code><br><strong>Public callers:</strong> <a href="../../api/reference/display_guardrail_results/"><code>display_guardrail_results</code></a>, <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><br><strong>Tests:</strong> tests/contract/test_public_contract.py, tests/unit/test_generated_docs_links.py, tests/unit/test_guardrail_display_modes.py, tests/unit/test_reference_agent_docs.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/pipeline.md, docs/api/reference/display_guardrail_results.md, docs/api/reference/run_table_guardrails.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/_data/refactor-signals.json, docs/reference/callable-flow.md</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
<tr>
<td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a></td>
<td class="flow-cell-module"><code>pipeline</code></td>
<td class="flow-cell-wide">Not reachable from exported public callable entry points in the generated static call graph.</td>
<td class="flow-cell-wide"><strong>Public callers:</strong> <a href="../../api/reference/run_table_guardrails/"><code>run_table_guardrails</code></a><br><strong>Tests:</strong> tests/integration/test_spark_flows.py, tests/unit/test_function_catalogue.py, tests/unit/test_metadata_writer_ownership.py, tests/unit/test_pipeline_helpers.py<br><strong>Docs/scripts:</strong> scripts/generate_function_reference.py, scripts/reference_docs_metadata.py<br><strong>Dynamic/text refs:</strong> docs/api/modules/fabric_input_output.md, docs/api/modules/metadata.md, docs/api/modules/pipeline.md, docs/api/reference/run_table_guardrails.md, docs/api/reference/write_pipeline_lineage.md, docs/api/reference/write_pipeline_run_summary.md, docs/reference/_data/automation-manifest.json, docs/reference/_data/callable-flow.json, docs/reference/_data/callable-surface-audit.json, docs/reference/_data/dependency-metadata.json, docs/reference/_data/function-manifest.json, docs/reference/callable-flow.md, scripts/generate_function_reference.py, scripts/reference_docs_metadata.py</td>
<td class="flow-cell-wide">Add explicit graph edge</td>
</tr>
</tbody>
</table>
</div>
