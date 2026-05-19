# `business_context` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 6</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns business meaning for tables and columns.

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
      <td><a href="../../reference/draft_business_context/"><code>draft_business_context</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Run Fabric AI to draft column business context suggestions.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/review_business_context/"><code>review_business_context</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Display interactive approval widget.</td>
      <td><a href="../../reference/internal/business_context/_require_ipywidgets/"><code>_require_ipywidgets</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/write_business_context/"><code>write_business_context</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Persist approved business context rows via metadata writer.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/extract_column_business_context_suggestions/"><code>extract_column_business_context_suggestions</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Extract review-ready business context suggestion rows from AI responses.</td>
      <td><a href="../../reference/internal/business_context/_extract_column_business_context_suggestions/"><code>_extract_column_business_context_suggestions</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_reviewed_business_context_rows/"><code>get_reviewed_business_context_rows</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Return reviewed business context rows from widget state.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/prepare_business_context_profile_input/"><code>prepare_business_context_profile_input</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Prepare profile rows for business context prompt drafting.</td>
      <td><a href="../../reference/internal/business_context/_prepare_business_context_profile_input/"><code>_prepare_business_context_profile_input</code></a> (internal)</td>
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
      <td><a href="../../reference/internal/business_context/_extract_column_business_context_suggestions/"><code>_extract_column_business_context_suggestions</code></a></td>
      <td><a href="../../reference/extract_column_business_context_suggestions/"><code>extract_column_business_context_suggestions</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_parse_ai_dict_response/"><code>_parse_ai_dict_response</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_prepare_business_context_profile_input/"><code>_prepare_business_context_profile_input</code></a></td>
      <td><a href="../../reference/prepare_business_context_profile_input/"><code>prepare_business_context_profile_input</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/business_context/_require_ipywidgets/"><code>_require_ipywidgets</code></a></td>
      <td><a href="../../reference/review_business_context/"><code>review_business_context</code></a></td>
    </tr>
  </tbody>
</table>
</div>

### Callable relationships

<div class="module-relationship-list">
#### Module relationships
#### Functions in this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/business_context/#_extract_column_business_context_suggestions"><code>_extract_column_business_context_suggestions</code></a> → <a class="reference-chip" href="../modules/business_context/#_parse_ai_dict_response"><code>_parse_ai_dict_response</code></a>
<a class="reference-chip" href="../../reference/extract_column_business_context_suggestions/"><code>extract_column_business_context_suggestions</code></a> → <a class="reference-chip" href="../modules/business_context/#_extract_column_business_context_suggestions"><code>_extract_column_business_context_suggestions</code></a>
<a class="reference-chip" href="../../reference/prepare_business_context_profile_input/"><code>prepare_business_context_profile_input</code></a> → <a class="reference-chip" href="../modules/business_context/#_prepare_business_context_profile_input"><code>_prepare_business_context_profile_input</code></a>
<a class="reference-chip" href="../../reference/review_business_context/"><code>review_business_context</code></a> → <a class="reference-chip" href="../modules/business_context/#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</div>
#### External callers

None.
#### External callees

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/metadata/#build_metadata_column_key"><code>metadata.build_metadata_column_key</code></a>
<a class="reference-chip" href="../modules/metadata/#build_metadata_table_key"><code>metadata.build_metadata_table_key</code></a>
<a class="reference-chip" href="../modules/metadata/#write_column_business_context"><code>metadata.write_column_business_context</code></a>
</div>
</div>
