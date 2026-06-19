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

## Implementation details

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

??? info "Call flow"

    Unique internal helpers: 10. Repeated calls may appear in multiple branches.

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
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `96`
- Inbound references count: 0
- Outbound references count: 5
- Used in templates: 99_explore
- Glossary terms: metadata lakehouse, profile, data agreement

### Implementation contract

- **required_context:** Requires the metadata target configured by 00_env_config and optionally METADATA_SCHEMA for schema-enabled metadata lakehouses.
- **inputs:** table_name, optional agreement context, metadata_schema, spark_session, and advanced context override.
- **output:** Latest matching catalogue rows as a Spark DataFrame when possible, otherwise a list of dictionaries. Missing catalogue evidence returns a friendly not_found row.
- **side_effects:** Reads METADATA_DATA_CATALOGUE from the configured metadata target only; does not write metadata.
- **failure_modes:** Not documented yet
- **verification:** Verify exploratory notebooks call this helper only for context lookup and do not call write or guardrail helpers.

### Inbound references

Not documented yet

### Outbound references

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

### Internal relationship graph

### Public related functions

- <a href="read_data/"><code>fabricops_kit.fabric_input_output.read_data</code></a>
- <a href="profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

### Internal implementation summary

- Internal helper count: 10
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Profile</span><span class="glossary-chip-definition">Reusable measurements about source data or pipeline outputs, such as schema, row count, nulls, distinct values, and distributions.</span> <a href="../../../reference/glossary/#profile">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Data agreement</span><span class="glossary-chip-definition">FabricOps agreement record that captures ownership, steward context, usage, and expectations.</span> <a href="../../../reference/glossary/#data-agreement">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
