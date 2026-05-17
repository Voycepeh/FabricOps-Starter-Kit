# `data_lineage` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns source-to-target lineage and transformation evidence.

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
      <td><a href="../../reference/build_lineage_handover_markdown/"><code>build_lineage_handover_markdown</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build a concise markdown handover summary from lineage execution results.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/build_lineage_records/"><code>build_lineage_records</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build compact lineage records for downstream metadata sinks.</td>
      <td>—</td>
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
      <td><a href="../../reference/internal/data_lineage/_build_lineage_record_from_steps/"><code>_build_lineage_record_from_steps</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_build_lineage_records/"><code>_build_lineage_records</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_call_name/"><code>_call_name</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_enrich_lineage_steps_with_ai/"><code>_enrich_lineage_steps_with_ai</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_fallback_copilot_lineage_prompt/"><code>_fallback_copilot_lineage_prompt</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_flatten_chain/"><code>_flatten_chain</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_literal/"><code>_literal</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_name/"><code>_name</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_resolve_write_target/"><code>_resolve_write_target</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_scan_notebook_cells/"><code>_scan_notebook_cells</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_scan_notebook_lineage/"><code>_scan_notebook_lineage</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_step/"><code>_step</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_validate_lineage_steps/"><code>_validate_lineage_steps</code></a></td>
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
  n1["data_lineage._build_lineage_record_from_steps"] --> n1b["data_lineage._validate_lineage_steps"]
  n2["data_lineage._build_lineage_records"] --> n2b["data_lineage._build_lineage_record_from_steps"]
  n3["data_lineage._enrich_lineage_steps_with_ai"] --> n3b["data_lineage._fallback_copilot_lineage_prompt"]
  n4["data_lineage._flatten_chain"] --> n4b["data_lineage._name"]
  n5["data_lineage._resolve_write_target"] --> n5b["data_lineage._literal"]
  n6["data_lineage._scan_notebook_cells"] --> n6b["data_lineage._scan_notebook_lineage"]
  n7["data_lineage._scan_notebook_lineage"] --> n7b["data_lineage._call_name"]
  n8["data_lineage._scan_notebook_lineage"] --> n8b["data_lineage._flatten_chain"]
  n9["data_lineage._scan_notebook_lineage"] --> n9b["data_lineage._name"]
  n10["data_lineage._scan_notebook_lineage"] --> n10b["data_lineage._resolve_write_target"]
  n11["data_lineage._scan_notebook_lineage"] --> n11b["data_lineage._step"]
```
</div>

</details>

### Outbound

No outbound references detected.
