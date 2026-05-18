# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and samples.

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
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build canonical DQ-ready profiling rows from a Spark DataFrame.</td>
      <td><a href="../../reference/internal/data_profiling/_get_profiled_columns/"><code>_get_profiled_columns</code></a> (internal), <a href="../../reference/internal/data_profiling/_is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a> (internal)</td>
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
      <td><a href="../../reference/internal/data_profiling/_get_profiled_columns/"><code>_get_profiled_columns</code></a></td>
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a></td>
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
  </tbody>
</table>
</div>

### Callable relationships

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart LR
  classDef currentModule fill:#fff3e0,stroke:#ef6c00,stroke-width:3px,color:#3e2723;
  classDef externalModule fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,color:#616161;
  classDef currentCallable fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#90a4ae,stroke-width:1px;
  subgraph m_data_profiling[data_profiling]
    fabricops_kit_data_profiling__get_profiled_columns["_get_profiled_columns"]
    fabricops_kit_data_profiling__is_min_max_supported_type["_is_min_max_supported_type"]
    fabricops_kit_data_profiling_profile_dataframe["profile_dataframe"]
  end
  subgraph m_data_quality[data_quality]
    fabricops_kit_data_quality__prepare_dq_profile_input_rows["_prepare_dq_profile_input_rows"]
  end
  subgraph m_technical_columns[technical_columns]
    fabricops_kit_technical_columns__default_technical_columns["_default_technical_columns"]
  end
  fabricops_kit_data_profiling__get_profiled_columns --> fabricops_kit_technical_columns__default_technical_columns
  fabricops_kit_data_profiling_profile_dataframe --> fabricops_kit_data_profiling__get_profiled_columns
  fabricops_kit_data_profiling_profile_dataframe --> fabricops_kit_data_profiling__is_min_max_supported_type
  fabricops_kit_data_quality__prepare_dq_profile_input_rows --> fabricops_kit_data_profiling_profile_dataframe
  class m_data_profiling currentModule;
  class m_data_quality,m_technical_columns externalModule;
  class fabricops_kit_data_profiling__get_profiled_columns,fabricops_kit_data_profiling__is_min_max_supported_type,fabricops_kit_data_profiling_profile_dataframe currentCallable;
  class fabricops_kit_data_quality__prepare_dq_profile_input_rows,fabricops_kit_technical_columns__default_technical_columns externalCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a> → <a class="reference-chip" href="../modules/data_profiling/#_get_profiled_columns"><code>_get_profiled_columns</code></a>
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a> → <a class="reference-chip" href="../modules/data_profiling/#_is_min_max_supported_type"><code>_is_min_max_supported_type</code></a>
</div>
#### Used by other modules

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/data_quality/#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a> → <a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>
</div>
#### Uses other modules

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/data_profiling/#_get_profiled_columns"><code>_get_profiled_columns</code></a> → <a class="reference-chip" href="../modules/technical_columns/#_default_technical_columns"><code>_default_technical_columns</code></a>
</div>
</div>
