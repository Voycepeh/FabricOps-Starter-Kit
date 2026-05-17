# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 3 | 3 | 0 | 0 |
</div>

## Module purpose

Owns agreement discovery and selection helpers used to anchor notebook workflows to approved business agreements.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`get_selected_agreement`](../../reference/get_selected_agreement/) | Essential | function | Return selected agreement from widget flow. | — |
| [`load_agreements`](../../reference/load_agreements/) | Essential | function | Load latest distinct agreement metadata rows for widget selection. | [`_coerce_row_dicts`](../../reference/internal/data_agreement/_coerce_row_dicts/) (internal), [`_latest_distinct_agreements`](../../reference/internal/data_agreement/_latest_distinct_agreements/) (internal) |
| [`select_agreement`](../../reference/select_agreement/) | Essential | function | Render a widget dropdown and store selected agreement metadata row in module state. | [`_agreement_option_label`](../../reference/internal/data_agreement/_agreement_option_label/) (internal), [`_coerce_row_dicts`](../../reference/internal/data_agreement/_coerce_row_dicts/) (internal) |
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
| Helper | Related public callables |
|---|---|
| [`_agreement_option_label`](../../reference/internal/data_agreement/_agreement_option_label/) | [`select_agreement`](../../reference/select_agreement/) |
| [`_coerce_row_dicts`](../../reference/internal/data_agreement/_coerce_row_dicts/) | [`load_agreements`](../../reference/load_agreements/), [`select_agreement`](../../reference/select_agreement/) |
| [`_latest_distinct_agreements`](../../reference/internal/data_agreement/_latest_distinct_agreements/) | [`load_agreements`](../../reference/load_agreements/) |
</div>

### Module internal callable dependencies

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["data_agreement.load_agreements"] --> n1b["data_agreement._coerce_row_dicts"]
  n2["data_agreement.load_agreements"] --> n2b["data_agreement._latest_distinct_agreements"]
  n3["data_agreement.select_agreement"] --> n3b["data_agreement._agreement_option_label"]
  n4["data_agreement.select_agreement"] --> n4b["data_agreement._coerce_row_dicts"]
```
</div>

### Cross-module references

No cross-module references detected.
