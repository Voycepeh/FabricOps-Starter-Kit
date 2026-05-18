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

### Inside this module, used by, and uses

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart LR
  classDef currentModule fill:#fff3e0,stroke:#ef6c00,stroke-width:3px,color:#3e2723;
  classDef externalModule fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#616161;
  classDef currentCallable fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#90a4ae,stroke-width:1px;
  subgraph m_business_context[business_context]
    fabricops_kit_business_context__extract_column_business_context_suggestions["_extract_column_business_context_suggestions"]
    fabricops_kit_business_context__parse_ai_dict_response["_parse_ai_dict_response"]
    fabricops_kit_business_context__prepare_business_context_profile_input["_prepare_business_context_profile_input"]
    fabricops_kit_business_context__require_ipywidgets["_require_ipywidgets"]
    fabricops_kit_business_context_extract_column_business_context_suggestions["extract_column_business_context_suggestions"]
    fabricops_kit_business_context_prepare_business_context_profile_input["prepare_business_context_profile_input"]
    fabricops_kit_business_context_review_business_context["review_business_context"]
    fabricops_kit_business_context_write_business_context["write_business_context"]
  end
  subgraph m_metadata[metadata]
    fabricops_kit_metadata_build_metadata_column_key["build_metadata_column_key"]
    fabricops_kit_metadata_build_metadata_table_key["build_metadata_table_key"]
    fabricops_kit_metadata_write_column_business_context["write_column_business_context"]
  end
  fabricops_kit_business_context__extract_column_business_context_suggestions --> fabricops_kit_business_context__parse_ai_dict_response
  fabricops_kit_business_context_extract_column_business_context_suggestions --> fabricops_kit_business_context__extract_column_business_context_suggestions
  fabricops_kit_business_context_prepare_business_context_profile_input --> fabricops_kit_business_context__prepare_business_context_profile_input
  fabricops_kit_business_context_review_business_context --> fabricops_kit_business_context__require_ipywidgets
  fabricops_kit_business_context_review_business_context --> fabricops_kit_metadata_build_metadata_column_key
  fabricops_kit_business_context_review_business_context --> fabricops_kit_metadata_build_metadata_table_key
  fabricops_kit_business_context_write_business_context --> fabricops_kit_metadata_write_column_business_context
  class m_business_context currentModule;
  class fabricops_kit_business_context__extract_column_business_context_suggestions,fabricops_kit_business_context__parse_ai_dict_response,fabricops_kit_business_context__prepare_business_context_profile_input,fabricops_kit_business_context__require_ipywidgets,fabricops_kit_business_context_extract_column_business_context_suggestions,fabricops_kit_business_context_prepare_business_context_profile_input,fabricops_kit_business_context_review_business_context,fabricops_kit_business_context_write_business_context currentCallable;
  class fabricops_kit_metadata_build_metadata_column_key,fabricops_kit_metadata_build_metadata_table_key,fabricops_kit_metadata_write_column_business_context externalCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/business_context/#_extract_column_business_context_suggestions"><code>_extract_column_business_context_suggestions</code></a> → <a class="reference-chip" href="../modules/business_context/#_parse_ai_dict_response"><code>_parse_ai_dict_response</code></a>
<a class="reference-chip" href="../../reference/extract_column_business_context_suggestions/"><code>extract_column_business_context_suggestions</code></a> → <a class="reference-chip" href="../modules/business_context/#_extract_column_business_context_suggestions"><code>_extract_column_business_context_suggestions</code></a>
<a class="reference-chip" href="../../reference/prepare_business_context_profile_input/"><code>prepare_business_context_profile_input</code></a> → <a class="reference-chip" href="../modules/business_context/#_prepare_business_context_profile_input"><code>_prepare_business_context_profile_input</code></a>
<a class="reference-chip" href="../../reference/review_business_context/"><code>review_business_context</code></a> → <a class="reference-chip" href="../modules/business_context/#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</div>
#### Used by

None.
#### Uses

<div class="callable-chip-group">
<a class="reference-chip" href="../../reference/review_business_context/"><code>review_business_context</code></a> → <a class="reference-chip" href="../modules/metadata/#build_metadata_column_key"><code>build_metadata_column_key</code></a>
<a class="reference-chip" href="../../reference/review_business_context/"><code>review_business_context</code></a> → <a class="reference-chip" href="../modules/metadata/#build_metadata_table_key"><code>build_metadata_table_key</code></a>
<a class="reference-chip" href="../../reference/write_business_context/"><code>write_business_context</code></a> → <a class="reference-chip" href="../modules/metadata/#write_column_business_context"><code>write_column_business_context</code></a>
</div>
</div>
