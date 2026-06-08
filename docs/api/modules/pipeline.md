# `pipeline` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 6</span><span class="reference-chip">Outbound: 2</span><span class="reference-chip">Inbound: 0</span></div>

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
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>6</td>
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
      <td><a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write many-to-many source-to-target lineage evidence.</td>
      <td><a href="../../reference/internal/pipeline/_definition_name/"><code>_definition_name</code></a> (internal), <a href="../../reference/internal/pipeline/_now_iso/"><code>_now_iso</code></a> (internal), <a href="../../reference/internal/pipeline/_runtime_audit_fields/"><code>_runtime_audit_fields</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Write one pipeline runtime summary row to metadata.</td>
      <td><a href="../../reference/internal/pipeline/_definition_name/"><code>_definition_name</code></a> (internal), <a href="../../reference/internal/pipeline/_now_iso/"><code>_now_iso</code></a> (internal), <a href="../../reference/internal/pipeline/_summary_status/"><code>_summary_status</code></a> (internal)</td>
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
<a class="reference-chip" href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_definition_name"><code>_definition_name</code></a>, <a class="reference-chip" href="#_now_iso"><code>_now_iso</code></a>, <a class="reference-chip" href="#_runtime_audit_fields"><code>_runtime_audit_fields</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_definition_name"><code>_definition_name</code></a>, <a class="reference-chip" href="#_now_iso"><code>_now_iso</code></a>, <a class="reference-chip" href="#_summary_status"><code>_summary_status</code></a>
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
      <td><a href="../../reference/internal/pipeline/_definition_name/"><code>_definition_name</code></a></td>
      <td><a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/pipeline/_dq_summary_fields/"><code>_dq_summary_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/pipeline/_now_iso/"><code>_now_iso</code></a></td>
      <td><a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/pipeline/_runtime_audit_fields/"><code>_runtime_audit_fields</code></a></td>
      <td><a href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/pipeline/_summary_status/"><code>_summary_status</code></a></td>
      <td><a href="../../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/pipeline/_write_catalogue_evidence/"><code>_write_catalogue_evidence</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_definition_name"><code>_definition_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_summary_fields"><code>_dq_summary_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_now_iso"><code>_now_iso</code></a>
</li>
<li>
<a class="reference-chip" href="#_now_iso"><code>_now_iso</code></a>
</li>
<li>
<a class="reference-chip" href="#_runtime_audit_fields"><code>_runtime_audit_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_now_iso"><code>_now_iso</code></a>
</li>
<li>
<a class="reference-chip" href="#_summary_status"><code>_summary_status</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_catalogue_evidence"><code>_write_catalogue_evidence</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_definition_name"><code>_definition_name</code></a>, <a class="reference-chip" href="#_dq_summary_fields"><code>_dq_summary_fields</code></a>, <a class="reference-chip" href="#_runtime_audit_fields"><code>_runtime_audit_fields</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>
