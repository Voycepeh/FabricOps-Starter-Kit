# `pipeline` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 5</span><span class="reference-chip">Internal helpers: 11</span><span class="reference-chip">Outbound: 6</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns thin 02_pipeline metadata evidence helpers for catalogue evidence internals, lineage persistence, and runtime summaries.

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
      <td><code>pipeline</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns thin 02_pipeline metadata evidence helpers for catalogue evidence internals, lineage persistence, and runtime summaries.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>11</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>6</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>config</code>, <code>data_profiling</code>, <code>fabric_input_output</code>, <code>governance_review</code>, <code>guardrails</code>, <code>metadata</code></td>
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
      <td><a href="../../reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Prepare source or target table configs for 02_pipeline.</td>
      <td><code>_add_audit_columns</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.</td>
      <td><code>_build_guardrail_evidence_definitions</code> (internal), <code>_guardrail_can_continue</code> (internal), <code>_table_key</code> (internal), <code>_table_name</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Enrich profile rows with guardrail context and write catalogue evidence.</td>
      <td><code>_canonical_catalogue_profile_df</code> (internal), <code>_definition_name</code> (internal), <code>_dq_summary_fields</code> (internal), <code>_now_iso</code> (internal), <code>_runtime_audit_fields</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write many-to-many source-to-target lineage evidence.</td>
      <td><code>_definition_name</code> (internal), <code>_now_iso</code> (internal), <code>_runtime_audit_fields</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write one pipeline runtime summary row to metadata.</td>
      <td><code>_definition_name</code> (internal), <code>_now_iso</code> (internal), <code>_summary_status</code> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>pipeline</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_add_audit_columns</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_build_guardrail_evidence_definitions</code></span>, <span class="reference-chip"><code>_guardrail_can_continue</code></span>, <span class="reference-chip"><code>_table_key</code></span>, <span class="reference-chip"><code>_table_name</code></span>, <a class="reference-chip" href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_catalogue_profile_df</code></span>, <span class="reference-chip"><code>_definition_name</code></span>, <span class="reference-chip"><code>_dq_summary_fields</code></span>, <span class="reference-chip"><code>_now_iso</code></span>, <span class="reference-chip"><code>_runtime_audit_fields</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_definition_name</code></span>, <span class="reference-chip"><code>_now_iso</code></span>, <span class="reference-chip"><code>_runtime_audit_fields</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_definition_name</code></span>, <span class="reference-chip"><code>_now_iso</code></span>, <span class="reference-chip"><code>_summary_status</code></span>
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
      <td><code>_add_audit_columns</code></td>
      <td><a href="../../reference/prepare_pipeline_table_configs/"><code>prepare_pipeline_table_configs</code></a></td>
    </tr>
    <tr>
      <td><code>_build_guardrail_evidence_definitions</code></td>
      <td><a href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
    </tr>
    <tr>
      <td><code>_canonical_catalogue_profile_df</code></td>
      <td><a href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a></td>
    </tr>
    <tr>
      <td><code>_definition_name</code></td>
      <td><a href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a>, <a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_summary_fields</code></td>
      <td><a href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a></td>
    </tr>
    <tr>
      <td><code>_guardrail_can_continue</code></td>
      <td><a href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
    </tr>
    <tr>
      <td><code>_now_iso</code></td>
      <td><a href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a>, <a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
    </tr>
    <tr>
      <td><code>_runtime_audit_fields</code></td>
      <td><a href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a>, <a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
    </tr>
    <tr>
      <td><code>_summary_status</code></td>
      <td><a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
    </tr>
    <tr>
      <td><code>_table_key</code></td>
      <td><a href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
    </tr>
    <tr>
      <td><code>_table_name</code></td>
      <td><a href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_add_audit_columns</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_guardrail_evidence_definitions</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_table_key</code></span>, <span class="reference-chip"><code>_table_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_canonical_catalogue_profile_df</code></span>
</li>
<li>
<span class="reference-chip"><code>_definition_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_summary_fields</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_now_iso</code></span>
</li>
<li>
<span class="reference-chip"><code>_guardrail_can_continue</code></span>
</li>
<li>
<span class="reference-chip"><code>_now_iso</code></span>
</li>
<li>
<span class="reference-chip"><code>_runtime_audit_fields</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_now_iso</code></span>
</li>
<li>
<span class="reference-chip"><code>_summary_status</code></span>
</li>
<li>
<span class="reference-chip"><code>_table_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_table_name</code></span>
</li>
</ul>
</details>

### External callers

None.
### External callees

**config**
<a class="reference-chip" href="../config/#_current_audit_timestamp"><code>_current_audit_timestamp</code></a>, <a class="reference-chip" href="../config/#_get_audit_timezone"><code>_get_audit_timezone</code></a>

**data_profiling**
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**governance_review**
<a class="reference-chip" href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a>

**guardrails**
<a class="reference-chip" href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a>, <a class="reference-chip" href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a>, <a class="reference-chip" href="../../reference/stop_if_failed/"><code>stop_if_failed</code></a>, <a class="reference-chip" href="../../reference/validate_schema/"><code>validate_schema</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>
