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

### Module internal callable dependencies

Graph omitted because dependencies are simple one-to-one references.
<div class="module-table-scroll">
| Caller | Callee |
|---|---|
| `data_governance.extract_governance_suggestions` | `data_governance._extract_pii_suggestions` |
| `data_governance.load_governance` | `data_governance._coerce_row_dicts` |
| `data_governance.prepare_governance_input` | `data_governance._prepare_governance_input` |
| `data_governance.review_governance` | `data_governance._undo_last_action` |
| `data_governance.write_governance` | `data_governance._approved_widget_rows` |
</div>

### Outbound

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  c1["data_governance._approved_widget_rows"] --> d1["metadata._resolve_action_by"]
  c2["data_governance.review_governance"] --> d2["metadata._now_utc_iso"]
  c3["data_governance.review_governance"] --> d3["metadata.build_metadata_column_key"]
  c4["data_governance.review_governance"] --> d4["metadata.build_metadata_table_key"]
```
</div>
