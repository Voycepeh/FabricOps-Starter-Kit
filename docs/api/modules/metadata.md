# `metadata` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 3</span></div>

## Module purpose

Owns metadata/contract store access, evidence persistence, agreement metadata, notebook evidence, and contract assembly inputs.

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
      <td><a href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load notebook registration metadata rows for agreement notebook traceability.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Register current notebook metadata evidence for agreement traceability.</td>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a> (internal), <a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a> (internal), <a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

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
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_extract_columns_from_profile/"><code>_extract_columns_from_profile</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_key_part/"><code>_key_part</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_now_utc_iso/"><code>_now_utc_iso</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_resolve_action_by/"><code>_resolve_action_by</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_sha256_key/"><code>_sha256_key</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

### Callable relationships

<p><a href="../../reference/call-graph/?module=fabricops_kit.metadata" class="md-button md-button--primary">Open interactive module graph</a></p>

#### Inside this module

<section class="callable-relationship-card">
<h5>metadata</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/metadata/#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="../modules/metadata/#_runtime_context"><code>_runtime_context</code></a>, <a class="reference-chip" href="../modules/metadata/#_safe_str"><code>_safe_str</code></a>, <a class="reference-chip" href="../modules/metadata/#write_metadata_rows"><code>write_metadata_rows</code></a>
</li>
</ul>
<h6>Internal helpers</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../modules/metadata/#_context_get"><code>_context_get</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/metadata/#_extract_columns_from_profile"><code>_extract_columns_from_profile</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/metadata/#_key_part"><code>_key_part</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/metadata/#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="../modules/metadata/#_runtime_context"><code>_runtime_context</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/metadata/#_runtime_context"><code>_runtime_context</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/metadata/#_context_get"><code>_context_get</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/metadata/#_safe_str"><code>_safe_str</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/metadata/#_sha256_key"><code>_sha256_key</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/metadata/#_key_part"><code>_key_part</code></a>
</li>
</ul>
</section>

#### External callers

**business_context**
<a class="reference-chip" href="../../reference/review_business_context/"><code>review_business_context</code></a>, <a class="reference-chip" href="../../reference/write_business_context/"><code>write_business_context</code></a>

**data_governance**
<a class="reference-chip" href="../modules/data_governance/#_approved_widget_rows"><code>_approved_widget_rows</code></a>, <a class="reference-chip" href="../../reference/review_governance/"><code>review_governance</code></a>

**data_quality**
<a class="reference-chip" href="../modules/data_quality/#_attach_rule_metadata_keys"><code>_attach_rule_metadata_keys</code></a>, <a class="reference-chip" href="../modules/data_quality/#_build_dq_rule_deactivation_metadata_df"><code>_build_dq_rule_deactivation_metadata_df</code></a>, <a class="reference-chip" href="../modules/data_quality/#_build_dq_rule_deactivations"><code>_build_dq_rule_deactivations</code></a>, <a class="reference-chip" href="../modules/data_quality/#_build_dq_rule_history"><code>_build_dq_rule_history</code></a>, <a class="reference-chip" href="../modules/data_quality/#_build_dq_rules_metadata_df"><code>_build_dq_rules_metadata_df</code></a>

#### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

