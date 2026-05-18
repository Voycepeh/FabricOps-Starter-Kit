# `data_governance` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 6</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns sensitivity, PII, confidentiality, policy labels, and governance approval evidence.

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
      <td><a href="../../reference/review_governance/"><code>review_governance</code></a></td>
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
      <td><a href="../../reference/review_governance/"><code>review_governance</code></a></td>
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
  subgraph m_data_governance[data_governance]
    fabricops_kit_data_governance__approved_widget_rows["_approved_widget_rows"]
    fabricops_kit_data_governance__coerce_row_dicts["_coerce_row_dicts"]
    fabricops_kit_data_governance__extract_pii_suggestions["_extract_pii_suggestions"]
    fabricops_kit_data_governance__prepare_governance_input["_prepare_governance_input"]
    fabricops_kit_data_governance__undo_last_action["_undo_last_action"]
    fabricops_kit_data_governance_extract_governance_suggestions["extract_governance_suggestions"]
    fabricops_kit_data_governance_load_governance["load_governance"]
    fabricops_kit_data_governance_prepare_governance_input["prepare_governance_input"]
    fabricops_kit_data_governance_review_governance["review_governance"]
    fabricops_kit_data_governance_write_governance["write_governance"]
  end
  subgraph m_metadata[metadata]
    fabricops_kit_metadata__now_utc_iso["_now_utc_iso"]
    fabricops_kit_metadata__resolve_action_by["_resolve_action_by"]
    fabricops_kit_metadata_build_metadata_column_key["build_metadata_column_key"]
    fabricops_kit_metadata_build_metadata_table_key["build_metadata_table_key"]
  end
  fabricops_kit_data_governance__approved_widget_rows --> fabricops_kit_metadata__resolve_action_by
  fabricops_kit_data_governance_extract_governance_suggestions --> fabricops_kit_data_governance__extract_pii_suggestions
  fabricops_kit_data_governance_load_governance --> fabricops_kit_data_governance__coerce_row_dicts
  fabricops_kit_data_governance_prepare_governance_input --> fabricops_kit_data_governance__prepare_governance_input
  fabricops_kit_data_governance_review_governance --> fabricops_kit_data_governance__undo_last_action
  fabricops_kit_data_governance_review_governance --> fabricops_kit_metadata__now_utc_iso
  fabricops_kit_data_governance_review_governance --> fabricops_kit_metadata_build_metadata_column_key
  fabricops_kit_data_governance_review_governance --> fabricops_kit_metadata_build_metadata_table_key
  fabricops_kit_data_governance_write_governance --> fabricops_kit_data_governance__approved_widget_rows
  class m_data_governance currentModule;
  class fabricops_kit_data_governance__approved_widget_rows,fabricops_kit_data_governance__coerce_row_dicts,fabricops_kit_data_governance__extract_pii_suggestions,fabricops_kit_data_governance__prepare_governance_input,fabricops_kit_data_governance__undo_last_action,fabricops_kit_data_governance_extract_governance_suggestions,fabricops_kit_data_governance_load_governance,fabricops_kit_data_governance_prepare_governance_input,fabricops_kit_data_governance_review_governance,fabricops_kit_data_governance_write_governance currentCallable;
  class fabricops_kit_metadata__now_utc_iso,fabricops_kit_metadata__resolve_action_by,fabricops_kit_metadata_build_metadata_column_key,fabricops_kit_metadata_build_metadata_table_key externalCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../../reference/extract_governance_suggestions/"><code>extract_governance_suggestions</code></a> → <a class="reference-chip" href="../modules/data_governance/#_extract_pii_suggestions"><code>_extract_pii_suggestions</code></a>
<a class="reference-chip" href="../../reference/load_governance/"><code>load_governance</code></a> → <a class="reference-chip" href="../modules/data_governance/#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
<a class="reference-chip" href="../../reference/prepare_governance_input/"><code>prepare_governance_input</code></a> → <a class="reference-chip" href="../modules/data_governance/#_prepare_governance_input"><code>_prepare_governance_input</code></a>
<a class="reference-chip" href="../../reference/review_governance/"><code>review_governance</code></a> → <a class="reference-chip" href="../modules/data_governance/#_undo_last_action"><code>_undo_last_action</code></a>
<a class="reference-chip" href="../../reference/write_governance/"><code>write_governance</code></a> → <a class="reference-chip" href="../modules/data_governance/#_approved_widget_rows"><code>_approved_widget_rows</code></a>
</div>
#### Used by

None.
#### Uses

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/data_governance/#_approved_widget_rows"><code>_approved_widget_rows</code></a> → <a class="reference-chip" href="../modules/metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>
<a class="reference-chip" href="../../reference/review_governance/"><code>review_governance</code></a> → <a class="reference-chip" href="../modules/metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>
<a class="reference-chip" href="../../reference/review_governance/"><code>review_governance</code></a> → <a class="reference-chip" href="../modules/metadata/#build_metadata_column_key"><code>build_metadata_column_key</code></a>
<a class="reference-chip" href="../../reference/review_governance/"><code>review_governance</code></a> → <a class="reference-chip" href="../modules/metadata/#build_metadata_table_key"><code>build_metadata_table_key</code></a>
</div>
</div>
