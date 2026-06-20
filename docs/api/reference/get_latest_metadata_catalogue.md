# get_latest_metadata_catalogue

Fetch the latest metadata catalogue rows for a table without writing metadata.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:96`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in 99_explore for discovery, profiling, troubleshooting, or investigation when existing catalogue context may help.

### Do not use when

- Do not use as an enforcement, approval, or metadata persistence step; it is read-only exploration support.

### Additional context

Fetches existing METADATA_DATA_CATALOGUE evidence for a selected table and agreement context so 99_explore can stay context-aware and read-only.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def get_latest_metadata_catalogue(
    table_name: str,
    agreement: Mapping[str, Any] | None=None,
    metadata_schema: str | None=None,
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
latest_catalogue = get_latest_metadata_catalogue(table_name=source_table_name, agreement=AGREEMENT, metadata_schema=METADATA_SCHEMA, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Source table name to look up in ``METADATA_DATA_CATALOGUE``. |
| `agreement` | `Mapping[str, Any] \| None` | No | Selected agreement context from :func:`get_selected_agreement`. When an agreement id or contract version is present, matching catalogue rows are preferred. |
| `metadata_schema` | `str \| None` | No | Explicit metadata Lakehouse schema from ``00_env_config``. When omitted, the configured metadata schema is resolved from the active context. |
| `spark_session` | `Any` | No | Spark session used to read metadata and return display-friendly rows. |
| `context` | `dict[str, Any] \| None` | No | Advanced FabricOps context override. Defaults to the active ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |

## Returns

Latest matching catalogue rows as a Spark DataFrame when possible, otherwise a list of dictionaries. Missing catalogue evidence returns a friendly not_found row.

### Return interpretation

Rows describe the latest available catalogue profile for the requested table, or a friendly not_found message when none exists.

## Raises / Errors

Not documented yet

### Common failure causes

- The metadata catalogue table does not exist yet.
- No profile has been written for the selected table.
- The metadata lakehouse cannot be read.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- `fabricops_kit.fabric_input_output.read_lakehouse_table`
- `fabricops_kit.governance_review._catalogue_lookup_value`
- `fabricops_kit.governance_review._coerce_rows`

## Maintainer/developer implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `99_explore`

**Side effects:**

Reads METADATA_DATA_CATALOGUE from the configured metadata target only; does not write metadata.

**Notes:**

This helper is read-only. It reads ``METADATA_DATA_CATALOGUE`` from the
configured metadata target and does not write audit, approval, guardrail, or
pipeline metadata.

</details>

??? info "Maintainer/developer call flow"

    This maintainer/developer view is for source navigation, dependency review, and refactor planning. Internal/private helpers shown here are implementation details, not public API or normal notebook-callable concepts.

    Unique internal/private helpers: 10. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>get_latest_metadata_catalogue(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L78-L93"><code>_catalogue_lookup_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L187-L218"><code>_get_spark(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
    </div>

    ### Refactor signals

    <div class="callable-flow-table-wrap" markdown="0">
    <table class="callable-flow-table">
    <thead>
    <tr>
    <th class="flow-cell-name">Helper</th>
    <th class="flow-cell-module">Module</th>
    <th class="flow-cell-wide">Signals</th>
    <th class="flow-cell-wide">Used by</th>
    <th class="flow-cell-wide">Calls</th>
    <th class="flow-cell-wide">Suggested action</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a></td>
    <td class="flow-cell-module"><code>config</code></td>
    <td class="flow-cell-wide">High-fanout helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L995-L1019"><code>_detect_nested_metadata_delta_folders</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1103-L1110"><code>_resolve_metadata_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L736-L836"><code>_run_config_smoke_tests</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L1145-L1191"><code>_validate_metadata_table_registration</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L839-L949"><code>setup_notebook</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L551-L594"><code>read_lakehouse_csv</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L913-L1000"><code>read_lakehouse_excel</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L786-L910"><code>read_lakehouse_parquet</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L597-L659"><code>read_warehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L662-L727"><code>write_warehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a></td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a></td>
    <td class="flow-cell-wide">Keep stable</td>
    </tr>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a></td>
    <td class="flow-cell-module"><code>fabric_input_output</code></td>
    <td class="flow-cell-wide">High-fanout helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L604-L613"><code>_list_all_data_agreement_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L493-L494"><code>_write_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1600-L1607"><code>_read_guardrail_rule_metadata</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L965-L966"><code>_read_metadata_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2026-L2040"><code>_read_metadata_table_or_empty</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2085-L2096"><code>_write_rule_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L750-L760"><code>_write_table_metadata_enrichment_records</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194"><code>get_latest_metadata_catalogue</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1113-L1224"><code>record_table_governance</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L691-L913"><code>enforce_profile_behavior</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L398-L448"><code>_load_notebook_registry</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L276-L395"><code>_register_current_notebook</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L953-L1060"><code>write_catalogue_evidence</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1062-L1149"><code>write_pipeline_lineage</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321"><code>write_pipeline_run_summary</code></a></td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a></td>
    <td class="flow-cell-wide">Keep stable</td>
    </tr>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L187-L218"><code>_get_spark</code></a></td>
    <td class="flow-cell-module"><code>fabric_input_output</code></td>
    <td class="flow-cell-wide">Leaf internal helper, High-fanout helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L551-L594"><code>read_lakehouse_csv</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L913-L1000"><code>read_lakehouse_excel</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L786-L910"><code>read_lakehouse_parquet</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L597-L659"><code>read_warehouse_table</code></a></td>
    <td class="flow-cell-wide">—</td>
    <td class="flow-cell-wide">Keep stable</td>
    </tr>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a></td>
    <td class="flow-cell-module"><code>fabric_input_output</code></td>
    <td class="flow-cell-wide">Leaf internal helper, High-fanout helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L131-L135"><code>_qualified_table_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L157-L161"><code>_resolve_lakehouse_table_identifier</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L382-L435"><code>read_lakehouse_table</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table</code></a></td>
    <td class="flow-cell-wide">—</td>
    <td class="flow-cell-wide">Keep stable</td>
    </tr>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a></td>
    <td class="flow-cell-module"><code>governance_review</code></td>
    <td class="flow-cell-wide">Leaf internal helper, High-fanout helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L965-L966"><code>_read_metadata_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2026-L2040"><code>_read_metadata_table_or_empty</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194"><code>get_latest_metadata_catalogue</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L441-L457"><code>load_catalogue_profile_rows</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1722-L1760"><code>resolve_table_governance_policy</code></a></td>
    <td class="flow-cell-wide">—</td>
    <td class="flow-cell-wide">Keep stable</td>
    </tr>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a></td>
    <td class="flow-cell-module"><code>config</code></td>
    <td class="flow-cell-wide">Thin wrapper candidate, Single-use internal helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a></td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig</code></a></td>
    <td class="flow-cell-wide">Inspect for inline</td>
    </tr>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L78-L93"><code>_catalogue_lookup_value</code></a></td>
    <td class="flow-cell-module"><code>governance_review</code></td>
    <td class="flow-cell-wide">Single-use internal helper, Leaf internal helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194"><code>get_latest_metadata_catalogue</code></a></td>
    <td class="flow-cell-wide">—</td>
    <td class="flow-cell-wide">Review purpose</td>
    </tr>
    <tr>
    <td class="flow-cell-name"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a></td>
    <td class="flow-cell-module"><code>fabric_input_output</code></td>
    <td class="flow-cell-wide">Leaf internal helper</td>
    <td class="flow-cell-wide"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L131-L135"><code>_qualified_table_name</code></a>, <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a></td>
    <td class="flow-cell-wide">—</td>
    <td class="flow-cell-wide">Keep if transformation or validation</td>
    </tr>
    </tbody>
    </table>
    </div>

This callable uses 10 internal helpers for metadata loading, rule parsing, fabric or spark access, and other.

<div class="reference-helper-groups">
  <section class="reference-helper-group">
    <h4>Metadata loading</h4>
    <p>Load and identify the metadata or table context needed by the callable.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Rule parsing</h4>
    <p>Normalize stored or user-provided values before applying rules.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Fabric or Spark access</h4>
    <p>Access Fabric or Spark runtime services used by the implementation.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L187-L218"><code>_get_spark</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Other</h4>
    <p>Support lower-level implementation details that do not fit the main helper areas.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L78-L93"><code>_catalogue_lookup_value</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>
    </div>
  </section>
</div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.get_latest_metadata_catalogue`
- Short name: `get_latest_metadata_catalogue`
- Module: `governance_review`
- Public surface: Public Starter Kit function
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `96`
- Used by references count: 0
- Calls references count: 5
- Used in templates: 99_explore
- Glossary terms: metadata lakehouse, profile, data agreement

