# `data_governance` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Module pages document source modules and internal helpers for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable surface.

The public v1 callable surface is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 11</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence.

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
      <td><code>data_governance</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>0</td>
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
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>metadata</code></td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_governance</h5>
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
      <td><a href="../../reference/internal/data_governance/_approved_widget_rows/"><code>_approved_widget_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_build_governance_context/"><code>_build_governance_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_draft_governance/"><code>_draft_governance</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_extract_governance_suggestions/"><code>_extract_governance_suggestions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_extract_pii_suggestions/"><code>_extract_pii_suggestions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_load_governance/"><code>_load_governance</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_prepare_governance_input/"><code>_prepare_governance_input</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_undo_last_action/"><code>_undo_last_action</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_widget_review_governance/"><code>_widget_review_governance</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_write_governance/"><code>_write_governance</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_approved_widget_rows"><code>_approved_widget_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_governance_context"><code>_build_governance_context</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_draft_governance"><code>_draft_governance</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_governance_suggestions"><code>_extract_governance_suggestions</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_extract_pii_suggestions"><code>_extract_pii_suggestions</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_pii_suggestions"><code>_extract_pii_suggestions</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_governance"><code>_load_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_prepare_governance_input"><code>_prepare_governance_input</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_prepare_governance_input"><code>_prepare_governance_input</code></a>
</li>
<li>
<a class="reference-chip" href="#_undo_last_action"><code>_undo_last_action</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_review_governance"><code>_widget_review_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_undo_last_action"><code>_undo_last_action</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_governance"><code>_write_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_approved_widget_rows"><code>_approved_widget_rows</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**metadata**
<a class="reference-chip" href="../metadata/#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>
