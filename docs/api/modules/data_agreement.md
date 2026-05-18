# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 3</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns agreement discovery and selection helpers used to anchor notebook workflows to approved business agreements.

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
      <td><a href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return selected agreement from widget flow.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load latest distinct agreement metadata rows for widget selection.</td>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal), <a href="../../reference/internal/data_agreement/_latest_distinct_agreements/"><code>_latest_distinct_agreements</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render a widget dropdown and store selected agreement metadata row in module state.</td>
      <td><a href="../../reference/internal/data_agreement/_agreement_option_label/"><code>_agreement_option_label</code></a> (internal), <a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal)</td>
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
      <td><a href="../../reference/internal/data_agreement/_agreement_option_label/"><code>_agreement_option_label</code></a></td>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a>, <a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_distinct_agreements/"><code>_latest_distinct_agreements</code></a></td>
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a></td>
    </tr>
  </tbody>
</table>
</div>

### Callable relationships

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart TB
  classDef currentModule fill:#ffe8cc,stroke:#e65100,stroke-width:4px,color:#3e2723;
  classDef externalModule fill:#f7f7f7,stroke:#b0bec5,stroke-width:1px,color:#607d8b;
  classDef currentCallable fill:#ffd180,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#b0bec5,stroke-width:1px,color:#455a64;
  subgraph m_data_agreement[data_agreement]
    fabricops_kit_data_agreement__agreement_option_label["_agreement_option_label"]
    fabricops_kit_data_agreement__coerce_row_dicts["_coerce_row_dicts"]
    fabricops_kit_data_agreement__latest_distinct_agreements["_latest_distinct_agreements"]
    fabricops_kit_data_agreement_load_agreements["load_agreements"]
    fabricops_kit_data_agreement_select_agreement["select_agreement"]
  end
  fabricops_kit_data_agreement_load_agreements --> fabricops_kit_data_agreement__coerce_row_dicts
  fabricops_kit_data_agreement_load_agreements --> fabricops_kit_data_agreement__latest_distinct_agreements
  fabricops_kit_data_agreement_select_agreement --> fabricops_kit_data_agreement__agreement_option_label
  fabricops_kit_data_agreement_select_agreement --> fabricops_kit_data_agreement__coerce_row_dicts
  linkStyle 0,1,2,3 stroke:#ef6c00,stroke-width:2.2px;
  class m_data_agreement currentModule;
  class fabricops_kit_data_agreement__agreement_option_label,fabricops_kit_data_agreement__coerce_row_dicts,fabricops_kit_data_agreement__latest_distinct_agreements,fabricops_kit_data_agreement_load_agreements,fabricops_kit_data_agreement_select_agreement currentCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a> → <a class="reference-chip" href="../modules/data_agreement/#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
<a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a> → <a class="reference-chip" href="../modules/data_agreement/#_latest_distinct_agreements"><code>_latest_distinct_agreements</code></a>
<a class="reference-chip" href="../../reference/select_agreement/"><code>select_agreement</code></a> → <a class="reference-chip" href="../modules/data_agreement/#_agreement_option_label"><code>_agreement_option_label</code></a>
<a class="reference-chip" href="../../reference/select_agreement/"><code>select_agreement</code></a> → <a class="reference-chip" href="../modules/data_agreement/#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</div>
#### Used by other modules

None.
#### Uses other modules

None.
</div>
