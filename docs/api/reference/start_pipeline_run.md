# start_pipeline_run

??? info "Downstream callables: 7"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>start_pipeline_run(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L1027-L1043"><code>get_selected_agreement(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_agreement.py#L788-L1024"><code>widget_select_agreement(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L146-L166"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L31-L88"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L225-L233"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L322-L326"><code>read_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L329-L342"><code>write_lakehouse_table_core(...)</code></a></div>
    </div>

Start a guided notebook run and store runtime defaults.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>pipeline</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage guidance

### Use when

- Use near the top of 02_pipeline or read-only exploration notebooks that need agreement-aware runtime defaults.

### Do not use when

- Do not use when an advanced custom notebook needs to pass every runtime parameter explicitly to lower-level helpers.

### Additional context

Resolves runtime and agreement context once so template notebooks can call guardrail and summary helpers with concise defaults.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def start_pipeline_run(
    notebook_type: str='02_pipeline',
    select_agreement: bool=False,
    register_notebook: bool=False,
    read_only: bool=False,
    run_context: Any=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    pipeline_name: str | None=None,
    context: dict[str, Any] | None=None,
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
PIPELINE = start_pipeline_run(notebook_type="02_pipeline", select_agreement=True, register_notebook=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `notebook_type` | `str` | No | FabricOps notebook type to associate with the active context. |
| `select_agreement` | `bool` | No | When True, render the agreement selector and capture the selected agreement for downstream defaults. |
| `register_notebook` | `bool` | No | When True, allow ``widget_select_agreement`` to register this notebook to the selected agreement. Use ``False`` for read-only exploration. |
| `read_only` | `bool` | No | Marks the active context as read-only for exploratory notebooks. The startup helper itself does not write metadata unless ``register_notebook=True`` is explicitly requested. |
| `run_context` | `Any` | No | ``RUN_CONTEXT`` from ``00_env_config``. Defaults to the active notebook variable named ``RUN_CONTEXT``. |
| `spark_session` | `Any` | No | Spark session. Defaults to the active notebook variable named ``spark``. |
| `metadata_schema` | `str \| None` | No | ``METADATA_SCHEMA`` from ``00_env_config`` when schema routing is used. |
| `pipeline_name` | `str \| None` | No | Friendly pipeline name. Defaults to Fabric runtime notebook metadata. |
| `context` | `dict[str, Any] \| None` | No | Advanced FabricOps context override. |

## Returns

Internal runtime context object with run_id, pipeline_name, notebook identity, agreement identity, and Spark context for downstream defaults. The concrete context class is internal and not a primary public API.

### Return interpretation

The returned context can be assigned to PIPELINE for target config and lineage fields while downstream helpers read the same active defaults automatically. The concrete context class is internal and not a primary public API.

## Raises / Errors

Not documented yet

### Common failure causes

- RUN_CONTEXT is unavailable.
- spark is unavailable.
- No agreement exists when select_agreement=True.
- The user has not selected an agreement.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Data agreement</span><span class="glossary-chip-definition">FabricOps agreement record that captures ownership, steward context, usage, and expectations.</span> <a href="../../../reference/glossary/#data-agreement">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)
