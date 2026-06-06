# `governance_review` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 16</span><span class="reference-chip">Internal helpers: 5</span><span class="reference-chip">Outbound: 2</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns table-scoped 04_gov catalogue selection, explicit approval record builders, and metadata commit helpers.

## Module manifest

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Module name</td>
      <td><code>governance_review</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns table-scoped 04_gov catalogue selection, explicit approval record builders, and metadata commit helpers.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>16</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>fabric_input_output</code>, <code>metadata</code></td>
    </tr>
  </tbody>
</table>

## Public callables

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Callable</th>
      <th>Tier</th>
      <th>Type</th>
      <th>Summary</th>
      <th>Related helpers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/build_classification_records/"><code>build_classification_records</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build append-only approved METADATA_COLUMN_CLASSIFICATION records.</td>
      <td><a href="../../reference/internal/governance_review/_audit/"><code>_audit</code></a> (internal), <a href="../../reference/internal/governance_review/_json/"><code>_json</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/build_column_context_records/"><code>build_column_context_records</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build append-only approved METADATA_COLUMN_CONTEXT records from explicit human commits.</td>
      <td><a href="../../reference/internal/governance_review/_audit/"><code>_audit</code></a> (internal), <a href="../../reference/internal/governance_review/_json/"><code>_json</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/build_dq_rule_records/"><code>build_dq_rule_records</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build append-only approved METADATA_DQ_RULES records without enforcement.</td>
      <td><a href="../../reference/internal/governance_review/_audit/"><code>_audit</code></a> (internal), <a href="../../reference/internal/governance_review/_json/"><code>_json</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/build_profile_summary/"><code>build_profile_summary</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Summarize the selected catalogue profile before governance review.</td>
      <td><a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/catalogue_table_options/"><code>catalogue_table_options</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build one selectable option per logical table using the latest successful profile run.</td>
      <td><a href="../../reference/internal/governance_review/_is_success/"><code>_is_success</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/commit_column_classification/"><code>commit_column_classification</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Persist approved sensitivity and PII classification records after explicit human commit.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/commit_column_context/"><code>commit_column_context</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Persist approved business context records after an explicit human commit.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/commit_dq_rules/"><code>commit_dq_rules</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Persist approved DQ rule records after an explicit human commit.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_governance_metadata_schemas/"><code>get_governance_metadata_schemas</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return required governance metadata schemas prepared by 00_env_config.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return stable table identity selected by widget_select_catalogue_table.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/latest_by_column/"><code>latest_by_column</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load latest approved metadata state by stable column key.</td>
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load selected column profile rows from METADATA_DATA_CATALOGUE.</td>
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a> (internal), <a href="../../reference/internal/governance_review/_is_success/"><code>_is_success</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/setup_governance_metadata_tables/"><code>setup_governance_metadata_tables</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Create or validate catalogue, lineage, context, rule, and classification tables during 00_env_config.</td>
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_table_governance/"><code>widget_review_table_governance</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render non-persistent human review guidance for business context, DQ rules, and classification.</td>
      <td><a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render a searchable latest-successful-profile selector backed by METADATA_DATA_CATALOGUE.</td>
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/optional_ai_generate_response/"><code>optional_ai_generate_response</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Run Fabric AI suggestions when available and return None when unavailable.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>governance_review</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/build_classification_records/"><code>build_classification_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/build_column_context_records/"><code>build_column_context_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/build_dq_rule_records/"><code>build_dq_rule_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/build_profile_summary/"><code>build_profile_summary</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/catalogue_table_options/"><code>catalogue_table_options</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_is_success"><code>_is_success</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/commit_column_classification/"><code>commit_column_classification</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/commit_column_context/"><code>commit_column_context</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/commit_dq_rules/"><code>commit_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_governance_metadata_schemas/"><code>get_governance_metadata_schemas</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/latest_by_column/"><code>latest_by_column</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_is_success"><code>_is_success</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/optional_ai_generate_response/"><code>optional_ai_generate_response</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/setup_governance_metadata_tables/"><code>setup_governance_metadata_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="../../reference/get_governance_metadata_schemas/"><code>get_governance_metadata_schemas</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_table_governance/"><code>widget_review_table_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="../../reference/catalogue_table_options/"><code>catalogue_table_options</code></a>
</li>
</ul>
</section>

### Related internal helpers

<details>
<summary>Show internal helpers</summary>

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Related public callables</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/internal/governance_review/_audit/"><code>_audit</code></a></td>
      <td><a href="../../reference/build_classification_records/"><code>build_classification_records</code></a>, <a href="../../reference/build_column_context_records/"><code>build_column_context_records</code></a>, <a href="../../reference/build_dq_rule_records/"><code>build_dq_rule_records</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a></td>
      <td><a href="../../reference/latest_by_column/"><code>latest_by_column</code></a>, <a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>, <a href="../../reference/setup_governance_metadata_tables/"><code>setup_governance_metadata_tables</code></a>, <a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_is_success/"><code>_is_success</code></a></td>
      <td><a href="../../reference/catalogue_table_options/"><code>catalogue_table_options</code></a>, <a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_json/"><code>_json</code></a></td>
      <td><a href="../../reference/build_classification_records/"><code>build_classification_records</code></a>, <a href="../../reference/build_column_context_records/"><code>build_column_context_records</code></a>, <a href="../../reference/build_dq_rule_records/"><code>build_dq_rule_records</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_value/"><code>_value</code></a></td>
      <td><a href="../../reference/build_classification_records/"><code>build_classification_records</code></a>, <a href="../../reference/build_column_context_records/"><code>build_column_context_records</code></a>, <a href="../../reference/build_dq_rule_records/"><code>build_dq_rule_records</code></a>, <a href="../../reference/build_profile_summary/"><code>build_profile_summary</code></a>, <a href="../../reference/catalogue_table_options/"><code>catalogue_table_options</code></a>, <a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>, <a href="../../reference/widget_review_table_governance/"><code>widget_review_table_governance</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_success"><code>_is_success</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_json"><code>_json</code></a>
</li>
<li>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>, <a class="reference-chip" href="../metadata/#build_dq_rule_key"><code>build_dq_rule_key</code></a>, <a class="reference-chip" href="../metadata/#build_metadata_column_key"><code>build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#build_metadata_table_key"><code>build_metadata_table_key</code></a>, <a class="reference-chip" href="../../reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a>
