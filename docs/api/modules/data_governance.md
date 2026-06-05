# `data_governance` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 6</span><span class="reference-chip">Internal helpers: 6</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

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
      <td>6</td>
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
      <td><a href="../../reference/draft_governance/"><code>draft_governance</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Run Fabric AI personal-identifier suggestion prompt on prepared governance rows.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_governance/"><code>load_governance</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load approved governance metadata as read-only agreement context.</td>
      <td><a href="../../reference/internal/data_governance/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_governance/"><code>widget_review_governance</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Display governance review widget and capture approve/reject decisions in module state.</td>
      <td><a href="../../reference/internal/data_governance/_undo_last_action/"><code>_undo_last_action</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_governance/"><code>write_governance</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Persist approved governance rows to metadata table.</td>
      <td><a href="../../reference/internal/data_governance/_approved_widget_rows/"><code>_approved_widget_rows</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/extract_governance_suggestions/"><code>extract_governance_suggestions</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Extract review-ready governance suggestions from AI responses.</td>
      <td><a href="../../reference/internal/data_governance/_extract_pii_suggestions/"><code>_extract_pii_suggestions</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/prepare_governance_input/"><code>prepare_governance_input</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Prepare governance prompt input rows from profile evidence and approved context.</td>
      <td><a href="../../reference/internal/data_governance/_prepare_governance_input/"><code>_prepare_governance_input</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_governance</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/draft_governance/"><code>draft_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/extract_governance_suggestions/"><code>extract_governance_suggestions</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_extract_pii_suggestions"><code>_extract_pii_suggestions</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/load_governance/"><code>load_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/prepare_governance_input/"><code>prepare_governance_input</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_prepare_governance_input"><code>_prepare_governance_input</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_governance/"><code>widget_review_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_undo_last_action"><code>_undo_last_action</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/write_governance/"><code>write_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_approved_widget_rows"><code>_approved_widget_rows</code></a>
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
      <td><a href="../../reference/internal/data_governance/_approved_widget_rows/"><code>_approved_widget_rows</code></a></td>
      <td><a href="../../reference/write_governance/"><code>write_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_build_governance_context/"><code>_build_governance_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td><a href="../../reference/load_governance/"><code>load_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_extract_pii_suggestions/"><code>_extract_pii_suggestions</code></a></td>
      <td><a href="../../reference/extract_governance_suggestions/"><code>extract_governance_suggestions</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_prepare_governance_input/"><code>_prepare_governance_input</code></a></td>
      <td><a href="../../reference/prepare_governance_input/"><code>prepare_governance_input</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_governance/_undo_last_action/"><code>_undo_last_action</code></a></td>
      <td><a href="../../reference/widget_review_governance/"><code>widget_review_governance</code></a></td>
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
<a class="reference-chip" href="#_extract_pii_suggestions"><code>_extract_pii_suggestions</code></a>
</li>
<li>
<a class="reference-chip" href="#_prepare_governance_input"><code>_prepare_governance_input</code></a>
</li>
<li>
<a class="reference-chip" href="#_undo_last_action"><code>_undo_last_action</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**metadata**
<a class="reference-chip" href="../metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>, <a class="reference-chip" href="../metadata/#build_metadata_column_key"><code>build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#build_metadata_table_key"><code>build_metadata_table_key</code></a>
