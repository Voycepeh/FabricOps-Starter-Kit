# `data_quality` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Module pages document source modules and internal helpers for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable surface.

The public v1 callable surface is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 29</span><span class="reference-chip">Outbound: 3</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns DQ rule drafting, review, enforcement, quarantine, and quality results.

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
      <td><code>data_quality</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns DQ rule drafting, review, enforcement, quarantine, and quality results.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>29</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>data_profiling</code>, <code>fabric_input_output</code>, <code>metadata</code></td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_quality</h5>
<h6>Public callables</h6>
<p>None.</p>
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
      <td><a href="../../reference/internal/data_quality/_approved_dq_rules_from_review_rows/"><code>_approved_dq_rules_from_review_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_assert_dq_passed/"><code>_assert_dq_passed</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_attach_rule_metadata_keys/"><code>_attach_rule_metadata_keys</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rule_deactivation_metadata_df/"><code>_build_dq_rule_deactivation_metadata_df</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rule_deactivations/"><code>_build_dq_rule_deactivations</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rule_history/"><code>_build_dq_rule_history</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_build_dq_rules_metadata_df/"><code>_build_dq_rules_metadata_df</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_draft_dq_rules/"><code>_draft_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_enforce_dq/"><code>_enforce_dq</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_extract_candidate_rules_from_responses/"><code>_extract_candidate_rules_from_responses</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_extract_dq_rules/"><code>_extract_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_get_dq_review_results/"><code>_get_dq_review_results</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_latest_dq_rule_versions/"><code>_latest_dq_rule_versions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_load_active_dq_rule_metadata/"><code>_load_active_dq_rule_metadata</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_load_active_dq_rules/"><code>_load_active_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_load_dq_rules/"><code>_load_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_parse_dq_rules_dict_from_text/"><code>_parse_dq_rules_dict_from_text</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_prepare_dq_profile_input_rows/"><code>_prepare_dq_profile_input_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_prepare_dq_profile_rows_with_context/"><code>_prepare_dq_profile_rows_with_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_profile_for_dq/"><code>_profile_for_dq</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_require_ipywidgets/"><code>_require_ipywidgets</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_run_dq_rules/"><code>_run_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_split_dq_rows/"><code>_split_dq_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_suggest_dq_rules/"><code>_suggest_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_suggest_dq_rules_with_fabric_ai/"><code>_suggest_dq_rules_with_fabric_ai</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_validate_dq_rules/"><code>_validate_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_widget_review_dq_rule_deactivations/"><code>_widget_review_dq_rule_deactivations</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_widget_review_dq_rules/"><code>_widget_review_dq_rules</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_quality/_write_dq_rules/"><code>_write_dq_rules</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_approved_dq_rules_from_review_rows"><code>_approved_dq_rules_from_review_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_assert_dq_passed"><code>_assert_dq_passed</code></a>
</li>
<li>
<a class="reference-chip" href="#_attach_rule_metadata_keys"><code>_attach_rule_metadata_keys</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_dq_rule_deactivation_metadata_df"><code>_build_dq_rule_deactivation_metadata_df</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_dq_rule_deactivations"><code>_build_dq_rule_deactivations</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_dq_rule_history"><code>_build_dq_rule_history</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_dq_rules_metadata_df"><code>_build_dq_rules_metadata_df</code></a>
</li>
<li>
<a class="reference-chip" href="#_draft_dq_rules"><code>_draft_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_extract_dq_rules"><code>_extract_dq_rules</code></a>, <a class="reference-chip" href="#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>, <a class="reference-chip" href="#_suggest_dq_rules"><code>_suggest_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_enforce_dq"><code>_enforce_dq</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_load_active_dq_rules"><code>_load_active_dq_rules</code></a>, <a class="reference-chip" href="#_run_dq_rules"><code>_run_dq_rules</code></a>, <a class="reference-chip" href="#_split_dq_rows"><code>_split_dq_rows</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_candidate_rules_from_responses"><code>_extract_candidate_rules_from_responses</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_extract_dq_rules"><code>_extract_dq_rules</code></a>, <a class="reference-chip" href="#_parse_dq_rules_dict_from_text"><code>_parse_dq_rules_dict_from_text</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_dq_rules"><code>_extract_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_parse_dq_rules_dict_from_text"><code>_parse_dq_rules_dict_from_text</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_dq_review_results"><code>_get_dq_review_results</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_attach_rule_metadata_keys"><code>_attach_rule_metadata_keys</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_dq_rule_versions"><code>_latest_dq_rule_versions</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_active_dq_rule_metadata"><code>_load_active_dq_rule_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_dq_rule_versions"><code>_latest_dq_rule_versions</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_active_dq_rules"><code>_load_active_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_dq_rule_versions"><code>_latest_dq_rule_versions</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_dq_rules"><code>_load_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_load_active_dq_rules"><code>_load_active_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_dq_rules_dict_from_text"><code>_parse_dq_rules_dict_from_text</code></a>
</li>
<li>
<a class="reference-chip" href="#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_prepare_dq_profile_rows_with_context"><code>_prepare_dq_profile_rows_with_context</code></a>
</li>
<li>
<a class="reference-chip" href="#_profile_for_dq"><code>_profile_for_dq</code></a>
</li>
<li>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_run_dq_rules"><code>_run_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_split_dq_rows"><code>_split_dq_rows</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_split_dq_rows"><code>_split_dq_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_suggest_dq_rules"><code>_suggest_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_suggest_dq_rules_with_fabric_ai"><code>_suggest_dq_rules_with_fabric_ai</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_review_dq_rule_deactivations"><code>_widget_review_dq_rule_deactivations</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_review_dq_rules"><code>_widget_review_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_dq_rules"><code>_write_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_dq_rule_history"><code>_build_dq_rule_history</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**data_profiling**
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_build_dq_rule_key"><code>_build_dq_rule_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>
