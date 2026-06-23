# get_latest_metadata_catalogue

??? info "Downstream callables: 4"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>get_latest_metadata_catalogue(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L146-L166"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L31-L88"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L225-L233"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L321-L331"><code>read_lakehouse_table_core(...)</code></a></div>
    </div>

Fetch the latest metadata catalogue rows for a table without writing metadata.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>governance_review</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

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
| `table_name` | `str` | Yes | Not documented yet |
| `agreement` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `metadata_schema` | `str \| None` | No | Not documented yet |
| `spark_session` | `Any` | No | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |

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

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Profile</span><span class="glossary-chip-definition">Reusable measurements about source data or pipeline outputs, such as schema, row count, nulls, distinct values, and distributions.</span> <a href="../../../reference/glossary/#profile">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Data agreement</span><span class="glossary-chip-definition">FabricOps agreement record that captures ownership, steward context, usage, and expectations.</span> <a href="../../../reference/glossary/#data-agreement">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