### Implementation contract

- **required_context:** Requires the metadata target configured by 00_env_config and optionally METADATA_SCHEMA for schema-enabled metadata lakehouses.
- **inputs:** table_name, optional agreement context, metadata_schema, spark_session, and advanced context override.
- **output:** Latest matching catalogue rows as a Spark DataFrame when possible, otherwise a list of dictionaries. Missing catalogue evidence returns a friendly not_found row.
- **side_effects:** Reads METADATA_DATA_CATALOGUE from the configured metadata target only; does not write metadata.
- **failure_modes:** Not documented yet
- **verification:** Verify exploratory notebooks call this helper only for context lookup and do not call write or guardrail helpers.

### Used by references

Not documented yet

### Calls references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- `fabricops_kit.fabric_input_output.read_lakehouse_table`
- `fabricops_kit.governance_review._catalogue_lookup_value`
- `fabricops_kit.governance_review._coerce_rows`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L96-L194</a>
- Start line: `96`
- End line: `194`
- Signature:

```python
def get_latest_metadata_catalogue(
    table_name: str,
    agreement: Mapping[str, Any] | None=None,
    metadata_schema: str | None=None,
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
) -> Any:
```

### Maintainer/developer relationship graph

### Public related functions

- <a href="read_data/"><code>fabricops_kit.fabric_input_output.read_data</code></a>
- <a href="profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- `fabricops_kit.data_agreement.widget_select_agreement`

### Internal implementation summary

- Internal helper count: 10
- Grouped helper summary is rendered in the page-level maintainer/developer implementation details section; helper chips link to source.

</details>

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Profile</span><span class="glossary-chip-definition">Reusable measurements about source data or pipeline outputs, such as schema, row count, nulls, distinct values, and distributions.</span> <a href="../../../reference/glossary/#profile">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Data agreement</span><span class="glossary-chip-definition">FabricOps agreement record that captures ownership, steward context, usage, and expectations.</span> <a href="../../../reference/glossary/#data-agreement">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
