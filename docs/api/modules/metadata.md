# `metadata` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 3</span></div>

## Module purpose

Owns metadata/contract store access, evidence persistence, agreement metadata, notebook evidence, and contract assembly inputs.

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
      <td><a href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load notebook registration metadata rows for agreement notebook traceability.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Register current notebook metadata evidence for agreement traceability.</td>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a> (internal), <a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a> (internal), <a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a> (internal)</td>
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
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_extract_columns_from_profile/"><code>_extract_columns_from_profile</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_key_part/"><code>_key_part</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_now_utc_iso/"><code>_now_utc_iso</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_resolve_action_by/"><code>_resolve_action_by</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_sha256_key/"><code>_sha256_key</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["metadata._resolve_action_by"] --> n1b["metadata._context_get"]
  n2["metadata._resolve_action_by"] --> n2b["metadata._runtime_context"]
  n3["metadata._runtime_context"] --> n3b["metadata._context_get"]
  n4["metadata._sha256_key"] --> n4b["metadata._key_part"]
  n5["metadata.build_dq_rule_key"] --> n5b["metadata._sha256_key"]
  n6["metadata.build_evidence_row"] --> n6b["metadata._now_utc_iso"]
  n7["metadata.build_metadata_column_key"] --> n7b["metadata._sha256_key"]
  n8["metadata.build_metadata_table_key"] --> n8b["metadata._sha256_key"]
  n9["metadata.register_current_notebook"] --> n9b["metadata._context_get"]
  n10["metadata.register_current_notebook"] --> n10b["metadata._runtime_context"]
  n11["metadata.register_current_notebook"] --> n11b["metadata._safe_str"]
  n12["metadata.register_current_notebook"] --> n12b["metadata.write_metadata_rows"]
  n13["metadata.write_column_business_context"] --> n13b["metadata.write_metadata_rows"]
  n14["metadata.write_column_governance_context"] --> n14b["metadata.write_metadata_rows"]
  n15["metadata.write_metadata_rows"] --> n15b["metadata.column_context_rows_for_spark"]
```
</div>

</details>

### Outbound

Graph omitted because dependencies are simple one-to-one references.
<div class="module-table-scroll">
| Caller | Callee |
|---|---|
| `metadata.write_metadata_rows` | `fabric_input_output.write_lakehouse_table` |
</div>
