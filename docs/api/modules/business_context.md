# `business_context` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Module pages document source modules and internal helpers for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable surface.

The public v1 callable surface is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 8</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns business meaning for tables and columns.

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
      <td><code>business_context</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns business meaning for tables and columns.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>8</td>
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
<h5>business_context</h5>
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
      <td><a href="../../reference/internal/business_context/_draft_business_context/"><code>_draft_business_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_extract_column_business_context_suggestions/"><code>_extract_column_business_context_suggestions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_get_reviewed_business_context_rows/"><code>_get_reviewed_business_context_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_parse_ai_dict_response/"><code>_parse_ai_dict_response</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_prepare_business_context_profile_input/"><code>_prepare_business_context_profile_input</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_require_ipywidgets/"><code>_require_ipywidgets</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_widget_review_business_context/"><code>_widget_review_business_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_write_business_context/"><code>_write_business_context</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_draft_business_context"><code>_draft_business_context</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_column_business_context_suggestions"><code>_extract_column_business_context_suggestions</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_extract_column_business_context_suggestions"><code>_extract_column_business_context_suggestions</code></a>, <a class="reference-chip" href="#_parse_ai_dict_response"><code>_parse_ai_dict_response</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_reviewed_business_context_rows"><code>_get_reviewed_business_context_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_ai_dict_response"><code>_parse_ai_dict_response</code></a>
</li>
<li>
<a class="reference-chip" href="#_prepare_business_context_profile_input"><code>_prepare_business_context_profile_input</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_prepare_business_context_profile_input"><code>_prepare_business_context_profile_input</code></a>
</li>
<li>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_review_business_context"><code>_widget_review_business_context</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_business_context"><code>_write_business_context</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**metadata**
<a class="reference-chip" href="../metadata/#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_write_column_business_context"><code>_write_column_business_context</code></a>
