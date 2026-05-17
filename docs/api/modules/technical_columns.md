# `technical_columns` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns standard output/audit columns for pipeline outputs.

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
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Apply canonical technical/audit enrichment in one notebook-facing wrapper.</td>
      <td><a href="../../reference/internal/technical_columns/_add_audit_columns/"><code>_add_audit_columns</code></a> (internal), <a href="../../reference/internal/technical_columns/_add_datetime_features/"><code>_add_datetime_features</code></a> (internal), <a href="../../reference/internal/technical_columns/_add_hash_columns/"><code>_add_hash_columns</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

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
      <td><a href="../../reference/internal/technical_columns/_add_audit_columns/"><code>_add_audit_columns</code></a></td>
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_add_datetime_features/"><code>_add_datetime_features</code></a></td>
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_add_hash_columns/"><code>_add_hash_columns</code></a></td>
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_assert_columns_exist/"><code>_assert_columns_exist</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_bucket_values_pandas/"><code>_bucket_values_pandas</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_default_technical_columns/"><code>_default_technical_columns</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_get_fabric_runtime_context/"><code>_get_fabric_runtime_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_hash_row/"><code>_hash_row</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_non_technical_columns/"><code>_non_technical_columns</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_safe_string/"><code>_safe_string</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

</details>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["technical_columns._add_audit_columns"] --> n1b["technical_columns._assert_columns_exist"]
  n2["technical_columns._add_audit_columns"] --> n2b["technical_columns._bucket_values_pandas"]
  n3["technical_columns._add_audit_columns"] --> n3b["technical_columns._get_fabric_runtime_context"]
  n4["technical_columns._add_datetime_features"] --> n4b["technical_columns._assert_columns_exist"]
  n5["technical_columns._add_hash_columns"] --> n5b["technical_columns._assert_columns_exist"]
  n6["technical_columns._add_hash_columns"] --> n6b["technical_columns._hash_row"]
  n7["technical_columns._add_hash_columns"] --> n7b["technical_columns._non_technical_columns"]
  n8["technical_columns._bucket_values_pandas"] --> n8b["technical_columns._safe_string"]
  n9["technical_columns._hash_row"] --> n9b["technical_columns._safe_string"]
  n10["technical_columns._non_technical_columns"] --> n10b["technical_columns._default_technical_columns"]
  n11["technical_columns.standardize_columns"] --> n11b["technical_columns._add_audit_columns"]
  n12["technical_columns.standardize_columns"] --> n12b["technical_columns._add_datetime_features"]
  n13["technical_columns.standardize_columns"] --> n13b["technical_columns._add_hash_columns"]
```
</div>

</details>

### Outbound

No outbound references detected.
